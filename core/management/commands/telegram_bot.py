"""
Management command: python manage.py telegram_bot

Bot Telegram do Conecta Radar FCM.
Permite que alunos se cadastrem para receber notificacoes segmentadas por ano.

Fluxo:
  Aluno envia /start
    -> Bot pergunta: "¿En qué año estás?"
    -> Aluno clica no botao do seu ano
    -> Bot salva TelegramSubscriber no banco
    -> Aluno recebe avisos da Cartelera apenas do seu ano

Comandos:
  /start    - Cadastrar ou atualizar ano
  /meu_ano  - Ver ano atual cadastrado
  /cancelar - Desativar notificacoes
  /ajuda    - Ver todos os comandos

Uso:
  python manage.py telegram_bot          # roda em polling continuo
  python manage.py telegram_bot --once   # processa updates pendentes e sai
"""
import logging
import os
import time

import requests
from django.core.management.base import BaseCommand

from accounts.models import TelegramSubscriber

logger = logging.getLogger(__name__)

# ── Configuracao ──────────────────────────────────────────────
POLL_TIMEOUT  = 30   # long polling timeout (segundos)
POLL_INTERVAL = 1    # pausa entre ciclos (segundos)

YEAR_BUTTONS = [
    [
        {'text': '🎓 Ingreso',    'callback_data': 'year:ingreso'},
        {'text': '1° Año',        'callback_data': 'year:1'},
    ],
    [
        {'text': '2° Año',        'callback_data': 'year:2'},
        {'text': '3° Año',        'callback_data': 'year:3'},
    ],
    [
        {'text': '4° Año',        'callback_data': 'year:4'},
        {'text': '5° Año',        'callback_data': 'year:5'},
    ],
    [
        {'text': '6° Año',        'callback_data': 'year:6'},
        {'text': '🏥 Internado',  'callback_data': 'year:internado'},
    ],
    [
        {'text': '📢 Todos los años', 'callback_data': 'year:todos'},
    ],
]

YEAR_DISPLAY = {
    'ingreso':   '🎓 Ingreso',
    '1':         '1° Año',
    '2':         '2° Año',
    '3':         '3° Año',
    '4':         '4° Año',
    '5':         '5° Año',
    '6':         '6° Año',
    'internado': '🏥 Internado',
    'todos':     '📢 Todos los años',
}

WELCOME_TEXT = (
    "👋 *¡Bienvenido al Conecta Radar FCM!*\n\n"
    "🔔 Recibí avisos de la Cartelera de la Facultad de Ciencias Médicas — "
    "*directamente en tu Telegram, filtrados por tu año*.\n\n"
    "📚 ¿En qué año de la carrera estás?"
)

HELP_TEXT = (
    "🤖 *Conecta Radar FCM — Comandos*\n\n"
    "/start — Registrarse o cambiar de año\n"
    "/meu\\_ano — Ver tu año actual\n"
    "/cancelar — Desactivar notificaciones\n"
    "/ajuda — Ver esta ayuda\n\n"
    "💡 Los avisos llegan automáticamente cada vez que "
    "la Cartelera FCM se actualiza."
)


class TelegramAPI:
    """Wrapper minimalista para a API do Telegram Bot."""

    def __init__(self, token: str):
        self.token = token
        self.base  = f'https://api.telegram.org/bot{token}'
        self.session = requests.Session()

    def _post(self, method: str, **kwargs) -> dict:
        try:
            r = self.session.post(f'{self.base}/{method}', json=kwargs, timeout=35)
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            logger.error(f'Telegram API error [{method}]: {exc}')
            return {}

    def get_updates(self, offset: int = 0, timeout: int = POLL_TIMEOUT) -> list:
        data = self._post('getUpdates', offset=offset, timeout=timeout,
                          allowed_updates=['message', 'callback_query'])
        return data.get('result', [])

    def send_message(self, chat_id: int, text: str,
                     reply_markup: dict = None, parse_mode: str = 'Markdown') -> dict:
        kwargs = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
        if reply_markup:
            kwargs['reply_markup'] = reply_markup
        return self._post('sendMessage', **kwargs)

    def answer_callback(self, callback_id: str, text: str = '') -> dict:
        return self._post('answerCallbackQuery',
                          callback_query_id=callback_id, text=text)

    def edit_message_text(self, chat_id: int, message_id: int,
                          text: str, parse_mode: str = 'Markdown') -> dict:
        return self._post('editMessageText', chat_id=chat_id,
                          message_id=message_id, text=text, parse_mode=parse_mode)


def inline_keyboard(buttons: list) -> dict:
    return {'inline_keyboard': buttons}


# ── Handlers ──────────────────────────────────────────────────

def handle_start(api: TelegramAPI, chat_id: int,
                 first_name: str, username: str):
    """Envia mensagem de boas-vindas com teclado de seleção de ano."""
    api.send_message(
        chat_id, WELCOME_TEXT,
        reply_markup=inline_keyboard(YEAR_BUTTONS),
    )
    logger.info(f'/start recebido de {username or chat_id}')


