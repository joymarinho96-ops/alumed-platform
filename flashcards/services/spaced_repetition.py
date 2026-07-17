from dataclasses import dataclass
from datetime import datetime, timedelta
from math import ceil

from django.utils import timezone

from flashcards.models import StudentFlashcardProgress


@dataclass
class ReviewResult:
    next_review_at: datetime
    interval_days: int
    ease_factor: float
    mastery_score: float
    priority: float


def get_exam_mode(days_until_exam: int) -> str:
    """
    Retorna o modo de estudo baseado em quantos dias restam até o exame.
    """
    if days_until_exam <= 2:
        return "emergency"

    if days_until_exam <= 7:
        return "intensive"

    if days_until_exam <= 14:
        return "reinforcement"

    return "normal"


class SpacedRepetitionEngine:

    """
    Motor de repetição espaçada do ALUMED OS.

    Combina:
    - qualidade da resposta;
    - acerto ou erro;
    - tempo de resposta;
    - dificuldade do flashcard;
    - proximidade da prova;
    - desempenho histórico.
    """

    MIN_EASE_FACTOR = 1.3
    MAX_EASE_FACTOR = 3.2

    def process_review(
        self,
        progress: StudentFlashcardProgress,
        *,
        was_correct: bool,
        response_time_seconds: float,
        confidence: int,
        exam_date: datetime | None = None,
    ) -> ReviewResult:
        """
        confidence:
            1 = chutei
            2 = muita dúvida
            3 = lembrei com esforço
            4 = respondi bem
            5 = domínio completo
        """

        confidence = max(1, min(confidence, 5))
        response_time_seconds = max(response_time_seconds, 0)

        quality = self._calculate_quality(
            was_correct=was_correct,
            confidence=confidence,
            response_time_seconds=response_time_seconds,
            difficulty=progress.flashcard.difficulty,
        )

        self._update_statistics(
            progress=progress,
            was_correct=was_correct,
            response_time_seconds=response_time_seconds,
        )

        self._update_ease_factor(
            progress=progress,
            quality=quality,
        )

        interval_days = self._calculate_interval(
            progress=progress,
            quality=quality,
            exam_date=exam_date,
        )

        mastery_score = self._calculate_mastery(
            progress=progress,
            quality=quality,
            response_time_seconds=response_time_seconds,
        )

        next_review_at = timezone.now() + timedelta(
            days=interval_days,
        )

        priority = self._calculate_priority(
            progress=progress,
            exam_date=exam_date,
            mastery_score=mastery_score,
        )

        progress.interval_days = interval_days
        progress.mastery_score = mastery_score
        progress.priority = priority # <- Salva a prioridade calculada no banco de dados!
        progress.last_reviewed_at = timezone.now()
        progress.next_review_at = next_review_at

        progress.save(
            update_fields=[
                "repetitions",
                "consecutive_correct",
                "consecutive_errors",
                "interval_days",
                "ease_factor",
                "mastery_score",
                "priority", # <- Persiste no banco de dados!
                "total_reviews",
                "correct_reviews",
                "average_response_time",
                "last_reviewed_at",
                "next_review_at",
            ]
        )

        return ReviewResult(
            next_review_at=next_review_at,
            interval_days=interval_days,
            ease_factor=round(progress.ease_factor, 2),
            mastery_score=round(mastery_score, 2),
            priority=round(priority, 2),
        )

    def _calculate_quality(
        self,
        *,
        was_correct: bool,
        confidence: int,
        response_time_seconds: float,
        difficulty: int,
    ) -> int:
        if not was_correct:
            return 0 if confidence >= 4 else 1

        quality = confidence

        expected_time = {
            1: 12,
            2: 18,
            3: 25,
            4: 35,
            5: 45,
        }.get(difficulty, 25)

        if response_time_seconds > expected_time * 2:
            quality -= 1

        if response_time_seconds <= expected_time * 0.6:
            quality += 1

        return max(0, min(quality, 5))

    def _update_statistics(
        self,
        *,
        progress: StudentFlashcardProgress,
        was_correct: bool,
        response_time_seconds: float,
    ) -> None:
        previous_reviews = progress.total_reviews
        progress.total_reviews += 1

        if was_correct:
            progress.correct_reviews += 1
            progress.consecutive_correct += 1
            progress.consecutive_errors = 0
        else:
            progress.consecutive_errors += 1
            progress.consecutive_correct = 0

        if previous_reviews == 0:
            progress.average_response_time = response_time_seconds
        else:
            total_time = (
                progress.average_response_time * previous_reviews
            ) + response_time_seconds

            progress.average_response_time = (
                total_time / progress.total_reviews
            )

    def _update_ease_factor(
        self,
        *,
        progress: StudentFlashcardProgress,
        quality: int,
    ) -> None:
        adjustment = (
            0.1
            - (5 - quality)
            * (0.08 + (5 - quality) * 0.02)
        )

        progress.ease_factor += adjustment

        progress.ease_factor = max(
            self.MIN_EASE_FACTOR,
            min(progress.ease_factor, self.MAX_EASE_FACTOR),
        )

    def _calculate_interval(
        self,
        *,
        progress: StudentFlashcardProgress,
        quality: int,
        exam_date: datetime | None,
    ) -> int:
        if quality < 3:
            progress.repetitions = 0
            interval = 1

        elif progress.repetitions == 0:
            progress.repetitions = 1
            interval = 1

        elif progress.repetitions == 1:
            progress.repetitions = 2
            interval = 3

        elif progress.repetitions == 2:
            progress.repetitions = 3
            interval = 7

        else:
            progress.repetitions += 1

            interval = ceil(
                max(progress.interval_days, 1)
                * progress.ease_factor
            )

        difficulty_factor = {
            1: 1.25,
            2: 1.10,
            3: 1.00,
            4: 0.80,
            5: 0.65,
        }.get(progress.flashcard.difficulty, 1.0)

        interval = max(
            1,
            round(interval * difficulty_factor),
        )

        interval = self._adjust_for_exam(
            interval_days=interval,
            exam_date=exam_date,
        )

        return interval

    def _adjust_for_exam(
        self,
        *,
        interval_days: int,
        exam_date: datetime | None,
    ) -> int:
        if exam_date is None:
            return interval_days

        now = timezone.now()

        if timezone.is_naive(exam_date):
            exam_date = timezone.make_aware(exam_date)

        days_until_exam = max(
            (exam_date - now).days,
            0,
        )

        mode = get_exam_mode(days_until_exam)

        if mode == "emergency":
            return 1

        if mode == "intensive":
            return min(interval_days, 2)

        if mode == "reinforcement":
            return min(interval_days, 4)

        if days_until_exam <= 30:
            return min(interval_days, 7)

        return interval_days


    def _calculate_mastery(
        self,
        *,
        progress: StudentFlashcardProgress,
        quality: int,
        response_time_seconds: float,
    ) -> float:
        accuracy_score = progress.accuracy

        confidence_score = quality / 5 * 100

        speed_score = 100

        if progress.average_response_time > 0:
            speed_ratio = (
                response_time_seconds
                / progress.average_response_time
            )

            speed_score = max(
                0,
                min(100, 120 - speed_ratio * 40),
            )

        consistency_score = min(
            progress.consecutive_correct * 15,
            100,
        )

        mastery = (
            accuracy_score * 0.40
            + confidence_score * 0.25
            + speed_score * 0.15
            + consistency_score * 0.20
        )

        if progress.consecutive_errors > 0:
            mastery -= progress.consecutive_errors * 10

        return max(0, min(mastery, 100))

    def _calculate_priority(
        self,
        *,
        progress: StudentFlashcardProgress,
        exam_date: datetime | None,
        mastery_score: float,
    ) -> float:
        difficulty_score = progress.flashcard.difficulty * 10
        weakness_score = 100 - mastery_score
        error_score = progress.consecutive_errors * 15

        exam_urgency = 0

        if exam_date is not None:
            now = timezone.now()

            if timezone.is_naive(exam_date):
                exam_date = timezone.make_aware(exam_date)

            days_until_exam = max(
                (exam_date - now).days,
                0,
            )

            exam_urgency = max(
                0,
                100 - days_until_exam * 4,
            )

        priority = (
            weakness_score * 0.45
            + difficulty_score * 0.20
            + error_score * 0.15
            + exam_urgency * 0.20
        )

        return max(0, min(priority, 100))
