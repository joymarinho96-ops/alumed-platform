from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Deck(models.Model):
    title     = models.CharField(max_length=150, verbose_name="Título")
    subject   = models.CharField(max_length=100, verbose_name="Materia")
    exam_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Examen")
    is_public = models.BooleanField(default=False, verbose_name="Público")

    class Meta:
        verbose_name        = 'Deck'
        verbose_name_plural = 'Decks'
        ordering            = ['subject', 'title']

    def __str__(self):
        return f"{self.title} ({self.subject})"


class Flashcard(models.Model):
    deck        = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="flashcards")
    question    = models.TextField(verbose_name="Pregunta")
    answer      = models.TextField(verbose_name="Respuesta")
    explanation = models.TextField(blank=True, verbose_name="Explicación")
    difficulty  = models.PositiveSmallIntegerField(default=3, verbose_name="Dificultad")

    class Meta:
        verbose_name        = 'Flashcard'
        verbose_name_plural = 'Flashcards'

    def __str__(self):
        return f"Card #{self.id} em {self.deck.title} ({self.question[:40]}...)"


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
    priority              = models.FloatField(default=0.0, db_index=True)
    
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


from django.conf import settings

class StudyStreak(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="study_streak"
    )

    current_streak  = models.PositiveIntegerField(default=0, verbose_name="Racha Actual")
    longest_streak  = models.PositiveIntegerField(default=0, verbose_name="Racha Máxima")
    last_study_date = models.DateField(null=True, blank=True, verbose_name="Última Fecha de Estudio")

    class Meta:
        verbose_name        = "Racha de Estudio"
        verbose_name_plural = "Rachas de Estudio"

    def __str__(self):
        return f"{self.student.username} — Racha: {self.current_streak} días"

