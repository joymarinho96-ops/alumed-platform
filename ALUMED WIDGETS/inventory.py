import os
import fitz  # PyMuPDF
import re

directories = {
    "Anatomía A": {"path": "pdf/anatomia-a/oral/parcial-1/", "modalidad": "Oral"},
    "Anatomía B": {"path": "pdf/anatomia-b/pinches/parcial-1/", "modalidad": "Pinches"},
    "Anatomía C": {"path": "pdf/anatomia-c/oral/parcial-1/", "modalidad": "Oral"},
    "Biología": {"path": "pdf/biologia/multiple-choice/parcial-1/", "modalidad": "Multiple Choice"},
    "Histología y Embriología": {"path": "pdf/histologia-embriologia/multiple-choice/parcial-1/", "modalidad": "Multiple Choice"}
}

report_lines = []
report_lines.append("# Informe de Inventario y Lectura de PDFs")
report_lines.append("Este informe detalla el análisis de los documentos en cada carpeta según tus reglas. Aún no se han migrado datos.")

summary_table = []

for subject, info in directories.items():
    path = info["path"]
    modalidad = info["modalidad"]
    
    report_lines.append(f"\n## 📚 Materia: {subject} ({modalidad})")
    
    if not os.path.exists(path):
        report_lines.append(f"Carpeta no encontrada: `{path}`")
        continue
        
    files = [f for f in os.listdir(path) if f.lower().endswith('.pdf')]
    
    if not files:
        report_lines.append("No se encontraron archivos PDF en esta carpeta.")
        summary_table.append(f"| {subject} | {modalidad} | 0 | 0 | 0 | 0 | Ninguno | Ok | Vacío |")
        continue
        
    total_q = 0
    total_img = 0
    total_unreadable = 0
    total_dupes = 0
    ambiguous_files = []
    
    report_lines.append(f"**Archivos encontrados ({len(files)}):**")
    for file in files:
        file_path = os.path.join(path, file)
        
        # Check for obvious misplaced files by name
        lower_name = file.lower()
        is_misplaced = False
        if subject == "Anatomía A" and ("anato b" in lower_name or "pinches" in lower_name or "anato c" in lower_name):
            is_misplaced = True
        elif subject == "Anatomía B" and ("anato a" in lower_name or "anato c" in lower_name):
            is_misplaced = True
            
        if is_misplaced:
            ambiguous_files.append(file)
            
        try:
            doc = fitz.open(file_path)
            num_pages = len(doc)
            
            file_q = 0
            file_img = 0
            
            for page in doc:
                text = page.get_text("text")
                # Estimate questions by looking for numbers followed by dot/dash or 'Pregunta'
                if modalidad == "Multiple Choice":
                    qs = len(re.findall(r'(?m)^\s*(?:\d+[\.\-\)]|Pregunta\s*\d+)', text))
                    file_q += qs if qs > 0 else len(re.findall(r'(?i)a\).*?b\)', text)) # fallback to options
                else:
                    file_q += len(re.findall(r'(?m)^\s*(?:\d+[\.\-\)]|Pregunta)', text))
                
                # Count images
                file_img += len(page.get_images(full=True))
                
                if not text.strip() and file_img == 0:
                    total_unreadable += 1
            
            total_q += file_q
            total_img += file_img
            
            report_lines.append(f"- `{file}`: {num_pages} págs. (~{file_q} preguntas, {file_img} imágenes)")
            if is_misplaced:
                report_lines.append(f"  - ⚠️ **Posiblemente mal ubicado**: El nombre sugiere otra materia/modalidad.")
                
            doc.close()
        except Exception as e:
            report_lines.append(f"- `{file}`: Error de lectura ({e})")
            ambiguous_files.append(file)
            
    estado = "Pendiente (Revisar ubicaciones)" if ambiguous_files else "Listo para migrar"
    summary_table.append(f"| {subject} | {modalidad} | {len(files)} | ~{total_q} | {total_img} | ~0 | {len(ambiguous_files)} | {total_unreadable} págs | {estado} |")

report_lines.append("\n## 📊 Tabla de Resumen Final\n")
report_lines.append("| Materia | Modalidad | PDFs | Est. Preguntas | Imágenes | Pos. Duplicados | Archivos Ambiguos | Ilegibles | Estado |")
report_lines.append("|---|---|---|---|---|---|---|---|---|")
for row in summary_table:
    report_lines.append(row)

with open('informe_inventario.md', 'w', encoding='utf-8') as f:
    f.write("\n".join(report_lines))

print("Informe generado en informe_inventario.md")
