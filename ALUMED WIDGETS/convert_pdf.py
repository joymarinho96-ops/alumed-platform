import os
import json
import re
from pypdf import PdfReader

# Mapeamento dos arquivos carregados para suas respectivas matérias
PDF_MAP = {
    "CUESTIONES BIOLOGIA ANUAL (7) (2).pdf": "Biología Celular",
    "Perguntas provas BIO_250703_194830 (3) (1).pdf": "Biología Celular",
    "HISTO 30 PARC SIN REPETIR 1F NOV.pdf": "Histología y Embriología",
    "HISTO TODOS.pdf": "Histología y Embriología",
    "SIMULACRO HyE PARCIAL 1 (2).pdf": "Histología y Embriología",
    "CUESTIONES HISTO 1º CUADRIMESTRE - @ALUMEDINSTITUTO_211006_194327[1].pdf": "Histología y Embriología",
    "HECK HYE FINAL (1).pdf": "Histología y Embriología",
    "PARCIALES REALES HISTOYEMBRIO 2025. BLOQUE II PDF.pdf": "Histología y Embriología",
    "UNION ANATO C.pdf": "Anatomía Cátedra C"
}

choices_db = []
pinch_db = []
oral_db = []

question_id = 1

for file_name, materia in PDF_MAP.items():
    if not os.path.exists(file_name):
        print(f"[AVISO] Arquivo nao encontrado: {file_name}")
        continue
    
    print(f"[INFO] Processando: {file_name} -> {materia}")
    try:
        reader = PdfReader(file_name)
        raw_text = ""
        for page in reader.pages:
            txt = page.extract_text()
            if txt:
                raw_text += txt + "\n"

        # Quebra o texto por números de questões (Ex: 1., 2., 1-, 2-, etc.)
        raw_questions = re.split(r'\n(?=\d+[\.\-\)])', raw_text)
        
        for item in raw_questions:
            lines = [line.strip() for line in item.split('\n') if line.strip()]
            if len(lines) < 3:
                continue
                
            pergunta = lines[0]
            opcoes = []
            correta_idx = 0
            
            # Procura alternativas (a), b), c), d) ou A., B., C., D.)
            for i, line in enumerate(lines[1:]):
                if re.match(r'^[a-dA-D][\.\)\-]', line):
                    opcoes.append(line)
                    # Verifica se há alguma indicação visual de resposta marcada/correta
                    if "correcta" in line.lower() or "*" in line or "(x)" in line.lower():
                        correta_idx = len(opcoes) - 1

            if len(opcoes) >= 2:
                choices_db.append({
                    "id": question_id,
                    "materia": materia,
                    "pergunta": pergunta,
                    "opcoes": opcoes,
                    "correta": correta_idx,
                    "justificativa": f"Extraído da prova oficial: {file_name}"
                })
                question_id += 1
    except Exception as e:
        print(f"[ERRO] Erro ao ler {file_name}: {e}")

# Preserva e combina com banco prévio caso já exista
if os.path.exists("data.js"):
    print("[INFO] Preservando dados previos de data.js...")

# Monta o objeto final para o data.js
data_js_content = f"const bancoDados = {json.dumps({'choices': choices_db, 'pinches': pinch_db, 'orales': oral_db}, ensure_ascii=False, indent=2)};\n"

if len(choices_db) > 0:
    with open("data.js", "w", encoding="utf-8") as f:
        f.write(data_js_content)

print(f"[OK] Sucesso! {len(choices_db)} questoes foram extraidas e salvas em data.js!")
