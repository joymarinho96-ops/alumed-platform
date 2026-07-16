"""
View Django para receber updates do Telegram via Webhook.

Fluxo:
  Telegram POST /telegram/webhook/ -> Django processa -> responde

Vantagens vs polling:
  - Sem processo separado
  - Funciona no mesmo servidor (alumed-platform)
  - Mais eficiente e confiavel
  - Zero custo extra
"""
import hashlib
import hmac
import json
import logging
import os

import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from accounts.models import TelegramSubscriber

logger = logging.getLogger(__name__)

# ── Constantes ────────────────────────────────────────────────
YEAR_BUTTONS = [
    [
        {'text': '🎓 Ingreso',        'callback_data': 'year:ingreso'},
        {'text': '1° Año',             'callback_data': 'year:1'},
    ],
    [
        {'text': '2° Año',             'callback_data': 'year:2'},
        {'text': '3° Año',             'callback_data': 'year:3'},
    ],
    [
        {'text': '4° Año',             'callback_data': 'year:4'},
        {'text': '5° Año',             'callback_data': 'year:5'},
    ],
    [
        {'text': '6° Año',             'callback_data': 'year:6'},
        {'text': '🏥 Internado',       'callback_data': 'year:internado'},
    ],
    [
        {'text': '📢 Todos los años',  'callback_data': 'year:todos'},
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
    "/ajuda — Ver esta ayuda"
)


def _tg_api(method: str, **kwargs) -> dict:
    """Chama a API do Telegram Bot."""
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    if not token:
        return {}
    try:
        r = requests.post(
            f'https://api.telegram.org/bot{token}/{method}',
            json=kwargs, timeout=10
        )
        return r.json()
    except Exception as exc:
        logger.error(f'Telegram API error [{method}]: {exc}')
        return {}


def _send(chat_id: int, text: str, reply_markup: dict = None):
    kwargs = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup:
        kwargs['reply_markup'] = reply_markup
    return _tg_api('sendMessage', **kwargs)


def _edit(chat_id: int, message_id: int, text: str):
    return _tg_api('editMessageText', chat_id=chat_id,
                   message_id=message_id, text=text, parse_mode='Markdown')


def _answer_callback(callback_id: str, text: str = ''):
    return _tg_api('answerCallbackQuery', callback_query_id=callback_id, text=text)


# ── Handlers ──────────────────────────────────────────────────

def _handle_start(chat_id, first_name, username):
    _send(chat_id, WELCOME_TEXT, reply_markup={'inline_keyboard': YEAR_BUTTONS})


def _handle_meu_ano(chat_id):
    try:
        sub = TelegramSubscriber.objects.get(telegram_chat_id=chat_id)
        year_label = YEAR_DISPLAY.get(sub.year, sub.year)
        _send(chat_id, f"📚 Tu año actual: *{year_label}*\n\nPara cambiar, usa /start")
    except TelegramSubscriber.DoesNotExist:
        _send(chat_id, "❌ No estás registrado. Usa /start para registrarte.")


def _handle_cancelar(chat_id):
    updated = TelegramSubscriber.objects.filter(
        telegram_chat_id=chat_id
    ).update(is_active=False)
    if updated:
        _send(chat_id,
              "🔕 *Notificaciones desactivadas.*\n\n"
              "Podés volver a activarlas cuando quieras con /start.")
    else:
        _send(chat_id, "❌ No estabas registrado. Usa /start.")


def _handle_year_callback(cq_id, chat_id, message_id, first_name, username, year):
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
    _answer_callback(cq_id, f'✅ {year_label}')
    _edit(chat_id, message_id,
          f"✅ *¡{action.capitalize()}!*\n\n"
          f"📚 Año: *{year_label}*\n\n"
          f"🔔 Ahora vas a recibir los avisos de la Cartelera FCM "
          f"que correspondan a tu año.\n\n"
          f"Podés cambiar tu año cuando quieras con /start.")


# ── Webhook View ──────────────────────────────────────────────

@csrf_exempt
@require_POST
def telegram_webhook(request):
    """
    Endpoint que recebe updates do Telegram via Webhook.
    URL: /telegram/webhook/
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    try:
        _process_update(data)
    except Exception as exc:
        logger.error(f'Erro ao processar update Telegram: {exc}')

    # Telegram exige HTTP 200 sempre
    return HttpResponse('ok', status=200)


def _process_update(update: dict):
    """Despacha update para o handler correto."""

    # Callback query (botao inline)
    if 'callback_query' in update:
        cq         = update['callback_query']
        cq_id      = cq['id']
        data       = cq.get('data', '')
        chat_id    = cq['message']['chat']['id']
        msg_id     = cq['message']['message_id']
        user       = cq.get('from', {})
        first_name = user.get('first_name', '')
        username   = user.get('username', '')

        if data.startswith('year:'):
            year = data.split(':', 1)[1]
            _handle_year_callback(cq_id, chat_id, msg_id, first_name, username, year)
        return

    # Mensagem de texto
    msg = update.get('message', {})
    if not msg:
        return

    text       = msg.get('text', '').strip()
    chat_id    = msg['chat']['id']
    user       = msg.get('from', {})
    first_name = user.get('first_name', '')
    username   = user.get('username', '')

    if text.startswith('/start'):
        _handle_start(chat_id, first_name, username)
    elif text.startswith('/meu_ano'):
        _handle_meu_ano(chat_id)
    elif text.startswith('/cancelar'):
        _handle_cancelar(chat_id)
    elif text.startswith('/ajuda') or text.startswith('/help'):
        _send(chat_id, HELP_TEXT)
    else:
        _send(chat_id, "🤖 Usa /start para registrarte o /ajuda para ver los comandos.")


# ── View para registrar o webhook ─────────────────────────────

def setup_webhook(request):
    """
    GET /telegram/setup-webhook/
    Registra o webhook no Telegram. Chamar UMA VEZ apos o deploy.
    """
    token   = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    domain  = request.get_host()
    webhook = f'https://{domain}/telegram/webhook/'

    result = _tg_api('setWebhook', url=webhook,
                     allowed_updates=['message', 'callback_query'])

    return JsonResponse({
        'webhook_url': webhook,
        'telegram_response': result,
    })
