from django.db.models import Avg, Sum
from flashcards.models import StudentFlashcardProgress, StudyStreak


def get_student_study_analytics(student):
    """
    Retorna estatísticas consolidadas sobre o desempenho e consistência de estudo do aluno.
    """
    progress_qs = StudentFlashcardProgress.objects.filter(student=student)
    
    total_cards_studied = progress_qs.count()
    
    if total_cards_studied == 0:
        return {
            "total_cards": 0,
            "accuracy": 0.0,
            "average_response_time": 0.0,
            "average_mastery": 0.0,
            "total_reviews": 0,
            "streak": 0,
        }

    stats = progress_qs.aggregate(
        avg_mastery=Avg("mastery_score"),
        avg_response_time=Avg("average_response_time"),
        sum_total_reviews=Sum("total_reviews"),
        sum_correct_reviews=Sum("correct_reviews"),
    )

    total_reviews   = stats.get("sum_total_reviews") or 0
    correct_reviews = stats.get("sum_correct_reviews") or 0
    accuracy        = (correct_reviews / total_reviews * 100.0) if total_reviews > 0 else 100.0

    # Carrega ofensiva
    try:
        streak_obj = student.study_streak
        streak = streak_obj.current_streak
    except StudyStreak.DoesNotExist:
        streak = 0

    return {
        "total_cards": total_cards_studied,
        "accuracy": round(accuracy, 1),
        "average_response_time": round(stats.get("avg_response_time") or 0.0, 1),
        "average_mastery": round(stats.get("avg_mastery") or 0.0, 1),
        "total_reviews": total_reviews,
        "streak": streak,
    }
