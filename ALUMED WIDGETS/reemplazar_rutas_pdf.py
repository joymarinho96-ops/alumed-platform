import json
import re
import os

print("=== REEMPLAZANDO REFERENCIAS A 'PDF APUNTES' POR 'pdf/' ===")

# 1. Update data.js
with open("data.js", "r", encoding="utf-8") as f:
    raw = f.read()

# Replace any occurrence in data.js
raw_updated = re.sub(r'(?i)pdf\s*apuntes[\\/]', 'pdf/', raw)

with open("data.js", "w", encoding="utf-8") as f:
    f.write(raw_updated)

print("1. data.js actualizado. Todas las referencias a 'PDF APUNTES' cambiadas a 'pdf/'.")

# 2. Update config files or scripts if any
scripts = ["excavador_definitivo.py", "clasificador_tp.py", "excavar_todo.py"]
for s in scripts:
    if os.path.exists(s):
        with open(s, "r", encoding="utf-8") as f:
            stext = f.read()
        stext_updated = re.sub(r'(?i)pdf\s*apuntes[\\/]', 'pdf/', stext)
        stext_updated = re.sub(r'(?i)pdfs_apuntes[\\/]', 'pdf/', stext_updated)
        with open(s, "w", encoding="utf-8") as f:
            f.write(stext_updated)

print("2. Scripts del proyecto actualizados para buscar únicamente en 'pdf/'.")
