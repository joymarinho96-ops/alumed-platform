"""
Management command: python manage.py scrape_cartelera

Scraper robusto da Cartelera FCM-UNLP.

Estrutura real inspecionada em 2026-07-16:
  URL base:   https://cartelera.med.unlp.edu.ar/
  Container:  div.card.card-outline-success  (58 avisos encontrados)
  Data:       div.card-header > h5.m-b-0.text-white  (ex: "[DATE] 14/07/2026")
  Título:     div.card-body > h4.card-title > a[href]
  Subtítulo:  div.card-body > h6.card-subtitle  (texto "-" quando vazio)
  Emissor:    div.card-body > p.card-text.text-right
  Link:       /noticia/<id>  (relativo -> absoluto)

Deduplicação: usa external_id (/noticia/<id>) como chave única.
  - Nunca duplica avisos existentes.
  - Detecta mudanças de conteúdo via content_hash.
  - Apenas atualiza last_seen_at em avisos sem mudança.

Notificação: separa captura de envio.
  - Salva no banco com notified_at=None.
  - Outro comando/task envia as notificações.

Uso no Railway: Scheduled Job a cada 15-30 min.
  python manage.py scrape_cartelera
  python manage.py scrape_cartelera --dry-run   (sem salvar)
  python manage.py scrape_cartelera --notify    (salva + envia Telegram)
"""
import hashlib
import logging
import os
import re
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import CarteleraItem

logger = logging.getLogger(__name__)

# ── Configuração ──────────────────────────────────────────────
BASE_URL      = 'https://cartelera.med.unlp.edu.ar'
CARTELERA_URL = f'{BASE_URL}/'

# Headers disfarçados de Chrome 120 real — evita bloqueios
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept':           'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language':  'es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding':  'gzip, deflate, br',
    'Referer':          'https://www.med.unlp.edu.ar/',
    'DNT':              '1',
    'Connection':       'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest':   'document',
    'Sec-Fetch-Mode':   'navigate',
    'Sec-Fetch-Site':   'same-origin',
    'Cache-Control':    'max-age=0',
}
TIMEOUT = 20  # segundos



# ── Parser ────────────────────────────────────────────────────
def _clean_text(text: str) -> str:
    """Remove espaços extras, ícones unicode e texto de ícones FontAwesome."""
    if not text:
        return ''
    return re.sub(r'\s+', ' ', text).strip()


def _parse_date(date_text: str) -> date | None:
    """
    Converte datas do formato 'DD/MM/YYYY' para objeto date.
    Retorna None se não conseguir parsear.
    """
    # Remove ícones e espaços extras (ex: " [DATE] 14/07/2026")
    cleaned = re.sub(r'[^\d/]', ' ', date_text).strip()
    match = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', cleaned)
    if not match:
        return None
    try:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        return date(year, month, day)
    except (ValueError, TypeError):
        return None


def _make_hash(title: str, date_str: str, issuer: str) -> str:
    """SHA-256 de título+data+emissor -- detecta mudanças de conteúdo."""
    raw = f'{title}|{date_str}|{issuer}'.lower().strip()
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def _extract_external_id(href: str) -> str:
    """
    Extrai ID do aviso do path.
    Ex: '/noticia/263' -> 'noticia_263'
    """
    path = href.strip('/')
    return path.replace('/', '_')


