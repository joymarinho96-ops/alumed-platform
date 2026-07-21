from rest_framework import serializers

from .models import (
    Favorite,
    Flashcard,
    FlashcardReview,
    MedicalExample,
    Quiz,
    QuizAttempt,
    QuizQuestion,
    RootEntry,
    Term,
    Translation,
    UserTermProgress,
    WordPart,
)


class WordPartSerializer(serializers.ModelSerializer):
    part_type_label = serializers.CharField(source="get_part_type_display", read_only=True)

    class Meta:
        model = WordPart
        fields = (
            "id",
            "part_type",
            "part_type_label",
            "form",
            "normalized_form",
            "meaning",
            "origin_language",
            "grammatical_function",
            "display_order",
            "confidence",
            "notes",
        )


class TranslationSerializer(serializers.ModelSerializer):
    language_label = serializers.CharField(source="get_language_display", read_only=True)

    class Meta:
        model = Translation
        fields = ("id", "language", "language_label", "text", "translation_type", "notes")


class MedicalExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalExample
        fields = ("id", "context", "title", "content", "language")


class RootEntrySerializer(serializers.ModelSerializer):
    root_type_label = serializers.CharField(source="get_root_type_display", read_only=True)
    term_total = serializers.IntegerField(read_only=True)

    class Meta:
        model = RootEntry
        fields = (
            "id",
            "form",
            "normalized_form",
            "root_type",
            "root_type_label",
            "origin_language",
            "original_script",
            "core_meaning",
            "explanation",
            "mnemonic",
            "variants",
            "common_combinations",
            "subjects",
            "term_total",
        )


class TermListSerializer(serializers.ModelSerializer):
    word_parts = WordPartSerializer(many=True, read_only=True)
    translations = TranslationSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    favorite_total = serializers.IntegerField(read_only=True)

    class Meta:
        model = Term
        fields = (
            "id",
            "slug",
            "latin_name",
            "standard_term",
            "literal_translation",
            "medical_definition",
            "subject",
            "origin_language",
            "difficulty",
            "word_parts",
            "translations",
            "is_favorited",
            "favorite_total",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(user=request.user, term=obj).exists()


class TermDetailSerializer(serializers.ModelSerializer):
    word_parts = WordPartSerializer(many=True, read_only=True)
    translations = TranslationSerializer(many=True, read_only=True)
    examples = MedicalExampleSerializer(many=True, read_only=True)
    roots = serializers.SerializerMethodField()
    related_terms = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    study_status = serializers.SerializerMethodField()

    class Meta:
        model = Term
        fields = (
            "id",
            "slug",
            "latin_name",
            "standard_term",
            "pronunciation",
            "audio_url",
            "grammatical_class",
            "gender",
            "declension",
            "literal_translation",
            "medical_definition",
            "etymology",
            "naming_logic",
            "naming_category",
            "mnemonic",
            "mnemonic_spanish",
            "mnemonic_portuguese",
            "exam_trap",
            "rapid_review",
            "specialty",
            "subject",
            "anatomical_system",
            "anatomical_region",
            "difficulty",
            "origin_language",
            "term_type",
            "validation_status",
            "source_notes",
            "word_parts",
            "translations",
            "examples",
            "roots",
            "related_terms",
            "is_favorited",
            "study_status",
        )

    def get_roots(self, obj):
        return [
            {
                "id": link.root.id,
                "form": link.root.form,
                "root_type": link.root.root_type,
                "origin_language": link.root.origin_language,
                "core_meaning": link.root.core_meaning,
                "note": link.note,
            }
            for link in obj.root_links.all()
        ]

    def get_related_terms(self, obj):
        return [
            {
                "slug": relation.target_term.slug,
                "latin_name": relation.target_term.latin_name,
                "literal_translation": relation.target_term.literal_translation,
                "relationship_type": relation.relationship_type,
                "relationship_description": relation.description,
            }
            for relation in obj.outgoing_relationships.all()
        ]

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(user=request.user, term=obj).exists()

    def get_study_status(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        progress = UserTermProgress.objects.filter(user=request.user, term=obj).first()
        return progress.status if progress else None


class FavoriteSerializer(serializers.ModelSerializer):
    term = TermListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ("id", "term", "created_at")


class UserTermProgressSerializer(serializers.ModelSerializer):
    term = TermListSerializer(read_only=True)

    class Meta:
        model = UserTermProgress
        fields = ("id", "term", "status", "last_viewed", "mastery_score", "private_notes", "study_count", "updated_at")


class FlashcardSerializer(serializers.ModelSerializer):
    term = serializers.StringRelatedField()

    class Meta:
        model = Flashcard
        fields = ("id", "term", "card_type", "question", "answer", "explanation", "is_active")


class FlashcardReviewSerializer(serializers.ModelSerializer):
    flashcard = FlashcardSerializer(read_only=True)

    class Meta:
        model = FlashcardReview
        fields = (
            "id",
            "flashcard",
            "rating",
            "reviewed_at",
            "next_review",
            "interval",
            "ease_factor",
            "review_count",
            "mistake_count",
        )


class QuizQuestionSerializer(serializers.ModelSerializer):
    term_slug = serializers.CharField(source="term.slug", read_only=True)

    class Meta:
        model = QuizQuestion
        fields = ("id", "display_order", "question_type", "prompt", "options", "correct_answer", "explanation", "term_slug")


class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ("id", "title", "subject", "difficulty", "description", "is_public", "questions")


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz = serializers.StringRelatedField()

    class Meta:
        model = QuizAttempt
        fields = ("id", "quiz", "score", "accuracy", "started_at", "completed_at", "answers")
