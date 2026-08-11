import json
import os

print("=== RE-ASIGNANDO MATERIAS POR FUENTE DE RUTA EN DATA.JS ===")

with open("data.js", "r", encoding="utf-8") as f:
    raw = f.read()

first_b = raw.find('{')
last_b = raw.rfind('}')
banco = json.loads(raw[first_b:last_b+1])

choices = banco.get("choices", [])
orales = []
pinches = []

fixed_choices = []
for q in choices:
    fuente = (q.get("fuenteInterna", "") or q.get("fuente", "")).lower()
    mat = q.get("materia", "Biología")
    mod = q.get("modalidad", "CHOICE")
    
    if "anatomia-b" in fuente or "pinches" in fuente or "anato b" in fuente:
        mat = "Anatomía Cátedra B"
        mod = "PINCHE_STATION"
    elif "anatomia-a" in fuente or "anato a" in fuente:
        mat = "Anatomía Cátedra A"
        if mod != "CHOICE":
            mod = "ORAL"
    elif "anatomia-c" in fuente or "union anato c" in fuente or "anato c" in fuente:
        mat = "Anatomía Cátedra C"
    elif "histologia" in fuente or "embrio" in fuente or "hye" in fuente:
        mat = "Histología y Embriología"
    elif "biologia" in fuente or "bio" in fuente:
        mat = "Biología"
        
    q["materia"] = mat
    q["modalidad"] = mod
    fixed_choices.append(q)
    
    if mod == "ORAL":
        orales.append(q)
    elif mod == "PINCHE_STATION":
        pinches.append(q)

banco["choices"] = fixed_choices
banco["orales"] = orales
banco["pinches"] = pinches

# Write back to data.js
out_content = "const bancoDados = " + json.dumps(banco, ensure_ascii=False, indent=2) + ";"
with open("data.js", "w", encoding="utf-8") as f:
    f.write(out_content)

print(f"Re-asignación finalizada:")
print(f"  - bancoDados.choices.length: {len(banco['choices'])}")
print(f"  - bancoDados.orales.length: {len(banco['orales'])}")
print(f"  - bancoDados.pinches.length: {len(banco['pinches'])}")
