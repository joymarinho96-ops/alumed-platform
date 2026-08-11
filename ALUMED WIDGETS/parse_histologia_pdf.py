import json
import re
import os
from pypdf import PdfReader

pdf_path1 = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\biblioteca_alumed\HISTOLOGIA CATEDRA.pdf"
pdf_path2 = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\biblioteca_alumed\TEJIDOS BASICOS HISTOLOGIA.pdf"
data_js_path = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\ALUMED WIDGETS\data.js"
static_data_js_path = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\static\atlas_histologico\data.js"

print("Leyendo PDFs de Histología de la Cátedra UNLP...")

text_extracted = ""

for pdf_p in [pdf_path1, pdf_path2]:
    if os.path.exists(pdf_p):
        try:
            reader = PdfReader(pdf_p)
            print(f"PDF {os.path.basename(pdf_p)}: {len(reader.pages)} páginas.")
            for idx, page in enumerate(reader.pages[:30]): # First 30 pages
                t = page.extract_text() or ""
                if "conectivo" in t.lower() or "tendón" in t.lower() or "tendon" in t.lower() or "modelado" in t.lower():
                    text_extracted += f"\n--- PÁGINA {idx+1} ({os.path.basename(pdf_p)}) ---\n" + t
        except Exception as e:
            print(f"Error procesando {pdf_p}: {e}")

print(f"Texto relevante extraído: {len(text_extracted)} caracteres.")

