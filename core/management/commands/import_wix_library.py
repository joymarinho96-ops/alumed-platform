import os
# Desativa a proteção de chamadas assíncronas do Django para evitar erros no Playwright
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import re
import sys
import time
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import close_old_connections
from playwright.sync_api import sync_playwright

from core.models import DigitalBook

logger = logging.getLogger(__name__)

# Configura encoding do console para evitar erros de emoji no Windows
sys.stdout.reconfigure(encoding='utf-8')

# Função para limpar emojis e deixar apenas o texto limpo para buscas do Playwright
def clean_folder_name(name):
    # Remove emojis usando expressões regulares Unicode de emoji comuns
    cleaned = re.sub(r'[\u2700-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDD10-\uDDFF]', '', name)
    # Remove espaços duplos
    return re.sub(r'\s+', ' ', cleaned).strip()

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
        
        self.stdout.write("🚀 Iniciando o robô de varredura recursiva do Wix com Estabilização e Dedup...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Vai até a biblioteca virtual
            url_wix = "https://secretaria478.wixsite.com/conectafcm/biblioteca-virtual"
            self.stdout.write(f"🔗 Acessando: {url_wix}")
            page.goto(url_wix)
            
            self.stdout.write("⏳ Aguardando widget carregar...")
            page.wait_for_timeout(8000)
            
            # Helper para capturar os dados visíveis da lista atual
            def get_current_items():
                items_data = page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('div, span, p'))
                        .filter(d => {
                            if (!d.innerText) return false;
                            const matches = d.innerText.includes('ítem') || d.innerText.includes('MB') || d.innerText.includes('KB') || d.innerText.includes('GB');
                            if (!matches || d.innerText.length >= 150) return false;
                            
                            // Validação de visibilidade física no DOM
                            const rect = d.getBoundingClientRect();
                            const style = window.getComputedStyle(d);
                            return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
                        })
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

            # Helper que espera até o DOM visível de fato mudar após um clique
            def wait_for_transition(old_items, timeout_sec=10):
                start = time.time()
                while time.time() - start < timeout_sec:
                    current = get_current_items()
                    if set(current) != set(old_items):
                        page.wait_for_timeout(2500) # delay de segurança para render total
                        return current
                    page.wait_for_timeout(500)
                page.wait_for_timeout(2000)
                return get_current_items()

            # Helper para retorno de Breadcrumbs ou botão voltar físico (com captura de depuração)
            def click_breadcrumb_parent(parent_name):
                clean_parent = clean_folder_name(parent_name).upper()
                js_code = '''() => {
                    const clean_parent = "___PARENT___";
                    
                    // 1. Tenta achar o botão de voltar físico do Wix File Share
                    const backElements = Array.from(document.querySelectorAll('button, div, span, svg, a'))
                        .filter(el => {
                            const label = el.getAttribute('aria-label') || '';
                            const testid = el.getAttribute('data-testid') || '';
                            const className = (typeof el.className === 'string') ? el.className : '';
                            const text = el.innerText || '';
                            
                            return label.toUpperCase().includes('VOLVER') || 
                                   label.toUpperCase().includes('BACK') || 
                                   testid.toUpperCase().includes('BACK') ||
                                   className.toUpperCase().includes('BACK') ||
                                   text.toUpperCase().trim() === 'VOLVER' ||
                                   text.toUpperCase().trim() === '<';
                        });
                    if (backElements.length > 0) {
                        backElements[0].click();
                        return { success: true, method: 'back_button', debug: [] };
                    }
                    
                    // 2. Captura candidatos para depurar no Python
                    const candidates = [];
                    Array.from(document.querySelectorAll('*'))
                        .forEach(el => {
                            const text = el.innerText || '';
                            const rect = el.getBoundingClientRect();
                            const is_visible = rect.width > 0 && rect.height > 0;
                            if (is_visible && text.toUpperCase().includes(clean_parent) && text.length < 150) {
                                candidates.push({
                                    tagName: el.tagName,
                                    text: text.replace(/\\n/g, '[NL]'),
                                    length: text.length,
                                    has_nl: text.includes('\\n')
                                });
                            }
                        });
                    
                    // 3. Fallback Breadcrumb: busca elemento curto sem quebra de linha que contêm o nome pai
                    const breadcrumbElements = Array.from(document.querySelectorAll('div, span, p, a'))
                        .filter(el => {
                            const text = el.innerText || '';
                            return text.toUpperCase().trim().includes(clean_parent) && 
                                   text.length < 25 &&
                                   !text.includes('\\n');
                        });
                    if (breadcrumbElements.length > 0) {
                        breadcrumbElements.sort((a, b) => a.innerText.length - b.innerText.length);
                        breadcrumbElements[0].click();
                        return { success: true, method: 'breadcrumb', debug: candidates };
                    }
                    return { success: false, method: 'none', debug: candidates };
                }'''.replace('___PARENT___', clean_parent)
                return page.evaluate(js_code)

            # Clica no nó raiz "MEDICINA" para iniciar
            try:
                old_items = get_current_items()
                page.get_by_text('MEDICINA').first.click(force=True, timeout=5000)
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
                    
                    # Ignora pastas de controle, navegação interna ou qualquer pasta que já esteja no caminho atual
                    if name in ('Nombre del ítem', 'MI Biblioteca', 'Archivos y carpetas') or name.upper() in [p.upper() for p in path]:
                        continue
                        
                    if 'ítem' in meta:
                        folders_to_visit.append(name)
                    elif any(unit in meta for unit in ('MB', 'KB', 'GB')):
                        files_to_download.append(name)
                
                # Dedup rigoroso de pastas usando string limpa sem emojis para evitar duplicidades do DOM do Wix
                seen_folders = set()
                deduped_folders = []
                for f in folders_to_visit:
                    clean_f = clean_folder_name(f).upper()
                    if clean_f not in seen_folders:
                        seen_folders.add(clean_f)
                        deduped_folders.append(f)
                folders_to_visit = deduped_folders

                self.stdout.write(f"   Encontrados: {len(folders_to_visit)} pastas e {len(files_to_download)} arquivos.")
                
                # 1. Processa arquivos no nível atual
                for file_name in files_to_download:
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
                    
                    # Verifica se o arquivo já existe na base de dados (com reconexão automática)
                    clean_title = re.sub(r'\.[a-zA-Z0-9]+$', '', file_name).strip()
                    
                    exists = False
                    for attempt in range(3):
                        try:
                            close_old_connections()
                            exists = DigitalBook.objects.filter(title=clean_title).exists()
                            break
                        except Exception as db_exc:
                            if attempt == 2:
                                self.stderr.write(f"   ⚠️ Falha definitiva ao checar existência no banco: {db_exc}")
                            time.sleep(1)
                    
                    if exists:
                        self.stdout.write(f"   ℹ️ [EXISTE] {clean_title} já cadastrado. Pulando.")
                        continue
                        
                    # Captura link de download via Playwright
                    self.stdout.write(f"   ⚡ [DOWNLOAD] Obtendo link de: {file_name}")
                    try:
                        pdf_url = None
                        clean_file_search = clean_folder_name(file_name)
                        try:
                            with page.expect_download(timeout=10000) as dl_info:
                                page.get_by_text(clean_file_search, exact=False).first.click(force=True, timeout=5000)
                            dl = dl_info.value
                            pdf_url = dl.url
                            dl.cancel()
                        except Exception:
                            # Fallback JS Click para arquivos
                            with page.expect_download(timeout=12000) as dl_info:
                                page.evaluate(f"() => {{ const el = Array.from(document.querySelectorAll('div, span, p')).find(e => e.innerText && e.innerText.toUpperCase().includes('{clean_file_search.upper()}')); if(el) el.click(); }}")
                            dl = dl_info.value
                            pdf_url = dl.url
                            dl.cancel()
                        
                        if pdf_url:
                            self.stdout.write(f"      🔗 Link obtido: {pdf_url[:80]}...")
                            if not dry_run:
                                year_str = f"{year}º Año"
                                saved = False
                                for attempt in range(3):
                                    try:
                                        close_old_connections()
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
                                        saved = True
                                        break
                                    except Exception as db_err:
                                        self.stderr.write(f"      ⚠️ Falha ao salvar no banco, tentando reconectar: {db_err}")
                                        time.sleep(1.5)
                                
                                if saved:
                                    self.books_imported += 1
                                    self.stdout.write(f"      💾 [SALVO] {clean_title} inserido no banco.")
                                else:
                                    self.stderr.write(f"      ❌ Erro definitivo ao salvar {clean_title} no banco.")
                            else:
                                self.stdout.write(f"      🧪 [DRY-RUN] {clean_title} seria salvo.")
                        
                    except Exception as err:
                        self.stderr.write(f"      ❌ Erro ao obter link de {file_name}: {err}")
                        
                # 2. Processa pastas recursivamente
                for folder_name in folders_to_visit:
                    self.stdout.write(f"   📂 [ENTRAR] Abrindo pasta: {folder_name}")
                    try:
                        old_items_list = get_current_items()
                        
                        # Limpa emojis do nome da pasta para a busca e clica
                        clean_search = clean_folder_name(folder_name)
                        
                        try:
                            page.get_by_text(clean_search, exact=False).first.click(force=True, timeout=5000)
                        except Exception:
                            # Fallback JS Click com Includes
                            page.evaluate(f"() => {{ const el = Array.from(document.querySelectorAll('div, span, p')).find(e => e.innerText && e.innerText.toUpperCase().includes('{clean_search.upper()}')); if(el) el.click(); }}")
                        
                        # Sincroniza e espera a transição da tabela para a nova pasta
                        new_items = wait_for_transition(old_items_list)
                        
                        if set(new_items) == set(old_items_list):
                            self.stderr.write(f"      ⚠️ Falha ao abrir a pasta {folder_name} (transição de tela falhou). Pulando pasta.")
                            continue
                        
                        # Chamada recursiva
                        scan_folder(path + [folder_name])
                        
                        # Retorna ao nível anterior usando breadcrumb cirúrgico
                        parent_folder_name = path[-1]
                        self.stdout.write(f"   ↩️ [VOLTAR] Retornando para: {parent_folder_name}")
                        
                        old_items_list = get_current_items()
                        
                        # Retorno cirúrgico via Breadcrumb / Botão de voltar
                        res = click_breadcrumb_parent(parent_folder_name)
                        
                        if res['success']:
                            self.stdout.write(f"      ✅ Voltou para {parent_folder_name} via {res['method']}")
                        else:
                            self.stderr.write(f"      ⚠️ Falha ao voltar para {parent_folder_name} (método: {res['method']})")
                            self.stderr.write("      🔍 Candidatos encontrados no DOM:")
                            # Dedup debug list
                            seen_candidates = set()
                            printed_count = 0
                            for item in res['debug']:
                                cand_str = f"<{item['tagName']}> (len: {item['length']}, has_nl: {item['has_nl']}): '{item['text']}'"
                                if cand_str not in seen_candidates:
                                    seen_candidates.add(cand_str)
                                    self.stderr.write(f"         - {cand_str}")
                                    printed_count += 1
                                    if printed_count >= 15:
                                        break
                        
                        # Sincroniza, espera retornar para a pasta pai e aplica estabilização obrigatória pós-retorno de 3s
                        wait_for_transition(old_items_list)
                        page.wait_for_timeout(3000)
                            
                    except Exception as err:
                        self.stderr.write(f"      ❌ Falha na navegação da pasta {folder_name}: {err}")
            
            # Inicia o escaneamento a partir da pasta raiz "MEDICINA"
            scan_folder(["MEDICINA"])
            
            browser.close()
            
        self.stdout.write(self.style.SUCCESS(f"🎉 Concluído! Total de {self.books_imported} livros importados para a biblioteca inteligente."))
