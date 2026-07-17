"""
Management command: python manage.py ingest_documents

Ingere PDFs, URLs e texto plano na base de conhecimento do Profe Joy IA.
Divide o conteúdo em chunks de ~500 tokens, gera embeddings OpenAI
e salva no banco (ProfeJoyChunk).

Uso:
  python manage.py ingest_documents --pdf https://example.com/anatomia.pdf --title "Anatomía" --year 1
  python manage.py ingest_documents --url https://example.com/page --title "Farmacología" --year 2
  python manage.py ingest_documents --text "Texto direto..." --title "Nota Clínica" --year 3
  python manage.py ingest_documents --clear  # remove todos os chunks
"""
import logging
import os
import io
import math
import time

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from accounts.models import ProfeJoyChunk

logger = logging.getLogger(__name__)

CHUNK_SIZE   = 500   # tokens aproximados por chunk (palavras)
CHUNK_OVERLAP = 50   # sobreposição entre chunks
EMBED_MODEL  = 'text-embedding-3-small'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
}


def _get_openai_client():
    from openai import OpenAI
    key = os.environ.get('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', '')
    if not key:
        raise ValueError('OPENAI_API_KEY não configurada nas variáveis de ambiente!')
    return OpenAI(api_key=key)


def extract_text_from_pdf_url(url: str) -> str:
    """Baixa um PDF de uma URL e extrai o texto com pypdf."""
    from pypdf import PdfReader
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    reader = PdfReader(io.BytesIO(resp.content))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.strip())
    return '\n\n'.join(pages)


def extract_text_from_url(url: str) -> str:
    """Raspa texto limpo de uma página web."""
    from bs4 import BeautifulSoup
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'lxml')
    # Remove scripts e estilos
    for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
        tag.decompose()
    return soup.get_text(separator='\n', strip=True)


def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Divide o texto em chunks de ~chunk_size palavras com sobreposição."""
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = ' '.join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        if end >= len(words):
            break
        start += chunk_size - overlap
    return chunks


def generate_embedding(client, text: str) -> list[float]:
    """Gera embedding via OpenAI text-embedding-3-small."""
    resp = client.embeddings.create(
        model=EMBED_MODEL,
        input=text[:8000],  # limite de tokens
    )
    return resp.data[0].embedding


class Command(BaseCommand):
    help = 'Ingere PDFs, URLs ou texto na base de conhecimento do Profe Joy IA.'

    def add_arguments(self, parser):
        parser.add_argument('--pdf',     type=str, help='URL de um PDF para ingerir')
        parser.add_argument('--url',     type=str, help='URL de uma página web para ingerir')
        parser.add_argument('--text',    type=str, help='Texto direto para ingerir')
        parser.add_argument('--title',   type=str, default='Material ALUMED', help='Título do material')
        parser.add_argument('--year',    type=str, default='', help='Ano letivo alvo (1,2,3...)')
        parser.add_argument('--subject', type=str, default='', help='Matéria (ex: Anatomía)')
        parser.add_argument('--clear',   action='store_true', help='Remove TODOS os chunks do banco')
        parser.add_argument('--list',    action='store_true', help='Lista todos os materiais ingeridos')

    def handle(self, *args, **options):
        if options['clear']:
            count = ProfeJoyChunk.objects.count()
            ProfeJoyChunk.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'[CLEAR] {count} chunks removidos.'))
            return

        if options['list']:
            items = ProfeJoyChunk.objects.values('title', 'source_type', 'year', 'subject') \
                        .distinct().order_by('title')
            self.stdout.write(f'\n{"="*60}')
            self.stdout.write(f'{"MATERIAL":<40} {"TIPO":<6} {"ANO":<8} MATÉRIA')
            self.stdout.write(f'{"="*60}')
            for item in items:
                self.stdout.write(
                    f'{item["title"][:39]:<40} {item["source_type"]:<6} '
                    f'{item["year"] or "geral":<8} {item["subject"]}'
                )
            self.stdout.write(f'Total: {ProfeJoyChunk.objects.count()} chunks\n')
            return

        # ── Detectar fonte ──
        title       = options['title']
        year        = options['year']
        subject     = options['subject']
        source_type = 'text'
        source_url  = ''
        raw_text    = ''

        if options['pdf']:
            source_url  = options['pdf']
            source_type = 'pdf'
            self.stdout.write(f'[PDF] Baixando: {source_url}')
            try:
                raw_text = extract_text_from_pdf_url(source_url)
                self.stdout.write(self.style.SUCCESS(f'[OK]  {len(raw_text)} chars extraídos'))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'[ERR] Falha ao extrair PDF: {exc}'))
                return

        elif options['url']:
            source_url  = options['url']
            source_type = 'url'
            self.stdout.write(f'[URL] Raspando: {source_url}')
            try:
                raw_text = extract_text_from_url(source_url)
                self.stdout.write(self.style.SUCCESS(f'[OK]  {len(raw_text)} chars extraídos'))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'[ERR] Falha ao raspar URL: {exc}'))
                return

        elif options['text']:
            raw_text = options['text']
            self.stdout.write(f'[TEXT] {len(raw_text)} chars recebidos')

        else:
            self.stderr.write(self.style.ERROR('Informe --pdf, --url ou --text'))
            return

        if not raw_text.strip():
            self.stderr.write(self.style.WARNING('[WARN] Texto vazio — nada para ingerir'))
            return

        # ── Chunking ──
        chunks = split_into_chunks(raw_text)
        self.stdout.write(f'[SPLIT] {len(chunks)} chunks gerados')

        # ── Remove chunks anteriores do mesmo material ──
        deleted, _ = ProfeJoyChunk.objects.filter(title=title).delete()
        if deleted:
            self.stdout.write(f'[CLEAN] {deleted} chunks antigos removidos')

        # ── Embeddings + Salvar ──
        client = _get_openai_client()
        saved = 0
        for i, chunk in enumerate(chunks):
            try:
                embedding = generate_embedding(client, chunk)
                ProfeJoyChunk.objects.create(
                    title=title,
                    source_url=source_url,
                    source_type=source_type,
                    content=chunk,
                    embedding=embedding,
                    chunk_index=i,
                    year=year,
                    subject=subject,
                )
                saved += 1
                if (i + 1) % 5 == 0:
                    self.stdout.write(f'  ... {i+1}/{len(chunks)} chunks salvos')
                time.sleep(0.2)  # rate limit
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'[ERR] Chunk {i}: {exc}'))

        self.stdout.write(self.style.SUCCESS(
            f'\n[DONE] {saved}/{len(chunks)} chunks salvos para "{title}" (ano={year or "geral"})'
        ))
