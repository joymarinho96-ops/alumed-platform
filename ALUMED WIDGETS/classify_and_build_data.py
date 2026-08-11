#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALUMED OS — Clasificador Estricto por Materia y TP (UNLP)
Engenharia de Software Full-Stack & Arquitetura EdTech.
Processes all raw question JSON files and formats data.js.
"""

import json
import re
import os

BASE_DIR = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\ALUMED WIDGETS"
PARSED_JSON = os.path.join(BASE_DIR, "parsed_questions.json")
OUTPUT_DATA_JS = os.path.join(BASE_DIR, "data.js")
OUTPUT_STATIC_JS = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\static\atlas_histologico\data.js"

# Rules for TP classification according to UNLP syllabus
SYLLABUS_MAP = {
    "Biología Celular": [
        ("TP 1: Agua, Soluciones y Osmolaridad / Biomoléculas", 
         ["agua", "solucion", "solución", "osmolaridad", "ósmosis", "osmosis", "biomolécula", "biomolecula", "buffer", "tampón", "tampon", "ph", "glúcido", "glucido", "lípido", "lipido", "proteína", "proteina", "ácido nucleico", "aminoácido", "aminoacido", "enlace peptídico"]),
        ("TP 2: Membrana Plasmática y Transportes",
         ["membrana", "transport", "difusión", "difusion", "bomba", "na+/k+", "atpasa", "canal", "acuaporina", "bicapa", "fluidez", "colesterol", "endocitosis", "exocitosis", "fagocitosis", "pinocitosis", "pasivo", "activo primario", "activo secundario"]),
        ("TP 3: Sistema de Endomembranas (RER, REL, Golgi, Lisosomas)",
         ["endomembrana", "rer", "rel", "retículo", "reticulo", "golgi", "lisosoma", "peroxisoma", "glicosilación", "glicosilacion", "vesícula", "vesicula", "clatrina", "copi", "copii", "secreción", "secrecion", "digestión celular"]),
        ("TP 4: Bioenergética, Mitocondria y Citoesqueleto",
         ["bioenergética", "bioenergetica", "mitocondria", "citoesqueleto", "microtúbulo", "microtubulo", "microfilamento", "filamento intermedio", "actina", "tubulina", "cilio", "flagelo", "cresta mitocondrial", "cadena respiratoria", "fosforilación oxidativa", "krebs", "atp sintasa"]),
        ("TP 5: Núcleo, Replicación y Transcripción",
         ["núcleo", "nucleo", "envoltura nuclear", "poro nuclear", "cromatina", "heterocromatina", "eucromatina", "replicación", "replicacion", "adn polimerasa", "transcripción", "transcripcion", "arn polimerasa", "promotor", "splicing", "exón", "exon", "intrón", "intron"]),
        ("TP 6: Traducción, Ciclo Celular y Mitosis/Meiosis",
         ["traducción", "traduccion", "ribosoma", "arnt", "arnm", "codón", "codon", "ciclo celular", "mitosis", "meiosis", "profase", "metafase", "anafase", "telofase", "huso", "crossing over", "recombinación", "cdk", "ciclina", "p53", "apoptosis", "caspasa"])
    ],
    "Histología y Embriología": [
        ("TP 1: Microscopía y Técnica Histológica / Tejido Epitelial",
         ["microscopía", "microscopia", "técnica histológica", "tecnica histologica", "fijación", "fijacion", "hematoxilina", "eosina", "tinción", "epitelio", "revestimiento", "glandular", "lámina basal", "desmosoma", "chapa estriada", "microvellosidad"]),
        ("TP 2: Tejido Conectivo (Denso, Laxo) y Adiposo",
         ["conectivo", "conjuntivo", "fibroblasto", "colágeno", "colageno", "matriz extracelular", "adipocito", "tejido adiposo", "laxo", "denso", "sustancia fundamental"]),
        ("TP 3: Tejido Cartilaginoso y Óseo / Osificación",
         ["cartílago", "cartilago", "hueso", "óseo", "oseo", "condrocito", "osteocito", "osteoblasto", "osteoclasto", "osteona", "havers", "volkmann", "osificación", "osificacion", "trabécula", "trabecula"]),
        ("TP 4: Tejido Muscular y Nervioso",
         ["músculo", "musculo", "estriado", "liso", "cardíaco", "cardiaco", "sarcómero", "sarcomero", "miofilamento", "neurona", "axón", "axon", "dendrita", "glía", "glia", "astrocito", "oligodendrocito", "mielina", "sinapsis"]),
        ("TP 5: Sistema Cardiovascular y Linfático / Sangre",
         ["cardiovascular", "vaso", "arteria", "vena", "capilar", "endotelio", "corazón", "corazon", "linfático", "linfatico", "ganglio", "bazo", "timo", "sangre", "eritrocito", "leucocito", "plaqueta", "hematopoyesis"]),
        ("TP Embrio 1: Primeras Semanas (Gametogénesis, Fecundación, Nidación)",
         ["gametogénesis", "gametogenesis", "espermatozoide", "ovocito", "fecundación", "fecundacion", "cigoto", "mórula", "morula", "blastocisto", "implantación", "implantacion", "nidación", "nidacion", "trofoblasto", "embrioblasto", "epiblasto", "hipoblasto", "acrosoma"]),
        ("TP Embrio 2: Gastrulación, Disco Trilaminar y Plegamiento",
         ["gastrulación", "gastrulacion", "disco trilaminar", "ectodermo", "mesodermo", "endodermo", "notocorda", "tubo neural", "neurulación", "neurulacion", "somita", "plegamiento", "nódulo de hensen"]),
        ("TP Embrio 3: Placenta, Cordón Umbilical y Anexos Embrionarios",
         ["placenta", "corion", "amnios", "cordón umbilical", "cordon umbilical", "vellosidad coriónica", "vellosidad corionica", "saco vitelino", "alantoides", "caduca"])
    ],
    "Anatomía": [
        ("TP 1: Generalidades, Osteología y Artrología",
         ["generalidades", "osteología", "osteologia", "artrología", "artrologia", "hueso", "articulación", "articulacion", "sinovial", "ligamento", "cápsula", "cervical", "columna", "cráneo", "craneo", "cara", "bóveda", "base"]),
        ("TP 2: Miembro Superior (Músculos, Vasos, Nervios, Topografía)",
         ["miembro superior", "escápula", "escapula", "clavícula", "clavicula", "húmero", "humero", "cúbito", "cubito", "radio", "carpo", "plexo braquial", "arteria axilar", "arteria humeral", "nervio radial", "nervio mediano", "nervio cubital", "axila", "biceps", "triceps", "deltoides"]),
        ("TP 3: Miembro Inferior (Músculos, Vasos, Nervios, Topografía)",
         ["miembro inferior", "coxal", "fémur", "femur", "rótula", "rotula", "tibia", "peroné", "perone", "tarso", "arteria femoral", "nervio ciático", "nervio ciatico", "triángulo femoral", "triangulo femoral", "hueco poplíteo", "hueco popliteo", "cuádriceps", "cuadriceps", "glúteo", "gluteo"]),
        ("TP 4: Esplacnología / Paredes Anteroposteriores de Tronco",
         ["esplacnología", "esplacnologia", "viscera", "víscera", "corazón", "pulmón", "pulmon", "hígado", "higado", "estómago", "estomago", "intestino", "riñón", "riñon", "mediastino", "peritoneo", "pleura", "diafragma", "recto abdominal", "oblicuo", "pared abdominal", "pared torácica"])
    ]
}

def clean_text(text):
    if not text:
        return ""
    text = text.replace("\u0000", "").replace("\ufffd", "?").strip()
    return text

def clasificar_tp(materia, texto):
    texto_lower = texto.lower()
    
    # Map materia string to canonical subject key
    cat_key = "Biología Celular"
    if "Histo" in materia or "Embrio" in materia:
        cat_key = "Histología y Embriología"
    elif "Anato" in materia:
        cat_key = "Anatomía"
    elif "Bio" in materia:
        cat_key = "Biología Celular"
        
    tps = SYLLABUS_MAP[cat_key]
    best_tp = tps[0][0]
    max_score = 0
    
    for tp_nombre, keywords in tps:
        score = sum(1 for kw in keywords if kw in texto_lower)
        if score > max_score:
            max_score = score
            best_tp = tp_nombre
            
    return best_tp

def main():
    print("Iniciando clasificación y empaquetado por TP...")
    
    with open(PARSED_JSON, 'r', encoding='utf-8') as f:
        raw_questions = json.load(f)
        
    choices = []
    for i, q in enumerate(raw_questions, 1):
        materia_raw = q.get('materia', 'Biología Celular')
        # Normalize materia name
        if "Anato" in materia_raw:
            materia = materia_raw
        elif "Histo" in materia_raw or "Embrio" in materia_raw:
            materia = "Histología y Embriología"
        else:
            materia = "Biología Celular"
            
        enunciado = clean_text(q.get('enunciado', ''))
        explicacion = clean_text(q.get('explicacion', q.get('justificativa', '')))
        opcoes_raw = q.get('opcoes', q.get('opciones', []))
        opcoes = [clean_text(o) for o in opcoes_raw if clean_text(o)]
        
        # Ensure 4 options formatted
        formatted_options = []
        letters = ['A', 'B', 'C', 'D']
        for idx, opt in enumerate(opcoes[:4]):
            if opt.startswith(('A)', 'B)', 'C)', 'D)', 'A.', 'B.', 'C.', 'D.')):
                formatted_options.append(opt)
            else:
                formatted_options.append(f"{letters[idx]}) {opt}")
                
        correta = q.get('correta', 0)
        if not isinstance(correta, int) or correta < 0 or correta >= len(formatted_options):
            correta = 0
            
        texto_comb = f"{enunciado} {explicacion} {' '.join(formatted_options)}"
        tp_assigned = clasificar_tp(materia, texto_comb)
        
        choices.append({
            "id": i,
            "materia": materia,
            "tp": tp_assigned,
            "pergunta": enunciado,
            "opcoes": formatted_options,
            "correta": correta,
            "justificativa": explicacion if explicacion else "Devolución oficial del Método Profe Joy basada en el programa de la cátedra UNLP."
        })
        
    print(f"Preguntas procesadas y clasificadas por TP: {len(choices)}")
    
    # Structure bancoDados
    bancoDados = {
        "choices": choices,
        "pinches": [
            {
                "id": 1,
                "materia": "Histología y Embriología",
                "tp": "TP 1: Microscopía y Técnica Histológica / Tejido Epitelial",
                "imagem": "assets/epitelio_cilindrico.jpg",
                "pergunta": "Identifique el preparado e indique la estructura señalada:",
                "respostasAceitas": ["epitelio cilindrico simple", "chapa estriada", "enterocito"]
            },
            {
                "id": 2,
                "materia": "Anatomía",
                "tp": "TP 2: Miembro Superior (Músculos, Vasos, Nervios, Topografía)",
                "imagem": "assets/arteria_axilar.jpg",
                "pergunta": "Identifique el vaso señalado en la fosa axilar:",
                "respostasAceitas": ["arteria axilar", "arteria humeral", "plexo braquial"]
            }
        ],
        "orales": [
            {
                "id": 1,
                "materia": "Anatomía Cátedra C",
                "tp": "TP 2: Miembro Superior (Músculos, Vasos, Nervios, Topografía)",
                "bolilla": "Bolilla: Región Axilar y Conducto Braquial",
                "casoClinico": "Paciente de 25 años presenta traumatismo en hombro con sospecha de lesión vascular en fosa axilar...",
                "checklist": ["Límites de la fosa axilar", "Contenido del paquete vasculonervioso", "Ramas de la arteria axilar"]
            }
        ]
    }
    
    # Write to data.js
    js_content = f"// ALUMED OS — Banco de Preguntas Clasificado por TP (UNLP)\n"
    js_content += f"// Generado por Arquiteto EdTech ALUMED OS\n\n"
    js_content += f"const bancoDados = {json.dumps(bancoDados, indent=2, ensure_ascii=False)};\n"
    
    with open(OUTPUT_DATA_JS, 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    with open(OUTPUT_STATIC_JS, 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print(f"data.js generado con éxito en ambos destinos!")

if __name__ == "__main__":
    main()