def parse_cartelera(html: str) -> list[dict]:
    """
    Parseia o HTML da Cartelera FCM-UNLP e retorna lista de avisos.

    Estrutura real verificada:
      div.card.card-outline-success
        └── div.card-header
        │     └── h5.m-b-0.text-white   -> data
        └── div.card-body
              ├── h4.card-title > a[href]  -> título + link
              ├── h6.card-subtitle         -> subtítulo (ou "-")
              └── p.card-text.text-right   -> emissor
    """
    soup = BeautifulSoup(html, 'lxml')
    avisos = []

    # Cada aviso está em div.card.card-outline-success
    cards = soup.select('div.card.card-outline-success')
    logger.info(f'Parser encontrou {len(cards)} cards na página')

    for card in cards:
        try:
            # ── DATA ──
            header = card.select_one('div.card-header h5.m-b-0')
            date_str = _clean_text(header.get_text()) if header else ''

            # ── TÍTULO + LINK ──
            title_tag = card.select_one('div.card-body h4.card-title a')
            if not title_tag:
                continue  # Sem título = sem aviso válido
            title = _clean_text(title_tag.get_text())
            href  = title_tag.get('href', '')
            if not href:
                continue

            # URL absoluta
            url = href if href.startswith('http') else f'{BASE_URL}{href}'
            external_id = _extract_external_id(href)

            # ── SUBTÍTULO ──
            subtitle_tag = card.select_one('div.card-body h6.card-subtitle')
            subtitle_raw = _clean_text(subtitle_tag.get_text()) if subtitle_tag else ''
            subtitle = '' if subtitle_raw in ('-', '--', '') else subtitle_raw

            # ── EMISSOR ──
            issuer_tag = card.select_one('div.card-body p.card-text')
            issuer = _clean_text(issuer_tag.get_text()) if issuer_tag else ''

            # ── HASH ──
            content_hash = _make_hash(title, date_str, issuer)
            date_parsed  = _parse_date(date_str)

            avisos.append({
                'external_id':  external_id,
                'content_hash': content_hash,
                'title':        title,
                'subtitle':     subtitle,
                'issuer':       issuer,
                'date_str':     date_str,
                'date_parsed':  date_parsed,
                'url':          url,
            })
        except Exception as exc:
            logger.warning(f'Erro ao parsear card: {exc}')
            continue

    return avisos


# ── Motor de Classificação por Ano ────────────────────────────
# Mapeia palavras-chave do título/subtítulo/emissor para anos da FCM-UNLP.
# String vazia ('') = aviso geral para todos os alunos.

YEAR_KEYWORDS: dict[str, list[str]] = {
    'ingreso': [
        'ingresante', 'ingreso', 'ingresantes 2025', 'ingresantes 2026',
        'premed', 'preingreso', 'pre-ingreso', 'nivelacion', 'curso ingreso',
    ],
    '1': [
        'anatomia', 'histologia', 'embriologia', 'quimica biologica',
        'biologia celular', 'primer ano', '1er ano', '1° ano', 'primer año',
        '1er año', 'bioquimica', 'introduccion a la medicina', 'ciencias exactas',
        'fisiologia', 'biologia',
    ],
    '2': [
        'microbiologia', 'parasitologia', 'farmacologia basica', 'patologia general',
        'semiologia', 'segundo ano', '2do ano', '2° ano', 'segundo año',
        'propedeutica', 'fisiopatologia', 'bioquimica clinica',
    ],
    '3': [
        'patologia', 'farmacologia aplicada', 'clinica medica',
        'tercer ano', '3er ano', '3° ano', 'tercer año',
    ],
    '4': [
        'medicina interna', 'cirugia', 'pediatria', 'ginecologia', 'obstetricia',
        'cuarto ano', '4to ano', '4° ano', 'cuarto año', 'psiquiatria',
    ],
    '5': [
        'salud publica', 'medicina legal', 'neurologia', 'dermatologia',
        'oftalmologia', 'otorrinolaringologia', 'infectologia', 'terapia intensiva',
        'quinto ano', '5to ano', '5° ano', 'quinto año', 'urologia',
        'ortopedia', 'traumatologia',
    ],
    '6': [
        'sexto ano', '6to ano', '6° ano', 'sexto año', 'rotacion',
        'rotaciones', 'practica final', 'medicina general', 'medicina familiar',
    ],
    'internado': [
        'internado', 'internados', 'residencia', 'concurso residencia',
        'residencias medicas', 'mir', 'examen residencia',
    ],
}

