import os
import glob
import shutil

base_dir = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\ATLAS HISTOLOGICOS"
user_img_dir = os.path.join(base_dir, "MIS_IMAGENES")
assets_dir = os.path.join(base_dir, "assets")
static_assets_dir = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\static\atlas_histologico\assets"

os.makedirs(assets_dir, exist_ok=True)
os.makedirs(static_assets_dir, exist_ok=True)

# Copy all user images from MIS_IMAGENES into assets and static/atlas_histologico/assets
files = glob.glob(os.path.join(user_img_dir, "*.*"))
copied_count = 0

for file_path in files:
    filename = os.path.basename(file_path)
    if filename.lower().endswith(".txt"):
        continue
        
    dest_path1 = os.path.join(assets_dir, filename)
    dest_path2 = os.path.join(static_assets_dir, filename)
    
    shutil.copy2(file_path, dest_path1)
    shutil.copy2(file_path, dest_path2)
    copied_count += 1
    print(f"Copiada foto local: {filename}")

print(f"Total fotos copiadas desde MIS_IMAGENES: {copied_count}")
