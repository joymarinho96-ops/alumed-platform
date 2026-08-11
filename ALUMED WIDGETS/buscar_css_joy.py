with open("style.css", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, l in enumerate(lines):
    if "joy" in l.lower():
        print(f"Line {idx+1}: {l.strip()}")
