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

def limpiar_enunciado(texto):
    if not texto:
        return ""
    # Quitar marcas de agua de PDF, pies de página o encabezados repetidos
    t = re.sub(r'CÁTEDRA DE HISTOLOGÍA Y EMBRIOLOGÍA.*?\n', '', texto, flags=re.IGNORECASE)
    t = re.sub(r'FACULTAD DE CIENCIAS MÉDICAS UNLP.*?\n', '', t, flags=re.IGNORECASE)
    t = re.sub(r'Página \d+ de \d+', '', t, flags=re.IGNORECASE)
    t = re.sub(r'^\d+[\.\-\)]\s*', '', t) # Quitar numeración inicial si existe
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def estructurar_feedback_joy(q):
    materia = q.get('materia', 'Histología y Embriología')
    tp = q.get('tp', 'TP General')
    just = q.get('justificativa', 'Explicación del Método Profe Joy basada en la Cátedra UNLP.')

    return f"""🎯 **1. ¿Qué está preguntando?**
Se evalúa el concepto central de {tp} ({materia}).

🔍 **2. ¿Dónde está la trampa o la lógica?**
La cátedra evalúa la capacidad de diferenciar estructuras verdaderas de distractores técnicos habituales en el examen.

💡 **3. ¿Por qué funciona así?**
{just}

👁️ **4. ¿Cómo creas la imagen mental?**
Visualiza el preparado microscópico reconociendo las características diagnósticas principales antes de seleccionar la opción."""

cleaned_count = 0
for q in choices:
    orig_p = q.get('pergunta', '')
    clean_p = limpiar_enunciado(orig_p)
    if clean_p != orig_p:
        q['pergunta'] = clean_p
        cleaned_count += 1
    
    # Asegurar feedback estructurado Profe Joy en 4 pasos
    q['justificativa'] = estructurar_feedback_joy(q)

banco['choices'] = choices

js_out = f"// ALUMED OS — Banco de Preguntas Limpio & Método Profe Joy\n"
js_out += f"const bancoDados = {json.dumps(banco, indent=2, ensure_ascii=False)};\n"

with open(data_js_path, 'w', encoding='utf-8') as f:
    f.write(js_out)
with open(static_data_js_path, 'w', encoding='utf-8') as f:
    f.write(js_out)

print(f"Limpieza completada con éxito! Se limpiaron {cleaned_count} enunciados. Total preguntas: {len(choices)}")