# ── Mapa de Cátedras por Ano (FCM-UNLP) ──────────────────────
# Extraído do HTML real de cartelera.med.unlp.edu.ar
# Chave: ID da cátedra | Valor: ano(s) alvo (string CSV)
CATEDRA_YEAR_MAP: dict[int, str] = {
    # ── MEDICINA ── 1° Ano ─────────────────────────────────────
    1:  '1',   # Biología
    5:  '1',   # Ciencias Exactas
    26: '1',   # Citología, Histología y Embriología
    32: '1',   # Anatomía A
    4:  '1',   # Anatomía B
    68: '1',   # Anatomía C
    58: '1',   # Bioquímica y Biología Molecular
    # ── MEDICINA ── 2° Ano ─────────────────────────────────────
    21: '2',   # Fisiología y Física Biológica
    6:  '2',   # Microbiología y Parasitología
    69: '2',   # Farmacología Básica
    9:  '2',   # Bioquímica Clínica I
    8:  '2',   # Bioquímica Clínica II
    # ── MEDICINA ── 3° Ano ─────────────────────────────────────
    71: '3',   # Patología A
    18: '3',   # Patología B
    23: '3',   # Farmacología Aplicada
    # ── MEDICINA ── 4° Ano ─────────────────────────────────────
    60: '4',   # Medicina Interna A
    24: '4',   # Medicina Interna B
    63: '4',   # Medicina Interna C
    7:  '4',   # Medicina Interna D
    70: '4',   # Medicina Interna E
    61: '4',   # Medicina Interna F
    3:  '4',   # Cirugía A
    64: '4',   # Cirugía B
    67: '4',   # Cirugía C
    19: '4',   # Cirugía D
    22: '4',   # Cirugía E
    11: '4',   # Pediatría A
    16: '4',   # Pediatría B
    30: '4',   # Ginecología A
    25: '4',   # Ginecología B
    17: '4',   # Obstetricia
    31: '4',   # Psiquiatría
    # ── MEDICINA ── 5° Ano ─────────────────────────────────────
    75: '5',   # Salud Pública
    33: '5',   # Deontología Médica y Medicina Legal
    80: '5',   # Neurología
    20: '5',   # Dermatología
    34: '5',   # Oftalmología
    37: '5',   # Ortopedia y Traumatología
    36: '5',   # Otorrinolaringología
    29: '5',   # Infectología
    28: '5',   # Terapia Intensiva
    10: '5',   # Toxicología
    38: '5',   # Urología
    78: '5',   # Cirugía de Tórax
    # ── MEDICINA ── 6° Ano / Internado ────────────────────────
    204: '6',  # Medicina General y Familiar
    55:  '6',  # Salud y Medicina Comunitaria
    56:  '6',  # Ecología Humana y Promoción de la Salud
    # ── Materias Optativas / Todos ────────────────────────────
    66:  '',   # Bioética (todos)
    76:  '',   # Ciencias Sociales y Medicina (todos)
    73:  '',   # Historia de la Medicina (todos)
    65:  '',   # Filosofía Médica (todos)
    72:  '',   # Literatura, Cine y Medicina (todos)
    74:  '',   # Diagnóstico por Imágenes (todos)
    79:  '',   # Informática Básica (todos)
    77:  '',   # Informática Médica (todos)
    82:  '',   # Inglés Médico (todos)
    35:  '',   # Genética (todos)
    27:  '',   # Inmunología (todos)
    84:  '',   # Epidemiología (todos)
    85:  '',   # Neuroanatomía Semiológica (todos)
    83:  '',   # El paciente con enfermedad crónica (todos)
    86:  '',   # Departamento de Informática (todos)
    87:  '',   # Seminarios de Investigación (todos)
    88:  '',   # Enfermedades Poco Frecuentes (todos)
    89:  '',   # Discapacidad Intelectual (todos)
    206: '',   # Neurocirugía (todos)
    57:  '',   # Educación para la Salud (todos)
    54:  '',   # Salud Ambiental (todos)
    62:  '',   # Psicología Médica (todos)
    # ── EU (Enfermería Universitaria) ─────────────────────────
    39:  '1',  # EU - 1º Año
    40:  '2',  # EU - 2º Año
    41:  '3',  # EU - 3º Año
    14:  '',   # EU - Información General
    # ── LEN (Lic. en Nutrición) ───────────────────────────────
    42:  '1',  # LEN - 1º AÑO
    43:  '2',  # LEN - 2º AÑO
    44:  '3',  # LEN - 3º AÑO
    45:  '4',  # LEN - 4º AÑO
    46:  '5',  # LEN - 5º AÑO
    12:  '',   # LEN - INFORMACIÓN GENERAL
    # ── LOB (Lic. en Obstetricia) ─────────────────────────────
    47:  '1',  # LOB - 1º AÑO
    48:  '2',  # LOB - 2º Año
    49:  '3',  # LOB - 3º Año
    50:  '4',  # LOB - 4º Año
    13:  '',   # LOB - Información General
    90:  '',   # LOB - PFO
    # ── TPC (Tec. en Prácticas Cardiológicas) ─────────────────
    51:  '1',  # TPC - 1º Año
    52:  '2',  # TPC - 2º Año
    53:  '3',  # TPC - 3º Año
    15:  '',   # TPC - Información General
}

