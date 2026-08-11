import json
import re

with open('parsed_questions.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

def clean_question(text):
    original = text
    estado_limpieza = "Limpio"
    
    # 1. Strip leading numbers (e.g. "1.", "Pregunta 1:")
    text = re.sub(r'^\s*(Pregunta\s*\d+[:\.\-]?|\d+[\.\)\-]?)\s*', '', text, flags=re.IGNORECASE)
    
    # 2. Specific metadata removal
    # If the text has 'autor' but not at the start, it's risky to use .*
    # We will remove specific exact matches
    safe_removals = [
        r'(?i)C[AÁ]TEDRA\s+"?[A-Z]?"?\s+DE\s+[A-Z,\s]+[–\-]\s*F\.C\.M\.\s*[–\-]\s*U\.N\.L\.P\.',
        r'(?i)C[AÁ]TEDRA.*?U\.N\.L\.P\.',
        r'(?i)F\.C\.M\.',
        r'(?i)U\.N\.L\.P\.',
        r'(?i)Autor Responsable\s*:?\s*[A-Za-z\s\.]+(?=\s|\n|$)',
        r'(?i)Diseño y Edición\s*[A-Za-z\s\.]+(?=\s|\n|$)',
        r'(?i)FIG\.\s*\d+(\.\d+)?',
        r'(?i)Figura\s*\d+(\.\d+)?',
        r'(?i)P[aá]gina\s*\d+',
        r'(?i)SEGMENTACI[OÓ]N Sucesi[oó]n de mitosis.*?con autod',
        r'(?i)®\s*Cátedra.*?Reserva de derechos\..*?(?=\n|$)',
        r'(?i)®\s*\d{4}\.\s*Reserva de derechos\..*?(?=\n|$)'
    ]
    
    for p in safe_removals:
        text = re.sub(p, '', text)
    
    # Clean whitespace
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()
    
    # Check for ambiguous remaining artifacts
    ambiguous_keywords = ['autor ', 'catedra ', 'cátedra ', 'fig.', 'figura ', 'diseño ']
    if any(k in text.lower() for k in ambiguous_keywords):
        estado_limpieza = "Pendiente de limpieza manual"
        
    return original, text, estado_limpieza

cleaned_qs = []
for q in qs:
    original_text = q.get('enunciado', '')
    original_text, clean_text, estado = clean_question(original_text)
    
    new_q = {
        "id": q.get("id"),
        "materia": q.get("materia"),
        "tema": q.get("tema", ""),
        "pregunta": clean_text,
        "opciones": q.get("opcoes", []),
        "correta": q.get("correta"),
        "explicacion": q.get("justificativa", ""),
        "fuenteInterna": q.get("fuente", ""),
        "autorInterno": "",
        "paginaInterna": None,
        "figuraInterna": "",
        "textoContextualInterno": original_text,
        "estadoLimpieza": estado,
        "formato": q.get("formato")
    }
    cleaned_qs.append(new_q)

# Write parsed_questions_cleaned.json (to preserve the original for now)
with open('parsed_questions_cleaned.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_qs, f, ensure_ascii=False, indent=2)

# Overwrite data.js
with open('data.js', 'w', encoding='utf-8') as f:
    f.write('const bancoDados = {\n  choices: ')
    json.dump(cleaned_qs, f, ensure_ascii=False, indent=2)
    f.write('\n};\n')

print(f"Limpieza completada. {len(cleaned_qs)} preguntas procesadas.")
