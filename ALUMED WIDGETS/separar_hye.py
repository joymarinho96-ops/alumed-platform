import json
import re

with open('data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract JSON part
start_idx = content.find('{')
end_idx = content.rfind('}') + 1
json_str = content[start_idx:end_idx]

try:
    data = json.loads(json_str)
except Exception as e:
    print(f"Error parsing JSON: {e}")
    exit(1)

choices = data.get('choices', [])
initial_count = len(choices)

# 1. Remove questions with "figura" or "imagen" in the text
def has_figure(q):
    text = q.get('pregunta', '').lower()
    return bool(re.search(r'\b(figura|imagen)\b', text))

filtered_choices = [q for q in choices if not has_figure(q)]
print(f"Removed {initial_count - len(filtered_choices)} questions with figures.")

# 2. Separate Histologia and Embriologia
keywords_embrio = ['embrión', 'embriologia', 'embriología', 'desarrollo', 'feto', 'fecundación', 'somita', 'gastrulación', 'placenta', 'semana', 'derivado', 'blastocisto', 'trofoblasto', 'mesodermo', 'ectodermo', 'endodermo', 'notocorda', 'neurulación', 'saco vitelino', 'amnios', 'corion', 'alantoides', 'espermatogénesis', 'ovogénesis', 'meiosis', 'fecundacion', 'embrion', 'espermatozoide', 'ovocito', 'blastómero', 'mórula', 'implantación', 'disco bilaminar', 'disco trilaminar', 'somitogénesis', 'plegamiento', 'faringe', 'arcos faríngeos', 'bolsas faríngeas', 'hendiduras faríngeas', 'placodas', 'organogénesis', 'teratógeno']
keywords_histo = ['tejido', 'epitelio', 'célula', 'tinción', 'microscopio', 'glándula', 'colágeno', 'fibroblasto', 'macrófago', 'cartílago', 'hueso', 'osteona', 'sangre', 'eritrocito', 'leucocito', 'músculo', 'sarcómero', 'nervioso', 'neurona', 'glía', 'sinapsis', 'epidermis', 'dermis', 'hematoxilina', 'eosina', 'pas', 'tricrómico', 'órgano', 'mucosa', 'submucosa', 'muscular', 'serosa', 'endotelio', 'mesotelio', 'reticular', 'elástico', 'adiposo', 'adipocito', 'condrocito', 'osteocito', 'osteoclasto', 'osteoblasto', 'linfocito', 'neutrófilo', 'eosinófilo', 'basófilo', 'monocito', 'plaqueta', 'megacariocito', 'médula ósea', 'timo', 'bazo', 'ganglio linfático', 'amígdala', 'corazón', 'arteria', 'vena', 'capilar', 'pulmón', 'tráquea', 'bronquio', 'alvéolo', 'riñón', 'nefrona', 'glomérulo', 'túbulo', 'uréter', 'vejiga', 'estómago', 'intestino', 'hígado', 'páncreas', 'vesícula biliar', 'salival', 'hipófisis', 'tiroides', 'paratiroides', 'suprarrenal', 'testículo', 'ovario', 'útero', 'vagina', 'trompa', 'próstata', 'ojo', 'oído', 'piel']

hye_count = 0
histo_count = 0
embrio_count = 0

for q in filtered_choices:
    mat = q.get('materia', '').lower()
    if 'histolog' in mat or 'embriolog' in mat:
        hye_count += 1
        text = q.get('pregunta', '').lower()
        opts = ' '.join([str(opt) for opt in q.get('opciones', [])]).lower()
        full_text = text + ' ' + opts
        
        score_embrio = sum(full_text.count(kw) for kw in keywords_embrio)
        score_histo = sum(full_text.count(kw) for kw in keywords_histo)
        
        # Determine based on scores
        if score_embrio > score_histo:
            q['materia'] = 'Embriología'
            embrio_count += 1
        elif score_histo > score_embrio:
            q['materia'] = 'Histología'
            histo_count += 1
        else:
            # If scores are tied and 0, or tied and > 0, we can guess by searching for 'histologia' vs 'embriologia' in original materia, but original is 'histologia-embriologia' usually.
            # Default to Histología as it represents a larger portion of the subject, unless 'embrio' is explicitly in the tp.
            tp = q.get('tpPrincipal', '').lower()
            if 'embrio' in tp or 'fecund' in tp or 'desarrollo' in tp:
                q['materia'] = 'Embriología'
                embrio_count += 1
            else:
                q['materia'] = 'Histología' 
                histo_count += 1

data['choices'] = filtered_choices

print(f"Total HyE processed: {hye_count}")
print(f"Assigned to Histología: {histo_count}")
print(f"Assigned to Embriología: {embrio_count}")

# Save the new data
new_content = content[:start_idx] + json.dumps(data, indent=2, ensure_ascii=False) + content[end_idx:]
with open('data.js', 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Saved to data.js")
