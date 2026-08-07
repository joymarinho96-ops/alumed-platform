import os
import glob
import shutil

base_dir = r"c:\Users\joyce\OneDrive\Desktop\ATLAS HISTOLOGICOS"
user_img_dir = os.path.join(base_dir, "MIS_IMAGENES")
assets_dir = os.path.join(base_dir, "assets")
app_js_path = os.path.join(base_dir, "app.js")

# Map of keyword in filename to slide IDs
keyword_map = {
    'mesotelio': ['epi-1'],
    'chapa': ['epi-2'],
    'goblet': ['epi-2'],
    'traquea': ['epi-3', 'esp-1'],
    'esofago': ['epi-4'],
    'urotelio': ['epi-5'],
    'vejiga': ['epi-5'],
    'pancreas': ['epi-6'],
    'laxo': ['con-1'],
    'dermis': ['con-2'],
    'tendon': ['con-3'],
    'plasmocito': ['con-4'],
    'mastocito': ['con-5'],
    'adiposo': ['con-6'],
    'hialino': ['esp-1'],
    'osificacion': ['esp-2'],
    'elastico': ['esp-3'],
    'fibrocartilago': ['esp-4'],
    'hueso': ['esp-5', 'esp-6', 'esp-7'],
    'osteona': ['esp-5', 'esp-6', 'esp-7'],
    'medula_espinal': ['ner-1'],
    'cerebelo': ['ner-2'],
    'purkinje': ['ner-2'],
    'nervio': ['ner-3'],
    'ganglio_espinal': ['ner-4'],
    'meissner': ['ner-5'],
    'auerbach': ['ner-6'],
    'esqueletico': ['mus-1', 'mus-2'],
    'cardiaco': ['mus-3'],
    'corazon': ['mus-3'],
    'liso': ['mus-4'],
    'ileon': ['mus-5'],
    'timo': ['lin-1'],
    'linfatico': ['lin-2'],
    'bazo': ['lin-3'],
    'aorta': ['car-1'],
    'cava': ['car-2'],
    'vasculo': ['car-3'],
    'sangre': ['san-1'],
    'frotis': ['san-1'],
    'medula_osea': ['san-2'],
    'placenta': ['emb-1']
}

with open(app_js_path, 'r', encoding='utf-8') as f:
    app_js_content = f.read()

updated = False
files = glob.glob(os.path.join(user_img_dir, "*.*"))

for file_path in files:
    filename = os.path.basename(file_path).lower()
    if filename.endswith(".txt"):
        continue
        
    dest_name = f"user_{filename}"
    dest_path = os.path.join(assets_dir, dest_name)
    shutil.copy2(file_path, dest_path)
    
    # Check which slide IDs to map
    for kw, slide_ids in keyword_map.items():
        if kw in filename:
            for s_id in slide_ids:
                old_entry_pattern = f"'{s_id}': \"url("
                if old_entry_pattern in app_js_content:
                    start_idx = app_js_content.find(f"'{s_id}': \"url(")
                    end_idx = app_js_content.find(')"', start_idx)
                    if start_idx != -1 and end_idx != -1:
                        old_line = app_js_content[start_idx:end_idx+2]
                        new_line = f"'{s_id}': \"url('assets/{dest_name}')\""
                        app_js_content = app_js_content.replace(old_line, new_line)
                        updated = True
                        print(f"Mapped {filename} -> {s_id} ({dest_name})")

if updated:
    with open(app_js_path, 'w', encoding='utf-8') as f:
        f.write(app_js_content)
    print("app.js updated successfully with user images!")
else:
    print("No new user image mappings needed.")
