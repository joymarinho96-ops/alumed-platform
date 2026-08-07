import logging
from datetime import datetime, timedelta, time
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import CarteleraItem, UserCalendarEvent
from core.google_calendar_service import GoogleCalendarService

logger = logging.getLogger(__name__)
User = get_user_model()

def async_sync_google_event(user_id, item_id):
    """
    Tarea asíncrona para sincronizar un CarteleraItem con Google Calendar.
    """
    try:
        user = User.objects.get(id=user_id)
        cartelera_item = CarteleraItem.objects.get(id=item_id)
    except (User.DoesNotExist, CarteleraItem.DoesNotExist):
        logger.error(f"Error: Usuario {user_id} o Item {item_id} no encontrado.")
        return "Not found"

    # Preparar fechas
    if cartelera_item.date_parsed:
        tz = timezone.get_current_timezone()
        dt_start = datetime.combine(cartelera_item.date_parsed, time(8, 0))
        dt_start_aware = timezone.make_aware(dt_start, tz)
        dt_end = dt_start_aware.replace(hour=9)
        start_date_iso = dt_start_aware.isoformat()
        end_date_iso = dt_end.isoformat()
    else:
        logger.warning(f"CarteleraItem {item_id} no tiene fecha parseada. Omitiendo.")
        return "No date"

    event_payload = {
        'title': cartelera_item.title,
        'description': getattr(cartelera_item, 'body_text', getattr(cartelera_item, 'subtitle', '')),
        'date_iso': start_date_iso,
        'end_date_iso': end_date_iso,
    }

    # Buscar si ya existe sincronizado
    user_event = UserCalendarEvent.objects.filter(user=user, cartelera_event=cartelera_item).first()
    google_event_id = user_event.google_event_id if user_event else None

    try:
        service = GoogleCalendarService(user)
        event = service.insert_or_update_event(event_payload, google_event_id)

        if not user_event:
            UserCalendarEvent.objects.create(
                user=user,
                cartelera_event=cartelera_item,
                google_event_id=event.get('id')
            )
        return "Success"
    except PermissionError:
        logger.warning(f"Usuario {user.username} revocó permisos o el token falló.")
        return "Permission Error"
    except Exception as e:
        logger.error(f"Error sincronizando evento para {user.username}: {e}")
        return "Error"

