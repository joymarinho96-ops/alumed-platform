import json

with open("data.js", "r", encoding="utf-8") as f:
    c = f.read().replace("const bancoDados =", "").strip().rstrip(";")
data = json.loads(c)

choices = data.get("choices", [])
materias = {}
modalidades = {}

for q in choices:
    m = q.get("materia", "S/D")
    mod = q.get("modalidad", "S/D")
    materias[m] = materias.get(m, 0) + 1
    modalidades[mod] = modalidades.get(mod, 0) + 1

print("=== DISTRIBUCIÓN POR MATERIA EN DATA.JS ===")
for m, count in materias.items():
    print(f"  - '{m}': {count} preguntas")

print("\n=== DISTRIBUCIÓN POR MODALIDAD EN DATA.JS ===")
for mod, count in modalidades.items():
    print(f"  - '{mod}': {count} preguntas")
