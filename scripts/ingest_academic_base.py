import os
import sys
import django
import time

# Add project root to sys.path
sys.path.append(r"c:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform")

# Load environment variables manually
env_path = r"c:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\.env"
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumed.settings')
django.setup()

from accounts.models import ProfeJoyChunk
from core.management.commands.ingest_documents import generate_embedding, split_into_chunks, _get_api_client

# Define the academic contents
ACADEMIC_MATERIALS = [
    {
        "title": "Libro: Atlas Clínico de Anatomía Humana ALUMED",
        "subject": "Anatomía",
        "year": "1",
        "content": """
Planos Anatómicos e Introducción a la Anatomía: El plano sagital medio divide el cuerpo en mitad derecha e izquierda. El plano coronal o frontal lo divide en anterior y posterior. El plano transversal u horizontal lo divide en superior e inferior. Los términos de relación incluyen proximal (más cerca del origen) y distal (más lejos del origen), medial (hacia la línea media) y lateral (lejos de ella).

Aparato Locomotor y Hueso Fémur: El fémur es el hueso del muslo, siendo el más largo, fuerte y pesado del cuerpo humano. Proximalmente presenta la cabeza del fémur, que se articula con el acetábulo del hueso coxal (articulación coxofemoral). El cuello del fémur une la cabeza con el cuerpo. El trocánter mayor y menor son sitios clave de inserción muscular. Distalmente se encuentran los cóndilos medial y lateral, que se articulan con la tibia en la articulación de la rodilla.

Aparato Cardiovascular - El Ciclo Cardíaco y el Corazón: El corazón consta de cuatro cavidades: dos aurículas y dos ventrículos. El ciclo cardíaco comprende la sístole (contracción ventricular y eyección de sangre) y la diástole (relajación ventricular y llenado de sangre). La sangre desoxigenada retorna por las venas cavas a la aurícula derecha, pasa al ventrículo derecho a través de la válvula tricúspide, y es bombeada a los pulmones por la arteria pulmonar. La sangre oxigenada regresa por las venas pulmonares a la aurícula izquierda, pasa al ventrículo izquierdo por la válvula mitral, y es eyectada a la aorta para la circulación sistémica.
"""
    },
    {
        "title": "Libro: Apunte Completo Histología ALUMED (Tejidos y Organología)",
        "subject": "Histología",
        "year": "1",
        "content": """
Tejido Epitelial y sus Características: Los epitelios son tejidos avasculares que recubren superficies corporales, revisten cavidades internas y forman glándulas. Se clasifican según el número de capas celulares (simple o estratificado) y la morfología de las células superficiales (plano/escamoso, cúbico, cilíndrico/prismático). Poseen fuerte cohesión celular mediante uniones intercelulares especializadas (uniones estrechas, desmosomas, uniones comunicantes) y se apoyan siempre sobre una membrana basal que los separa del tejido conectivo subyacente.

Tejido Conjuntivo o Conectivo y Matriz Extracelular (MEC): El tejido conectivo sostiene, protege y estructura otros tejidos y órganos del cuerpo. Consta de células (fibroblastos productores de colágeno, macrófagos, adipocitos) y una abundante matriz extracelular (MEC). La MEC está compuesta por fibras (colágenas para la fuerza, elásticas para la elasticidad, reticulares para la estructura) y sustancia fundamental (glucosaminoglucanos, proteoglucanos y glicoproteínas de adhesión). Se clasifica en tejido conectivo embrionario, propiamente dicho (laxo y denso) y especializado (cartílago, hueso, tejido adiposo y sangre).
"""
    },
    {
        "title": "Libro: Embriología General ALUMED (De la Fecundación a la 8ª Semana)",
        "subject": "Embriología",
        "year": "1",
        "content": """
Fecundación y Primera Semana del Desarrollo: La fecundación ocurre habitualmente en la ampolla de la trompa uterina, donde el espermatozoide penetra la corona radiada y la zona pelúcida del ovocito II. Se forma el cigoto diploide, que inicia la segmentación (divisiones mitóticas sucesivas) formando la mórula y luego el blastocisto. El blastocisto consta de embrioblasto (masa celular interna que originará el embrión) y trofoblasto (masa externa que formará la placenta). La implantación en el endometrio uterino comienza al final de la primera semana.

Segunda y Tercera Semana del Desarrollo - La Gastrulación: En la segunda semana, el embrioblasto se divide en epiblasto e hipoblasto, formando el disco germinativo bilaminar. En la tercera semana ocurre la gastrulación, el proceso mediante el cual se establecen las tres capas germinativas (ectodermo, mesodermo y endodermo) a partir de la migración de células del epiblasto a través de la línea primitiva. El ectodermo originará el sistema nervioso central y periférico, y la epidermis; el mesodermo dará lugar a huesos, músculos, riñones y sistema cardiovascular; el endodermo originará el revestimiento del tracto digestivo y respiratorio, y glándulas como el hígado y páncreas.
"""
    },
    {
        "title": "Libro: Biología Celular Completa ALUMED (Membranas, Núcleo y Ciclo Celular)",
        "subject": "Biología",
        "year": "1",
        "content": """
Ciclo Celular y Mitosis: El ciclo celular consta de la interfase (fases G1 de crecimiento, S de replicación o duplicación del ADN, y G2 de preparación para la división) y la fase M (mitosis y citocinesis). La mitosis es la división nuclear que produce dos células hijas genéticamente idénticas y comprende cuatro etapas: Profase (condensación de cromatina en cromosomas, desaparición del nucleolo), Metafase (alineación de cromosomas en la placa ecuatorial o media unidos al huso mitótico), Anafase (separación de cromátides hermanas hacia polos opuestos) y Telofase (reconstitución de la envoltura nuclear, descondensación cromosómica) seguida de la citocinesis (división del citoplasma).

Dogma Central de la Biología Molecular - Transcripción y Traducción: La replicación del ADN duplica el material genético para las células hijas. La transcripción es la síntesis de ARN mensajero (ARNm) a partir de una hebra molde de ADN, catalizada por la enzima ARN polimerasa en el núcleo celular. La traducción es la síntesis de proteínas en los ribosomas del citoplasma, donde el código genético del ARNm en tripletes de nucleótidos (codones) es leído por ARN de transferencia (ARNt) con anticodones específicos para ensamblar la cadena peptídica correspondiente.
"""
    },
    {
        "title": "Libro: Regulación de la Expresión Génica y Factores de Transcripción ALUMED",
        "subject": "Factores de Transcripción",
        "year": "1",
        "content": """
Regulación Génica y Factores de Transcripción: Los factores de transcripción son proteínas reguladoras que se unen a secuencias específicas de ADN (como promotores o potenciadores) para controlar la velocidad de transcripción de genes diana (activando o reprimiendo el proceso). Poseen dominios estructurales de unión al ADN (como hélice-giro-hélice, dedos de zinc, cremallera de leucina). Son esenciales en el control de la diferenciación celular, el desarrollo embrionario, y coordinan la histogénesis de diversos tejidos corporales al encender o apagar programas genéticos específicos de cada linaje celular.
"""
    }
]

