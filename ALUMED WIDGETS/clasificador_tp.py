import json
import re
import os

# Definition of TP syllabus maps for all subjects/cátedras
MAPAS_TP = {
    "Biología": {
        "TP1": {"nombre": "Introducción a la Biología & Organización Celular", "keywords": ["procariota", "eucariota", "célula", "organela", "virus", "viroide", "prion"]},
        "TP2": {"nombre": "Componentes Químicos I (Agua y Pequeñas Moléculas)", "keywords": ["agua", "puente de hidrógeno", "ph", "buffer", "tampón", "ion", "hidrofílico", "hidrofóbico"]},
        "TP3": {"nombre": "Componentes Químicos II (Lípidos y Macromoléculas)", "keywords": ["lípido", "proteína", "carbohidrato", "aminoácido", "enlace peptídico", "glúcido", "ácido graso", "triglicérido", "fosfolípido"]},
        "TP4": {"nombre": "Bioenergética y Cinética Enzimática", "keywords": ["enzima", "catálisis", "sitio activo", "km", "vmax", "inhibidor", "alostérico", "atp", "energía libre", "termodinámica"]},
        "TP5": {"nombre": "Mecanismos Genéticos Básicos I", "keywords": ["adn", "arn", "nucleótido", "replicación", "polimerasa", "horquilla", "codón", "genes"]},
        "TP6": {"nombre": "Mecanismos Genéticos Básicos II (Expresión y Regulación)", "keywords": ["transcripción", "traducción", "promotor", "operón", "splicing", "intrón", "exón", "ribosoma", "arnt", "arnm"]},
        "TP7": {"nombre": "Membrana Plasmática y Transporte (Ósmosis/Osmolaridad)", "keywords": ["membrana", "transporte", "difusión", "ósmosis", "osmolaridad", "bomba", "na+/k+", "canales", "acuaporina", "bicapa"]},
        "TP8": {"nombre": "Metabolismo Intermedio y Mitocondrias", "keywords": ["mitocondria", "glucólisis", "krebs", "cadena respiratoria", "fosforilación oxidativa", "piruvato", "atp sintasa"]},
        "TP9": {"nombre": "Membranas Internas I (RE y Golgi)", "keywords": ["retículo", "endoplásmico", "golgi", "glicosilación", "secreción", "vesícula", "somatico", "rugoso", "liso"]},
        "TP10": {"nombre": "Membranas Internas II (Lisosomas y Peroxisomas)", "keywords": ["lisosoma", "peroxisoma", "endosoma", "fagocitosis", "autofagia", "hidrolasa", "catalasa", "digestión celular"]},
        "TP11": {"nombre": "El Núcleo Celular", "keywords": ["núcleo", "envoltura nuclear", "poro nuclear", "nucleólo", "cromatina", "heterocromatina", "eucromatina", "histona"]},
        "TP12": {"nombre": "Citoesqueleto, Adhesión y Matriz Extracelular", "keywords": ["citoesqueleto", "microtúbulo", "microfilamento", "filamento intermedio", "actina", "tubulina", "cilio", "flagelo", "matriz extracelular", "colágeno"]},
        "TP13": {"nombre": "Ciclo Celular y Apoptosis", "keywords": ["ciclo celular", "g1", "g2", "s", "p53", "cdk", "ciclina", "checkpoint", "punto de control", "apoptosis", "caspasa"]},
        "TP14": {"nombre": "Mecanismos de División Celular (Mitosis y Meiosis)", "keywords": ["mitosis", "meiosis", "profase", "metafase", "anafase", "telofase", "huso", "crossing over", "recombinación", "gameto"]},
        "TP15": {"nombre": "Transmisión del Material Genético", "keywords": ["mendel", "herencia", "alelo", "genotipo", "fenotipo", "dominante", "recesivo", "ligado al sexo"]},
        "TP16": {"nombre": "Las Células en su Contexto Social (Comunicación)", "keywords": ["comunicación celular", "receptor", "ligando", "segundo mensajero", "ampc", "quinasa", "transducción", "señalización"]}
    },
    "Histología y Embriología": {
        "TP1": {"nombre": "Técnica Histológica", "keywords": ["técnica", "fijación", "hematoxilina", "eosina", "tinción", "microscopio", "corte", "parafina"]},
        "TP2": {"nombre": "Tejido Epitelial", "keywords": ["epitelio", "revestimiento", "glandular", "cilio", "microvellosidad", "lámina basal", "unión ocluyente", "desmosoma"]},
        "TP3": {"nombre": "Tejido Conectivo y Adiposo", "keywords": ["conectivo", "conjuntivo", "fibroblasto", "colágeno", "matriz", "adipocito", "grasa", "laxo", "denso"]},
        "TP4": {"nombre": "Tejido Cartilaginoso y Óseo", "keywords": ["hueso", "cartílago", "osteocito", "osteoblasto", "osteoclasto", "condrocito", "osteona", "havers", "trabécula"]},
        "TP5": {"nombre": "Sangre y Hematopoyesis", "keywords": ["sangre", "glóbulo", "eritrocito", "leucocito", "plaqueta", "médula ósea", "hematopoyesis", "neutrófilo", "linfocito"]},
        "TP6": {"nombre": "Tejido Nervioso y Sistema Nervioso", "keywords": ["neurona", "axón", "dendrita", "glía", "astroctio", "oligodendrocito", "mielina", "sinapsis", "sustancia gris", "sustancia blanca"]},
        "TP7": {"nombre": "Tejido Muscular", "keywords": ["músculo", "estriado", "liso", "cardíaco", "sarcómero", "miocito", "miofilamento", "disco intercalar"]},
        "TP8": {"nombre": "Sistema Cardiovascular", "keywords": ["vaso", "arteria", "vena", "capilar", "endotelio", "corazón", "miocardio", "endocardio"]},
        "TP9": {"nombre": "Tejido Linfoide y Sistema Linfoide", "keywords": ["linfático", "ganglio", "bazo", "timo", "amígdala", "folículo linfoide"]},
        "TP10": {"nombre": "Embriología: Fecundación y Primeras Semanas", "keywords": ["fecundación", "zocota", "mórula", "blastocisto", "implantación", "trofoblasto", "embrioblasto", "segregación"]},
        "TP11": {"nombre": "Embriología: 3ª y 4ª Semana (Gastrulación/Neurulación)", "keywords": ["gastrulación", "ectodermo", "mesodermo", "endodermo", "notocorda", "tubo neural", "somita", "neurulación"]},
        "TP12": {"nombre": "Embriología: Placenta y Anexos Embrionarios", "keywords": ["placenta", "corion", "amnios", "cordón umbilical", "vellosidad coriónica", "saco vitelino"]}
    },
    "Anatomía Cátedra A": {
        "TP1": {"nombre": "Huesos del Miembro Superior", "keywords": ["escápula", "clavícula", "húmero", "cúbito", "radio", "carpo", "metacarpo", "falange"]},
        "TP2": {"nombre": "Huesos del Miembro Inferior", "keywords": ["coxal", "fémur", "rótula", "tibia", "peroné", "tarso", "metatarso"]},
        "TP3": {"nombre": "Columna Vertebral y Tórax", "keywords": ["vértebra", "cervical", "torácica", "lumbar", "sacro", "costilla", "esternón"]},
        "TP4": {"nombre": "Cráneo (Bóveda y Base)", "keywords": ["frontal", "parietal", "occipital", "temporal", "esfenoides", "etmoides", "agujero", "fosa cranial"]},
        "TP5": {"nombre": "Macizo Facial", "keywords": ["maxilar", "cigomático", "nasal", "vómer", "mandíbula", "orbita"]},
        "TP6": {"nombre": "Artrología", "keywords": ["articulación", "sinovial", "ligamento", "cápsula", "menisco", "diartrosis"]},
        "TP7": {"nombre": "Miología Miembro Superior", "keywords": ["biceps", "triceps", "deltoides", "pectoral", "manguito rotador", "pronador", "supinador"]},
        "TP8": {"nombre": "Miología Miembro Inferior", "keywords": ["cuádriceps", "isquiotibial", "glúteo", "gastrocnemio", "sóleo", "aductor"]},
        "TP9": {"nombre": "Miología del Tronco", "keywords": ["recto abdominal", "oblicuo", "diafragma", "dorsal ancho", "trapecio"]},
        "TP10": {"nombre": "Miología Cabeza y Cuello", "keywords": ["estrenocleidomastoideo", "masetero", "temporal", "mimica", "suprahioideo"]}
    },
    "Anatomía Cátedra B": {
        "TP1": {"nombre": "Osteología y Artrología MMSS", "keywords": ["húmero", "radio", "cúbito", "escápula", "articulación hombro", "codo"]},
        "TP2": {"nombre": "Miología y Neurovascular MMSS", "keywords": ["plexo braquial", "arteria humoral", "nervio radial", "nervio mediano", "nervio cubital"]},
        "TP3": {"nombre": "Osteología y Artrología MMII", "keywords": ["fémur", "tibia", "cadera", "rodilla", "tobillo"]},
        "TP4": {"nombre": "Miología y Neurovascular MMII", "keywords": ["arteria femoral", "nervio ciático", "triángulo femoral", "hueco poplíteo"]},
        "TP5": {"nombre": "Esqueleto Axial y Pared Torácica", "keywords": ["columna", "tórax", "costillas", "intercostal"]}
    },
    "Anatomía Cátedra C": {
        "TP1": {"nombre": "Aparato Locomotor (MMSS y MMII)", "keywords": ["miembro superior", "miembro inferior", "hueso", "articulación", "músculo"]},
        "TP2": {"nombre": "Cabeza y Cuello", "keywords": ["cráneo", "cara", "cuello", "triángulo del cuello", "carótida"]},
        "TP3": {"nombre": "Tórax y Paredes", "keywords": ["tórax", "pared torácica", "diafragma", "mediastino"]}
    }
}

