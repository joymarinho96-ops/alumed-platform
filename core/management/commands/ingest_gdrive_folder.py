"""
Management command: python manage.py ingest_gdrive_folder

Baixa e vettoriza automaticamente arquivos de una pasta do Google Drive (ex: PDFs de resúmenes)
e insere no banco ProfeJoyChunk para a IA Profe Joy.

Uso:
  python manage.py ingest_gdrive_folder --folder_id 1piahEDvWInkqjINFgJEXLxCD1J2lm8IP
"""
import os
import sys
import logging
import tempfile
import gdown
from pypdf import PdfReader
from django.core.management.base import BaseCommand
from accounts.models import ProfeJoyChunk
from core.management.commands.ingest_documents import (
    split_into_chunks,
    generate_embedding,
    _get_api_client
)

logger = logging.getLogger(__name__)
sys.stdout.reconfigure(encoding='utf-8')

class Command(BaseCommand):
    help = "Processa pasta do Google Drive e injeta documentos na base RAG da Profe Joy IA."

    def add_arguments(self, parser):
        parser.add_argument(
            '--folder_id',
            type=str,
            default='1piahEDvWInkqjINFgJEXLxCD1J2lm8IP',
            help='ID da pasta do Google Drive'
        )
        parser.add_argument(
            '--subject',
            type=str,
            default='Medicina',
            help='Matéria padrão dos documentos'
        )

    def handle(self, *args, **options):
        folder_id = options['folder_id']
        default_subject = options['subject']
        folder_url = f"https://drive.google.com/drive/folders/{folder_id}"

        self.stdout.write(f"📁 Baixando arquivos do Google Drive: {folder_url}")

        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                downloaded_files = gdown.download_folder(url=folder_url, output=tmp_dir, quiet=False, use_cookies=False)
            except Exception as e:
                self.stderr.write(f"⚠️ Descarga parcial o aviso de espacio: {e}")
                downloaded_files = []
                for root, dirs, files in os.walk(tmp_dir):
                    for f in files:
                        downloaded_files.append(os.path.join(root, f))

            if not downloaded_files:
                # Search any files downloaded in tmp_dir
                for root, dirs, files in os.walk(tmp_dir):
                    for f in files:
                        downloaded_files.append(os.path.join(root, f))

            self.stdout.write(self.style.SUCCESS(f"✅ Encontrados {len(downloaded_files)} archivos descargados."))

            # API Client for embeddings
            client_type = 'mock'
            client = None
            try:
                client_type, client = _get_api_client()
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️ Usando cliente mock para embeddings: {e}"))

            for file_path in downloaded_files:
                if not os.path.exists(file_path):
                    continue
                if not file_path.lower().endswith('.pdf'):
                    self.stdout.write(f"ℹ️ Saltando archivo no PDF: {os.path.basename(file_path)}")
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
                    continue

                filename = os.path.basename(file_path)
                title = os.path.splitext(filename)[0]
                self.stdout.write(f"\n📖 Procesando apunte: {title}")

                try:
                    reader = PdfReader(file_path)
                    pages = []
                    for p in reader.pages:
                        t = p.extract_text()
                        if t:
                            pages.append(t.strip())
                    text = "\n\n".join(pages)
                except Exception as read_err:
                    self.stderr.write(f"❌ Error leyendo PDF {filename}: {read_err}")
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
                    continue

                # Remove file from disk immediately to free space
                try:
                    os.remove(file_path)
                except Exception:
                    pass

                if not text or len(text.strip()) < 30:
                    self.stdout.write(self.style.WARNING(f"⚠️ PDF vacío o de imágenes sin texto: {filename}"))
                    continue

                chunks = split_into_chunks(text, chunk_size=500, overlap=50)
                self.stdout.write(f"   ✂️ Dividido en {len(chunks)} fragmentos RAG.")

                # Clean existing chunks for this file title if re-ingesting
                ProfeJoyChunk.objects.filter(title=title).delete()

                saved = 0
                for idx, chunk_text in enumerate(chunks):
                    emb = []
                    if client_type != 'mock':
                        try:
                            emb = generate_embedding(client_type, client, chunk_text)
                        except Exception as emb_err:
                            logger.warning(f"Error generando embedding chunk {idx}: {emb_err}")

                    ProfeJoyChunk.objects.create(
                        title=title,
                        source_type='pdf',
                        source_url=folder_url,
                        year='1',
                        subject=default_subject,
                        chunk_index=idx,
                        content=chunk_text,
                        embedding=emb
                    )
                    saved += 1

                self.stdout.write(self.style.SUCCESS(f"   ✅ Guardados {saved} chunks para '{title}'"))

        self.stdout.write(self.style.SUCCESS(f"\n🎉 ¡Proceso finalizado! Total de chunks en DB: {ProfeJoyChunk.objects.count()}"))
