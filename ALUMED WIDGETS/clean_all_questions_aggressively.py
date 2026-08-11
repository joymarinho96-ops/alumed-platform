import json
import re

data_js_path = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\ALUMED WIDGETS\data.js"
static_data_js_path = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\static\atlas_histologico\data.js"

with open(data_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find("const bancoDados = ")
if start_idx != -1:
    json_str = content[start_idx + len("const bancoDados = "):].strip().rstrip(";")
    banco = json.loads(json_str)
else:
    raise ValueError("const bancoDados not found")

choices = banco.get("choices", [])

def limpiar_pregunta_agresivo(texto):
    if not texto:
        return ""
    
    t = texto

    # Remove leading numbering like "5. ", "12) ", "1.- "
    t = re.sub(r'^\s*\d+[\.\-\)]\s*', '', t)

    # Remove CÁTEDRA headers
    t = re.sub(r'CÁTEDRA\s*["\']?[AB]["\']?\s*DE\s*CITOLOGÍA,?\s*HISTOLOGÍA\s*Y\s*EMBRIOLOGÍA\s*-\s*F\.?C\.?M\.?\s*-\s*U\.?N\.?L\.?P\.?', '', t, flags=re.IGNORECASE)
    t = re.sub(r'CÁTEDRA\s*.*?\s*U\.?N\.?L\.?P\.?', '', t, flags=re.IGNORECASE)
    t = re.sub(r'FACULTAD\s*DE\s*CIENCIAS\s*MÉDICAS.*?', '', t, flags=re.IGNORECASE)

    # Remove Fig / Figure / Autor / Edición credits
    t = re.sub(r'FIG\.\s*\d+[\.\d]*', '', t, flags=re.IGNORECASE)
    t = re.sub(r'Autor\s*Responsable:?.*?(Camihort|Degregori|Med\.|Diseño|\-)', '', t, flags=re.IGNORECASE)
    t = re.sub(r'Diseño\s*y\s*Edición:?.*?(Degregori|Camihort|Pablo|Gisela|\-)', '', t, flags=re.IGNORECASE)
    t = re.sub(r'Med\.\s*Gisela\s*CAMIHORT', '', t, flags=re.IGNORECASE)
    t = re.sub(r'Pablo\s*DEGREGORI', '', t, flags=re.IGNORECASE)

    # If sentence was truncated or repeated words from PDF, keep first clean question line
    # Remove repeated capitalized CÁTEDRA or credit blocks
    t = re.sub(r'SEGMENTACIÓN\s*Sucesión\s*de\s*mitosis.*', '', t, flags=re.IGNORECASE)

    # Clean multiple spaces and whitespace
    t = re.sub(r'\s+', ' ', t).strip()

    # If question starts with lowercase or fragment, capitalize
    if t and len(t) > 1:
        t = t[0].upper() + t[1:]

    return t

cleaned_count = 0
for q in choices:
    orig = q.get('pergunta', '')
    cleaned = limpiar_pregunta_agresivo(orig)
    if cleaned != orig:
        q['pergunta'] = cleaned
        cleaned_count += 1

banco['choices'] = choices

js_out = f"// ALUMED OS — Banco de Preguntas Limpio (Solo la Pregunta Directa)\n"
js_out += f"const bancoDados = {json.dumps(banco, indent=2, ensure_ascii=False)};\n"

with open(data_js_path, 'w', encoding='utf-8') as f:
    f.write(js_out)
with open(static_data_js_path, 'w', encoding='utf-8') as f:
    f.write(js_out)

print(f"Limpieza agresiva finalizada con éxito! Se limpiaron {cleaned_count} preguntas.")
