from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
import re as _re

# ─────────────────────────────────────────────────────────────────────────────
# Profile
# ─────────────────────────────────────────────────────────────────────────────

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    wix_member_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    avatar = models.CharField(max_length=50, blank=True, default='av01')
    last_announcement_view_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Perfil de {self.user.username}'


# ─────────────────────────────────────────────────────────────────────────────
# ChatMessage
# ─────────────────────────────────────────────────────────────────────────────

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"De {self.sender} para {self.receiver} em {self.timestamp}"

    @staticmethod
    def cleanup_old_messages():
        """Remove mensagens com mais de 10 dias"""
        cutoff_date = timezone.now() - timedelta(days=10)
        ChatMessage.objects.filter(timestamp__lt=cutoff_date).delete()


# ─────────────────────────────────────────────────────────────────────────────
# Controle de Acesso por Produto (independente de Enrollment)
# ─────────────────────────────────────────────────────────────────────────────

class AccessProduct(models.Model):
    """
    Representa um produto de acesso do ecossistema ALUMED OS.
    Produtos: CONECTA_FCM, ALUMED_CAMPUS, CLUB_ALUMED.
    Completamente independente de Course/Enrollment.
    """
    PRODUCT_CHOICES = [
        ('CONECTA_FCM',   'Conecta FCM'),
        ('ALUMED_CAMPUS', 'ALUMED Campus (Premium)'),
        ('CLUB_ALUMED',   'Club ALUMED'),
    ]
    slug        = models.CharField(max_length=50, unique=True, choices=PRODUCT_CHOICES,
                                   verbose_name='Identificador do Produto')
    name        = models.CharField(max_length=100, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descricao')
    is_active   = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Produto de Acesso'
        verbose_name_plural = 'Produtos de Acesso'

    def __str__(self):
        return self.name


class UserAccess(models.Model):
    """
    Concede acesso de um usuario a um AccessProduct.
    Pode ter expiracao. Criado manualmente ou via Wix webhook.
    Independente de Enrollment de cursos.
    """
    SOURCE_CHOICES = [
        ('wix',          'Wix Webhook'),
        ('manual',       'Manual Staff'),
        ('transferencia','Transferencia Bancaria'),
        ('cortesia',     'Cortesia'),
    ]
    user       = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='access_grants',
                                   verbose_name='Usuario')
    product    = models.ForeignKey(AccessProduct, on_delete=models.CASCADE,
                                   related_name='grants',
                                   verbose_name='Produto')
    is_active  = models.BooleanField(default=True, verbose_name='Ativo')
    granted_at = models.DateTimeField(auto_now_add=True, verbose_name='Concedido em')
    expires_at = models.DateTimeField(null=True, blank=True,
                                      verbose_name='Expira em',
                                      help_text='Deixar em branco = sem expiracao')
    source     = models.CharField(max_length=20, choices=SOURCE_CHOICES,
                                  default='manual', verbose_name='Origem')
    notes      = models.TextField(blank=True, verbose_name='Observacoes')

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = 'Acesso de Usuario'
        verbose_name_plural = 'Acessos de Usuarios'
        ordering = ['-granted_at']

    def is_valid(self):
        """Retorna True se o acesso esta ativo e nao expirado."""
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def __str__(self):
        exp = self.expires_at.strftime('%d/%m/%Y') if self.expires_at else 'sem expiracao'
        return f"{self.user.username} -> {self.product.slug} (expira: {exp})"


# ─────────────────────────────────────────────────────────────────────────────
# Signals
# ─────────────────────────────────────────────────────────────────────────────

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)


# ─────────────────────────────────────────────────────────────────────────────
# Conecta FCM — Preferencias, Suscripciones y Auditoría de Consentimiento
#
# Independiente de Enrollment y cursos ALUMED.
# La BD es la ÚNICA fuente de verdad.
# El backend valida slugs contra accounts.conecta_catalog.
# ─────────────────────────────────────────────────────────────────────────────

def _normalize_e164(raw: str) -> str:
    """Convierte número argentino a formato E.164 (+54...)."""
    digits = _re.sub(r'\D', '', raw)
    if not digits:
        return ''
    if digits.startswith('54') and len(digits) >= 12:
        return '+' + digits
    if digits.startswith('0'):
        digits = digits[1:]
    return '+54' + digits


