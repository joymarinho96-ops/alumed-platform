#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALUMED OS — Parser v2 robusto para multiples formatos de examen UNLP.
Detecta: formato Moodle, formato numerado clasico, formato letras.
"""
import json, re, sys, os
from collections import Counter

INPUT  = 'extracted_raw.json'
OUTPUT = 'parsed_questions.json'

# ── Corrección de encoding ────────────────────────────────────
def fix_text(t):
    """Fix common encoding issues in extracted text."""
    if not t:
        return ''
    replacements = {
        '\u0000': '', '\ufffd': '', 'fi': 'fi', 'fl': 'fl',
        'Se\u00f1al\u00e1': 'Señalá', '\u00e9n': 'én'
    }
    for k, v in replacements.items():
        t = t.replace(k, v)
    return t

# ── Extraccion por formato Moodle ─────────────────────────────
# Formato: "Pregunta N\n...\nSeleccione una:\nA. opt\nB. opt\nRespuesta correcta\nLa respuesta correcta es: ..."
def parse_moodle_format(text, materia, fname):
    qs = []
    # Split by "Pregunta N" or "Pregunta\nN"
    blocks = re.split(r'\nPregunta\s+\d+\n', text)
    if len(blocks) < 2:
        blocks = re.split(r'\nPregunta \d+\n', text)
    
    for block in blocks[1:]:  # skip first (header)
        block = fix_text(block)
        
        # Extract enunciado: everything before "Seleccione una:" or first option
        m_sel = re.search(r'\nSeleccione\s+una[:\s]', block)
        opts_start = m_sel.start() if m_sel else -1
        
        if opts_start < 0:
            # Try finding first option
            m_opt = re.search(r'\n[A-E][\.)] ', block)
            opts_start = m_opt.start() if m_opt else -1
        
        if opts_start < 0:
            continue
        
        # Clean enunciado
        header = block[:opts_start]
        # Remove score info like "Puntúa 1,00 sobre 1,00" or "Correcta"
        header = re.sub(r'(?:Correcta|Incorrecta|Puntu[a-z].*?\n|Punt[a-z].*?\n)', '', header, flags=re.IGNORECASE)
        enunciado = re.sub(r'\s+', ' ', header).strip()
        
        if len(enunciado) < 15:
            continue
        
        # Extract options
        opts_text = block[opts_start:]
        opts_raw = re.findall(r'\n([A-E])[\.)] (.+?)(?=\n[A-E][\.)]|\nRespuesta|$)', opts_text, re.DOTALL)
        opciones = [re.sub(r'\s+', ' ', opt[1]).strip() for opt in opts_raw]
        opciones = [o for o in opciones if len(o) > 2]
        
        if len(opciones) < 2:
            continue
        
        # Extract correct answer
        m_corr = re.search(r'Respuesta correcta\s+La respuesta correcta es:?\s+(.+?)(?:\n/|\Z)', opts_text, re.DOTALL)
        correta = -1
        if m_corr:
            correct_text = re.sub(r'\s+', ' ', m_corr.group(1)).strip()[:150]
            # Match against options
            for i, opt in enumerate(opciones):
                if len(correct_text) > 10 and correct_text[:50] in opt[:60]:
                    correta = i
                    break
                if len(opt) > 10 and opt[:50] in correct_text[:60]:
                    correta = i
                    break
        
        qs.append({
            'enunciado': enunciado[:400],
            'opcoes': opciones[:5],
            'correta': correta,
            'materia': materia,
            'fuente': fname,
            'formato': 'moodle'
        })
    
    return qs

# ── Extraccion formato clasico numerado ────────────────────────
# "1. Enunciado\na) opt\nb) opt\nRespuesta: B"
def parse_classic_format(text, materia, fname):
    qs = []
    fix = fix_text(text)
    
    # Split by numbered questions
    pattern = re.compile(r'(?:^|\n)[ \t]*(\d{1,3})[\.)\-][ \t]+', re.MULTILINE)
    matches  = list(pattern.finditer(fix))
    
    for i, m in enumerate(matches):
        num = int(m.group(1))
        if num > 300 or num < 1:
            continue
        
        end   = matches[i+1].start() if i+1 < len(matches) else len(fix)
        block = fix[m.start():end].strip()
        
        lines = block.split('\n')
        enunciado_lines = []
        opciones = []
        correta = -1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for answer key line
            m_key = re.match(r'^(?:respuesta|clave|rpta|resp)[:\s*]+([a-eA-E1-5])', line, re.IGNORECASE)
            if m_key:
                correta = {'A':0,'B':1,'C':2,'D':3,'E':4,'1':0,'2':1,'3':2,'4':3}.get(m_key.group(1).upper(), -1)
                continue
            
            # Check for option line: "a) xxx" or "A. xxx" or "A) xxx"
            m_opt = re.match(r'^([a-eA-E])[\.)\-:][ \t]+(.+)', line)
            if m_opt:
                opciones.append(re.sub(r'\s+', ' ', m_opt.group(2)).strip())
                continue
            
            if not opciones:
                enunciado_lines.append(line)
        
        enunciado = re.sub(r'\s+', ' ', ' '.join(enunciado_lines)).strip()
        opciones   = [o for o in opciones if len(o) > 2]
        
        if len(enunciado) < 15 or len(opciones) < 2:
            continue
        
        qs.append({
            'enunciado': enunciado[:400],
            'opcoes': opciones[:5],
            'correta': correta,
            'materia': materia,
            'fuente': fname,
            'formato': 'clasico'
        })
    
    return qs

# ── Deteccion de formato ───────────────────────────────────────
def detect_format(text):
    if 'Pregunta' in text and 'Seleccione una' in text:
        return 'moodle'
    if re.search(r'^\d{1,3}[\.)\-]', text, re.MULTILINE):
        return 'clasico'
    return 'unknown'

# ── Mapeo de materias ─────────────────────────────────────────
MATERIA_MAP = {
    'Anatomia Catedra C': 'Anatomía Cátedra C',
    'Anatomia Catedra B': 'Anatomía Cátedra B',
    'Anatomia Catedra A': 'Anatomía Cátedra A',
    'Histologia y Embriologia': 'Histología y Embriología',
    'Biologia': 'Biología',
}

# ── MAIN ──────────────────────────────────────────────────────
if not os.path.exists(INPUT):
    print(f'ERROR: {INPUT} not found.')
    sys.exit(1)

with open(INPUT, encoding='utf-8') as f:
    raw = json.load(f)

all_questions = []

for entry in raw:
    fname   = entry.get('file', '')
    materia = entry.get('materia', 'General')
    text    = entry.get('text', '')
    
    if not text or len(text) < 50:
        print(f'SKIP (sin texto): {fname[:50]}')
        continue
    
    fmt = detect_format(text)
    
    if fmt == 'moodle':
        qs = parse_moodle_format(text, materia, fname)
    else:
        qs = parse_classic_format(text, materia, fname)
    
    print(f'[{fmt:7}] {len(qs):3d} preguntas <- {fname[:55]}')
    all_questions.extend(qs)

# ── Deduplicar ────────────────────────────────────────────────
seen = set()
unique = []
for q in all_questions:
    key = q['enunciado'][:80].lower()
    key = re.sub(r'\s+', ' ', key)
    if key not in seen and len(key) > 15:
        seen.add(key)
        unique.append(q)

# ── Asignar IDs y limpiar ─────────────────────────────────────
final = []
for i, q in enumerate(unique, 1):
    final.append({
        'id':       i,
        'materia':  q['materia'],
        'enunciado':q['enunciado'],
        'opcoes':   q['opcoes'],
        'correta':  q['correta'],
        'fuente':   q['fuente'],
        'formato':  q['formato']
    })

print(f'\n=== RESUMEN ===')
print(f'Preguntas unicas:   {len(final)}')
print(f'Con clave correcta: {sum(1 for q in final if q["correta"] >= 0)}')
print(f'Sin clave (manual): {sum(1 for q in final if q["correta"] < 0)}')

cnt = Counter(q['materia'] for q in final)
for mat, n in cnt.most_common():
    print(f'  {mat}: {n}')

with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

print(f'\nGuardado: {OUTPUT}')
