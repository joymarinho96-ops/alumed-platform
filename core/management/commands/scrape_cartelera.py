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
BASE_URL    = 'https://cartelera.med.unlp.edu.ar'
CARTELERA_URL = f'{BASE_URL}/'
HEADERS = {
    'User-Agent': 'ALUMED-Bot/1.0 (FCM-UNLP student platform; +https://alumed.com)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
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
        'anatomia', 'histologia', 'embriologia', 'fisiologia', 'quimica biologica',
        'biologia celular', 'primer ano', '1er ano', '1° ano', 'primer año',
        '1er año', 'bioquimica', 'introduccion a la medicina',
    ],
    '2': [
        'microbiologia', 'parasitologia', 'farmacologia', 'patologia general',
        'semiologia', 'segundo ano', '2do ano', '2° ano', 'segundo año',
        'propedeutica', 'fisiopatologia',
    ],
    '3': [
        'clinica medica', 'cirugia', 'pediatria', 'ginecologia', 'obstetricia',
        'tercer ano', '3er ano', '3° ano', 'tercer año', 'medicina interna',
        'diagnostico por imagenes', 'urologia',
    ],
    '4': [
        'cuarto ano', '4to ano', '4° ano', 'cuarto año', 'salud publica',
        'medicina legal', 'psiquiatria', 'neurologia', 'infectologia',
        'dermatologia', 'oftalmologia', 'otorrinolaringologia',
    ],
    '5': [
        'quinto ano', '5to ano', '5° ano', 'quinto año', 'medicina familiar',
        'geriatria', 'oncologia', 'hematologia', 'endocrinologia',
        'reumatologia', 'cardiologia',
    ],
    '6': [
        'sexto ano', '6to ano', '6° ano', 'sexto año', 'rotacion',
        'rotaciones', 'practica final', 'egresado',
    ],
    'internado': [
        'internado', 'internados', 'residencia', 'concurso residencia',
        'residencias medicas', 'mir', 'examen residencia',
    ],
}

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
    Faz requisição segura à Cartelera FCM-UNLP.
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
    Notificacao segmentada por ano da carreira.

    Logica:
    - Se target_years == '' -> aviso geral -> envia para o canal principal (TELEGRAM_CHAT_ID)
    - Se target_years == '1,2' -> filtra alunos com profile.year in ['1','2']
      e envia mensagens individuais via TELEGRAM_BOT_TOKEN para cada chat_id pessoal
      (se o aluno tiver telegram_chat_id cadastrado no perfil -- campo futuro).
    - Por enquanto, envia para o canal principal com tag de ano no titulo.

    Retorna True se pelo menos uma mensagem foi enviada com sucesso.
    """
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id   = os.environ.get('TELEGRAM_CHAT_ID', '')

    if not bot_token or not chat_id:
        logger.warning('TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID nao configurados')
        return False

    # Etiqueta do ano para o titulo da mensagem
    if item.target_years:
        anos_display = {
            'ingreso': 'Ingreso',
            '1': '1 Ano', '2': '2 Ano', '3': '3 Ano',
            '4': '4 Ano', '5': '5 Ano', '6': '6 Ano',
            'internado': 'Internado',
        }
        anos_lista = [anos_display.get(a, a) for a in item.target_years.split(',')]
        tag = ' | '.join(anos_lista)
        header = f'[PIN] *CARTELERA FCM* [{tag}]\n\n'
    else:
        header = '[PIN] *CARTELERA FCM* [TODOS LOS ALUMNOS]\n\n'

    text = (
        f"{header}"
        f"[DATE] {item.date_str}\n"
        f"*{item.title}*\n"
        f"{('_' + item.subtitle + '_' + chr(10)) if item.subtitle else ''}"
        f"[ORG] {item.issuer or 'Sin emisor'}\n\n"
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
        logger.info(f'Aviso {item.external_id} notificado | anos={item.target_years or "geral"}')
        return True
    except Exception as exc:
        logger.error(f'Erro ao enviar Telegram segmentado {item.external_id}: {exc}')
        return False


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

        # ── 1. Fetch ──
        try:
            self.stdout.write('[*] Buscando cartelera...')
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

        # ── 2. Parse ──
        avisos = parse_cartelera(html)
        self.stdout.write(f'[LIST] Avisos encontrados: {len(avisos)}')

        if limit:
            avisos = avisos[:limit]
            self.stdout.write(f'[CFG]  Limitado a {limit} avisos')

        if not avisos:
            self.stdout.write(self.style.WARNING('[WARN]  Nenhum aviso encontrado -- verificar seletores'))
            return

        # ── 3. Salvar / Deduplicar ──
        stats = {'new': 0, 'updated': 0, 'unchanged': 0, 'notified': 0}

        for aviso in avisos:
            self.stdout.write(
                f"  -> [{aviso['date_str']}] {aviso['title'][:60]}… | {aviso['issuer']}"
            )

            if dry_run:
                # Apenas verificar se existe
                exists = CarteleraItem.objects.filter(external_id=aviso['external_id']).exists()
                status = '[EXISTS] JÁ EXISTE' if exists else '[NEW] NOVO'
                self.stdout.write(f'     {status}')
                continue

            # Buscar existente
            try:
                existing = CarteleraItem.objects.get(external_id=aviso['external_id'])
                if existing.content_hash != aviso['content_hash']:
                    # Conteúdo mudou -- atualizar
                    for field in ('title', 'subtitle', 'issuer', 'date_str',
                                  'date_parsed', 'url', 'content_hash'):
                        setattr(existing, field, aviso[field])
                    existing.is_active = True
                    existing.save()
                    stats['updated'] += 1
                    self.stdout.write(self.style.WARNING('     [UPDATED] Atualizado (conteúdo mudou)'))
                else:
                    # Sem mudança -- apenas toca last_seen_at (auto_now=True)
                    existing.is_active = True
                    existing.save(update_fields=['is_active', 'last_seen_at'])
                    stats['unchanged'] += 1
            except CarteleraItem.DoesNotExist:
                # Novo aviso -- classificar por ano e salvar
                target_years = classify_years(
                    aviso.get('title', ''),
                    aviso.get('subtitle', ''),
                    aviso.get('issuer', ''),
                )
                item = CarteleraItem.objects.create(**aviso, target_years=target_years)
                stats['new'] += 1
                label = f'[ANOS: {target_years}]' if target_years else '[GERAL]'
                self.stdout.write(self.style.SUCCESS(f'     [OK] Novo aviso salvo {label}'))

                # ── 4. Notificar (se solicitado) -- segmentado por ano ──
                if do_notify:
                    sent = send_telegram_segmented(item)
                    if sent:
                        item.notified_at = timezone.now()
                        item.save(update_fields=['notified_at'])
                        stats['notified'] += 1
                        self.stdout.write(self.style.SUCCESS('     [SENT] Notificacao enviada'))

        # ── 5. Marcar avisos não vistos como inativos ──
        if not dry_run and avisos:
            active_ids = [a['external_id'] for a in avisos]
            inactive = CarteleraItem.objects.exclude(external_id__in=active_ids).filter(is_active=True)
            if inactive.exists():
                count = inactive.update(is_active=False)
                self.stdout.write(self.style.WARNING(f'\n[ARCHIVE]  {count} avisos marcados como inativos'))

        # 6. Resumo
        self.stdout.write('\n' + '-' * 50)
        self.stdout.write(self.style.SUCCESS(
            '[DONE] Concluido!\n'
            f'   [NEW]     Novos:       {stats["new"]}\n'
            f'   [UPDATED] Atualizados: {stats["updated"]}\n'
            f'   [OK]      Sem mudanca: {stats["unchanged"]}\n'
            f'   [SENT]    Notificados: {stats["notified"]}'
        ))


