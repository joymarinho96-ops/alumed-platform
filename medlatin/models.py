from __future__ import annotations

from django.contrib.auth.models import User
from django.db import models
from django.db.models import UniqueConstraint
from django.template.defaultfilters import slugify


class ValidationStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    AI_DRAFT = "ai_draft", "AI-assisted draft"
    REVIEWED = "reviewed", "Reviewed"
    VALIDATED = "validated", "Medically validated"


class PartType(models.TextChoices):
    PREFIX = "prefix", "Prefix"
    ROOT = "root", "Root"
    COMBINING_VOWEL = "combining_vowel", "Combining vowel"
    SUFFIX = "suffix", "Suffix"
    COMPOUND = "compound_element", "Compound element"
    WHOLE = "whole_lexical_unit", "Whole lexical unit"


class RootType(models.TextChoices):
    PREFIX = "prefix", "Prefix"
    ROOT = "root", "Root"
    SUFFIX = "suffix", "Suffix"
    PREPOSITION = "preposition", "Preposition"
    COMBINING = "combining_form", "Combining form"


class TranslationLanguage(models.TextChoices):
    SPANISH = "es", "Spanish"
    PORTUGUESE = "pt-BR", "Portuguese"
    ENGLISH = "en", "English"


class RelationshipType(models.TextChoices):
    SYNONYM = "synonym", "Synonym"
    ANTONYM = "antonym", "Antonym"
    DERIVED = "derived_term", "Derived term"
    SAME_ROOT = "same_root", "Same root"
    PARENT = "parent_concept", "Parent concept"
    CHILD = "child_concept", "Child concept"
    NEIGHBOR = "neighboring_structure", "Neighboring structure"
    CONFUSED = "frequently_confused", "Frequently confused"


class ProgressStatus(models.TextChoices):
    SAVED = "saved", "Saved"
    LEARNING = "learning", "Learning"
    MASTERED = "mastered", "Mastered"


class FlashcardRating(models.TextChoices):
    AGAIN = "again", "Again"
    HARD = "hard", "Hard"
    GOOD = "good", "Good"
    EASY = "easy", "Easy"


class QuestionType(models.TextChoices):
    MULTIPLE = "multiple_choice", "Multiple choice"
    MATCHING = "matching", "Matching"
    FILL = "fill_blank", "Fill in the blank"
    DECOMPOSITION = "decomposition", "Word decomposition"
    TRUE_FALSE = "true_false", "True or false"
    ETYMOLOGY = "incorrect_etymology", "Incorrect etymology"
    NAMING = "naming_logic", "Naming logic"
    TRAP = "exam_trap", "Exam trap"


class Term(models.Model):
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    latin_name = models.CharField(max_length=180, db_index=True)
    standard_term = models.CharField(max_length=180, blank=True)
    pronunciation = models.CharField(max_length=180, blank=True)
    audio_url = models.URLField(blank=True)
    grammatical_class = models.CharField(max_length=80, blank=True, db_index=True)
    gender = models.CharField(max_length=40, blank=True, db_index=True)
    declension = models.CharField(max_length=60, blank=True, db_index=True)
    literal_translation = models.TextField()
    medical_definition = models.TextField()
    etymology = models.TextField()
    naming_logic = models.TextField()
    naming_category = models.CharField(max_length=100, blank=True, db_index=True)
    mnemonic = models.TextField(blank=True)
    mnemonic_spanish = models.TextField(blank=True)
    mnemonic_portuguese = models.TextField(blank=True)
    exam_trap = models.TextField(blank=True)
    rapid_review = models.TextField(blank=True)
    specialty = models.CharField(max_length=120, blank=True, db_index=True)
    subject = models.CharField(max_length=120, blank=True, db_index=True)
    anatomical_system = models.CharField(max_length=120, blank=True, db_index=True)
    anatomical_region = models.CharField(max_length=120, blank=True)
    difficulty = models.PositiveSmallIntegerField(default=2, db_index=True)
    origin_language = models.CharField(max_length=160, db_index=True)
    term_type = models.CharField(max_length=100, blank=True, db_index=True)
    validation_status = models.CharField(
        max_length=24,
        choices=ValidationStatus.choices,
        default=ValidationStatus.AI_DRAFT,
        db_index=True,
    )
    source_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["latin_name"]
        indexes = [
            models.Index(fields=["latin_name", "origin_language"]),
            models.Index(fields=["subject", "anatomical_system"]),
            models.Index(fields=["validation_status", "difficulty"]),
        ]

    def __str__(self) -> str:
        return self.latin_name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base_slug = slugify(self.standard_term or self.latin_name) or "term"
            slug = base_slug
            index = 2
            while Term.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{index}"
                index += 1
            self.slug = slug
        super().save(*args, **kwargs)


class WordPart(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="word_parts")
    part_type = models.CharField(max_length=24, choices=PartType.choices, db_index=True)
    form = models.CharField(max_length=120)
    normalized_form = models.CharField(max_length=120, db_index=True)
    meaning = models.CharField(max_length=255)
    origin_language = models.CharField(max_length=120)
    grammatical_function = models.CharField(max_length=160, blank=True)
    display_order = models.PositiveSmallIntegerField(default=1)
    confidence = models.DecimalField(max_digits=3, decimal_places=2, default=1)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["display_order", "id"]
        indexes = [models.Index(fields=["normalized_form", "part_type"])]

    def __str__(self) -> str:
        return f"{self.term.latin_name}: {self.form}"


