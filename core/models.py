from django.db import models
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
    pdf_url = models.URLField(verbose_name="Enlace de la Fuente Original", blank=True)
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
