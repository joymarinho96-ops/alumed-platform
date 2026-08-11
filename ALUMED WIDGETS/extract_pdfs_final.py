#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALUMED OS — Extractor masivo de PDFs
Lee TODOS los archivos de exámenes reales, simulacros y bases de preguntas.
"""

import pdfplumber, os, json, sys

PDFS_DIR = 'PDFS_APUNTES'
OUT_FILE  = 'extracted_raw.json'

def infer_materia(fname):
    upper = fname.upper()
    if 'ANATO' in upper:
        if ' C' in upper: return 'Anatomía Cátedra C'
        if ' B' in upper: return 'Anatomía Cátedra B'
        if ' A' in upper: return 'Anatomía Cátedra A'
        return 'Anatomía Cátedra C' # default
    if 'BIO' in upper and 'HISTO' not in upper:
        return 'Biología'
    if 'HISTO' in upper or 'EMBRIO' in upper or 'HYE' in upper:
        return 'Histología y Embriología'
    return 'General'

def extract_text(fpath, max_pages=80):
    texts = []
    try:
        with pdfplumber.open(fpath) as pdf:
            pages = pdf.pages[:min(max_pages, len(pdf.pages))]
            for i, page in enumerate(pages):
                # Redirect stderr to suppress warnings about fonts
                old_stderr = sys.stderr
                sys.stderr = open(os.devnull, 'w')
                try:
                    t = page.extract_text()
                finally:
                    sys.stderr.close()
                    sys.stderr = old_stderr
                if t:
                    texts.append(t)
    except Exception as e:
        return f'ERROR: {e}'
    return '\n'.join(texts)

results = []
all_files = [f for f in os.listdir(PDFS_DIR) if f.lower().endswith('.pdf')]

for fname in all_files:
    fpath = os.path.join(PDFS_DIR, fname)
    materia = infer_materia(fname)
    size_mb = os.path.getsize(fpath) / (1024*1024)
    print(f'[{size_mb:5.1f}MB] Leyendo: {fname[:60]}')
    sys.stdout.flush()
    text = extract_text(fpath, max_pages=150)
    
    if text.startswith('ERROR'):
        print(f'         -> {text}')
        results.append({'file': fname, 'materia': materia, 'text': '', 'error': text})
        continue
    
    # Optional: we can capture all text up to 150 pages without arbitrary small cap
    print(f'         -> {len(text):,} caracteres')
    sys.stdout.flush()
    results.append({
        'file':    fname,
        'materia': materia,
        'text':    text   # take everything extracted up to 150 pages
    })

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

total_chars = sum(len(r.get('text','')) for r in results)
print(f'\nExtraccion completa. {len(results)} archivos, {total_chars:,} caracteres totales.')
print(f'Guardado en: {OUT_FILE}')
