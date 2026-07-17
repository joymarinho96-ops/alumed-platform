from rest_framework import serializers
from flashcards.models import Deck, Flashcard, StudentFlashcardProgress, StudyStreak


class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = [
            "id",
            "title",
            "subject",
            "exam_date",
            "is_public",
        ]


class FlashcardSerializer(serializers.ModelSerializer):
    deck = DeckSerializer(read_only=True)

    class Meta:
        model = Flashcard
        fields = [
            "id",
            "deck",
            "question",
            "answer",
            "explanation",
            "difficulty",
        ]


class StudentFlashcardProgressSerializer(serializers.ModelSerializer):
    flashcard = FlashcardSerializer(read_only=True)

    class Meta:
        model = StudentFlashcardProgress
        fields = [
            "id",
            "flashcard",
            "repetitions",
            "consecutive_correct",
            "consecutive_errors",
            "interval_days",
            "ease_factor",
            "mastery_score",
            "priority",
            "total_reviews",
            "correct_reviews",
            "average_response_time",
            "last_reviewed_at",
            "next_review_at",
            "accuracy",
        ]


class StudyStreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyStreak
        fields = [
            "current_streak",
            "longest_streak",
            "last_study_date",
        ]