# Cátedras prioritárias para raspar (por ano FCM-UNLP Medicina + anos gerais)
# Scrapa apenas estas para não sobrecarregar o servidor
CATEDRAS_TO_SCRAPE: list[int] = [
    # Ano 1 - Medicina
    1, 5, 26, 32, 4, 68, 58,
    # Ano 2 - Medicina
    21, 6, 69,
    # Ano 3 - Medicina
    71, 18, 23,
    # Ano 4 - Medicina
    60, 24, 11, 16, 3, 64, 17, 31,
    # Ano 5 - Medicina
    75, 33, 80, 20, 34, 29,
    # Gerais / todos
    66, 84, 86,
    # EU por ano
    39, 40, 41,
    # LEN por ano
    42, 43, 44, 45, 46,
    # LOB por ano
    47, 48, 49, 50,
    # TPC por ano
    51, 52, 53,
]


# Palavras que indicam aviso GERAL (para todos os anos)
GENERAL_KEYWORDS = [
    'todos los alumnos', 'todos los estudiantes', 'comunidad', 'general',
    'secretaria academica', 'beca', 'becas', 'biblioteca', 'extension',
    'bienestar', 'boleto', 'comedor', 'inscripcion general',
    'elecciones', 'claustro', 'centro de estudiantes',
]


def classify_years(title: str, subtitle: str, issuer: str) -> str:
    """
    Analisa título, subtítulo e emissor do aviso e retorna os anos alvo
    em formato CSV. Ex: '1,2' | 'ingreso' | '' (todos).

    Logica:
    1. Se contém palavras-chave gerais -> '' (todos os alunos)
    2. Se contém palavras-chave de ano(s) específico(s) -> CSV desses anos
    3. Se nenhuma palavra-chave -> '' (todos, por segurança)
    """
    texto = f"{title} {subtitle} {issuer}".lower()
    # Normaliza acentos para comparação
    import unicodedata
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')

    # Verificar se é aviso geral
    for kw in GENERAL_KEYWORDS:
        kw_norm = unicodedata.normalize('NFKD', kw).encode('ascii', 'ignore').decode('ascii')
        if kw_norm in texto:
            return ''  # geral

    # Verificar anos específicos
    anos_encontrados = []
    for year, keywords in YEAR_KEYWORDS.items():
        for kw in keywords:
            kw_norm = unicodedata.normalize('NFKD', kw).encode('ascii', 'ignore').decode('ascii')
            if kw_norm in texto:
                if year not in anos_encontrados:
                    anos_encontrados.append(year)
                break  # basta uma kw por ano

    if anos_encontrados:
        # Ordenar: ingreso < 1 < 2 ... < internado
        order = ['ingreso', '1', '2', '3', '4', '5', '6', 'internado']
        anos_encontrados.sort(key=lambda x: order.index(x) if x in order else 99)
        return ','.join(anos_encontrados)

    return ''  # sem match = geral


