#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALUMED OS — Integrador final: combina preguntas reales con data.js existente.
- Preserva el array `parciales` del data.js actual
- Agrega las 370 preguntas reales al bancoDados.choices
- Limpia encoding roto (caracters con 0000, fffd, etc)
"""
import json, re, os

INPUT    = 'parsed_questions.json'
EXISTING = 'data.js'
OUTPUT   = 'data.js'
BACKUP   = '_backup_data_original.js'

# Backup existing data.js
if os.path.exists(EXISTING) and not os.path.exists(BACKUP):
    with open(EXISTING, encoding='utf-8') as f:
        original = f.read()
    with open(BACKUP, 'w', encoding='utf-8') as f:
        f.write(original)
    print(f'Backup creado: {BACKUP}')

# Load questions
with open(INPUT, encoding='utf-8') as f:
    questions = json.load(f)
print(f'Preguntas cargadas: {len(questions)}')

# Fix encoding function
def fix(s):
    if not isinstance(s, str):
        return s
    # Remove null chars, replacement chars
    s = s.replace('\x00', '').replace('\ufffd', '?')
    # Fix common OCR/encoding issues in Spanish
    fixes = {
        'fi': 'fi', 'fl': 'fl', 'ff': 'ff',
        'ffi': 'ffi', 'ffl': 'ffl',
        'Se al': 'Señal', 'se ala': 'señala',
    }
    for bad, good in fixes.items():
        s = s.replace(bad, good)
    # Clean excessive whitespace
    s = re.sub(r'\s+', ' ', s).strip()
    return s

MATERIA_DISPLAY = {
    'Anatomía Cátedra C': 'Anatomía Cátedra C',
    'Anatomía Cátedra B': 'Anatomía Cátedra B',
    'Anatomía Cátedra A': 'Anatomía Cátedra A',
    'Histología y Embriología': 'Histología y Embriología',
    'Biología': 'Biología',
}

TIPO_FUENTE_MAP = {
    'SIMULACRO': 'simulacro',
    'FINAL':     'examen-final',
    'PARCIAL':   'examen-parcial',
    'PARC':      'examen-parcial',
    'HISTO 30':  'examen-parcial',
    'CUESTIONES':'simulacro',
    'UNION':     'examen-parcial',
}

def get_tipo(fname):
    fu = fname.upper()
    for k, v in TIPO_FUENTE_MAP.items():
        if k in fu:
            return v
    return 'examen'

# Build clean choices list
choices = []
for i, q in enumerate(questions, 1):
    mat_raw  = q.get('materia', 'Biología')
    materia  = MATERIA_DISPLAY.get(mat_raw, mat_raw)
    enunc    = fix(q.get('enunciado', ''))
    opcoes   = [fix(o) for o in q.get('opcoes', []) if fix(o) and len(fix(o)) > 1]
    correta  = q.get('correta', -1)
    fname    = q.get('fuente', '')
    
    # Skip if question too short or no options
    if len(enunc) < 15 or len(opcoes) < 2:
        continue
    
    # Ensure correta is valid
    tiene_clave = isinstance(correta, int) and 0 <= correta < len(opcoes)
    
    # Skip questions where enunciado contains score/format noise
    if any(kw in enunc.lower() for kw in ['puntúa 1,00', 'puntua 1,00', 'parcial:', 'grupo', 'nombre y apellido']):
        # Clean: take only part before the noise
        for kw in ['puntúa', 'puntua', 'parcial:', 'nombre y apellido']:
            if kw in enunc.lower():
                idx = enunc.lower().find(kw)
                if idx > 20:
                    enunc = enunc[:idx].strip()
    
    if len(enunc) < 15:
        continue
    
    choices.append({
        'id':              i,
        'materia':         materia,
        'catedra':         q.get('catedra'),
        'pergunta':        enunc,
        'opcoes':          opcoes[:4],
        'correta':         correta if tiene_clave else 0,
        'tieneClave':      tiene_clave,
        'justificativa':   '',
        'tipoFuente':      get_tipo(fname),
        # Metadatos internos — nunca renderizados en la UI
        'archivo':         fname,
        'pagina':          '',
        'tema':            '',
        'subtema':         '',
        'fragmentoApunte': '',
        'joy':             {}
    })

print(f'Choices limpios: {len(choices)}')

# Now build the full data.js content
# Read the existing parciales from the current data.js
existing_content = ''
if os.path.exists(BACKUP):
    with open(BACKUP, encoding='utf-8') as f:
        existing_content = f.read()

# Extract parciales section
parciales_match = re.search(
    r'const parciales = \[.*?\];',
    existing_content,
    re.DOTALL
)
parciales_section = parciales_match.group(0) if parciales_match else 'const parciales = [];'

# Generate choices JS
def to_js(v):
    if v is None:
        return 'null'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return '[' + ', '.join(to_js(x) for x in v) + ']'
    if isinstance(v, dict):
        parts = [f'{json.dumps(k)}: {to_js(v2)}' for k, v2 in v.items()]
        return '{' + ', '.join(parts) + '}'
    return str(v)

choices_lines = []
for q in choices:
    line = (
        f'    {{ '
        f'id: {q["id"]}, '
        f'materia: {to_js(q["materia"])}, '
        f'catedra: {to_js(q["catedra"])}, '
        f'pergunta: {to_js(q["pergunta"])}, '
        f'opcoes: {to_js(q["opcoes"])}, '
        f'correta: {q["correta"]}, '
        f'tieneClave: {to_js(q["tieneClave"])}, '
        f'justificativa: "", '
        f'tipoFuente: {to_js(q["tipoFuente"])}, '
        f'archivo: {to_js(q["archivo"])}, '
        f'pagina: "", tema: "", subtema: "", '
        f'fragmentoApunte: "", joy: {{}} '
        f'}},'
    )
    choices_lines.append(line)

from collections import Counter
cnt = Counter(q['materia'] for q in choices)
stats_comment = '\n'.join(f'//   {mat}: {n} preguntas' for mat, n in cnt.most_common())

output = f'''/**
 * ALUMED OS — data.js
 * Banco de Preguntas REAL extraído de PDFs UNLP Medicina
 * Total: {len(choices)} preguntas de exámenes reales
 * Generado automáticamente — Actualizar justificativa y joy manualmente
 *
 * Distribución por materia:
{stats_comment}
 *
 * PRIVACIDAD: Los campos archivo/pagina son internos. NUNCA renderizarlos en la UI.
 */

const bancoDados = {{
  choices: [
{chr(10).join(choices_lines)}
  ],

  // Pinches: agregar imágenes anatómicas con pinchos
  pinches: [],

  // Orales: agregar bolillas y casos clínicos
  orales: []
}};

// ═══════════════════════════════════════════════════════════════
//  CALENDARIO DE PARCIALES — 1er Año UNLP 2026
//  Datos verificados con Python datetime.
//  Joyce puede actualizar hora, modalidad, aula, estado, observacion.
// ═══════════════════════════════════════════════════════════════
'''

# Append parciales section
output += parciales_section + '\n'

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(output)

print(f'Guardado: {OUTPUT}')
print(f'  Tamanho: {len(output):,} bytes')
print(f'  Choices: {len(choices)}')
