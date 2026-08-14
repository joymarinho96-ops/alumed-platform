import os
import sys
import json
import pandas as pd
import django

sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
sys.path.append(r"c:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumed.settings')
django.setup()

from core.models import DigitalBook

def parse_path_folders(path_str):
    try:
        folders = json.loads(path_str)
        return [f['name'].upper() for f in folders]
    except Exception:
        return []

def populate_all_medicina():
    csv_path = os.path.join("..", "BibliotecaJoy", "FileshareFiles.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join("BibliotecaJoy", "FileshareFiles.csv")
        if not os.path.exists(csv_path):
            print("❌ CSV no encontrado.")
            return

    print("📖 Cargando e ingiriendo TODOS los años de MEDICINA desde FileshareFiles.csv...")
    df = pd.read_csv(csv_path)

    imported_count = 0
    skipped_count = 0
    duplicate_count = 0

    for idx, row in df.iterrows():
        name = row['Name']
        ext = str(row['Extension']).lower()
        path_folders = parse_path_folders(row['Path'])
        path_joined = " | ".join(path_folders)
        
        # We only want to process MEDICINA files
        if "MEDICINA" not in path_folders:
            skipped_count += 1
            continue

        # Determine subject mapping
        subject = "otras"
        
        # 1. 1st year subjects
        if "ANATOMÍA" in path_joined or "ANATOMIA" in path_joined:
            subject = "anato"
        elif "HISTOLOGÍA Y EMBRIOLOGÍA" in path_joined or "HISTO Y EMBRIO" in path_joined:
            subject = "histo"
            if "EMBRIO" in name.upper() or "EMBRIOLOGÍA" in path_joined:
                subject = "embrio"
        elif "HISTOLOGÍA" in path_joined or "HISTO" in path_joined:
            subject = "histo"
        elif "EMBRIOLOGÍA" in path_joined or "EMBRIO" in path_joined:
            subject = "embrio"
        elif "BIOLOGÍA" in path_joined or "BIOLOGIA" in path_joined or "BIOLO" in path_joined:
            subject = "bio"
        
        # 2. 2nd year subjects
        elif "QUÍMICA" in path_joined or "QUIMICA" in path_joined or "BIOQUÍMICA" in path_joined or "BIOQUIMICA" in path_joined:
            subject = "quimica"
        elif "FISIOLOGÍA" in path_joined or "FISIOLOGIA" in path_joined or "FISIO" in path_joined or "BIOFÍSICA" in path_joined or "BIOFISICA" in path_joined:
            subject = "fisio"
            
        # 3. 3rd year subjects
        elif "MICROBIOLOGÍA" in path_joined or "MICROBIOLOGIA" in path_joined or "MICRO" in path_joined or "PARASITOLOGÍA" in path_joined or "PARASITOLOGIA" in path_joined:
            subject = "micro"
        elif "PATOLOGÍA" in path_joined or "PATOLOGIA" in path_joined or "PATO" in path_joined:
            subject = "pato"
        elif "FARMACOLOGÍA" in path_joined or "FARMACOLOGIA" in path_joined or "FARMA" in path_joined:
            subject = "farma"
            
        # 4. 4th/5th year subjects
        elif "SEMIOLOGÍA" in path_joined or "SEMIOLOGIA" in path_joined or "SEMIO" in path_joined:
            subject = "semiologia"
        elif "PEDIATRÍA" in path_joined or "PEDIATRIA" in path_joined:
            subject = "pediatria"
        elif "GINECOLOGÍA" in path_joined or "GINECOLOGIA" in path_joined or "OBSTETRICIA" in path_joined:
            subject = "ginecologia"
        elif "CIRUGÍA" in path_joined or "CIRUGIA" in path_joined:
            subject = "cirugia"
        elif "CLÍNICA" in path_joined or "CLINICA" in path_joined:
            subject = "clinica"
            
        # Determine year
        year = "1º Año"
        if "2DO AÑO" in path_joined or "2° AÑO" in path_joined or "2º AÑO" in path_joined:
            year = "2º Año"
        elif "3ER AÑO" in path_joined or "3° AÑO" in path_joined or "3º AÑO" in path_joined:
            year = "3º Año"
        elif "4TO" in path_joined or "4° AÑO" in path_joined or "5TO" in path_joined or "5° AÑO" in path_joined or "4TO Y 5TO AÑO" in path_joined:
            year = "4º y 5º Año"
            
        # Determine Category
        category = "Apunte de Cátedra"
        if "LIBROS" in path_joined:
            category = "Libro Oficial"
        elif "RESUMEN" in name.upper() or "RESUMENES" in path_joined:
            category = "Resumen de Alumno"
        elif "SIMULACRO" in path_joined or "EXAMEN" in path_joined or "PARCIAL" in path_joined or "FINAL" in path_joined:
            category = "Simulacro / Parcial"

        # Check if already exists
        exists = DigitalBook.objects.filter(title=name, subject=subject).exists()
        if exists:
            duplicate_count += 1
            continue
            
        # Register new DigitalBook
        DigitalBook.objects.create(
            title=name,
            description=f"Recurso digital oficial para estudiantes de Medicina de la UNLP. Tema: {category}.",
            subject=subject,
            category=category,
            year=year,
            platform="Conecta FCM",
            author=row['Owner'] if pd.notna(row['Owner']) else "Cátedra FCM",
            page_count=1,
            status="confirmado",
            tags=f"{subject}, {ext}, conecta, medicina"
        )
        imported_count += 1

    print(f"\n✅ Ingesta masiva finalizada!")
    print(f"Libros importados nuevos para MEDICINA: {imported_count}")
    print(f"Registros omitidos (no MEDICINA): {skipped_count}")
    print(f"Duplicados omitidos: {duplicate_count}")
    print(f"Total actual de libros en BD: {DigitalBook.objects.count()}")

if __name__ == "__main__":
    populate_all_medicina()
