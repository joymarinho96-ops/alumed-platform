import re

with open("app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if any(k in line for k in ["option-btn", "escaparHTML", "letraOpcion", "opciones", "opcoes"]):
        print(f"Line {idx+1}: {line.strip()}")
