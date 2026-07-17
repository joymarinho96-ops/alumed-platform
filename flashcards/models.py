from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Flashcard(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Muy Fácil'),
        (2, 'Fácil'),
        (3, 'Medio'),
        (4, 'Difícil'),
        (5, 'Muy Difícil'),
    ]

    question   = models.TextField(verbose_name='Pregunta')
    answer     = models.TextField(verbose_name='Respuesta')
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES, default=3, verbose_name='Dificultad')
    subject    = models.CharField(max_length=200, verbose_name='Materia')
    topic      = models.CharField(max_length=200, blank=True, verbose_name='Tema/Tópico') # <- Novo campo!
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name        = 'Flashcard'
        verbose_name_plural = 'Flashcards'
        ordering            = ['subject', '-created_at']

    def __str__(self):
        return f"[{self.subject}] {self.question[:50]}..."


class StudentFlashcardProgress(models.Model):
    student               = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flashcard_progress')
    flashcard             = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name='progress_records')
    
    # Métricas de repetição espaçada
    repetitions           = models.PositiveIntegerField(default=0)
    consecutive_correct   = models.PositiveIntegerField(default=0)
    consecutive_errors     = models.PositiveIntegerField(default=0)
    interval_days         = models.PositiveIntegerField(default=0)
    ease_factor           = models.FloatField(default=2.5)
    mastery_score         = models.FloatField(default=0.0)
    priority              = models.FloatField(default=0.0, db_index=True) # <- Otimizado: salvo no banco para a ordenação!
    
    # Estatísticas de desempenho
    total_reviews         = models.PositiveIntegerField(default=0)
    correct_reviews       = models.PositiveIntegerField(default=0)
    average_response_time = models.FloatField(default=0.0)
    
    last_reviewed_at      = models.DateTimeField(null=True, blank=True)
    next_review_at        = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        unique_together     = ('student', 'flashcard')
        verbose_name        = 'Progreso de Flashcard'
        verbose_name_plural = 'Progresos de Flashcards'
        ordering            = ['-priority', 'next_review_at']

    def __str__(self):
        return f"{self.student.username} - {self.flashcard.id} [mastery: {self.mastery_score:.1f}%]"

    @property
    def accuracy(self) -> float:
        """Percentual de acertos históricos."""
        if self.total_reviews == 0:
            return 100.0
        return (self.correct_reviews / self.total_reviews) * 100.0
