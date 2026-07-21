from django.contrib import admin

from .models import (
    Favorite,
    Flashcard,
    FlashcardReview,
    MedicalExample,
    Quiz,
    QuizAttempt,
    QuizQuestion,
    Relationship,
    RootEntry,
    Term,
    TermRootLink,
    Translation,
    UserTermProgress,
    WordPart,
)


class WordPartInline(admin.TabularInline):
    model = WordPart
    extra = 0
    ordering = ("display_order",)


class TranslationInline(admin.TabularInline):
    model = Translation
    extra = 0


class MedicalExampleInline(admin.TabularInline):
    model = MedicalExample
    extra = 0


class TermRootLinkInline(admin.TabularInline):
    model = TermRootLink
    extra = 0
    autocomplete_fields = ("root",)


@admin.action(description="Mark selected terms as AI-assisted draft")
def mark_ai_draft(modeladmin, request, queryset):
    queryset.update(validation_status="ai_draft")


@admin.action(description="Mark selected terms as reviewed")
def mark_reviewed(modeladmin, request, queryset):
    queryset.update(validation_status="reviewed")


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = (
        "latin_name",
        "subject",
        "anatomical_system",
        "origin_language",
        "difficulty",
        "validation_status",
    )
    list_filter = ("subject", "anatomical_system", "origin_language", "difficulty", "validation_status")
    search_fields = ("latin_name", "standard_term", "literal_translation", "medical_definition", "slug")
    prepopulated_fields = {"slug": ("latin_name",)}
    inlines = [WordPartInline, TranslationInline, MedicalExampleInline, TermRootLinkInline]
    actions = [mark_ai_draft, mark_reviewed]


@admin.register(RootEntry)
class RootEntryAdmin(admin.ModelAdmin):
    list_display = ("form", "root_type", "origin_language", "core_meaning")
    list_filter = ("root_type", "origin_language")
    search_fields = ("form", "normalized_form", "core_meaning", "variants")


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ("source_term", "relationship_type", "target_term")
    list_filter = ("relationship_type",)
    search_fields = ("source_term__latin_name", "target_term__latin_name", "description")
    autocomplete_fields = ("source_term", "target_term")


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ("term", "card_type", "is_active")
    list_filter = ("card_type", "is_active")
    search_fields = ("term__latin_name", "question", "answer")
    autocomplete_fields = ("term",)


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 0
    autocomplete_fields = ("term",)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "difficulty", "is_public")
    list_filter = ("subject", "difficulty", "is_public")
    search_fields = ("title", "description")
    inlines = [QuizQuestionInline]


admin.site.register(Translation)
admin.site.register(MedicalExample)
admin.site.register(TermRootLink)
admin.site.register(Favorite)
admin.site.register(UserTermProgress)
admin.site.register(FlashcardReview)
admin.site.register(QuizAttempt)
