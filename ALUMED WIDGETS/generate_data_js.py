#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALUMED OS — Generador de data.js con banco de preguntas real extraido de los PDFs.
Combina preguntas parseadas con la estructura existente del banco de datos.
"""
import json, re, os

INPUT   = 'parsed_questions.json'
OUTPUT  = 'data_new.js'

# ── Mapeo de materia a colorKey ───────────────────────────────
MATERIA_MAP = {
    'Anatomía Cátedra C': {'materia': 'Anatomía Cátedra C', 'colorKey': 'anatoc', 'catedra': 'C'},
    'Anatomía Cátedra B': {'materia': 'Anatomía Cátedra B', 'colorKey': 'anatob', 'catedra': 'B'},
    'Anatomía Cátedra A': {'materia': 'Anatomía Cátedra A', 'colorKey': 'anatoa', 'catedra': 'A'},
    'Histología y Embriología': {'materia': 'Histología y Embriología', 'colorKey': 'hye', 'catedra': None},
    'Biología': {'materia': 'Biología', 'colorKey': 'bio', 'catedra': None},
}

# Fix encoding
def fix_enc(s):
    if not s:
        return ''
    return s.replace('\u0000', '').replace('\ufffd', '?').strip()

with open(INPUT, encoding='utf-8') as f:
    questions = json.load(f)

print(f'Cargadas: {len(questions)} preguntas')

# ── Construir choices ─────────────────────────────────────────
choices = []
for i, q in enumerate(questions, 1):
    materia_raw = q.get('materia', 'General')
    meta = MATERIA_MAP.get(materia_raw, {'materia': materia_raw, 'colorKey': 'bio', 'catedra': None})
    
    enunciado = fix_enc(q.get('enunciado', ''))
    opcoes    = [fix_enc(o) for o in q.get('opcoes', []) if fix_enc(o)]
    correta   = q.get('correta', -1)
    fuente    = q.get('fuente', '')
    
    # Determinar tipo de fuente (sin exponer nombre real del archivo)
    tipo_fuente = 'examen'
    if 'SIMULACRO' in fuente.upper():
        tipo_fuente = 'simulacro'
    elif 'FINAL' in fuente.upper():
        tipo_fuente = 'examen-final'
    elif 'PARCIAL' in fuente.upper() or 'PARC' in fuente.upper():
        tipo_fuente = 'examen-parcial'
    
    # Correta válida: si es -1, dejamos en 0 para que el alumno use "sin clave"
    # Marcamos si tiene clave real
    tiene_clave = correta >= 0 and correta < len(opcoes)
    
    choices.append({
        'id':         i,
        'materia':    meta['materia'],
        'catedra':    meta['catedra'],
        'pergunta':   enunciado,
        'opcoes':     opcoes[:4],
        'correta':    correta if tiene_clave else 0,
        'tieneClave': tiene_clave,
        'justificativa': '',
        'tipoFuente': tipo_fuente,
        # Metadatos internos (no renderizados en la UI)
        'archivo':    fuente,
        'pagina':     '',
        'tema':       '',
        'subtema':    '',
        'fragmentoApunte': '',
        'joy':        {}
    })

# Stats
from collections import Counter
cnt = Counter(q['materia'] for q in choices)
for mat, n in cnt.most_common():
    print(f'  {mat}: {n}')
print(f'  Con clave real: {sum(1 for q in choices if q["tieneClave"])}')
print(f'  Sin clave: {sum(1 for q in choices if not q["tieneClave"])}')

# ── Serializar como JS ────────────────────────────────────────
def to_js_str(s):
    return json.dumps(s, ensure_ascii=False)

def to_js_arr(arr):
    items = ', '.join(to_js_str(a) for a in arr)
    return f'[{items}]'

lines = ['// ALUMED OS — Banco de Preguntas REAL (extraido de PDFs UNLP)',
         '// Auto-generado por ALUMED Parser — NO EDITAR MANUALMENTE',
         '// Total: ' + str(len(choices)) + ' preguntas de examenes reales',
         '',
         'const bancoDados = {',
         '  choices: [']

for q in choices:
    joy_str = '{}'  # empty joy block
    line = (
        f'    {{ id:{q["id"]}, materia:{to_js_str(q["materia"])}, '
        f'catedra:{to_js_str(q["catedra"]) if q["catedra"] else "null"}, '
        f'pergunta:{to_js_str(q["pergunta"])}, '
        f'opcoes:{to_js_arr(q["opcoes"])}, '
        f'correta:{q["correta"]}, '
        f'tieneClave:{"true" if q["tieneClave"] else "false"}, '
        f'justificativa:"", '
        f'tipoFuente:{to_js_str(q["tipoFuente"])}, '
        f'archivo:{to_js_str(q["archivo"])}, '
        f'pagina:"", tema:"", subtema:"", '
        f'fragmentoApunte:"", joy:{joy_str} }},'
    )
    lines.append(line)

# Close choices, add empty pinches and orales
lines.append('  ],')
lines.append('')
lines.append('  // Pinches: agregar imágenes anatómicas aquí')
lines.append('  pinches: [],')
lines.append('')
lines.append('  // Orales: agregar bolillas aquí')
lines.append('  orales: []')
lines.append('};')

content = '\n'.join(lines)

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nGuardado: {OUTPUT} ({len(content):,} bytes, {len(choices)} preguntas)')
