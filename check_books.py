
import os, django, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumed.settings')
django.setup()

from core.models import DigitalBook
books = DigitalBook.objects.all().order_by('subject','title')
total = books.count()

sin_url = list(books.filter(pdf_url='').values('id','title','subject'))
con_url = list(books.exclude(pdf_url='').values('id','title','subject','pdf_url'))

print(f"Total: {total} | Con URL: {len(con_url)} | Sin URL: {len(sin_url)}")
print("\n=== PRIMEROS 30 CON URL ===")
for b in con_url[:30]:
    print(f"ID:{b['id']:4d} | {b['subject']:12s} | {b['title'][:50]:50s} | {b['pdf_url'][:70]}")

print("\n=== PRIMEROS 20 SIN URL ===")
for b in sin_url[:20]:
    print(f"ID:{b['id']:4d} | {b['subject']:12s} | {b['title'][:60]}")