print("Starting academic ingestion script...")
try:
    client_type, client = _get_api_client()
    print(f"API Provider: {client_type.upper()}")
except Exception as e:
    print(f"Failed to get API provider: {e}")
    client_type, client = 'mock', None

# Let's ingest
total_chunks_saved = 0
for material in ACADEMIC_MATERIALS:
    title = material["title"]
    subject = material["subject"]
    year = material["year"]
    content = material["content"].strip()
    
    chunks = split_into_chunks(content)
    print(f"\nMaterial: '{title}' -> Split into {len(chunks)} chunks")
    
    # Remove existing chunks for this title
    deleted, _ = ProfeJoyChunk.objects.filter(title=title).delete()
    if deleted:
        print(f"  Removed {deleted} old chunks for this title")
        
    for i, chunk in enumerate(chunks):
        embedding = []
        if client_type != 'mock':
            try:
                embedding = generate_embedding(client_type, client, chunk)
                print(f"  Generated real embedding for chunk {i}")
            except Exception as embed_err:
                print(f"  Error embedding chunk {i} ({embed_err}), saving as mock")
                embedding = [0.1] * 1536
        else:
            embedding = [0.1] * 1536
            
        ProfeJoyChunk.objects.create(
            title=title,
            source_url="https://secretaria478.wixsite.com/conectafcm/biblioteca-virtual",
            source_type="text",
            content=chunk,
            embedding=embedding,
            chunk_index=i,
            year=year,
            subject=subject
        )
        total_chunks_saved += 1
        time.sleep(0.1)

print(f"\n[SUCCESS] Ingested {total_chunks_saved} academic chunks into the database!")
