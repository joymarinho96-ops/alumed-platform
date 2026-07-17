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


from django.db.models import Avg

def get_subject_mastery(student):
    """
    Retorna o nível médio de domínio (mastery_score) do estudante agrupado por matéria.
    """
    return (
        StudentFlashcardProgress.objects
        .filter(student=student)
        .values("flashcard__subject")
        .annotate(
            average_mastery=Avg("mastery_score")
        )
        .order_by("flashcard__subject")
    )


def build_profe_joy_context(progress):
    """
    Retorna o contexto do flashcard estruturado para consumo pela Profe Joy IA.
    """
    return {
        "subject": progress.flashcard.subject,
        "topic": progress.flashcard.topic,
        "question": progress.flashcard.question,
        "correct_answer": progress.flashcard.answer,
        "mastery": progress.mastery_score,
        "consecutive_errors": progress.consecutive_errors,
    }


