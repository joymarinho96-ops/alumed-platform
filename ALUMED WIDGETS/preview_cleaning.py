import json, re

with open('parsed_questions.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

def clean_question(text):
    original = text
    text = re.sub(r'^\s*(Pregunta\s*\d+[:\.\-]?|\d+[\.\)\-]?)\s*', '', text, flags=re.IGNORECASE)
    
    meta_patterns = [
        r'(?i)autor\s*responsable\s*:?.*',
        r'(?i)autor\s*:?.*',
        r'(?i)c[aá]tedra.*u\.n\.l\.p\.',
        r'(?i)c[aá]tedra\s*[\'\"].*?[\'\"]?.*',
        r'(?i)f\.c\.m\.',
        r'(?i)u\.n\.l\.p\.',
        r'(?i)fig\.\s*\d+(\.\d+)?',
        r'(?i)figura\s*\d+(\.\d+)?',
        r'(?i)diseño y edición.*',
        r'(?i)p[aá]gina\s*\d+',
        r'(?i)segmentaci[oó]n sucesi[oó]n de mitosis.*autod',
    ]
    for p in meta_patterns:
        text = re.sub(p, '', text)
    
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    
    return original, text.strip()

samples = []
messy_keywords = ['autor', 'catedra', 'cátedra', 'f.c.m', 'u.n.l.p', 'fig.', 'figura', 'diseño', 'pagina']
for q in qs:
    text = q.get('enunciado', '')
    if any(k in text.lower() for k in messy_keywords) or text[0:1].isdigit():
        samples.append(text)
    if len(samples) >= 20:
        break

if len(samples) < 20:
    samples.extend([q.get('enunciado', '') for q in qs if q.get('enunciado', '') not in samples][:20-len(samples)])

with open('muestras_limpieza.md', 'w', encoding='utf-8') as f:
    f.write('# Muestra de Limpieza (20 Registros)\n\n')
    for i, text in enumerate(samples[:20]):
        old, new = clean_question(text)
        f.write(f'### Registro {i+1}\n')
        f.write(f'**ANTES:**\n`{old}`\n\n')
        f.write(f'**DESPUÉS:**\n`{new}`\n\n')
        f.write('---\n')
