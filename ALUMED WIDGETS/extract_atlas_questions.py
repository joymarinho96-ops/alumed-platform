import json

data_js_path = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\ALUMED WIDGETS\data.js"
artifact_out = r"C:\Users\joyce\.gemini\antigravity\brain\9c0711de-334d-4eab-bd97-fbb4455aace4\preguntas_atlas_dual.md"

with open(data_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find("const bancoDados = ")
if start_idx != -1:
    json_str = content[start_idx + len("const bancoDados = "):].strip()
    if json_str.endswith(";"):
        json_str = json_str[:-1].strip()
    banco = json.loads(json_str)
else:
    raise ValueError("const bancoDados not found")

choices = banco.get("choices", [])
pinches = banco.get("pinches", [])
orales = banco.get("orales", [])

# First group by Materia, then inside by TP
materia_groups = {}
for q in choices:
    mat = q.get("materia", "Biología Celular")
    tp = q.get("tp", "General")
    
    if mat not in materia_groups:
        materia_groups[mat] = {}
    if tp not in materia_groups[mat]:
        materia_groups[mat][tp] = []
    materia_groups[mat][tp].append(q)

md_lines = []
md_lines.append("# 🔬 Banco de Preguntas Oficial — Módulo Dual ALUMED OS (UNLP)\n\n")
md_lines.append(f"- **Total Preguntas Múltiple Opción Extraídas**: `{len(choices)}` preguntas\n")
md_lines.append(f"- **Total Estaciones Pinches**: `{len(pinches)}` estaciones\n")
md_lines.append(f"- **Total Casos Examen Oral**: `{len(orales)}` casos\n\n")

md_lines.append("---\n\n")

for mat_name, tp_dict in materia_groups.items():
    total_mat_q = sum(len(qs) for qs in tp_dict.values())
    md_lines.append(f"# 📘 MATERIA: {mat_name.upper()} ({total_mat_q} Preguntas Totales)\n\n")
    
    for tp_name, q_list in tp_dict.items():
        md_lines.append(f"## 📌 {tp_name} ({len(q_list)} Preguntas)\n\n")
        for idx, q in enumerate(q_list, 1):
            md_lines.append(f"### {idx}. {q['pergunta']}\n\n")
            md_lines.append("**Opciones**:\n")
            for opt in q.get('opcoes', []):
                md_lines.append(f"- {opt}\n")
            
            corr_idx = q.get('correta', 0)
            corr_letter = ['A', 'B', 'C', 'D'][corr_idx] if isinstance(corr_idx, int) and corr_idx < 4 else 'A'
            md_lines.append(f"\n> [!TIP]\n> **Respuesta Correcta**: Opción {corr_letter}\n> **Justificación Profe Joy**: {q.get('justificativa', 'Basada en el programa oficial UNLP.')}\n\n")
    md_lines.append("---\n\n")

with open(artifact_out, 'w', encoding='utf-8') as f:
    f.writelines(md_lines)

print(f"Artifact reorganizado por Materia -> TP en: {artifact_out}")
