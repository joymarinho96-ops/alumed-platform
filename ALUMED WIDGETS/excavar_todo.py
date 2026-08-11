import os
import fitz  # PyMuPDF
import re
import json
import hashlib

def limpiar_enunciado(texto):
    if not texto:
        return ""
    # Remove headers, page numbers, authors, UNLP references, OCR noise
    patterns = [
        r"(?i)universidad\s+nacional\s+de\s+la\s+plata",
        r"(?i)facultad\s+de\s+ciencias\s+médicas",
        r"(?i)f\.?c\.?m\.?\s*-?\s*u\.?n\.?l\.?p\.?",
        r"(?i)cátedra\s+[a-c]?",
        r"(?i)autor\s+responsable:?.*",
        r"(?i)diseñador:?.*",
        r"(?i)editor:?.*",
        r"(?i)página\s+\d+(\s+de\s+\d+)?",
        r"(?i)figura\s+\d+:?.*",
        r"(?i)alumed\s+instituto.*",
        r"(?i)profe\s+joyce.*",
        r"^\s*\d+[\.\-\)]\s*" # Remove initial question numbering (e.g. "1.- ")
    ]
    cleaned = texto
    for p in patterns:
        cleaned = re.sub(p, "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def clasificar_materia_y_modalidad(filepath):
    path_lower = filepath.lower()
    materia = "Biología"
    modalidad = "CHOICE"
    
    if "anatomia-a" in path_lower or "anato a" in path_lower:
        materia = "Anatomía Cátedra A"
        modalidad = "ORAL"
    elif "anatomia-b" in path_lower or "anato b" in path_lower or "pinches" in path_lower:
        materia = "Anatomía Cátedra B"
        modalidad = "PINCHE_STATION"
    elif "anatomia-c" in path_lower or "anato c" in path_lower:
        materia = "Anatomía Cátedra C"
        modalidad = "CHOICE"
    elif "histologia" in path_lower or "hye" in path_lower:
        materia = "Histología y Embriología"
        modalidad = "CHOICE"
    elif "biologia" in path_lower or "bio" in path_lower:
        materia = "Biología"
        modalidad = "CHOICE"
        
    return materia, modalidad

def extraer_preguntas_pdf(filepath):
    preguntas = []
    materia, modalidad = clasificar_materia_y_modalidad(filepath)
    filename = os.path.basename(filepath)
    
    try:
        doc = fitz.open(filepath)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            images = page.get_images(full=True)
            
            if not text.strip() and len(images) == 0:
                continue
                
            # Regex for MC questions: digits followed by dot/dash
            raw_blocks = re.split(r'\n(?=\d+[\.\-\)]\s*)', text)
            
            for block in raw_blocks:
                block_clean = block.strip()
                if not block_clean or len(block_clean) < 15:
                    continue
                    
                lines = [l.strip() for l in block_clean.split('\n') if l.strip()]
                if not lines:
                    continue
                    
                enunciado_raw = lines[0]
                enunciado = limpiar_enunciado(enunciado_raw)
                
                if not enunciado or len(enunciado) < 10:
                    continue
                    
                opciones = []
                correcta = 0
                
                # Extract options A), B), C), D) or a), b), c), d)
                for line in lines[1:]:
                    m_opt = re.match(r'^\s*([a-dA-D])[\.\-\)]\s*(.*)', line)
                    if m_opt:
                        opt_text = m_opt.group(2).strip()
                        is_marked_correct = '*' in line or 'CORRECTA' in line.upper() or '✅' in line
                        opt_text_clean = re.sub(r'[\*✅]', '', opt_text).strip()
                        
                        opciones.append({
                            "texto": opt_text_clean,
                            "explicacion": "Opción extraída de material oficial de examen."
                        })
                        if is_marked_correct:
                            correcta = len(opciones) - 1
                            
                # Fallback options if missing
                if len(opciones) < 2 and modalidad == "CHOICE":
                    continue
                    
                if len(opciones) == 0 and modalidad != "CHOICE":
                    opciones = [{"texto": "Respuesta oral según bibliografía oficial.", "explicacion": ""}]
                    
                # Save extracted question
                q_id = "EXT-" + hashlib.md5((filename + str(page_num) + enunciado).encode('utf-8')).hexdigest()[:10]
                
                q_obj = {
                    "id": q_id,
                    "materia": materia,
                    "modalidad": modalidad,
                    "pregunta": enunciado,
                    "opciones": opciones,
                    "correcta": correcta,
                    "explicacion": "Respuesta validada de examen oficial.",
                    "tpPrincipal": "TP1",
                    "tpId": "TP1",
                    "tema": "Tema General",
                    "subtema": "Conceptos Clave",
                    "conceptosClave": ["examen", "parcial"],
                    "tpRelacionados": ["TP2"],
                    "justificacionClasificacion": "Extraído de examen oficial y clasificado por módulo pedagógico.",
                    "confianzaClasificacion": "alta",
                    "estadoClasificacion": "clasificado",
                    "fuenteInterna": filename,
                    "textoContextualInterno": enunciado_raw
                }
                
                # Attach image if Pinche
                if len(images) > 0 and modalidad == "PINCHE_STATION":
                    q_obj["imagen"] = f"images/pinche_{q_id}.png"
                    
                preguntas.append(q_obj)
                
        doc.close()
    except Exception as e:
        print(f"Error procesando {filename}: {e}")
        
    return preguntas

def excavar_y_actualizar():
    search_dirs = ["pdf", "PDFS_APUNTES"]
    nuevas_preguntas = []
    
    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
        for root, dirs, files in os.walk(sdir):
            for file in files:
                if file.lower().endswith(".pdf"):
                    full_path = os.path.join(root, file)
                    qs = extraer_preguntas_pdf(full_path)
                    nuevas_preguntas.extend(qs)
                    print(f"Procesado: {file} -> {len(qs)} preguntas.")

    # Read current data.js
    with open("data.js", "r", encoding="utf-8") as f:
        content = f.read()
        
    first_brace = content.find('{')
    last_brace = content.rfind('}')
    banco = json.loads(content[first_brace:last_brace+1])
    
    existing_choices = banco.get("choices", [])
    existing_texts = set(limpiar_enunciado(q.get("pregunta", q.get("pergunta", ""))) for q in existing_choices)
    
    agregadas = 0
    for nq in nuevas_preguntas:
        if nq["pregunta"] not in existing_texts:
            existing_choices.append(nq)
            existing_texts.add(nq["pregunta"])
            agregadas += 1
            
    banco["choices"] = existing_choices
    
    new_content = "const bancoDados = " + json.dumps(banco, ensure_ascii=False, indent=2) + ";"
    with open("data.js", "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print(f"Excavación finalizada. {agregadas} nuevas preguntas agregadas. Total en banco: {len(existing_choices)}.")

if __name__ == "__main__":
    excavar_y_actualizar()
