import os
import glob

template_dir = r"c:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\templates"
for filepath in glob.glob(os.path.join(template_dir, "**/*.html"), recursive=True):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if "Biblioteca" in line or "biblioteca" in line:
                print(f"{filepath}:{i+1}:{line.strip()}")
