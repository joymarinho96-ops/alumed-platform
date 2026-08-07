from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from alumed.url_utils import normalize_gcs_url

def _url_ativa(url):
    return normalize_gcs_url(url)


class Announcement(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    content = models.TextField(verbose_name="Conteúdo")
    image = models.ImageField(upload_to='announcements/', verbose_name="Imagen", null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Aviso"
        verbose_name_plural = "Avisos"
        ordering = ['-created_at']

class Popup(models.Model):
    title = models.CharField(max_length=100, verbose_name="Título (Opcional)", blank=True)
    message = models.CharField(max_length=255, verbose_name="Mensaje")
    image = models.ImageField(upload_to='popups/', verbose_name="Imagen (Opcional)", null=True, blank=True)
    link_text = models.CharField(max_length=50, verbose_name="Texto del Botón", default="Ver más")
    link_url = models.CharField(max_length=255, verbose_name="URL del Botón", blank=True)
    is_active = models.BooleanField(default=False, verbose_name="Activo")

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = "Popup Promocional"
        verbose_name_plural = "Popups Promocionales"

class Event(models.Model):
    EVENT_CHOICES = [
        ('exam', 'Examen'),
        ('notice', 'Aviso'),
    ]

    title = models.CharField(max_length=200, verbose_name="Título")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin", help_text="Si el evento dura solo un día, esta fecha debe ser igual a la de inicio.")
    event_type = models.CharField(max_length=10, choices=EVENT_CHOICES, verbose_name="Tipo de Evento")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Evento del Calendario"
        verbose_name_plural = "Eventos del Calendario"
        ordering = ['start_date']

class LibraryResource(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción", blank=True)
    # Adicionado default='' para evitar problemas de migração
    download_url = models.URLField(verbose_name="Link de Descarga (Google Cloud)", help_text="Pegue aquí el enlace del archivo", default='')
    cover_image = models.ImageField(upload_to='library/covers/', verbose_name="Imagen de Portada", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    @property
    def download_url_ativa(self):
        return _url_ativa(self.download_url)

    @property
    def url_ativa(self):
        return self.download_url_ativa

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Recurso de Biblioteca"
        verbose_name_plural = "Biblioteca Virtual"
        ordering = ['-created_at']


class DigitalBook(models.Model):
    SUBJECT_CHOICES = [
        ('histo', 'Histología'),
        ('embrio', 'Embriología'),
        ('bio', 'Biología'),
        ('anato', 'Anatomía'),
        ('transcripcion', 'Factores de Transcripción'),
        ('simulacros', 'Simulacros y Exámenes'),
        ('quimica', 'Química Biológica / Bioquímica'),
        ('fisio', 'Fisiología y Biofísica'),
        ('micro', 'Microbiología y Parasitología'),
        ('pato', 'Patología'),
        ('farma', 'Farmacología'),
        ('semiologia', 'Semiología y Medicina Interna'),
        ('pediatria', 'Pediatría'),
        ('ginecologia', 'Ginecología y Obstetricia'),
        ('cirugia', 'Cirugía'),
        ('clinica', 'Clínica Médica'),
        ('otras', 'Otras Asignaturas'),
    ]

    STATUS_CHOICES = [
        ('confirmado', 'Confirmado'),
        ('posible', 'Posible'),
        ('duplicado', 'Duplicado'),
        ('revisar', 'Revisar'),
    ]

    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción", blank=True)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, verbose_name="Materia/Categoría")
    category = models.CharField(max_length=50, verbose_name="Tema/Subcategoría", default="Apunte Completo")
    year = models.CharField(max_length=20, verbose_name="Año", default="1º Año")
    platform = models.CharField(max_length=50, verbose_name="Plataforma", default="Studocu")
    pdf_url = models.URLField(max_length=1500, verbose_name="Enlace de la Fuente Original", blank=True)
    author = models.CharField(max_length=100, verbose_name="Autor", blank=True)
    page_count = models.IntegerField(default=1, verbose_name="Cantidad de Páginas")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmado', verbose_name="Estado")
    tags = models.CharField(max_length=255, verbose_name="Etiquetas", help_text="Separadas por coma", blank=True)
    
    cover_image = models.ImageField(upload_to='library/covers/', verbose_name="Imagen de Portada", null=True, blank=True)
    pdf_file = models.FileField(upload_to='library/pdfs/', verbose_name="Archivo PDF Local", null=True, blank=True)
    
    extracted_text = models.TextField(verbose_name="Texto Extraído", blank=True)
    ai_summary = models.TextField(verbose_name="Resumen de IA", blank=True)
    ai_flashcards = models.JSONField(verbose_name="Flashcards de IA", null=True, blank=True)
    ai_quiz = models.JSONField(verbose_name="Quiz de IA", null=True, blank=True)
    joy_method = models.JSONField(verbose_name="Método Joy", null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    def __str__(self):
        return f"{self.title} ({self.get_subject_display()}) - {self.platform}"

    class Meta:
        verbose_name = "Libro Digital"
        verbose_name_plural = "Libros Digitales"
        ordering = ['subject', '-created_at']



class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    description = models.TextField(verbose_name="Descripción")
    image = models.ImageField(upload_to='store/products/', verbose_name="Imagen del Producto")
    whatsapp_link = models.URLField(verbose_name="Enlace de WhatsApp", blank=True, null=True, help_text="Deje en blanco para generar automáticamente.")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Tienda Alumed"
        ordering = ['-created_at']

class Testimonial(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre del Estudiante")
    role = models.CharField(max_length=100, verbose_name="Rol/Curso", default="Estudiante")
    text = models.TextField(verbose_name="Testimonio")
    photo = models.ImageField(upload_to='testimonials/photos/', verbose_name="Foto de Perfil", null=True, blank=True)
    initial = models.CharField(max_length=2, verbose_name="Inicial (si no hay foto)", blank=True)
    rating = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Calificación (1-5)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Testimonio"
        verbose_name_plural = "Testimonios"
        ordering = ['-created_at']

class TestimonialVideo(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título del Video")
    video_url = models.URLField(verbose_name="URL del Video (Cloud/YouTube)", help_text="Link directo al video.")
    thumbnail = models.ImageField(upload_to='testimonials/thumbnails/', verbose_name="Miniatura", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def video_url_ativa(self):
        return _url_ativa(self.video_url)

    @property
    def url_ativa(self):
        return self.video_url_ativa

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Video Testimonio"
        verbose_name_plural = "Videos Testimonios"
        ordering = ['-created_at']


# ──────────────────────────────────────────────────────────────
# CARTELERA FCM-UNLP — Modelo de persistência de avisos
# Estrutura real inspecionada em 2026-07-16:
#   Container: div.card.card-outline-success
#   Data:      div.card-header > h5.m-b-0.text-white
#   Título:    div.card-body > h4.card-title > a[href]
#   Subtítulo: div.card-body > h6.card-subtitle
#   Emissor:   div.card-body > p.card-text.text-right
#   Link:      /noticia/<id>  → base: https://cartelera.med.unlp.edu.ar
# ──────────────────────────────────────────────────────────────
class CarteleraItem(models.Model):
    """
    Aviso capturado da Cartelera oficial FCM-UNLP.
    Cada aviso é identificado de forma única por external_id (path da URL).
    Nunca duplica — apenas atualiza last_seen_at se já existir.
    """
    # ── Identificação única ──────────────────────────────────────
    external_id  = models.CharField(
        max_length=100, unique=True, db_index=True,
        verbose_name='ID externo',
        help_text='Extraído do path /noticia/<id>'
    )
    content_hash = models.CharField(
        max_length=64, db_index=True,
        verbose_name='Hash do conteúdo',
        help_text='SHA-256 de título+data+emissor — detecta mudanças'
    )

    # ── Dados do aviso ───────────────────────────────────────────
    title        = models.CharField(max_length=500, verbose_name='Título')
    subtitle     = models.CharField(max_length=500, blank=True, verbose_name='Subtítulo')
    target_year  = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: Primer Año, Segundo Año, Medicina 2026")
    issuer       = models.CharField(max_length=300, blank=True, verbose_name='Organismo emissor')
    date_str     = models.CharField(max_length=30,  blank=True, verbose_name='Data (texto original)')
    date_parsed  = models.DateField(null=True, blank=True, verbose_name='Data (parseada)')
    url          = models.URLField(max_length=500, verbose_name='URL original')
    category     = models.CharField(max_length=200, blank=True, verbose_name='Categoria/Matéria')

    # ── Raspagem Profunda (Deep Scraping) ─────────────────────────
    body_text       = models.TextField(blank=True, verbose_name='Conteúdo completo do aviso')
    attachment_urls = models.JSONField(default=list, verbose_name='Links e PDFs anexados')
    is_deep_scraped = models.BooleanField(default=False, verbose_name='Raspagem profunda concluída')

    # ── Segmentação por ano ──────────────────────────────────────

    # CSV de anos alvo: '' = todos | 'ingreso,1,2' = só esses anos
    target_years = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name='Anos alvo',
        help_text='Vazio = todos os alunos. Ex: "ingreso,1,2" = só esses anos.',
    )

    # ── Controle de ciclo de vida ────────────────────────────────
    first_seen_at = models.DateTimeField(auto_now_add=True, verbose_name='Primeira vez visto')
    last_seen_at  = models.DateTimeField(auto_now=True,     verbose_name='Última vez visto')
    notified_at   = models.DateTimeField(null=True, blank=True, verbose_name='Notificado em')
    is_active     = models.BooleanField(default=True, verbose_name='Ainda ativo na cartelera')


    class Meta:
        ordering            = ['-date_parsed', '-first_seen_at']
        verbose_name        = 'Aviso da Cartelera'
        verbose_name_plural = 'Avisos da Cartelera'
        indexes = [
            models.Index(fields=['date_parsed', 'is_active']),
            models.Index(fields=['notified_at']),
        ]

    def __str__(self):
        return f"[{self.date_str}] {self.title[:60]} — {self.issuer or 'Sin emisor'}"

    @property
    def needs_notification(self):
        """True se ainda não foi notificado."""
        return self.notified_at is None


# ==========================================
# MENU ARQUITETA - BACKEND ADMIN MODELS
# ==========================================

# 1. Conecta Radar 📡 (Monitoramento y Automatización)
class ConectaRadarSession(models.Model):
    session_name = models.CharField(max_length=100)
    auth_cookies = models.JSONField(help_text="Cookies serializadas de la sesión")
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '📡 Sesión Radar (Nodo Activo)'
        verbose_name_plural = '📡 Sesiones Radar'

class RadarSweepLog(models.Model):
    YEAR_CHOICES = [(0, 'Ingreso'), (1, '1º Año'), (2, '2º Año'), (3, '3º Año')]
    target_year = models.IntegerField(choices=YEAR_CHOICES)
    endpoint_scraped = models.URLField()
    status = models.CharField(max_length=50, choices=[('SUCCESS', 'Éxito'), ('BLOCKED', 'Bloqueado'), ('ERROR', 'Error')])
    items_found = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '🧿 Log de Varredura (Sweep)'
        verbose_name_plural = '🧿 Logs de Varredura'


# 2. PrimeiroBiblio 📚 (Ingestión RAG - Profe Joy)
class PrimeiroBiblioTome(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pendiente'), ('PROCESSING', 'Procesando'), ('COMPLETED', 'Completado')]
    file = models.FileField(upload_to='biblioteca_raw/')
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100, help_text="Ej: Anatomía, Histología")
    vectorization_status = models.CharField(max_length=20, default='PENDING', choices=STATUS_CHOICES)
    total_chunks = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '📚 Tomo de Biblioteca (RAG)'
        verbose_name_plural = '📚 Tomos de Biblioteca'


# 3. Motor Legal ⚖️ (Estatuto & Direitos)
class EstatutoCodex(models.Model):
    article_number = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    legal_text = models.TextField()
    keywords = models.CharField(max_length=255, help_text="Ej: recursante, extranjero, correlatividad")

    class Meta:
        verbose_name = '⚖️ Códice del Estatuto (Regla)'
        verbose_name_plural = '⚖️ Códices del Estatuto'

class AegisDefenseDraft(models.Model):
    student_identifier = models.CharField(max_length=100)
    related_rule = models.ForeignKey(EstatutoCodex, on_delete=models.SET_NULL, null=True)
    generated_document = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '🛡️ Escudo Legal (Borrador)'
        verbose_name_plural = '🛡️ Escudos Legales'


# 4. Club AluMed & Pagos 💳 (Gestión de Accesos)
class ClubAluMedAdept(models.Model):
    student_email = models.EmailField(unique=True)
    wix_subscription_id = models.CharField(max_length=100, blank=True)
    has_atlas_access = models.BooleanField(default=False)
    has_microscope_access = models.BooleanField(default=False)
    has_profe_joy_premium = models.BooleanField(default=False)
    expiration_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = '💎 Adepto del Club (Acceso)'
        verbose_name_plural = '💎 Adeptos del Club'


# 5. O Escudo / Firewall 🛡️ (Seguridad)
class FirewallSigil(models.Model):
    service_name = models.CharField(max_length=100)
    token_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    rate_limit_requests = models.IntegerField(default=100, help_text="Reqs por minuto")
    rotated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '🔥 Sello de Fuego (API Key)'
        verbose_name_plural = '🔥 Sellos de Fuego'


class UserCalendarEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="synced_calendar_events")
    cartelera_event = models.ForeignKey(CarteleraItem, on_delete=models.CASCADE, related_name="user_syncs")
    google_event_id = models.CharField(max_length=255)
    synced_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'cartelera_event')

    def __str__(self):
        return f"{self.user.username} - {self.cartelera_event.title} ({self.google_event_id})"


class Materia(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre de la Materia')
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código Interno')
    ano_cursada = models.IntegerField(verbose_name='Año de Cursada', help_text='1, 2, 3...')

    def __str__(self):
        return self.nombre

class CursoWix(models.Model):
    titulo = models.CharField(max_length=255, verbose_name='Título del Curso')
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, null=True, blank=True, related_name='cursos_wix')
    wix_course_url = models.URLField(max_length=500, verbose_name='URL del Curso en Wix')
    imagen_portada = models.URLField(max_length=500, blank=True, verbose_name='URL de la Imagen')
    descripcion_corta = models.CharField(max_length=300, blank=True, verbose_name='Descripción corta')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='core_profile')
    avatar_url = models.URLField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True, help_text="Número de WhatsApp en formato E.164, ej: +5492211234567")
    current_year = models.CharField(max_length=50, blank=True, null=True, help_text="Año académico del alumno")
    whatsapp_notifications_enabled = models.BooleanField(default=True)
    bio = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    materias = models.ManyToManyField(Materia, blank=True, related_name='estudiantes')
    wix_member_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"


class WhatsAppMessageLog(models.Model):
    MESSAGE_TYPES = [
        ('welcome', 'Bienvenida'),
        ('event_alert', 'Alerta de Evento/Examen'),
        ('exam_reminder', 'Recordatorio'),
        ('support', 'Soporte'),
    ]
    STATUS_CHOICES = [
        ('queued', 'En cola'),
        ('sent', 'Enviado'),
        ('failed', 'Fallido'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    phone_number = models.CharField(max_length=30)
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPES)
    message_body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    api_response_id = models.CharField(max_length=255, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message_type} a {self.phone_number} ({self.status})"


class LibraryDownloadLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wix_item_id = models.CharField(max_length=100)
    item_title = models.CharField(max_length=255)
    materia = models.ForeignKey(Materia, null=True, blank=True, on_delete=models.SET_NULL)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.item_title}"


class LiveClass(models.Model):
    title = models.CharField(max_length=200, verbose_name='Título de la Clase')
    stream_url = models.URLField(max_length=500, verbose_name='URL del Streaming (Embed)')
    target_year = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: Ingreso, Primer Año, Segundo Año")
    is_active = models.BooleanField(default=False, verbose_name='En Vivo Ahora')
    scheduled_time = models.DateTimeField(verbose_name='Fecha y Hora Programada')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.target_year} ({'EN VIVO' if self.is_active else 'Programada'})"

    class Meta:
        verbose_name = '🔴 Clase en Vivo'
        verbose_name_plural = '🔴 Clases en Vivo'
        ordering = ['-scheduled_time']
