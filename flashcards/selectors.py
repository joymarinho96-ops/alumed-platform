from django.utils import timezone

from flashcards.models import StudentFlashcardProgress


def get_due_flashcards(student, limit: int = 20):
    """
    Retorna os flashcards vencidos do aluno.
    Ordenados por prioridade (urgência/fraqueza/exame) de forma decrescente
    e depois pela data de vencimento mais antiga.
    """
    return (
        StudentFlashcardProgress.objects
        .filter(
            student=student,
            next_review_at__lte=timezone.now(),
        )
        .select_related("flashcard")
        .order_by(
            "-priority",         # <- Otimizado: traz a maior prioridade primeiro!
            "next_review_at",
        )[:limit]
    )
