import json
import re
import os
import codecs

paths = [
    r'C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\static\atlas_histologico\data.js',
    r'C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\ALUMED WIDGETS\data.js'
]

def clean_data():
    for p in paths:
        if not os.path.exists(p):
            continue
            
        print(f"Cleaning {p}...")
        with codecs.open(p, 'r', 'utf-8') as f:
            content = f.read()
            
        json_start = content.find('{')
        if json_start == -1:
            print("Could not find start of JSON")
            continue
            
        json_str = content[json_start:]
        if json_str.strip().endswith(';'):
            json_str = json_str.strip()[:-1]
            
        try:
            data = json.loads(json_str)
        except Exception as e:
            print(f"JSON parsing error: {e}")
            continue
            
        original_count = len(data.get('choices', []))
        cleaned_choices = []
        
        # Regexes for junk text that should be STRIPPED out of the question
        regex_remove = [
            r'(?i)Gisela\s+CAMIHORT',
            r'(?i)DEGREGORI',
            r'(?i)Punta\s+\d+[,.]\d+\s+sobre\s+\d+[,.]\d+',
            r'(?i)Puntúa\s+\d+[,.]\d+\s+sobre\s+\d+[,.]\d+',
            r'(?i)Marcar\s+pregunta',
            r'(?i)Pregunta\s+\d+'
        ]
        
        # Regex to check if a question relies on an image
        regex_has_fig = r'(?i)\bfig\b|\bfig\.\b|\bfigura\b|fig\.\s*\d'
        
        for q in data.get('choices', []):
            pergunta = q.get('pergunta', '')
            opcoes = q.get('opcoes', [])
            
            # Check if 'fig' is in the question or options
            has_fig = bool(re.search(regex_has_fig, pergunta))
            if not has_fig:
                for opt in opcoes:
                    if re.search(regex_has_fig, opt):
                        has_fig = True
                        break
            
            if has_fig:
                # We drop this question
                continue
                
            # If we keep it, clean the text
            for r in regex_remove:
                pergunta = re.sub(r, '', pergunta)
                
            pergunta = re.sub(r'\s+', ' ', pergunta).strip()
            q['pergunta'] = pergunta
            
            # Clean options as well
            clean_opts = []
            for opt in opcoes:
                for r in regex_remove:
                    opt = re.sub(r, '', opt)
                clean_opts.append(re.sub(r'\s+', ' ', opt).strip())
            q['opcoes'] = clean_opts
            
            cleaned_choices.append(q)
            
        data['choices'] = cleaned_choices
        
        new_content = f"// ALUMED OS - Banco de Preguntas Limpio (Filtrado de nombres y figuras)\nconst bancoDados = {json.dumps(data, indent=2, ensure_ascii=False)};"
        
        with codecs.open(p, 'w', 'utf-8') as f:
            f.write(new_content)
            
        print(f"Done. Reduced from {original_count} to {len(cleaned_choices)} questions.")

if __name__ == '__main__':
    clean_data()
