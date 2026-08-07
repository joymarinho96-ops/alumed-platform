from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task
from django.utils import timezone
from datetime import datetime, time
from .models import CarteleraItem, UserCalendarEvent
from .google_calendar_service import GoogleCalendarService

@receiver(post_save, sender=CarteleraItem)
def update_synced_google_events(sender, instance, created, **kwargs):
    if not created:
        # El evento fue editado, actualizar a todos los alumnos vinculados
        sync_records = UserCalendarEvent.objects.filter(cartelera_event=instance).select_related('user')
        if not sync_records.exists():
            return
            
        # Generar las fechas para el payload usando date_parsed
        if instance.date_parsed:
            tz = timezone.get_current_timezone()
            dt_start = datetime.combine(instance.date_parsed, time(8, 0)) # Default 8:00 AM
            dt_start_aware = timezone.make_aware(dt_start, tz)
            
            dt_end = dt_start_aware.replace(hour=9) # 1 hora de duración
            
            start_date_iso = dt_start_aware.isoformat()
            end_date_iso = dt_end.isoformat()
        else:
            return # Sin fecha no podemos agendar

        event_payload = {
            'title': instance.title,
            'description': getattr(instance, 'body_text', getattr(instance, 'subtitle', '')),
            'date_iso': start_date_iso,
            'end_date_iso': end_date_iso,
        }

        for record in sync_records:
            # Encolamos la actualización asíncrona para no bloquear el guardado del CarteleraItem
            async_task('core.tasks.async_sync_google_event', record.user.id, instance.id)


from allauth.socialaccount.signals import social_account_added

@receiver(social_account_added)
def on_social_account_added(request, sociallogin, **kwargs):
    """
    Captura los datos del perfil de Google (first_name, last_name, avatar) 
    y los guarda en nuestro modelo User cuando un alumno vincula su cuenta o se registra.
    """
    if sociallogin.account.provider == 'google':
        user = sociallogin.user
        extra_data = sociallogin.account.extra_data
        
        # Extraemos nombre y apellido
        if not user.first_name:
            user.first_name = extra_data.get('given_name', '')
        if not user.last_name:
            user.last_name = extra_data.get('family_name', '')
            
        # Guardamos el avatar en el UserProfile
        avatar_url = extra_data.get('picture', '')
        if avatar_url:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.avatar_url = avatar_url
            profile.save()
        
        user.save()


from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # In case the profile doesn't exist for some reason
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=CarteleraItem)
def broadcast_whatsapp_on_event_update(sender, instance, created, **kwargs):
    """Dispara el broadcast de WhatsApp si el evento es nuevo o importante."""
    # Podrías agregar lógica para no enviar si no hubo cambios importantes
    # Por ahora disparamos en creación o actualización
    async_task('core.tasks.async_broadcast_event_whatsapp', cartelera_event_id=instance.id)
