import os
# Desativa a proteção de chamadas assíncronas do Django para evitar erros no Playwright
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import re
import sys
import time
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from playwright.sync_api import sync_playwright

from core.models import DigitalBook

logger = logging.getLogger(__name__)

# Configura encoding do console para evitar erros de emoji no Windows
sys.stdout.reconfigure(encoding='utf-8')

class Command(BaseCommand):
    help = "Varre a Biblioteca Virtual do Wix usando Playwright e importa todos os livros/apuntes para o banco de dados."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas varre os livros sem salvar no banco de dados',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write("🚀 Iniciando o robô de varredura recursiva do Wix com Sincronia Dinâmica de DOM...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Vai até a biblioteca virtual
            url_wix = "https://secretaria478.wixsite.com/conectafcm/biblioteca-virtual"
            self.stdout.write(f"🔗 Acessando: {url_wix}")
            page.goto(url_wix)
            
            self.stdout.write("⏳ Aguardando widget carregar...")
            page.wait_for_timeout(8000)
            
            # Helper para capturar os dados brutos da lista atual
            def get_current_items():
                items_data = page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('div, span, p'))
                        .filter(d => d.innerText && (d.innerText.includes('ítem') || d.innerText.includes('MB') || d.innerText.includes('KB') || d.innerText.includes('GB')) && d.innerText.length < 150)
                        .map(d => d.innerText.trim());
                }''')
                # Dedup
                unique_items = []
                seen_texts = set()
                for item in items_data:
                    if item not in seen_texts:
                        seen_texts.add(item)
                        unique_items.append(item)
                return unique_items

            # Helper que espera até o DOM de fato mudar após um clique
            def wait_for_transition(old_items, timeout_sec=10):
                start = time.time()
                while time.time() - start < timeout_sec:
                    current = get_current_items()
                    # Se o conjunto de itens mudou, a transição ocorreu!
                    if set(current) != set(old_items):
                        page.wait_for_timeout(2000) # delay de segurança para garantir render total
                        return current
                    page.wait_for_timeout(500)
                # Fallback: se der timeout, apenas espera mais 2 segundos e retorna
                page.wait_for_timeout(2000)
                return get_current_items()

            # Clica no nó raiz "MEDICINA" para iniciar
            try:
                old_items = get_current_items()
                try:
                    page.get_by_text('MEDICINA').first.click(force=True, timeout=5000)
                except Exception:
                    page.evaluate("() => { const el = Array.from(document.querySelectorAll('div, span, p')).find(e => e.innerText && e.innerText.trim() === 'MEDICINA'); if(el) el.click(); }")
                wait_for_transition(old_items)
                self.stdout.write("📂 Entrou na pasta raiz 'MEDICINA'.")
            except Exception as e:
                self.stderr.write(f"❌ Não conseguiu abrir a pasta raiz 'MEDICINA': {e}")
                browser.close()
                return

            self.books_imported = 0
            
            # Função recursiva de varredura
            def scan_folder(path):
                self.stdout.write(f"📂 [SCAN] Varrendo: {' > '.join(path)}")
                
                unique_items = get_current_items()
                folders_to_visit = []
                files_to_download = []
                
                for item in unique_items:
                    lines = item.split('\n')
                    if len(lines) < 2:
                        continue
                    
                    name = lines[0].strip()
                    meta = lines[1].strip()
                    
                    # Ignora pastas de controle ou navegação interna
                    if name in ('Nombre del ítem', 'MI Biblioteca', 'Archivos y carpetas'):
                        continue
                        
                    if 'ítem' in meta:
                        folders_to_visit.append(name)
                    elif any(unit in meta for unit in ('MB', 'KB', 'GB')):
                        files_to_download.append(name)
                
                self.stdout.write(f"   Encontrados: {len(folders_to_visit)} pastas e {len(files_to_download)} arquivos.")
                
                # 1. Processa arquivos no nível atual
                for file_name in files_to_download:
                    # Classificação inteligente baseada no caminho de pastas
                    subject = "otras"
                    badge = "Apunte"
                    year = 1
                    
                    # Mapeia o ano
                    for segment in path:
                        if '1ER' in segment or '1°' in segment or '1ER AÑO' in segment:
                            year = 1
                        elif '2DO' in segment or '2°' in segment or '2DO AÑO' in segment:
                            year = 2
                        elif '3ER' in segment or '3°' in segment or '3ER AÑO' in segment:
                            year = 3
                        elif '4°' in segment or '4TO' in segment or '4to' in segment:
                            year = 4
                        elif '5°' in segment or '5TO' in segment or '5to' in segment:
                            year = 5
                            
                    # Mapeia a matéria (subject)
                    path_str = ' '.join(path).lower()
                    if 'anatom' in path_str:
                        subject = 'anato'
                    elif 'histol' in path_str or 'histo' in path_str:
                        if 'embrio' in file_name.lower() or 'embrio' in path_str:
                            subject = 'embrio'
                        else:
                            subject = 'histo'
                    elif 'embrio' in path_str:
                        subject = 'embrio'
                    elif 'biolog' in path_str or 'bio' in path_str:
                        subject = 'bio'
                    elif 'fisio' in path_str:
                        subject = 'fisio'
                    elif 'quimica' in path_str or 'química' in path_str:
                        subject = 'quimica'
                    elif 'micro' in path_str:
                        subject = 'micro'
                    elif 'pato' in path_str:
                        subject = 'pato'
                    elif 'farmaco' in path_str or 'farma' in path_str:
                        subject = 'farma'
                    elif 'pediatr' in path_str:
                        subject = 'pediatria'
                    elif 'gineco' in path_str or 'obstetr' in path_str:
                        subject = 'ginecologia'
                    elif 'cirug' in path_str:
                        subject = 'cirugia'
                    elif 'clinica' in path_str or 'clínica' in path_str:
                        subject = 'clinica'
                        
                    # Mapeia tipo/badge
                    if 'LIBROS' in path:
                        badge = "Libro"
                    elif 'APUNTES' in path:
                        badge = "Apunte"
                    
                    # Verifica se o arquivo já existe na base de dados
                    clean_title = re.sub(r'\.[a-zA-Z0-9]+$', '', file_name).strip()
                    exists = DigitalBook.objects.filter(title=clean_title).exists()
                    
                    if exists:
                        self.stdout.write(f"   ℹ️ [EXISTE] {clean_title} já cadastrado. Pulando.")
                        continue
                        
                    # Captura link de download via Playwright
                    self.stdout.write(f"   ⚡ [DOWNLOAD] Obtendo link de: {file_name}")
                    try:
                        pdf_url = None
                        try:
                            with page.expect_download(timeout=10000) as dl_info:
                                page.get_by_text(file_name).first.click(force=True, timeout=5000)
                            dl = dl_info.value
                            pdf_url = dl.url
                            dl.cancel()
                        except Exception:
                            # Fallback JS Click para arquivos
                            with page.expect_download(timeout=12000) as dl_info:
                                page.evaluate(f"() => {{ const el = Array.from(document.querySelectorAll('div, span, p')).find(e => e.innerText && e.innerText.trim() === '{file_name}'); if(el) el.click(); }}")
                            dl = dl_info.value
                            pdf_url = dl.url
                            dl.cancel()
                        
                        if pdf_url:
                            self.stdout.write(f"      🔗 Link obtido: {pdf_url[:80]}...")
                            if not dry_run:
                                # Conversão do ano numérico para string do modelo
                                year_str = f"{year}º Año"
                                
                                DigitalBook.objects.create(
                                    title=clean_title,
                                    author="Cátedra UNLP",
                                    subject=subject,
                                    category="Libro" if badge == "Libro" else "Apunte Completo",
                                    pdf_url=pdf_url,
                                    description=f"Material de estudio de {subject.upper()} para {year_str}. Migrado dinámicamente de Conecta FCM.",
                                    status="confirmado",
                                    year=year_str,
                                    platform="Conecta FCM"
                                )
                                self.books_imported += 1
                                self.stdout.write(f"      💾 [SALVO] {clean_title} inserido no banco.")
                            else:
                                self.stdout.write(f"      🧪 [DRY-RUN] {clean_title} seria salvo.")
                        
                    except Exception as err:
                        self.stderr.write(f"      ❌ Erro ao obter link de {file_name}: {err}")
                        
                # 2. Processa pastas recursivamente
                for folder_name in folders_to_visit:
                    self.stdout.write(f"   📂 [ENTRAR] Abrindo pasta: {folder_name}")
                    try:
                        old_items_list = get_current_items()
                        
                        # Tenta clicar pelo texto
                        try:
                            # Busca elemento que contenha o nome exato e clica nele
                            page.get_by_text(folder_name).first.click(force=True, timeout=5000)
                        except Exception:
                            # Fallback JS Click para pastas
                            page.evaluate(f"() => {{ const el = Array.from(document.querySelectorAll('div, span, p')).find(e => e.innerText && e.innerText.trim() === '{folder_name}'); if(el) el.click(); }}")
                        
                        # Sincroniza e espera a transição da tabela para a nova pasta
                        wait_for_transition(old_items_list)
                        
                        # Chamada recursiva
                        scan_folder(path + [folder_name])
                        
                        # Retorna ao nível anterior usando o breadcrumb
                        parent_folder_name = path[-1]
                        self.stdout.write(f"   ↩️ [VOLTAR] Retornando para: {parent_folder_name}")
                        
                        old_items_list = get_current_items()
                        try:
                            page.get_by_text(parent_folder_name).first.click(force=True, timeout=5000)
                        except Exception:
                            # Fallback JS Click para o breadcrumb de retorno
                            page.evaluate(f"() => {{ const el = Array.from(document.querySelectorAll('div, span, p')).find(e => e.innerText && e.innerText.trim() === '{parent_folder_name}'); if(el) el.click(); }}")
                        
                        # Sincroniza e espera retornar para a pasta pai
                        wait_for_transition(old_items_list)
                            
                    except Exception as err:
                        self.stderr.write(f"      ❌ Falha na navegação da pasta {folder_name}: {err}")
            
            # Inicia o escaneamento a partir da pasta raiz "MEDICINA"
            scan_folder(["MEDICINA"])
            
            browser.close()
            
        self.stdout.write(self.style.SUCCESS(f"🎉 Concluído! Total de {self.books_imported} livros importados para a biblioteca inteligente."))
