with open("app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, l in enumerate(lines):
    if "generarPanelJoy" in l or "mc-joy-panel" in l or "metodo-joy" in l:
        print(f"Line {idx+1}: {l.strip()}")