class Translation(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="translations")
    language = models.CharField(max_length=10, choices=TranslationLanguage.choices, db_index=True)
    text = models.CharField(max_length=220, db_index=True)
    translation_type = models.CharField(max_length=80, default="preferred")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["language", "text"]
        constraints = [
            UniqueConstraint(fields=["term", "language", "translation_type"], name="unique_term_translation_type"),
        ]

    def __str__(self) -> str:
        return f"{self.term.latin_name} ({self.language})"


class MedicalExample(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="examples")
    context = models.CharField(max_length=120, db_index=True)
    title = models.CharField(max_length=180)
    content = models.TextField()
    language = models.CharField(max_length=10, choices=TranslationLanguage.choices)

    class Meta:
        ordering = ["context", "id"]

    def __str__(self) -> str:
        return f"{self.term.latin_name}: {self.title}"


class Relationship(models.Model):
    source_term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="outgoing_relationships")
    target_term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="incoming_relationships")
    relationship_type = models.CharField(max_length=30, choices=RelationshipType.choices, db_index=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["relationship_type", "target_term__latin_name"]
        constraints = [
            UniqueConstraint(
                fields=["source_term", "target_term", "relationship_type"],
                name="unique_medlatin_relationship",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.source_term} -> {self.target_term} ({self.relationship_type})"


class RootEntry(models.Model):
    form = models.CharField(max_length=120)
    normalized_form = models.CharField(max_length=120, db_index=True)
    root_type = models.CharField(max_length=20, choices=RootType.choices, db_index=True)
    origin_language = models.CharField(max_length=120, db_index=True)
    original_script = models.CharField(max_length=120, blank=True)
    core_meaning = models.CharField(max_length=255)
    explanation = models.TextField(blank=True)
    mnemonic = models.TextField(blank=True)
    variants = models.CharField(max_length=255, blank=True)
    common_combinations = models.TextField(blank=True)
    subjects = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["form"]
        constraints = [
            UniqueConstraint(fields=["normalized_form", "root_type"], name="unique_root_form_type"),
        ]

    def __str__(self) -> str:
        return self.form


class TermRootLink(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="root_links")
    root = models.ForeignKey(RootEntry, on_delete=models.CASCADE, related_name="term_links")
    note = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["display_order", "root__form"]
        constraints = [UniqueConstraint(fields=["term", "root"], name="unique_term_root_link")]

    def __str__(self) -> str:
        return f"{self.term} · {self.root}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="medlatin_favorites")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="favorites")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [UniqueConstraint(fields=["user", "term"], name="unique_medlatin_favorite")]

    def __str__(self) -> str:
        return f"{self.user.username} ♥ {self.term.latin_name}"


class UserTermProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="medlatin_term_progress")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="progress_records")
    status = models.CharField(max_length=20, choices=ProgressStatus.choices, default=ProgressStatus.LEARNING)
    last_viewed = models.DateTimeField(null=True, blank=True)
    mastery_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    private_notes = models.TextField(blank=True)
    study_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [UniqueConstraint(fields=["user", "term"], name="unique_medlatin_term_progress")]

    def __str__(self) -> str:
        return f"{self.user.username} · {self.term.latin_name}"


class Flashcard(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="flashcards")
    card_type = models.CharField(max_length=60, db_index=True)
    question = models.TextField()
    answer = models.TextField()
    explanation = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["term__latin_name", "card_type", "id"]

    def __str__(self) -> str:
        return f"{self.term.latin_name} · {self.card_type}"


class FlashcardReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="medlatin_flashcard_reviews")
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name="reviews")
    rating = models.CharField(max_length=12, choices=FlashcardRating.choices, default=FlashcardRating.GOOD)
    reviewed_at = models.DateTimeField(auto_now=True)
    next_review = models.DateTimeField(null=True, blank=True)
    interval = models.PositiveIntegerField(default=0)
    ease_factor = models.DecimalField(max_digits=4, decimal_places=2, default=2.50)
    review_count = models.PositiveIntegerField(default=0)
    mistake_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["next_review", "id"]
        constraints = [UniqueConstraint(fields=["user", "flashcard"], name="unique_medlatin_flashcard_review")]

    def __str__(self) -> str:
        return f"{self.user.username} · {self.flashcard_id}"


class Quiz(models.Model):
    title = models.CharField(max_length=180)
    subject = models.CharField(max_length=120, db_index=True)
    difficulty = models.PositiveSmallIntegerField(default=2, db_index=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_type = models.CharField(max_length=32, choices=QuestionType.choices)
    prompt = models.TextField()
    options = models.JSONField(default=list, blank=True)
    correct_answer = models.JSONField(default=dict, blank=True)
    explanation = models.TextField(blank=True)
    term = models.ForeignKey(Term, null=True, blank=True, on_delete=models.SET_NULL, related_name="quiz_questions")
    display_order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self) -> str:
        return f"{self.quiz.title} · Q{self.display_order}"


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="medlatin_quiz_attempts")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    score = models.PositiveIntegerField(default=0)
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    answers = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.user.username} · {self.quiz.title}"
