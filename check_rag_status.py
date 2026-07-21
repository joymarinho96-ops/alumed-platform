import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumed.settings')
django.setup()

from accounts.models import ProfeJoyChunk
from django.db.models import Count

total = ProfeJoyChunk.objects.count()
sem_embed = ProfeJoyChunk.objects.filter(embedding=[]).count()
com_embed = total - sem_embed

print(f"{'='*40}")
print(f"ESTADO DO RAG - Profe Joy")
print(f"{'='*40}")
print(f"Total de chunks na DB: {total}")
print(f"Chunks COM embedding:  {com_embed}")
print(f"Chunks SEM embedding:  {sem_embed}")
print()
print("Por matéria:")
for r in ProfeJoyChunk.objects.values('subject').annotate(c=Count('id')).order_by('subject'):
    print(f"  {r['subject'] or 'N/A'}: {r['c']} chunks")

print()
print("Títulos únicos:")
for r in ProfeJoyChunk.objects.values('title').distinct().order_by('title'):
    t = r['title'][:60] if r['title'] else 'N/A'
    print(f"  - {t}")
