from django.db import models
from django.conf import settings
from courses.models import Course

SUBJECT_CHOICES = [
    ('anatomia', 'Anatomía'),
    ('biologia', 'Biología'),
    ('histologia', 'Histología y Embriología'),
    ('sociales', 'Ciencias Sociales y Medicina'),
    ('fisiologia', 'Fisiología y Física Biológica'),
    ('bioquimica', 'Bioquímica y Biología Molecular'),
    ('psicologia', 'Psicología Médica'),
    ('farmacologia', 'Farmacología Básica'),
    ('microbiologia', 'Microbiología y Parasitología'),
    ('patologia', 'Patología'),
    ('semiologia', 'Semiología'),
]

class Topic(models.Model):
    """
    Representa un Testimonio en la plataforma.
    """
    title = models.CharField(max_length=200, verbose_name="Título del Testimonio")
    content = models.TextField(verbose_name="Contenido")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="forum_topics", verbose_name="Autor")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name="forum_topics", verbose_name="Curso Relacionado")
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, default='histologia', verbose_name="Materia")
    file = models.FileField(upload_to='forum/files/', null=True, blank=True, verbose_name="Archivo/Foto Adjunta")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Testimonio"
        verbose_name_plural = "Testimonios"
        ordering = ['-created_at']

class Reply(models.Model):
    """
    Representa uma resposta a um tópico.
    """
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="replies", verbose_name="Tópico")
    content = models.TextField(verbose_name="Conteúdo da Resposta")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="forum_replies", verbose_name="Autor")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    def __str__(self):
        return f"Resposta de {self.author.username} em '{self.topic.title}'"

    class Meta:
        verbose_name = "Resposta"
        verbose_name_plural = "Respostas"
        ordering = ['created_at']