def clasificar_pregunta(item):
    materia = item.get("materia", "Biología")
    texto_completo = (item.get("pregunta", "") + " " + item.get("explicacion", "") + " " + json.dumps(item.get("opciones", []))).lower()
    
    mapa = MAPAS_TP.get(materia, MAPAS_TP["Biología"])
    
    best_tp = "TP1"
    max_score = 0
    conceptos_encontrados = []
    
    for tp_id, tp_info in mapa.items():
        score = 0
        found_kw = []
        for kw in tp_info["keywords"]:
            if kw in texto_completo:
                score += 1
                found_kw.append(kw)
        if score > max_score:
            max_score = score
            best_tp = tp_id
            conceptos_encontrados = found_kw
            
    confianza = "alta" if max_score >= 3 else ("media" if max_score >= 1 else "baja")
    estado = "clasificado" if confianza in ["alta", "media"] else "pendiente_revision"
    
    item["tpPrincipal"] = best_tp
    item["tpId"] = best_tp
    item["tema"] = mapa.get(best_tp, {}).get("nombre", "General")
    item["subtema"] = conceptos_encontrados[0].capitalize() if conceptos_encontrados else "Conceptos Básicos"
    item["conceptosClave"] = conceptos_encontrados if conceptos_encontrados else ["general"]
    item["tpRelacionados"] = [tp for tp in mapa.keys() if tp != best_tp][:2]
    item["justificacionClasificacion"] = f"Clasificado en {best_tp} por coincidencia semántica de términos: {', '.join(conceptos_encontrados[:3]) if conceptos_encontrados else 'análisis temático general'}."
    item["confianzaClasificacion"] = confianza
    item["estadoClasificacion"] = estado
    
    return item

def procesar_data_js():
    with open("data.js", "r", encoding="utf-8") as f:
        content = f.read()
        
    json_str = content.replace("const bancoDados = ", "").strip().rstrip(";")
    data = json.loads(json_str)
    
    for cat in ["choices", "pinches", "orales"]:
        if cat in data:
            for item in data[cat]:
                clasificar_pregunta(item)
                
    new_content = "const bancoDados = " + json.dumps(data, ensure_ascii=False, indent=2) + ";"
    with open("data.js", "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print(f"Total clasificados en choices: {len(data.get('choices', []))}")

if __name__ == "__main__":
    procesar_data_js()