def async_delete_google_event(user_id, google_event_id, cartelera_event_id):
    """
    Tarea asíncrona para eliminar un evento de Google Calendar.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return "User not found"

    try:
        service = GoogleCalendarService(user)
        service.delete_event(google_event_id)
        logger.info(f"Evento {google_event_id} eliminado exitosamente para {user.username}")
    except PermissionError:
        logger.warning(f"Usuario {user.username} revocó permisos o el token falló al eliminar.")
    except Exception as e:
        logger.error(f"Error eliminando evento {google_event_id} para {user.username}: {e}")

    # Borrar el registro de todas formas
    UserCalendarEvent.objects.filter(user_id=user_id, cartelera_event_id=cartelera_event_id).delete()
    return "Deleted"


from .models import WhatsAppMessageLog, CarteleraItem, UserProfile
from .whatsapp_service import WhatsAppService
from django.contrib.auth.models import User
from django_q.tasks import async_task

def async_send_whatsapp_message(user_id, phone_number, message_type, text_content):
    """Tarea Q2 para enviar mensajes de WhatsApp e iterar Logs."""
    user = User.objects.filter(id=user_id).first() if user_id else None
    
    # Crear log en estado queued (si quieres registrarlo antes, pasalo por param, 
    # pero aquí lo creamos justo al intentar enviar)
    log = WhatsAppMessageLog.objects.create(
        user=user,
        phone_number=phone_number,
        message_type=message_type,
        message_body=text_content,
        status='queued'
    )
    
    try:
        service = WhatsAppService()
        response = service.send_text_message(phone_number, text_content)
        
        log.status = 'sent'
        if 'messages' in response and len(response['messages']) > 0:
            log.api_response_id = response['messages'][0].get('id', '')
        log.save()
    except Exception as e:
        log.status = 'failed'
        log.error_message = str(e)
        log.save()
        raise e

def async_broadcast_event_whatsapp(cartelera_event_id):
    """Tarea Q2 para buscar alumnos inscriptos y encolar avisos individuales."""
    try:
        evento = CarteleraItem.objects.select_related('materia').get(id=cartelera_event_id)
        if not evento.materia:
            return # No broadcast si no hay materia asociada
            
        materia_nombre = evento.materia.nombre
        
        # Buscar todos los alumnos inscriptos que tengan notificaciones activadas
        perfiles = UserProfile.objects.filter(
            materias=evento.materia,
            whatsapp_notifications_enabled=True,
            phone_number__isnull=False
        ).exclude(phone_number='')
        
        service = WhatsAppService()
        
        for perfil in perfiles:
            # Reutilizamos la lógica del servicio para construir el texto (sin enviarlo directo)
            # Para esto, podemos instanciar el servicio y generar el texto, luego encolar.
            # O simplemente construir el texto aquí.
            fecha_str = evento.date_parsed.strftime("%d/%m/%Y") if evento.date_parsed else "Próximamente"
            
            text = f"¡Hola {perfil.user.first_name}! 👋\n\n"
            text += f"📌 *Novedad en {materia_nombre}*\n"
            text += f"*{evento.title}*\n"
            text += f"🗓️ {fecha_str}\n\n"
            
            # Buscar si el perfil tiene un curso Wix para esta materia
            curso = perfil.materias.first().cursos_wix.first() if perfil.materias.first() else None
            if curso and curso.wix_course_url:
                text += f"🚀 Accede al campus: {curso.wix_course_url}\n\n"
                
            text += "Recuerda que puedes agendarlo en tu Google Calendar desde el Dashboard de ALUMED OS."
            
            # Encolar tarea de envío individual (así si uno falla, no arrastra al resto)
            async_task(
                'core.tasks.async_send_whatsapp_message',
                user_id=perfil.user.id,
                phone_number=perfil.phone_number,
                message_type='event_alert',
                text_content=text
            )
            
    except CarteleraItem.DoesNotExist:
        pass


def notify_upcoming_exams():
    """
    Cron Job: Se ejecuta diariamente a las 09:00 AM.
    Busca exámenes programados para las próximas 24 horas y dispara alertas de WhatsApp.
    """
    logger.info("Iniciando notify_upcoming_exams cron job...")
    ahora = timezone.now()
    manana = ahora + timedelta(days=1)
    
    # Buscar CarteleraItems que tengan fecha para mañana (simplificado: comparando la fecha, o un rango de 24 hs)
    # Suponiendo que date_parsed es DateField
    examenes_manana = CarteleraItem.objects.filter(
        date_parsed__year=manana.year,
        date_parsed__month=manana.month,
        date_parsed__day=manana.day,
        materia__isnull=False
    )
    
    link_biblioteca = "https://conecta-fcm.com/biblioteca/" # O puedes usar la url configurada en tu app
    
    for examen in examenes_manana:
        # Buscar alumnos inscriptos
        perfiles = UserProfile.objects.filter(
            materias=examen.materia,
            whatsapp_notifications_enabled=True,
            phone_number__isnull=False
        ).exclude(phone_number='')
        
        for perfil in perfiles:
            # Plantilla Profe Joy
            text = f"👋 ¡Hola {perfil.user.first_name}! Profe Joy por acá de Instituto Alumed 🩺
"
            text += f"📌 Recordatorio: Mañana rendís {examen.materia.nombre} ({examen.title}).
"
            text += f"📚 No olvides repasar las guías y resúmenes en la Biblioteca Virtual de Conecta FCM: {link_biblioteca}
"
            text += "¡Mucho éxito hoy! 💪"
            
            async_task(
                'core.tasks.async_send_whatsapp_message',
                user_id=perfil.user.id,
                phone_number=perfil.phone_number,
                message_type='exam_reminder',
                text_content=text
            )


def notify_secretaria_and_materias_updates(item_id):
    """
    Filtra los perfiles de los alumnos donde receive_whatsapp_notifications=True
    Y cuyo current_year coincida exactamente con el año de destino del aviso.
    """
    try:
        item = CarteleraItem.objects.get(id=item_id)
    except CarteleraItem.DoesNotExist:
        logger.error(f"CarteleraItem {item_id} no encontrado para notificar.")
        return

    # Si no tiene target_year, podríamos decidir si se manda a todos o no.
    if not item.target_year:
        logger.warning(f"CarteleraItem {item_id} no tiene target_year, no se envía notificación masiva para evitar spam.")
        return

    perfiles = UserProfile.objects.filter(
        whatsapp_notifications_enabled=True,
        phone_number__isnull=False,
        current_year=item.target_year
    ).exclude(phone_number='')

    link_biblioteca = "https://www.alumedestudiantes.com/biblioteca/"

    for perfil in perfiles:
        # Plantilla Profe Joy para aviso general
        text = f"👋 ¡Hola {perfil.user.first_name}! Profe Joy por acá de Instituto Alumed 🩺
"
        text += f"📢 Tenemos un aviso importante de Secretaría para tu año académico ({item.target_year}):

"
        text += f"📌 *{item.title}*
"
        
        # Agregar descripción o subtítulo si existe
        if getattr(item, 'subtitle', None):
            text += f"_{item.subtitle}_

"
            
        text += f"Recuerda que siempre puedes acceder a la plataforma para más detalles: {link_biblioteca}
"
        text += "¡Que tengas un excelente día! ✨"
        
        async_task(
            'core.tasks.async_send_whatsapp_message',
            user_id=perfil.user.id,
            phone_number=perfil.phone_number,
            message_type='event_alert',
            text_content=text
        )
