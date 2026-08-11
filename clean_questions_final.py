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
        
        # Strings to remove from text (Gisela, score texts)
        regex_remove = [
            r'(?i)Gisela\s+CAMIHORT',
            r'(?i)DEGREGORI',
            r'(?i)Gisela',
            r'(?i)Punta\s+\d+[,.]\d+\s+sobre\s+\d+[,.]\d+',
            r'(?i)Puntúa\s+\d+[,.]\d+\s+sobre\s+\d+[,.]\d+',
            r'(?i)Puntuación\s+obtenida:\s*\d+[,.]\d+',
            r'(?i)Marcar\s+pergunta',
            r'(?i)pergunta\s+\d+',
            r'-\s+$', # trailing dash
        ]
        
        # Regex to check if a question relies on an image
        regex_has_fig = r'(?i)\bfig\b|\bfig\.\b|\bfigura\b|fig\.\s*\d|\bimagen\b'
        
        for q in data.get('choices', []):
            pergunta = q.get('pergunta', '')
            opcoes = q.get('opcoes', [])
            
            # Check if 'fig' or 'imagen' is in the question
            if re.search(regex_has_fig, pergunta):
                continue
                
            # Or in the options
            has_fig_in_opt = False
            for opt in opcoes:
                if re.search(regex_has_fig, opt):
                    has_fig_in_opt = True
                    break
            
            if has_fig_in_opt:
                continue
                
            # If we keep it, clean the text
            for r in regex_remove:
                pergunta = re.sub(r, '', pergunta)
                
            pergunta = re.sub(r'\s+', ' ', pergunta).strip()
            # Trim trailing symbols if any
            pergunta = re.sub(r'^[-\s]+', '', pergunta)
            pergunta = re.sub(r'[-\s]+$', '', pergunta)
            
            q['pergunta'] = pergunta
            
            clean_opts = []
            for opt in opcoes:
                for r in regex_remove:
                    opt = re.sub(r, '', opt)
                opt = re.sub(r'\s+', ' ', opt).strip()
                clean_opts.append(opt)
            q['opcoes'] = clean_opts
            
            cleaned_choices.append(q)
            
        data['choices'] = cleaned_choices
        
        new_content = f"// ALUMED OS - Banco de perguntas Limpio (Filtrado de nombres y figuras)\nconst bancoDados = {json.dumps(data, indent=2, ensure_ascii=False)};"
        
        with codecs.open(p, 'w', 'utf-8') as f:
            f.write(new_content)
            
        print(f"Done. Reduced from {original_count} to {len(cleaned_choices)} questions.")

if __name__ == '__main__':
    clean_data()
