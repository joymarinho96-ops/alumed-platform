from django.utils import timezone

from flashcards.models import StudentFlashcardProgress


def build_daily_session(student, limit: int = 30):
    """
    Constrói a sessão diária de estudos do estudante.
    Retorna os flashcards vencidos ordenados por prioridade máxima (urgência/fraqueza/exames)
    e depois pela data de vencimento.
    """
    due_cards = (
        StudentFlashcardProgress.objects
        .filter(
            student=student,
            next_review_at__lte=timezone.now(),
        )
        .select_related("flashcard")
        .order_by(
            "-priority",         # <- Otimizado: Traz primeiro o de maior urgência/prioridade!
            "next_review_at",
        )[:limit]
    )

    return list(due_cards)
