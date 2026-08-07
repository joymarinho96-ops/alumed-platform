import requests
import urllib.parse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', 'https://api.whatsapp.com/v1/')
        self.token = getattr(settings, 'WHATSAPP_TOKEN', '')
        self.phone_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
        self.support_number = getattr(settings, 'ALUMED_SUPPORT_WHATSAPP_NUMBER', '')
        
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        # Ejemplo para Meta Cloud API: https://graph.facebook.com/v17.0/{phone_id}/messages
        self.endpoint = f"{self.api_url.rstrip('/')}/{self.phone_id}/messages"

    def send_text_message(self, phone_number, text):
        """Envía un mensaje de texto plano."""
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": text}
        }
        return self._post_request(payload)

    def send_template_notification(self, phone_number, template_name, language_code="es_AR", components=None):
        """Envía una plantilla pre-aprobada por Meta."""
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": components or []
            }
        }
        return self._post_request(payload)

    def send_event_alert(self, phone_number, student_name, event_title, event_date, materia_nombre, wix_url=""):
        """Envía una alerta de evento formateada (fallback a texto si no hay plantilla)."""
        # Aquí podrías usar send_template_notification si tienes una plantilla aprobada.
        # Por ahora enviamos un mensaje de texto enriquecido.
        fecha_str = event_date if event_date else "Próximamente"
        materia_str = materia_nombre if materia_nombre else "ALUMED"
        
        text = f"¡Hola {student_name}! 👋\\n\\n"
        text += f"📌 *Novedad en {materia_str}*\\n"
        text += f"*{event_title}*\\n"
        text += f"🗓️ {fecha_str}\\n\\n"
        
        if wix_url:
            text += f"🚀 Accede al campus: {wix_url}\\n\\n"
            
        text += "Recuerda que puedes agendarlo en tu Google Calendar desde el Dashboard de ALUMED OS."
        
        return self.send_text_message(phone_number, text)

    def build_support_whatsapp_url(self, student_name, materia_context=None):
        """Construye un wa.me link para que el alumno contacte a soporte."""
        mensaje = f"Hola, soy {student_name}. Necesito ayuda"
        if materia_context:
            mensaje += f" con la materia {materia_context}."
        else:
            mensaje += "."
            
        encoded_msg = urllib.parse.quote(mensaje)
        # Limpiar el support_number para que no tenga '+' o espacios
        clean_number = self.support_number.replace('+', '').replace(' ', '')
        return f"https://wa.me/{clean_number}?text={encoded_msg}"

    def _post_request(self, payload):
        """Método interno para despachar la petición a la API."""
        try:
            response = requests.post(self.endpoint, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"WhatsApp API Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"WhatsApp API Response: {e.response.text}")
            raise e
