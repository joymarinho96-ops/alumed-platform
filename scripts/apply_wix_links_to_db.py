import json
import os
import sys
import django

sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
sys.path.append(r"c:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumed.settings')
django.setup()

from core.models import DigitalBook

json_path = os.path.join("..", "biblioteca_viva.json")
if not os.path.exists(json_path):
    json_path = "biblioteca_viva.json"
    if not os.path.exists(json_path):
        print("❌ Archivo biblioteca_viva.json no encontrado.")
        sys.exit(0)

print(f"📖 Leyendo enlaces desde: {json_path}")
with open(json_path, "r", encoding="utf-8") as f:
    records = json.load(f)

print(f"Total de registros cargados: {len(records)}")

updated_count = 0
for r in records:
    title = r["titulo_livro"]
    url = r["url_wix"]
    
    # Update matching books in database
    books = DigitalBook.objects.filter(title__icontains=title)
    if books.exists():
        for b in books:
            b.pdf_url = url
            b.save()
            print(f" ✅ ID {b.id}: Vinculada URL para '{b.title}'")
            updated_count += 1
    else:
        # Create new entry if not exists
        b = DigitalBook.objects.create(
            title=title,
            subject=r.get("materia", "anato"),
            category="Libro Oficial",
            year="1º Año",
            pdf_url=url,
            status="confirmado"
        )
        print(f" ✨ Creado nuevo registro ID {b.id} con URL para '{title}'")
        updated_count += 1

print(f"\n🎉 Vinculación completa! {updated_count} libros actualizados con su enlace real en la base de datos.")
