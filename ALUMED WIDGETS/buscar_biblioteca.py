import re

for fname in ["index.html", "app.js"]:
    with open(fname, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if "biblioteca" in line.lower():
                print(f"{fname} Line {idx+1}: {line.strip()}")