class ConectaPreference(models.Model):
    """
    Preferencias de alertas del alumno para Conecta FCM.
    Una fila por usuario. Independiente de cursos comprados.
    La BD es la ÚNICA fuente de verdad; localStorage es solo caché.

    Reglas de negocio:
    - whatsapp_active=True requiere whatsapp_number válido (E.164).
    - email_active=True requiere alert_email válido.
    - consent_granted=True requiere al menos un canal activo.
    - Cambios de consentimiento generan ConectaConsentEvent.
    """
    CONSENT_VERSION = 'v1'

    user             = models.OneToOneField(
                           User, on_delete=models.CASCADE,
                           related_name='conecta_preference',
                           verbose_name='Usuario')
    # ── Canales ──────────────────────────────────────────────────────────────
    whatsapp_number  = models.CharField(
                           max_length=20, blank=True,
                           verbose_name='WhatsApp del alumno',
                           help_text='Normalizado a E.164: +5492211234567')
    alert_email      = models.EmailField(
                           blank=True,
                           verbose_name='Email del alumno')
    whatsapp_active  = models.BooleanField(default=False,
                           verbose_name='Alertas WhatsApp activas')
    email_active     = models.BooleanField(default=False,
                           verbose_name='Alertas Email activas')
    calendar_active  = models.BooleanField(default=False,
                           verbose_name='Sincronización Google Calendar')
    # ── Consentimiento actual ─────────────────────────────────────────────────
    consent_granted  = models.BooleanField(default=False,
                           verbose_name='Consentimiento otorgado')
    consent_at       = models.DateTimeField(null=True, blank=True,
                           verbose_name='Fecha del último consentimiento')
    consent_version  = models.CharField(max_length=10,
                           default=CONSENT_VERSION,
                           verbose_name='Versión del consentimiento')
    consent_channels = models.CharField(max_length=100, blank=True,
                           verbose_name='Canales autorizados',
                           help_text='whatsapp,email,calendar')
    is_active        = models.BooleanField(default=True,
                           verbose_name='Cuenta activa')
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Preferencia Conecta FCM'
        verbose_name_plural = 'Preferencias Conecta FCM'
        ordering            = ['-updated_at']

    def __str__(self):
        ch = [c for c, a in [('WA', self.whatsapp_active),
                               ('Email', self.email_active),
                               ('GCal', self.calendar_active)] if a]
        return f"{self.user.username} [{', '.join(ch) or 'sin alertas'}]"

    def revoke_consent(self, ip=None, ua=''):
        """Revoca consentimiento y registra evento de auditoría."""
        if not self.consent_granted:
            return
        self.consent_granted  = False
        self.whatsapp_active  = False
        self.email_active     = False
        self.calendar_active  = False
        self.consent_channels = ''
        self.save(update_fields=[
            'consent_granted', 'whatsapp_active', 'email_active',
            'calendar_active', 'consent_channels', 'updated_at',
        ])
        ConectaConsentEvent.objects.create(
            user=self.user,
            action='revoked',
            version=self.consent_version,
            channels='',
            whatsapp=self.whatsapp_number,
            email=self.alert_email,
            ip_address=ip,
            user_agent=ua or '',
        )


class ConectaSubscription(models.Model):
    """
    Una fila = una suscripción (activa o desactivada).
    No se borra — enabled=False preserva historial.
    label y year NO se almacenan aquí; se resuelven del catálogo.
    """
    TYPE_CHOICES = [
        ('institutional', 'Información Institucional'),
        ('subject',       'Materia de Medicina'),
    ]
    user       = models.ForeignKey(User, on_delete=models.CASCADE,
                     related_name='conecta_subscriptions',
                     verbose_name='Usuario')
    type       = models.CharField(max_length=15, choices=TYPE_CHOICES,
                     verbose_name='Tipo')
    key        = models.CharField(max_length=120,
                     verbose_name='Slug canónico')
    enabled    = models.BooleanField(default=True, verbose_name='Activa')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'type', 'key'],
                name='unique_conecta_subscription'
            )
        ]
        indexes = [
            models.Index(
                fields=['user', 'type', 'enabled'],
                name='idx_conecta_sub_user_type_en'
            )
        ]
        verbose_name        = 'Suscripción Conecta FCM'
        verbose_name_plural = 'Suscripciones Conecta FCM'

    def __str__(self):
        state = '✓' if self.enabled else '✗'
        return f"{state} {self.user.username} → [{self.type}] {self.key}"


class ConectaConsentEvent(models.Model):
    """
    Registro INMUTABLE de cada concesión o revocación de consentimiento.
    Nunca se edita. Nunca se borra. Solo auto_now_add.
    """
    ACTION_CHOICES = [('granted', 'Concedido'), ('revoked', 'Revocado')]

    user       = models.ForeignKey(User, on_delete=models.CASCADE,
                     related_name='consent_events',
                     verbose_name='Usuario')
    action     = models.CharField(max_length=10, choices=ACTION_CHOICES,
                     verbose_name='Acción')
    version    = models.CharField(max_length=10,
                     verbose_name='Versión del consentimiento')
    channels   = models.CharField(max_length=100, blank=True,
                     verbose_name='Canales autorizados')
    whatsapp   = models.CharField(max_length=20, blank=True,
                     verbose_name='WhatsApp registrado')
    email      = models.EmailField(blank=True,
                     verbose_name='Email registrado')
    ip_address = models.GenericIPAddressField(null=True, blank=True,
                     verbose_name='Dirección IP')
    user_agent = models.CharField(max_length=300, blank=True,
                     verbose_name='User-Agent')
    created_at = models.DateTimeField(auto_now_add=True,
                     verbose_name='Fecha/hora')

    class Meta:
        ordering            = ['-created_at']
        verbose_name        = 'Evento de Consentimiento'
        verbose_name_plural = 'Eventos de Consentimiento'

    def __str__(self):
        return f"{self.user.username} — {self.action} ({self.created_at:%d/%m/%Y %H:%M})"