def handle_meu_ano(api: TelegramAPI, chat_id: int):
    """Mostra o ano atual cadastrado."""
    try:
        sub = TelegramSubscriber.objects.get(telegram_chat_id=chat_id)
        year_label = YEAR_DISPLAY.get(sub.year, sub.year)
        text = (
            f"📚 Tu año actual: *{year_label}*\n\n"
            f"Para cambiar, usa /start"
        )
    except TelegramSubscriber.DoesNotExist:
        text = "❌ No estás registrado aún. Usa /start para registrarte."
    api.send_message(chat_id, text)


def handle_cancelar(api: TelegramAPI, chat_id: int):
    """Desativa as notificacoes do aluno."""
    updated = TelegramSubscriber.objects.filter(
        telegram_chat_id=chat_id
    ).update(is_active=False)

    if updated:
        text = (
            "🔕 *Notificaciones desactivadas.*\n\n"
            "Podés volver a activarlas cuando quieras con /start."
        )
    else:
        text = "❌ No estabas registrado. Usa /start para registrarte."
    api.send_message(chat_id, text)


def handle_year_callback(api: TelegramAPI, callback_id: str,
                         chat_id: int, message_id: int,
                         first_name: str, username: str, year: str):
    """Salva o ano escolhido e confirma."""
    sub, created = TelegramSubscriber.objects.update_or_create(
        telegram_chat_id=chat_id,
        defaults={
            'first_name': first_name or '',
            'username':   username or '',
            'year':       year,
            'is_active':  True,
        }
    )
    year_label = YEAR_DISPLAY.get(year, year)
    action     = 'registrado' if created else 'actualizado'

    # Confirmar no callback (remove o "carregando" do botao)
    api.answer_callback(callback_id, f'✅ {year_label}')

    # Editar a mensagem original com a confirmacao
    api.edit_message_text(
        chat_id, message_id,
        f"✅ *¡{action.capitalize()}!*\n\n"
        f"📚 Año: *{year_label}*\n\n"
        f"🔔 Ahora vas a recibir los avisos de la Cartelera FCM "
        f"que correspondan a tu año.\n\n"
        f"Podés cambiar tu año cuando quieras con /start."
    )
    logger.info(f'Subscriber {username or chat_id} {action} -> {year}')


# ── Loop principal ────────────────────────────────────────────

def process_update(api: TelegramAPI, update: dict):
    """Despacha cada update para o handler correto."""

    # Callback query (clique em botao inline)
    if 'callback_query' in update:
        cq        = update['callback_query']
        cq_id     = cq['id']
        data      = cq.get('data', '')
        chat_id   = cq['message']['chat']['id']
        msg_id    = cq['message']['message_id']
        user      = cq.get('from', {})
        first_name = user.get('first_name', '')
        username  = user.get('username', '')

        if data.startswith('year:'):
            year = data.split(':', 1)[1]
            handle_year_callback(api, cq_id, chat_id, msg_id,
                                 first_name, username, year)
        return

    # Mensagem de texto
    msg = update.get('message', {})
    if not msg:
        return

    text      = msg.get('text', '').strip()
    chat_id   = msg['chat']['id']
    user      = msg.get('from', {})
    first_name = user.get('first_name', '')
    username  = user.get('username', '')

    if text.startswith('/start'):
        handle_start(api, chat_id, first_name, username)
    elif text.startswith('/meu_ano'):
        handle_meu_ano(api, chat_id)
    elif text.startswith('/cancelar'):
        handle_cancelar(api, chat_id)
    elif text.startswith('/ajuda') or text.startswith('/help'):
        api.send_message(chat_id, HELP_TEXT)
    else:
        # Mensagem desconhecida
        api.send_message(
            chat_id,
            "🤖 Usa /start para registrarte o /ajuda para ver los comandos."
        )


class Command(BaseCommand):
    help = (
        'Roda o bot Telegram do Conecta Radar. '
        'Processa /start, selecao de ano e cancelamento. '
        'Usar --once para processar updates pendentes e sair (Railway Cron).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--once', action='store_true',
            help='Processa updates pendentes e sai (nao faz polling continuo)'
        )

    def handle(self, *args, **options):
        token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        if not token:
            self.stderr.write(self.style.ERROR(
                'TELEGRAM_BOT_TOKEN nao configurado!'
            ))
            return

        api    = TelegramAPI(token)
        offset = 0
        once   = options['once']

        self.stdout.write(self.style.SUCCESS(
            '[BOT] Conecta Radar FCM iniciado'
            + (' (modo --once)' if once else ' (polling continuo)')
        ))

        while True:
            try:
                updates = api.get_updates(offset=offset)
                for update in updates:
                    try:
                        process_update(api, update)
                    except Exception as exc:
                        logger.error(f'Erro ao processar update {update.get("update_id")}: {exc}')
                    offset = update['update_id'] + 1

                if once:
                    self.stdout.write(f'[BOT] Processados {len(updates)} updates. Encerrando.')
                    break

                time.sleep(POLL_INTERVAL)

            except KeyboardInterrupt:
                self.stdout.write('\n[BOT] Encerrado pelo usuario.')
                break
            except Exception as exc:
                logger.error(f'Erro no loop do bot: {exc}')
                time.sleep(5)
