from django.db import models
from django.conf import settings
from django.utils import timezone
from alumed.url_utils import build_video_source, normalize_gcs_url

def _url_ativa(url):
    return normalize_gcs_url(url)


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(default=30)
    image = models.ImageField(upload_to='courses/images/', null=True, blank=True)
    is_free = models.BooleanField(default=False, verbose_name="Curso Gratuito")
    wix_url = models.URLField(
        blank=True, null=True,
        verbose_name="URL do curso no Wix",
        help_text="Se preenchido, Entrar al curso abre este link no Wix. Se vazio, mostra Acceso en configuracion."
    )

    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    LESSON_TYPE_CHOICES = [
        ('video', 'Video'),
        ('pdf', 'PDF'),
        ('html', 'HTML'),
        ('podcast', 'Podcast'),
        ('simulacro', 'Simulacro'),
        ('special_content', 'ConteÃºdo Especial'),
    ]
    VIDEO_PROVIDER_CHOICES = [
        ('auto', 'Detectar automaticamente'),
        ('google_cloud', 'Google Cloud Storage'),
        ('youtube', 'YouTube'),
        ('google_drive', 'Google Drive'),
    ]
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True, help_text="DescriÃ§Ã£o da aula (pode conter links e texto).")
    lesson_type = models.CharField(max_length=15, choices=LESSON_TYPE_CHOICES, default='video')
    video_provider = models.CharField(
        max_length=20,
        choices=VIDEO_PROVIDER_CHOICES,
        default='auto',
        verbose_name="Origem do video",
        help_text="Use Auto para detectar pelo link, ou escolha YouTube/Google Drive/Google Cloud manualmente.",
    )
    video_url = models.URLField(blank=True, null=True, help_text="URL do vÃ­deo (Vimeo, YouTube, etc.)")
    file = models.FileField(upload_to='lessons/files/', blank=True, null=True, help_text="Arquivo da aula (vÃ­deo, PDF, etc.)")
    html_content = models.TextField(blank=True, help_text="Cole o conteÃºdo HTML aqui.")
    html_url = models.URLField(blank=True, null=True, help_text="URL do arquivo HTML hospedado (ex: Google Cloud). Se preenchido, o conteÃºdo HTML serÃ¡ carregado via iframe.")
    simulacro_url = models.URLField(blank=True, null=True, help_text="URL do Simulacro (HTML externo ou arquivo hospedado). SerÃ¡ exibido em iframe.")
    special_content_url = models.URLField(blank=True, null=True, help_text="URL para redirecionamento (ConteÃºdo Especial).")
    order = models.PositiveIntegerField(default=0)
    duration_in_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    @property
    def video_url_ativa(self):
        return _url_ativa(self.video_url)

    @property
    def video_source(self):
        return build_video_source(self.video_url, self.video_provider)

    @property
    def html_url_ativa(self):
        return _url_ativa(self.html_url)

    @property
    def simulacro_url_ativa(self):
        return _url_ativa(self.simulacro_url)

    @property
    def special_content_url_ativa(self):
        return _url_ativa(self.special_content_url)

    @property
    def url_ativa(self):
        if self.lesson_type == 'html':
            return self.html_url_ativa
        if self.lesson_type == 'simulacro':
            return self.simulacro_url_ativa
        if self.lesson_type == 'special_content':
            return self.special_content_url_ativa
        return self.video_url_ativa

    def __str__(self):
        return self.title

class PodcastEpisode(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='podcast_episodes')
    title = models.CharField(max_length=200, verbose_name="TÃ­tulo do Ãudio")
    audio_url = models.URLField(verbose_name="URL do Ãudio (Cloud)", help_text="Link direto para o arquivo de Ã¡udio.")
    duration = models.CharField(max_length=10, blank=True, null=True, verbose_name="DuraÃ§Ã£o (ex: 05:30)", help_text="Opcional")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "EpisÃ³dio de Podcast"
        verbose_name_plural = "EpisÃ³dios de Podcast"

    @property
    def audio_url_ativa(self):
        return _url_ativa(self.audio_url)

    @property
    def url_ativa(self):
        return self.audio_url_ativa

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField()
    access_source = models.CharField(
        max_length=20,
        choices=[
            ('wix', 'Wix Webhook'),
            ('transferencia', 'Transferencia Bancaria'),
            ('cortesia', 'CortesÃ­a/Beca'),
            ('ajuste_manual', 'Ajuste Manual Staff')
        ],
        default='wix'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='manual_enrollments_created'
    )
    internal_notes = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revoked_enrollments'
    )

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

class EnrollmentHistory(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollment_histories')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', 'CreaciÃ³n'),
            ('extend', 'ExtensiÃ³n'),
            ('revoke', 'RevocaciÃ³n'),
            ('expire', 'ExpiraciÃ³n')
        ]
    )
    access_source = models.CharField(max_length=20)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actions_performed'
    )
    notes = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historial de MatrÃ­cula"
        verbose_name_plural = "Historiales de MatrÃ­culas"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.action} on {self.timestamp.strftime('%d/%m/%Y')}"

class PaymentHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    days_added = models.IntegerField()
    payment_id = models.CharField(max_length=100, unique=True, null=True, blank=True, help_text="ID do pagamento no Mercado Pago")

    class Meta:
        verbose_name = "HistÃ³rico de Pagamento"
        verbose_name_plural = "HistÃ³rico de Pagamentos"
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.payment_date.strftime('%d/%m/%Y')}"

class LessonCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')

class Comment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f"Comment by {self.user.username} on {self.lesson.title}"

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"Like by {self.user.username} on {self.lesson.title}"

class Deck(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='decks')
    title = models.CharField(max_length=200, verbose_name="TÃ­tulo del Mazo")
    category = models.CharField(max_length=100, verbose_name="CategorÃ­a", default="General")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Flashcard(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='cards')
    front = models.TextField(verbose_name="Pregunta (Frente)")
    back = models.TextField(verbose_name="Respuesta (Dorso)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.deck.title} - {self.front[:30]}..."



class SimulacroQuestion(models.Model):
    SUBJECT_CHOICES = [('Anatomía', 'Anatomía'), ('Histología', 'Histología'), ('Biología', 'Biología'), ('Embriología', 'Embriología')]
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    CORRECT_CHOICES = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    correct_option = models.CharField(max_length=1, choices=CORRECT_CHOICES)
    explanation = models.TextField(blank=True, null=True, help_text='Explicación mostrada tras fallar')

    def __str__(self):
        return f'[{self.subject}] {self.question_text[:50]}...'
