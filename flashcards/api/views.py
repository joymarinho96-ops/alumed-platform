from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from flashcards.models import (
    Flashcard,
    StudentFlashcardProgress,
)
from flashcards.services.spaced_repetition import (
    SpacedRepetitionEngine,
)
from accounts.models import AcademicEvent


class SubmitFlashcardReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, flashcard_id: int):
        try:
            # Carrega flashcard junto com o Deck relacionado
            flashcard = Flashcard.objects.select_related("deck").get(
                id=flashcard_id,
            )
        except Flashcard.DoesNotExist:
            return Response(
                {"error": "Flashcard não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        was_correct = request.data.get("was_correct")
        response_time = request.data.get(
            "response_time_seconds"
        )
        confidence = request.data.get("confidence")

        if not isinstance(was_correct, bool):
            return Response(
                {"error": "Informe se a resposta estava correta."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mapeamento dinâmico de strings para inteiros (QUALITY_MAP)
        QUALITY_MAP = {
            "wrong": 1,
            "hard": 2,
            "remembered": 3,
            "easy": 4,
            "mastered": 5,
        }
        if isinstance(confidence, str) and confidence.lower() in QUALITY_MAP:
            confidence = QUALITY_MAP[confidence.lower()]

        try:
            response_time = float(response_time)
            confidence = int(confidence)
        except (TypeError, ValueError):
            return Response(
                {
                    "error": (
                        "Tempo de resposta ou confiança inválidos."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        progress, _ = (
            StudentFlashcardProgress.objects.get_or_create(
                student=request.user,
                flashcard=flashcard,
            )
        )

        # ── INTEGRAÇÃO PREMIUM COM DECKS E EXAMES ──
        # 1. Se o Deck possui uma data de exame configurada, use-a.
        # 2. Caso contrário, busca o próximo evento acadêmico parcial/final da matéria do Deck.
        exam_date = flashcard.deck.exam_date
        
        if not exam_date:
            next_exam = (
                AcademicEvent.objects
                .filter(
                    user=request.user,
                    subject__iexact=flashcard.deck.subject,
                    event_type__in=['parcial', 'final'],
                    start_datetime__gt=timezone.now()
                )
                .order_by('start_datetime')
                .first()
            )
            if next_exam:
                exam_date = next_exam.start_datetime

        engine = SpacedRepetitionEngine()

        result = engine.process_review(
            progress,
            was_correct=was_correct,
            response_time_seconds=response_time,
            confidence=confidence,
            exam_date=exam_date,
        )

        # ── ATUALIZAÇÃO DA OFENSIVA (STUDY STREAK) ──
        from datetime import timedelta
        from flashcards.models import StudyStreak
        
        today = timezone.localdate()
        streak, _ = StudyStreak.objects.get_or_create(student=request.user)
        
        if streak.last_study_date is None:
            # Primeiro estudo
            streak.current_streak = 1
        elif streak.last_study_date == today:
            # Já estudou hoje, mantém a ofensiva
            pass
        elif streak.last_study_date == today - timedelta(days=1):
            # Estudou ontem, aumenta a ofensiva
            streak.current_streak += 1
        else:
            # Quebrou a sequência, reinicia
            streak.current_streak = 1
            
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        streak.last_study_date = today
        streak.save()

        # Retorna o JSON exato no padrão do estudante
        return Response(
            {
                "message": "Revisão registrada",
                "interval_days": result.interval_days,
                "mastery_score": int(result.mastery_score),
                "next_review_at": result.next_review_at.isoformat(),
            }
        )

