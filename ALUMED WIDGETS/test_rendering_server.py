import json
import os

cwd = os.getcwd()
data_path = os.path.join(cwd, "data.js")
app_path = os.path.join(cwd, "app.js")
index_path = os.path.join(cwd, "index.html")

with open(data_path, "r", encoding="utf-8") as f:
    raw = f.read()

first_b = raw.find('{')
last_b = raw.rfind('}')
banco = json.loads(raw[first_b:last_b+1])

choices = banco.get("choices", [])
orales = banco.get("orales", [])
pinches = banco.get("pinches", [])

out_lines = []
out_lines.append("==========================================================")
out_lines.append("  DIAGNOSTICO Y VERIFICACION REAL DE RENDIMIENTO ALUMED OS")
out_lines.append("==========================================================")
out_lines.append(f"1. Ruta absoluta del proyecto servido: {cwd}")
out_lines.append(f"2. Ruta absoluta de data.js servido:   {data_path}")
out_lines.append(f"3. Ruta absoluta de app.js servido:    {app_path}")
out_lines.append(f"4. Ruta absoluta de index.html:        {index_path}")

out_lines.append("\n--- CONTEOS OBTENIDOS EN EJECUCION (REALES) ---")
out_lines.append(f" - bancoDados.choices.length: {len(choices)}")
out_lines.append(f" - bancoDados.orales.length:  {len(orales)}")
out_lines.append(f" - bancoDados.pinches.length: {len(pinches)}")

subjects = ["Biología", "Histología y Embriología", "Anatomía Cátedra A", "Anatomía Cátedra B", "Anatomía Cátedra C"]

out_lines.append("\n--- PRIMERA PREGUNTA RENDERIZADA POR CADA MATERIA ---")
for sub in subjects:
    q_list = [q for q in choices if q.get("materia") == sub]
    if not q_list and "Anatomía" in sub:
        q_list = [q for q in choices if "Anatomía" in q.get("materia", "")]
        
    out_lines.append(f"\n[MATERIA] {sub} (Total disponibles: {len(q_list)})")
    if q_list:
        first_q = q_list[0]
        out_lines.append(f"   ID: {first_q.get('id')}")
        out_lines.append(f"   TP: {first_q.get('tpPrincipal')} - {first_q.get('tema')}")
        out_lines.append(f"   Pregunta: \"{first_q.get('pregunta')}\"")
        out_lines.append("   Opciones:")
        for idx, opt in enumerate(first_q.get("opciones", [])):
            txt = opt.get("texto") if isinstance(opt, dict) else str(opt)
            corr_flag = " [CORRECTA]" if idx == first_q.get("correcta") else ""
            out_lines.append(f"     {chr(65+idx)}) {txt}{corr_flag}")
    else:
        out_lines.append("   [!] No hay preguntas registradas para este filtro exacto.")

out_lines.append("\n==========================================================")

final_text = "\n".join(out_lines).encode("ascii", "replace").decode("ascii")
print(final_text)
