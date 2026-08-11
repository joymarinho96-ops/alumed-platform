python -c "
import pdfplumber, os, json, re, sys

PDFS_DIR = r'PDFS_APUNTES'
OUT_FILE  = 'extracted_raw.json'

# Archivos prioritarios: exámenes reales, simulacros y bases de preguntas
PRIORITY_FILES = [
    'FINALES TODOS BIO (1).pdf',
    'HISTO 30 PARC SIN REPETIR 1F NOV.pdf',
    'HISTO TODOS.pdf',
    'CUESTIONES HISTO 1º CUADRIMESTRE - @ALUMEDINSTITUTO_211006_194327[1].pdf',
    'SIMULACRO HyE PARCIAL 1 (2) (1).pdf',
    'SIMULACRO HyE PARCIAL 1 (2).pdf',
    'SIMULACRO PARCIAL ANATO B (1).pdf',
    'PARCIALES REALES HISTOYEMBRIO 2025. BLOQUE II PDF.pdf',
    'PREGUNTAS REALES EMBRIO (1).pdf',
    'PARCIALITO HYE 1.pdf',
    'PARCIALITO HYE 2.pdf',
    'HECK HYE FINAL (1).pdf',
    'examenes parciales pasados hye papel escrito fotos.pdf',
    '19-00 - 2P3F - GRUPOS 10, 11, 12, 13 y 14.pdf',
    '19_00 - 2P3F - GRUPOS 10, 11, 12, 13 y 14.pdf',
    'PARCIALES VIEJOS - Ciencias sociales y medicina.pdf',
]

results = []

def extract_text_from_pdf(pdf_path, max_pages=60):
    text = ''
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total = len(pdf.pages)
            pages = pdf.pages[:min(max_pages, total)]
            for page in pages:
                t = page.extract_text()
                if t:
                    text += t + '\n'
    except Exception as e:
        text = f'ERROR: {e}'
    return text

for fname in PRIORITY_FILES:
    fpath = os.path.join(PDFS_DIR, fname)
    if not os.path.exists(fpath):
        print(f'SKIP (not found): {fname}')
        continue
    size_mb = os.path.getsize(fpath) / 1024 / 1024
    print(f'Reading ({size_mb:.1f}MB): {fname}')
    sys.stdout.flush()
    text = extract_text_from_pdf(fpath, max_pages=40)
    results.append({'file': fname, 'text': text[:50000]})  # cap 50k chars per file
    print(f'  -> {len(text)} chars extracted')
    sys.stdout.flush()

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f'Done. Saved to {OUT_FILE}')
"
