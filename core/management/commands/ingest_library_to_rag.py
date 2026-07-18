import os
# Desativa a proteção assíncrona do Django
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import sys
import logging
from django.core.management.base import BaseCommand
from core.models import DigitalBook
from accounts.models import ProfeJoyChunk
from core.management.commands.ingest_documents import (
    _get_api_client,
    extract_text_from_pdf_url,
    split_into_chunks,
    generate_embedding,
)

logger = logging.getLogger(__name__)

# Configura encoding do console para evitar erros de emoji no Windows
sys.stdout.reconfigure(encoding='utf-8')

class Command(BaseCommand):
    help = "Processa todos os PDFs da biblioteca digital, extrai texto, gera embeddings e os injeta no RAG do Profe Joy IA."

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Limite de livros a processar (0 para todos)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Processa livros mesmo que já estejam no RAG',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        force = options['force']
        
        self.stdout.write("🧠 Iniciando o pipeline de vetorização para o Profe Joy IA...")
        
        # 1. Obtém o cliente de API de embeddings ativo (Gemini ou OpenAI)
        try:
            client_type, client = _get_api_client()
            self.stdout.write(self.style.SUCCESS(f"✅ Motor de embedding ativo: {client_type.upper()}"))
        except Exception as e:
            self.stderr.write(f"❌ Erro de chaves de API: {e}")
            return

        # 2. Busca livros da biblioteca digital com URLs válidas
        books = DigitalBook.objects.exclude(pdf_url="")
        if limit > 0:
            books = books[:limit]
            
        self.stdout.write(f"📖 Total de livros elegíveis na biblioteca: {books.count()}")
        
        processed_count = 0
        
        for i, book in enumerate(books):
            self.stdout.write(f"\n📖 [{i+1}/{books.count()}] Processando: {book.title}")
            
            # Verifica se já está vetorizado
            source_title = f"Biblioteca: {book.title}"
            exists = ProfeJoyChunk.objects.filter(title=source_title).exists()
            if exists and not force:
                self.stdout.write(f"   ℹ️ [PULADO] Já vetorizado na base de conhecimento. Use --force para reprocessar.")
                continue
                
            self.stdout.write(f"   ⏳ Baixando PDF e extraindo texto de: {book.pdf_url[:80]}...")
            try:
                # Extrai texto usando a função do ingest_documents
                text = extract_text_from_pdf_url(book.pdf_url)
                if not text or len(text.strip()) < 50:
                    self.stderr.write("   ❌ Texto extraído muito curto ou inválido. Pulando.")
                    continue
                    
                self.stdout.write(f"   📄 Texto extraído com sucesso ({len(text)} caracteres).")
                
                # Divide o texto em chunks
                chunks = split_into_chunks(text, chunk_size=500, overlap=50)
                self.stdout.write(f"   ✂️ Dividido em {len(chunks)} fragmentos (chunks).")
                
                # Limpa chunks antigos se estiver forçando o reprocessamento
                if exists:
                    deleted, _ = ProfeJoyChunk.objects.filter(title=source_title).delete()
                    self.stdout.write(f"   🗑️ Removidos {deleted} chunks anteriores.")
                
                # Mapeia a matéria e ano para o chunk
                # Mapeia ano string "1º Año" para "1"
                year_num = "1"
                if book.year:
                    match = re.search(r'\d+', book.year)
                    if match:
                        year_num = match.group(0)
                
                saved_chunks = 0
                for index, chunk in enumerate(chunks):
                    # Gera o embedding do fragmento
                    try:
                        embedding = generate_embedding(client_type, client, chunk)
                    except Exception as api_err:
                        self.stderr.write(f"   ❌ Erro ao gerar embedding no chunk {index}: {api_err}")
                        break
                        
                    # Cria o chunk vetorial no Supabase/Postgres
                    ProfeJoyChunk.objects.create(
                        title=source_title,
                        source_url=book.pdf_url,
                        content=chunk,
                        embedding=embedding,
                        source_type='pdf',
                        chunk_index=index,
                        year=year_num,
                        subject=book.subject,
                    )
                    saved_chunks += 1
                    
                self.stdout.write(self.style.SUCCESS(f"   💾 Vetorização concluída! {saved_chunks} chunks injetados."))
                processed_count += 1
                
            except Exception as err:
                self.stderr.write(f"   ❌ Erro durante processamento do livro: {err}")
                continue
                
        self.stdout.write(self.style.SUCCESS(f"\n🎉 Pipeline finalizado! {processed_count} livros vetorizados e inseridos na base de dados do Profe Joy."))
import re