class AcademicEvent(models.Model):
    """
    Evento acadêmico pessoal do aluno.
    Privado: apenas o dono pode ver/editar/deletar.
    """
    TYPE_CHOICES = [
        ('final',       'Final'),
        ('parcial',     'Parcial'),
        ('tp',          'TP'),
        ('inscripcion', 'Inscripción'),
        ('clase',       'Clase especial'),
        ('simulacro',   'Simulacro'),
        ('meta',        'Meta personal'),
        ('otro',        'Otro'),
    ]
    STATUS_CHOICES = [
        ('pending',  'Inscripción pendiente'),
        ('open',     'Inscripción abierta'),
        ('upcoming', 'Próximo'),
        ('done',     'Realizado'),
    ]
    COLOR_MAP = {
        'final':       '#ef4444',
        'parcial':     '#f59e0b',
        'tp':          '#8b5cf6',
        'inscripcion': '#06b6d4',
        'clase':       '#3b82f6',
        'simulacro':   '#f97316',
        'meta':        '#10b981',
        'otro':        '#94a3b8',
    }

    user                        = models.ForeignKey(
                                      User, on_delete=models.CASCADE,
                                      related_name='academic_events')
    title                       = models.CharField(max_length=200, verbose_name='Título')
    subject                     = models.CharField(max_length=100, blank=True, verbose_name='Materia')
    event_type                  = models.CharField(max_length=15, choices=TYPE_CHOICES, verbose_name='Tipo')
    start_datetime              = models.DateTimeField(verbose_name='Fecha y hora')
    end_datetime                = models.DateTimeField(null=True, blank=True, verbose_name='Fin')
    location                    = models.CharField(max_length=200, blank=True, verbose_name='Lugar/Aula')
    notes                       = models.TextField(blank=True, verbose_name='Observaciones')
    registration_open_at        = models.DateTimeField(null=True, blank=True, verbose_name='Apertura de inscripción')
    registration_deadline       = models.DateTimeField(null=True, blank=True, verbose_name='Cierre de inscripción')
    registration_confirmed      = models.BooleanField(default=False, verbose_name='Inscripción confirmada')
    inscription_alert_dismissed = models.BooleanField(default=False, verbose_name='Alerta descartada')
    google_event_id             = models.CharField(max_length=300, blank=True, verbose_name='ID Google Calendar')
    google_calendar_id          = models.CharField(max_length=300, blank=True, verbose_name='Calendar ID')
    google_synced_at            = models.DateTimeField(null=True, blank=True, verbose_name='Último sync Google')
    status                      = models.CharField(max_length=15, choices=STATUS_CHOICES,
                                      default='upcoming', verbose_name='Estado')
    created_at                  = models.DateTimeField(auto_now_add=True)
    updated_at                  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['start_datetime']
        verbose_name        = 'Evento Académico'
        verbose_name_plural = 'Eventos Académicos'
        indexes             = [models.Index(fields=['user', 'start_datetime'],
                                   name='idx_academic_event_user_dt')]

    def __str__(self):
        return f"{self.title} ({self.user.username}) — {self.start_datetime:%d/%m/%Y}"

    @property
    def days_until(self):
        from django.utils import timezone
        delta = self.start_datetime.date() - timezone.now().date()
        return delta.days

    @property
    def color(self):
        return self.COLOR_MAP.get(self.event_type, '#94a3b8')

    @property
    def needs_inscription_alert(self):
        """True se faltam ≤10 dias e inscrição não confirmada."""
        if self.event_type not in ('final', 'parcial', 'inscripcion', 'simulacro'):
            return False
        if self.registration_confirmed or self.inscription_alert_dismissed:
            return False
        return 0 <= self.days_until <= 10

    def to_dict(self):
        from django.utils import timezone
        return {
            'id':                    self.pk,
            'title':                 self.title,
            'subject':               self.subject,
            'event_type':            self.event_type,
            'event_type_display':    self.get_event_type_display(),
            'start_datetime':        self.start_datetime.isoformat(),
            'end_datetime':          self.end_datetime.isoformat() if self.end_datetime else None,
            'location':              self.location,
            'notes':                 self.notes,
            'registration_open_at':  self.registration_open_at.isoformat() if self.registration_open_at else None,
            'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            'registration_confirmed':self.registration_confirmed,
            'inscription_alert_dismissed': self.inscription_alert_dismissed,
            'google_event_id':       self.google_event_id,
            'google_synced':         bool(self.google_event_id),
            'status':                self.status,
            'status_display':        self.get_status_display(),
            'days_until':            self.days_until,
            'color':                 self.color,
            'needs_inscription_alert': self.needs_inscription_alert,
            'created_at':            self.created_at.isoformat(),
        }
