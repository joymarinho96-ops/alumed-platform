import logging
from datetime import datetime, timedelta
from allauth.socialaccount.models import SocialToken

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    def __init__(self, user):
        self.user = user
        self.service = self._get_calendar_service()

    def _get_calendar_service(self):
        try:
            token = SocialToken.objects.get(account__user=self.user, account__provider='google')
        except SocialToken.DoesNotExist:
            raise PermissionError("not_linked")
            
        credentials = Credentials(
            token=token.token,
            refresh_token=token.token_secret,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=token.app.client_id,
            client_secret=token.app.secret
        )
        return build('calendar', 'v3', credentials=credentials)

    def insert_or_update_event(self, event_data, google_event_id=None):
        """Si existe google_event_id, actualiza (patch/update); si no, lo crea (insert)."""
        body = {
            'summary': event_data['title'],
            'description': event_data.get('description', ''),
            'start': {'dateTime': event_data['date_iso'], 'timeZone': 'America/Argentina/Buenos_Aires'},
            'end': {'dateTime': event_data['end_date_iso'], 'timeZone': 'America/Argentina/Buenos_Aires'},
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 60},
                ],
            },
        }

        try:
            if google_event_id:
                # Actualizar evento existente
                event = self.service.events().patch(
                    calendarId='primary',
                    eventId=google_event_id,
                    body=body
                ).execute()
                logger.info(f"Evento {event_data['title']} actualizado en Google Calendar para {self.user.email}")
            else:
                # Crear nuevo evento
                event = self.service.events().insert(
                    calendarId='primary',
                    body=body
                ).execute()
                logger.info(f"Evento {event_data['title']} creado en Google Calendar para {self.user.email}")
            return event
        except HttpError as e:
            if e.resp.status in [401, 403]:
                raise PermissionError("not_linked")
            raise e

    def delete_event(self, google_event_id):
        """Elimina un evento del calendario de Google."""
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=google_event_id
            ).execute()
            logger.info(f"Evento {google_event_id} eliminado de Google Calendar para {self.user.email}")
        except HttpError as e:
            if e.resp.status == 404:
                pass  # El evento ya fue borrado directamente desde Google Calendar
            elif e.resp.status in [401, 403]:
                raise PermissionError("not_linked")
            else:
                raise e


    @staticmethod
    def sync_exams_to_user_calendar(social_token, exams_list):
        """
        Sincronización masiva de exámenes/parciales.
        """
        try:
            credentials = Credentials(
                token=social_token.token,
                refresh_token=social_token.token_secret,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=social_token.app.client_id,
                client_secret=social_token.app.secret
            )
            service = build('calendar', 'v3', credentials=credentials)
            
            from datetime import timedelta
            
            for exam in exams_list:
                # Assuming exam is a dict or model with date_iso, title, description
                date_iso = exam.date_iso if hasattr(exam, 'date_iso') else exam.get('date_iso')
                title = exam.title if hasattr(exam, 'title') else exam.get('title')
                desc = exam.description if hasattr(exam, 'description') else exam.get('description', '')
                
                if not date_iso:
                    continue
                    
                end_date_iso = date_iso + timedelta(hours=2) # 2 hour exam
                
                body = {
                    'summary': f"⚠️ EXAMEN: {title}",
                    'description': desc,
                    'start': {
                        'dateTime': date_iso.isoformat(),
                        'timeZone': 'America/Argentina/Buenos_Aires',
                    },
                    'end': {
                        'dateTime': end_date_iso.isoformat(),
                        'timeZone': 'America/Argentina/Buenos_Aires',
                    },
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'popup', 'minutes': 24 * 60}, # 1 día antes
                            {'method': 'popup', 'minutes': 2 * 60},  # 2 horas antes
                        ],
                    }
                }
                
                # Check if event already exists (we could use an extended property or UserCalendarEvent model here)
                # For simplicity in this bulk sync, we just insert.
                # A more robust solution would check UserCalendarEvent to update instead of insert.
                service.events().insert(calendarId='primary', body=body).execute()
                
            return True, "Sincronización masiva exitosa"
        except HttpError as error:
            logger.error(f"Error HTTP sincronizando masivamente con Google Calendar: {error}")
            return False, str(error)
        except Exception as e:
            logger.error(f"Error inesperado en sincronización masiva: {e}")
            return False, str(e)
