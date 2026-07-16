from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ─────────────────────────────────────────────────────────────────────────────
# CATÁLOGO
# ─────────────────────────────────────────────────────────────────────────────

class Subject(models.Model):
    YEAR_CHOICES = [(i, f'{i}° Año') for i in range(1, 7)]

    name   = models.CharField(max_length=100, unique=True, verbose_name='Materia')
    emoji  = models.CharField(max_length=8, default='📚')
    year   = models.PositiveSmallIntegerField(choices=YEAR_CHOICES, default=1, verbose_name='Año')
    color  = models.CharField(max_length=20, default='#8b5cf6', help_text='Color hex para UI')
    active = models.BooleanField(default=True)
    order  = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['year', 'order', 'name']
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'

    def __str__(self):
        return f'{self.emoji} {self.name} ({self.year}° Año)'


class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    name    = models.CharField(max_length=150, verbose_name='Tema')
    active  = models.BooleanField(default=True)
    order   = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        unique_together = [('subject', 'name')]
        verbose_name = 'Tema'
        verbose_name_plural = 'Temas'

    def __str__(self):
        return f'{self.subject.name} › {self.name}'


# ─────────────────────────────────────────────────────────────────────────────
# BANCO DE QUESTÕES
# ─────────────────────────────────────────────────────────────────────────────

class Question(models.Model):
    TYPE_CHOICE = 'choice'
    TYPE_ORAL   = 'oral'
    TYPE_CHOICES = [
        (TYPE_CHOICE, 'Múltiple opción'),
        (TYPE_ORAL,   'Oral'),
    ]
    DIFF_CHOICES = [
        ('easy',   'Fácil'),
        ('medium', 'Media'),
        ('hard',   'Difícil'),
    ]
    SOURCE_CHOICES = [
        ('unlp',    'UNLP Oficial'),
        ('alumed',  'ALUMED'),
        ('profe',   'Profe Joy'),
        ('other',   'Otro'),
    ]

    subject     = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions')
    topic       = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    q_type      = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_CHOICE, verbose_name='Tipo')
    difficulty  = models.CharField(max_length=10, choices=DIFF_CHOICES, default='medium', verbose_name='Dificultad')
    year        = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Año cursada')
    statement   = models.TextField(verbose_name='Enunciado')
    explanation = models.TextField(blank=True, verbose_name='Explicación / Resolución')
    image       = models.ImageField(upload_to='simulator/questions/', null=True, blank=True, verbose_name='Imagen')
    tags        = models.CharField(max_length=300, blank=True, help_text='Separar con comas')
    source      = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='alumed')
    active      = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['subject', 'difficulty', 'id']
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
        indexes = [
            models.Index(fields=['subject', 'q_type', 'active']),
            models.Index(fields=['topic', 'difficulty']),
        ]

    def __str__(self):
        return f'[{self.get_difficulty_display()}] {self.statement[:80]}'

    @property
    def correct_alternatives(self):
        return self.alternatives.filter(is_correct=True)


class Alternative(models.Model):
    question   = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='alternatives')
    text       = models.TextField(verbose_name='Texto de la opción')
    is_correct = models.BooleanField(default=False, verbose_name='¿Es correcta?')
    order      = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Alternativa'
        verbose_name_plural = 'Alternativas'

    def __str__(self):
        mark = '✓' if self.is_correct else '✗'
        return f'{mark} {self.text[:60]}'


# ─────────────────────────────────────────────────────────────────────────────
# SESIONES DE SIMULADO
# ─────────────────────────────────────────────────────────────────────────────

class SimSession(models.Model):
    MODE_CHOICE = 'choice'
    MODE_ORAL   = 'oral'
    MODE_UNLP   = 'unlp'
    MODE_CHOICES = [
        (MODE_CHOICE, 'Múltiple opción'),
        (MODE_ORAL,   'Oral'),
        (MODE_UNLP,   'Modo UNLP'),
    ]
    STATUS_ACTIVE   = 'active'
    STATUS_FINISHED = 'finished'
    STATUS_CHOICES  = [
        (STATUS_ACTIVE,   'En curso'),
        (STATUS_FINISHED, 'Finalizado'),
    ]

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sim_sessions')
    mode        = models.CharField(max_length=10, choices=MODE_CHOICES, default=MODE_CHOICE)
    subject     = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    topic       = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty  = models.CharField(max_length=10, blank=True)
    preset      = models.CharField(max_length=60, blank=True, help_text='Nombre del preset UNLP')
    total_q     = models.PositiveSmallIntegerField(default=0, verbose_name='Total preguntas')
    correct     = models.PositiveSmallIntegerField(default=0, verbose_name='Correctas')
    score       = models.FloatField(default=0.0, verbose_name='% acierto')
    duration_s  = models.PositiveIntegerField(default=0, verbose_name='Duración (segundos)')
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    # ordered list of question PKs (JSON)
    question_order = models.JSONField(default=list, blank=True)
    current_index  = models.PositiveSmallIntegerField(default=0)
    time_limit_s   = models.PositiveIntegerField(default=0, help_text='0 = sin límite')
    started_at  = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Sesión de Simulado'
        verbose_name_plural = 'Sesiones de Simulado'

    def __str__(self):
        return f'{self.user.username} | {self.get_mode_display()} | {self.score:.0f}% ({self.started_at:%d/%m/%Y})'

    def finish(self):
        answers = self.answers.all()
        self.total_q    = answers.count()
        self.correct    = answers.filter(is_correct=True).count()
        self.score      = round(self.correct / self.total_q * 100, 1) if self.total_q else 0
        self.status     = self.STATUS_FINISHED
        self.finished_at = timezone.now()
        if self.started_at:
            self.duration_s = int((self.finished_at - self.started_at).total_seconds())
        self.save()


class UserAnswer(models.Model):
    session      = models.ForeignKey(SimSession, on_delete=models.CASCADE, related_name='answers')
    question     = models.ForeignKey(Question, on_delete=models.CASCADE)
    chosen_alts  = models.ManyToManyField(Alternative, blank=True, verbose_name='Opciones elegidas')
    is_correct   = models.BooleanField(default=False)
    time_spent_s = models.PositiveSmallIntegerField(default=0, verbose_name='Tiempo (s)')
    oral_text    = models.TextField(blank=True, verbose_name='Respuesta oral escrita')
    ai_feedback  = models.TextField(blank=True, verbose_name='Feedback IA')
    answered_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('session', 'question')]
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'

    def __str__(self):
        mark = '✓' if self.is_correct else '✗'
        return f'{mark} {self.session.user.username} — Q{self.question_id}'
