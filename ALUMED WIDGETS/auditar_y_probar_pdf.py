import os
import re
import json

out_lines = []
out_lines.append("==========================================================")
out_lines.append("  AUDITORIA Y PRUEBA DE CARGA DE CARPETA FUENTE 'pdf/'")
out_lines.append("==========================================================")

cwd = os.getcwd()
pdf_root = os.path.join(cwd, "pdf")
out_lines.append(f"1. Ruta absoluta resuelta para PDF/: {pdf_root}")
out_lines.append(f"2. Existe la carpeta 'pdf/'?: {os.path.exists(pdf_root)}")

autorizadas = [
    "anatomia-a",
    "anatomia-b",
    "anatomia-c",
    "biologia",
    "histologia-embriologia"
]

out_lines.append("\n--- 3. VERIFICACION DE MATERIAS AUTORIZADAS ---")
archivos_prueba = {}

for m in autorizadas:
    m_path = os.path.join(pdf_root, m)
    if os.path.exists(m_path):
        found_files = []
        for root, dirs, files in os.walk(m_path):
            for f in files:
                if f.lower().endswith(('.pdf', '.pptx', '.ppt')):
                    rel = os.path.relpath(os.path.join(root, f), pdf_root)
                    found_files.append(rel)
        
        archivos_prueba[m] = found_files[0] if found_files else None
        out_lines.append(f" [OK] Materia '{m}': {len(found_files)} archivos academicos. Ejemplo real: {found_files[0] if found_files else 'Sin archivos'}")
    else:
        out_lines.append(f" [ERR] Materia '{m}': Ruta no encontrada ({m_path})")

out_lines.append("\n--- 4. PURGA DE DEPENDENCIAS LEGADAS ---")
patrones_legados = [
    r"PDF APUNTES",
    r"PDF_APUNTES",
    r"PDFS_APUNTES",
    r"APUNTES PDFS",
    r"pdf-apuntes"
]

archivos_proyecto = ["data.js", "app.js", "index.html", "excavador_definitivo.py", "clasificador_tp.js"]
purv_count = 0

for file_name in archivos_proyecto:
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            content = f.read()
            
        modified = False
        for p in patrones_legados:
            if re.search(p, content, re.IGNORECASE):
                content = re.sub(p, "pdf", content, flags=re.IGNORECASE)
                modified = True
                purv_count += 1
                
        if modified:
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(content)
            out_lines.append(f"   -> Saneado: {file_name}")

out_lines.append(f"Total de referencias legadas purgadas: {purv_count}")

out_lines.append("\n--- 5. PRUEBA DE CONSUMO DESDE DATA.JS ---")
with open("data.js", "r", encoding="utf-8") as f:
    raw = f.read()

first_b = raw.find('{')
last_b = raw.rfind('}')
banco = json.loads(raw[first_b:last_b+1])

choices = banco.get("choices", [])

for m, sample_rel in archivos_prueba.items():
    if sample_rel:
        matched = [q for q in choices if sample_rel.lower() in (q.get("fuenteInterna", "") or "").lower()]
        out_lines.append(f" [CONSUMO] Materia '{m}': {len(matched)} preguntas consumidas activamente desde '{sample_rel}'")

out_lines.append("\n==========================================================")
out_lines.append("AUDITORIA DE RUTA PDF/ COMPLETADA EXITOSAMENTE.")
out_lines.append("==========================================================")

final_out = "\n".join(out_lines).encode("ascii", "replace").decode("ascii")
print(final_out)