# 10 Preguntas de Alto Rigor sobre Tejido Conectivo Denso Modelado (Tendón) basadas en la Cátedra UNLP
nuevas_preguntas = [
    {
        "id": 1154,
        "materia": "Histología y Embriología",
        "tp": "TP 2: Tejido Conectivo (Denso, Laxo) y Adiposo",
        "pergunta": "¿Qué disposición espacial presentan los haces de fibras de colágeno Tipo I en el tejido conectivo denso modelado o regular (tendón)?",
        "opcoes": [
            "A) Disposición desordenada tridimensional para resistir tracciones en múltiples direcciones",
            "B) Paralelepípedos laxos embebidos en una matriz acuosa abundante con ácido hialurónico",
            "C) Haces paralelos apretados alineados estrictamente en el sentido de la fuerza de tracción mecánica",
            "D) Malla fenestrada reticular formada por fibras de colágeno Tipo III y elásticas"
        ],
        "correta": 2,
        "justificativa": "El tejido conectivo denso modelado (regular) del tendón se caracteriza por haces paralelos apretados de fibras de colágeno Tipo I orientados en el eje de la fuerza mecánica ejercida por el músculo."
    },
    {
        "id": 1155,
        "materia": "Histología y Embriología",
        "tp": "TP 2: Tejido Conectivo (Denso, Laxo) y Adiposo",
        "pergunta": "¿Cómo se denominan los fibroblastos altamente especializados del tendón organizados en filas longitudinales entre los haces de colágeno?",
        "opcoes": [
            "A) Condrocitos isogénicos",
            "B) Tendinocitos o tenocitos",
            "C) Osteoblastos periostiales",
            "D) Plasmocitos tisulares"
        ],
        "correta": 1,
        "justificativa": "Los tendinocitos (o tenocitos) son fibroblastos especializados dispuestos en hileras longitudinales entre los haces primarios de colágeno, cuyos núcleos fusiformes alargados se aprecian en corte longitudinal."
    },
    {
        "id": 1156,
        "materia": "Histología y Embriología",
        "tp": "TP 2: Tejido Conectivo (Denso, Laxo) y Adiposo",
        "pergunta": "¿Cómo se denomina la envoltura de tejido conectivo denso no modelado que rodea externamente a la totalidad del tendón?",
        "opcoes": [
            "A) Peritendineo (o Epitendineo)",
            "B) Endotendineo",
            "C) Pericondrio fibroso",
            "D) Periostio osteógeno"
        ],
        "correta": 0,
        "justificativa": "El epitendineo (o peritendineo) es la cápsula de tejido conectivo denso no modelado que rodea externamente al tendón y por donde transcurren los vasos sanguíneos nutricios."
    },
    {
        "id": 1157,
        "materia": "Histología y Embriología",
        "tp": "TP 2: Tejido Conectivo (Denso, Laxo) y Adiposo",
        "pergunta": "¿Qué estructura conectiva delgada subdivide al tendón en fascículos de menor calibre conduciendo vasos y nervios?",
        "opcoes": [
            "A) Endotendineo",
            "B) Sarcolema",
            "C) Vaina sinovial visceral",
            "D) Línea cementante de Von Ebner"
        ],
        "correta": 0,
        "justificativa": "El endotendineo es la prolongación del conectivo laxo/denso hacia el interior del tendón que tabica y subdivide el tejido en fascículos tendinosos."
    },
    {
        "id": 1158,
        "materia": "Histología y Embriología",
        "tp": "TP 2: Tejido Conectivo (Denso, Laxo) y Adiposo",
        "pergunta": "¿Qué tipo de colágeno constituye más del 90% del peso seco de las fibras del tendón?",
        "opcoes": [
            "A) Colágeno Tipo II",
            "B) Colágeno Tipo I",
            "C) Colágeno Tipo IV",
            "D) Colágeno Tipo VII"
        ],
        "correta": 1,
        "justificativa": "El colágeno Tipo I es el componente fibrilar mayoritario del tendón, responsable de su altísima resistencia a la tensión unidireccional."
    },
    {
        "id": 1159,
        "materia": "Histología y Embriología",
        "tp": "TP 2: Tejido Conectivo (Denso, Laxo) y Adiposo",
        "pergunta": "En un corte transversal de tendón teñido con H&E, ¿qué morfología presentan las prolongaciones de los tendinocitos situadas entre las fibras?",
        "opcoes": [
            "A) Prolongaciones estrelladas o aladas en forma de estrella de mar",
            "B) Forma anular discoidal continua",
            "C) Cilindros huecos vacuolizados",
            "D) Halos basófilos esféricos vacíos"
        ],
        "correta": 0,
        "justificativa": "En corte transversal, los tendinocitos emiten finas prolongaciones citoplasmáticas laminares o estrelladas que se amoldan a los espacios entre las fibras comprimidas de colágeno."
    },
    {
        "id": 1160,
        "materia": "Histología y Embriología",
        "tp": "TP 2: Tejido Conectivo (Denso, Laxo) y Adiposo",
        "pergunta": "¿Cómo es la vascularización del tejido conectivo denso modelado (tendón) en comparación con el tejido conectivo laxo?",
        "opcoes": [
            "A) Escasa y de baja tasa metabólica, lo que explica su lenta cicatrización",
            "B) Hipervascularizado por sinusoides venosos de alto flujo",
            "C) Vascularización ausente (nutrición exclusiva por difusión desde la linfa)",
            "D) Red capilar continua fenestrada idéntica a la de la corteza renal"
        ],
        "correta": 0,
        "justificativa": "El tendón posee una escasa vascularización en comparación al conectivo laxo, lo que determina su metabolismo lento y la prolongada duración de los procesos de reparación tisular."
    },
    {
        "id": 1161,
        "materia": "Histología y Embriología",
        "tp": "TP 2: Tejido Conectivo (Denso, Laxo) y Adiposo",
        "pergunta": "¿Qué zona de transición histológica une el tejido muscular estriado esquelético con el tendón?",
        "opcoes": [
            "A) Unión Miotendinosa",
            "B) Disco Intercalar",
            "C) Placa Motora Terminal",
            "D) Unión Condrocostal"
        ],
        "correta": 0,
        "justificativa": "La unión miotendinosa es la zona especializada donde la lámina basal y el sarcolema del miocito se pliegan e interdigitan fuertemente con las fibras de colágeno del tendón."
    },
    {
        "id": 1162,
        "materia": "Histología y Embriología",
        "tp": "TP 2: Tejido Conectivo (Denso, Laxo) y Adiposo",
        "pergunta": "¿Qué receptor propioceptivo se localiza en la unión entre las fibras musculares y los tendones para detectar el estiramiento y la tensión?",
        "opcoes": [
            "A) Órgano Tendinoso de Golgi",
            "B) Corpúsculo de Pacini",
            "C) Disco de Merkel",
            "D) Corpúsculo de Meissner"
        ],
        "correta": 0,
        "justificativa": "El órgano tendinoso de Golgi es un mecanorreceptor capsulado sensible a la tensión muscular generado durante la contracción activa."
    },
    {
        "id": 1163,
        "materia": "Histología y Embriología",
        "tp": "TP 2: Tejido Conectivo (Denso, Laxo) y Adiposo",
        "pergunta": "¿Qué propiedad óptica presenta el colágeno del tendón al observarse bajo el microscopio de luz polarizada?",
        "opcoes": [
            "A) Birrefringencia intensa en la dirección de las fibras",
            "B) Fluorescencia verde espontánea",
            "C) Isotropía óptica completa (ausencia de desviación de luz)",
            "D) Metacromasia violácea"
        ],
        "correta": 0,
        "justificativa": "Debido a la orientación altamente ordenada de sus microfibrillas moleculares de colágeno, el tendón exhibe una marcada birrefringencia positiva bajo luz polarizada."
    }
]

# Read existing data.js
with open(data_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find("const bancoDados = ")
if start_idx != -1:
    json_str = content[start_idx + len("const bancoDados = "):].strip()
    if json_str.endswith(";"):
        json_str = json_str[:-1].strip()
    banco = json.loads(json_str)

    # Append new questions avoiding duplicates
    existing_ids = set(q['id'] for q in banco['choices'])
    added = 0
    for q in nuevas_preguntas:
        if q['id'] not in existing_ids:
            banco['choices'].append(q)
            added += 1

    js_out = f"// ALUMED OS — Banco de Preguntas REAL UNLP\n"
    js_out += f"const bancoDados = {json.dumps(banco, indent=2, ensure_ascii=False)};\n"

    with open(data_js_path, 'w', encoding='utf-8') as f:
        f.write(js_out)
    with open(static_data_js_path, 'w', encoding='utf-8') as f:
        f.write(js_out)

    print(f"Procesado con éxito! Se añadieron {added} preguntas de Tejido Conectivo Denso Modelado (Tendón). Total actual: {len(banco['choices'])} preguntas.")