def fetch_cartelera() -> str:
    """
    Faz requisição segura à Cartelera FCM-UNLP (página principal).
    Levanta exceção em caso de falha para o caller tratar.
    """
    response = requests.get(
        CARTELERA_URL,
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    response.encoding = response.apparent_encoding or 'utf-8'
    return response.text


def fetch_catedra(catedra_id: int) -> str | None:
    """
    Raspa uma página específica de cátedra: /catedra/{id}
    Retorna o HTML ou None em caso de erro.
    """
    import time
    url = f'{BASE_URL}/catedra/{catedra_id}'
    try:
        headers = dict(HEADERS)
        headers['Referer'] = CARTELERA_URL  # simula navegação da cartelera
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or 'utf-8'
        time.sleep(0.5)  # delay educado para não sobrecarregar o servidor
        return resp.text
    except Exception as exc:
        logger.warning(f'Falha ao raspar cátedra {catedra_id}: {exc}')
        return None


def deep_scrape_aviso(item: CarteleraItem) -> bool:
    """
    Entra no link interno do aviso (/noticia/<id>), extrai o texto completo
    e busca por links/PDFs de anexos. Baixa e extrai texto de arquivos PDF.
    """
    import io
    from bs4 import BeautifulSoup
    from pypdf import PdfReader
    
    url = item.url
    logger.info(f'[DEEP] Acessando aviso: {url}')
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(resp.text, 'lxml')
        
        # O corpo do aviso geralmente está na div .card-body principal
        body_div = soup.select_one('div.card.card-outline-success div.card-body') or soup.select_one('div.card-body')
        if not body_div:
            # Fallback para o body inteiro
            body_div = soup.select_one('body')
            
        if not body_div:
            return False
            
        # Extrai textos excluindo o cabeçalho e rodapé se existirem
        paragraphs = []
        for p in body_div.find_all(['p', 'div', 'li', 'h4', 'h5', 'h6', 'span']):
            text = p.get_text(strip=True)
            # Evita duplicar textos contidos em tags filhas
            if text and not any(text in existing for existing in paragraphs):
                paragraphs.append(text)
                
        full_text = '\n'.join(paragraphs)
        
        # Encontrar anexos
        attachments = []
        for link in body_div.find_all('a', href=True):
            href = link['href']
            # Se for relativo, torna absoluto
            abs_url = href if href.startswith('http') else f'{BASE_URL}{href}'
            
            # Evita links duplicados ou links de navegação comuns
            if abs_url != item.url and abs_url not in [a['url'] for a in attachments]:
                title = link.get_text(strip=True) or 'Enlace/Anexo'
                
                # Identifica se é arquivo
                is_file = any(abs_url.lower().endswith(ext) for ext in ('.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg', '.xls', '.xlsx'))
                
                attachments.append({
                    'title': title,
                    'url': abs_url,
                    'is_file': is_file
                })
                
                # Se for PDF, extrai texto do PDF e soma ao corpo
                if abs_url.lower().endswith('.pdf'):
                    try:
                        logger.info(f'   [PDF] Baixando anexo: {abs_url}')
                        pdf_resp = requests.get(abs_url, headers=HEADERS, timeout=TIMEOUT)
                        pdf_resp.raise_for_status()
                        reader = PdfReader(io.BytesIO(pdf_resp.content))
                        pdf_pages = []
                        for page in reader.pages:
                            p_txt = page.extract_text()
                            if p_txt:
                                pdf_pages.append(p_txt.strip())
                        if pdf_pages:
                            full_text += f"\n\n--- [Texto extraído do anexo PDF: {title}] ---\n" + '\n'.join(pdf_pages)
                            logger.info(f'   [PDF] {len(pdf_pages)} páginas extraídas')
                    except Exception as pdf_err:
                        logger.warning(f'   [PDF-ERR] Falha ao extrair PDF {abs_url}: {pdf_err}')
                        
        item.body_text = full_text.strip()
        item.attachment_urls = attachments
        item.is_deep_scraped = True
        item.save()
        logger.info(f'[DEEP] Sucesso! {len(item.body_text)} chars salvos e {len(attachments)} anexos listados.')
        return True
    except Exception as exc:
        logger.error(f'[DEEP] Falha ao processar aviso {item.external_id}: {exc}')
        return False


def ingest_to_rag(item: CarteleraItem) -> int:
    """
    Divide o texto limpo do aviso em chunks e gera embeddings (OpenAI, Gemini ou Mock).
    Insere na base de dados do Profe Joy (ProfeJoyChunk).
    """
    from accounts.models import ProfeJoyChunk
    from core.profe_joy_views import _get_api_client, _embed_query
    from core.management.commands.ingest_documents import split_into_chunks, generate_embedding
    
    if not item.body_text:
        return 0
        
    title = f"Cartelera: {item.title}"
    
    # Remove chunks anteriores da mesma notícia
    deleted, _ = ProfeJoyChunk.objects.filter(title=title).delete()

    
    # Prepara o texto com contexto do emissor e data
    header = f"Aviso de la Cartelera FCM-UNLP\nFecha: {item.date_str}\nEmisor: {item.issuer or 'Sin emisor'}\nTítulo: {item.title}\n"
    if item.subtitle:
        header += f"Subtítulo: {item.subtitle}\n"
    header += "\nContenido:\n"
    
    full_content = header + item.body_text
    
    chunks = split_into_chunks(full_content, chunk_size=300, overlap=30)
    if not chunks:
        return 0
        
    try:
        client_type, client = _get_api_client()
    except Exception:
        client_type, client = 'mock', None
        
    saved = 0
    for i, chunk in enumerate(chunks):
        try:
            embedding = []
            if client_type != 'mock':
                try:
                    embedding = generate_embedding(client_type, client, chunk)
                except Exception as api_err:
                    logger.warning(f'[RAG-ERR] Falha na API de embedding, usando mock: {api_err}')
                    client_type = 'mock'
                    
            ProfeJoyChunk.objects.create(
                title=title,
                source_url=item.url,
                source_type='url',
                content=chunk,
                embedding=embedding,
                chunk_index=i,
                year=item.target_years,
                subject=item.category or 'Cartelera',
            )
            saved += 1
        except Exception as exc:
            logger.error(f'[RAG-ERR] Erro no chunk {i} do aviso {item.external_id}: {exc}')
            
    return saved



def send_telegram(item: CarteleraItem) -> bool:
    """
    Envia notificação Telegram para um aviso.
    Usa variáveis de ambiente -- nunca credenciais hardcoded.
    Retorna True se enviado com sucesso.
    """
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id   = os.environ.get('TELEGRAM_CHAT_ID', '')

    if not bot_token or not chat_id:
        logger.warning('TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não configurados -- notificação ignorada')
        return False

    emoji_issuer = '[ORG]'
    text = (
        f"[PIN] *CARTELERA FCM-UNLP*\n\n"
        f"[DATE] {item.date_str}\n"
        f"*{item.title}*\n"
        f"{('_' + item.subtitle + '_' + chr(10)) if item.subtitle else ''}"
        f"{emoji_issuer} {item.issuer or 'Sin emisor'}\n\n"
        f"[LINK] [Ver aviso completo]({item.url})"
    )

    api_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    try:
        resp = requests.post(api_url, json={
            'chat_id':    chat_id,
            'text':       text,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': False,
        }, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as exc:
        logger.error(f'Erro ao enviar Telegram para aviso {item.external_id}: {exc}')
        return False


def send_telegram_segmented(item: CarteleraItem) -> bool:
    """
    Notificacao CIRURGICA por ano da carreira.

    Fluxo:
    1. Posta no canal principal (TELEGRAM_CHAT_ID) com tag do ano — visivel a todos.
    2. Envia DM individual para cada TelegramSubscriber cujo year bate com
       os target_years do aviso.
       - Aviso geral (target_years='') -> todos os subscribers ativos
       - Aviso de ano especifico -> apenas subscribers daquele ano + 'todos'

    Retorna True se pelo menos uma mensagem foi enviada.
    """
    from accounts.models import TelegramSubscriber

    bot_token  = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    channel_id = os.environ.get('TELEGRAM_CHAT_ID', '')

    if not bot_token:
        logger.warning('TELEGRAM_BOT_TOKEN nao configurado')
        return False

    # ── Montar texto do aviso ──────────────────────────────────
    anos_display = {
        'ingreso': '🎓 Ingreso', '1': '1° Año', '2': '2° Año',
        '3': '3° Año', '4': '4° Año', '5': '5° Año',
        '6': '6° Año', 'internado': '🏥 Internado',
    }
    if item.target_years:
        anos_lista = [anos_display.get(a, a) for a in item.target_years.split(',')]
        tag    = ' · '.join(anos_lista)
        header = f'📌 *CARTELERA FCM* — [{tag}]\n\n'
    else:
        header = '📌 *CARTELERA FCM* — [Todos los alumnos]\n\n'

    text = (
        f"{header}"
        f"📅 {item.date_str}\n"
        f"*{item.title}*\n"
        f"{('_' + item.subtitle + '_\n') if item.subtitle else ''}"
        f"🏛 {item.issuer or 'Sin emisor'}\n\n"
        f"🔗 [Ver aviso completo]({item.url})"
    )

    api_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    sent    = 0

    # ── 1. Postar no canal principal ───────────────────────────
    if channel_id:
        try:
            r = requests.post(api_url, json={
                'chat_id': channel_id, 'text': text,
                'parse_mode': 'Markdown', 'disable_web_page_preview': False,
            }, timeout=10)
            r.raise_for_status()
            sent += 1
            logger.info(f'Canal notificado | {item.external_id}')
        except Exception as exc:
            logger.error(f'Erro canal {item.external_id}: {exc}')

    # ── 2. DMs individuais segmentados ─────────────────────────
    subscribers = TelegramSubscriber.get_targets_for_years(item.target_years)
    total_subs  = subscribers.count()

    if total_subs == 0:
        logger.info(f'Sem subscribers para anos={item.target_years or "geral"}')
        return sent > 0

    logger.info(
        f'Enviando DMs para {total_subs} subscribers '
        f'| anos={item.target_years or "geral"} | {item.external_id}'
    )

    # Mensagem de DM (sem o header do canal — mais pessoal)
    dm_text = (
        f"🔔 *Nuevo aviso en Cartelera FCM*\n\n"
        f"📅 {item.date_str}\n"
        f"*{item.title}*\n"
        f"{('_' + item.subtitle + '_\n') if item.subtitle else ''}"
        f"🏛 {item.issuer or 'Sin emisor'}\n\n"
        f"🔗 [Ver aviso completo]({item.url})\n\n"
        f"_Para cancelar: /cancelar_"
    )

    for sub in subscribers:
        try:
            r = requests.post(api_url, json={
                'chat_id':    sub.telegram_chat_id,
                'text':       dm_text,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': False,
            }, timeout=10)
            r.raise_for_status()
            sent += 1
        except requests.exceptions.HTTPError as exc:
            # 403 = usuario bloqueou o bot -> desativar
            if r.status_code == 403:
                sub.is_active = False
                sub.save(update_fields=['is_active'])
                logger.warning(f'Subscriber {sub.telegram_chat_id} bloqueou o bot -> desativado')
            else:
                logger.error(f'DM falhou para {sub.telegram_chat_id}: {exc}')
        except Exception as exc:
            logger.error(f'DM erro {sub.telegram_chat_id}: {exc}')

    logger.info(f'Notificacao concluida | enviados={sent} (1 canal + {sent-1} DMs)')
    return sent > 0


# ── Management Command ────────────────────────────────────────
class Command(BaseCommand):
    help = (
        'Scrapa a Cartelera FCM-UNLP e salva os avisos no banco. '
        'Não duplica avisos. Separa captura de notificação. '
        'Rodar a cada 15-30 min no Railway como Scheduled Job.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Mostra o que seria salvo sem gravar no banco'
        )
        parser.add_argument(
            '--notify', action='store_true',
            help='Envia notificações Telegram para avisos novos'
        )
        parser.add_argument(
            '--limit', type=int, default=0,
            help='Limita quantidade de avisos processados (0 = sem limite)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        do_notify = options['notify']
        limit = options['limit']

        self.stdout.write(self.style.MIGRATE_HEADING(
            '\n[ALUMED] Conecta Radar -- Cartelera FCM-UNLP'
        ))
        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY-RUN] Nada sera salvo no banco'))

        # ── 1. Fetch página principal ──
        try:
            self.stdout.write('[*] Buscando cartelera principal...')
            html = fetch_cartelera()
            self.stdout.write(self.style.SUCCESS(f'[OK] HTML recebido ({len(html)} chars)'))
        except requests.exceptions.Timeout:
            self.stderr.write(self.style.ERROR('[ERROR] Timeout ao acessar a cartelera'))
            return
        except requests.exceptions.HTTPError as exc:
            self.stderr.write(self.style.ERROR(f'[ERROR] HTTP error: {exc}'))
            return
        except requests.exceptions.ConnectionError as exc:
            self.stderr.write(self.style.ERROR(f'[ERROR] Conexão falhou: {exc}'))
            return
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f'[ERROR] Erro inesperado no fetch: {exc}'))
            return

        # ── 2. Parse página principal ──
        avisos = parse_cartelera(html)
        self.stdout.write(f'[LIST] Avisos encontrados na principal: {len(avisos)}')

        # Classificar por palavras-chave (página principal não tem cátedra)
        for aviso in avisos:
            aviso['_target_years'] = classify_years(
                aviso.get('title', ''),
                aviso.get('subtitle', ''),
                aviso.get('issuer', ''),
            )

        # ── 3. Raspar TODAS as cátedras ──
        self.stdout.write(f'\n[*] Raspando {len(CATEDRAS_TO_SCRAPE)} cátedras específicas...')
        total_catedra_avisos = 0

        for catedra_id in CATEDRAS_TO_SCRAPE:
            year_for_catedra = CATEDRA_YEAR_MAP.get(catedra_id, '')
            html_cat = fetch_catedra(catedra_id)
            if not html_cat:
                continue

            avisos_cat = parse_cartelera(html_cat)
            if not avisos_cat:
                continue

            total_catedra_avisos += len(avisos_cat)
            # Para avisos de cátedra: ano vem do mapa (preciso) — não de palavras-chave
            for aviso in avisos_cat:
                aviso['_target_years'] = year_for_catedra
                # Merge: evita duplicatas com a lista principal
                already = any(a['external_id'] == aviso['external_id'] for a in avisos)
                if not already:
                    avisos.append(aviso)

            self.stdout.write(
                f'   [catedra/{catedra_id}] → {len(avisos_cat)} avisos | ano={year_for_catedra or "geral"}'
            )

        self.stdout.write(f'\n[LIST] Total após cátedras: {len(avisos)} avisos únicos')

        if limit:
            avisos = avisos[:limit]
            self.stdout.write(f'[CFG]  Limitado a {limit} avisos')

        if not avisos:
            self.stdout.write(self.style.WARNING('[WARN]  Nenhum aviso encontrado -- verificar seletores'))
            return

        # ── 4. Salvar / Deduplicar ──
        stats = {'new': 0, 'updated': 0, 'unchanged': 0, 'notified': 0}

        for aviso in avisos:
            self.stdout.write(
                f"  -> [{aviso['date_str']}] {aviso['title'][:60]}… | {aviso['issuer']}"
            )

            if dry_run:
                exists = CarteleraItem.objects.filter(external_id=aviso['external_id']).exists()
                status = '[EXISTS] JÁ EXISTE' if exists else '[NEW] NOVO'
                self.stdout.write(f'     {status}')
                continue

            target_years = aviso.pop('_target_years', classify_years(
                aviso.get('title', ''), aviso.get('subtitle', ''), aviso.get('issuer', '')
            ))

            try:
                existing = CarteleraItem.objects.get(external_id=aviso['external_id'])
                
                # Se mudou conteúdo OU se ainda não foi feito scraping profundo
                if existing.content_hash != aviso['content_hash'] or not existing.is_deep_scraped:
                    had_change = existing.content_hash != aviso['content_hash']
                    
                    for field in ('title', 'subtitle', 'issuer', 'date_str',
                                  'date_parsed', 'url', 'content_hash'):
                        setattr(existing, field, aviso[field])
                    existing.is_active = True
                    if target_years:
                        existing.target_years = target_years
                    existing.save()
                    
                    if had_change:
                        stats['updated'] += 1
                        self.stdout.write(self.style.WARNING('     [UPDATED] Atualizado'))
                    else:
                        stats['unchanged'] += 1
                        self.stdout.write('     [RE-SCRAPE] Forçando raspagem profunda')

                    # Raspagem profunda + RAG
                    if deep_scrape_aviso(existing):
                        chunks_count = ingest_to_rag(existing)
                        self.stdout.write(self.style.SUCCESS(f'     [RAG] {chunks_count} chunks gerados'))
                else:
                    existing.is_active = True
                    existing.save(update_fields=['is_active', 'last_seen_at'])
                    stats['unchanged'] += 1
            except CarteleraItem.DoesNotExist:
                item = CarteleraItem.objects.create(**aviso, target_years=target_years)
                stats['new'] += 1
                label = f'[ANOS: {target_years}]' if target_years else '[GERAL]'
                self.stdout.write(self.style.SUCCESS(f'     [OK] Novo aviso salvo {label}'))

                # Raspagem profunda + RAG
                if deep_scrape_aviso(item):
                    chunks_count = ingest_to_rag(item)
                    self.stdout.write(self.style.SUCCESS(f'     [RAG] {chunks_count} chunks gerados'))

                # ── 5. Notificar ──
                if do_notify:
                    sent = send_telegram_segmented(item)
                    if sent:
                        item.notified_at = timezone.now()
                        item.save(update_fields=['notified_at'])
                        stats['notified'] += 1
                        self.stdout.write(self.style.SUCCESS('     [SENT] Notificacao enviada'))


        # ── 6. Marcar inativos ──
        if not dry_run and avisos:
            active_ids = [a['external_id'] for a in avisos]
            inactive = CarteleraItem.objects.exclude(external_id__in=active_ids).filter(is_active=True)
            if inactive.exists():
                count = inactive.update(is_active=False)
                self.stdout.write(self.style.WARNING(f'\n[ARCHIVE]  {count} avisos marcados como inativos'))

        # ── 7. Resumo ──
        self.stdout.write('\n' + '-' * 50)
        self.stdout.write(self.style.SUCCESS(
            '[DONE] Concluido!\n'
            f'   [NEW]     Novos:       {stats["new"]}\n'
            f'   [UPDATED] Atualizados: {stats["updated"]}\n'
            f'   [OK]      Sem mudanca: {stats["unchanged"]}\n'
            f'   [SENT]    Notificados: {stats["notified"]}'
        ))



