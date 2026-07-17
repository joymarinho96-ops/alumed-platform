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
            flashcard = Flashcard.objects.get(
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

        # ── INTEGRAÇÃO PREMIUM ──
        # Busca a próxima prova parcial/final cadastrada do aluno para a matéria do card
        next_exam = (
            AcademicEvent.objects
            .filter(
                user=request.user,
                subject__iexact=flashcard.subject,
                event_type__in=['parcial', 'final'],
                start_datetime__gt=timezone.now()
            )
            .order_by('start_datetime')
            .first()
        )
        exam_date = next_exam.start_datetime if next_exam else None

        engine = SpacedRepetitionEngine()

        result = engine.process_review(
            progress,
            was_correct=was_correct,
            response_time_seconds=response_time,
            confidence=confidence,
            exam_date=exam_date, # <- Motor agora se adapta com a data da prova!
        )

        # Retorna o JSON exato no padrão do estudante
        return Response(
            {
                "message": "Revisão registrada",
                "interval_days": result.interval_days,
                "mastery_score": int(result.mastery_score), # Retorna inteiro como na especificação (ex: 72)
                "next_review_at": result.next_review_at.isoformat(),
            }
        )

