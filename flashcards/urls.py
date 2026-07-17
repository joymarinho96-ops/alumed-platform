from django.urls import path

from flashcards.views import (
    flashcard_dashboard_view,
    deck_detail_view,
    flashcard_study_view,
)
from flashcards.api.views import (
    SubmitFlashcardReviewView,
)

app_name = "flashcards"

urlpatterns = [
    # Páginas de Frontend
    path("flashcards/", flashcard_dashboard_view, name="dashboard"),
    path("flashcards/deck/<int:deck_id>/", deck_detail_view, name="deck-detail"),
    path("flashcards/study/", flashcard_study_view, name="study-general"),
    path("flashcards/deck/<int:deck_id>/study/", flashcard_study_view, name="study-deck"),

    # APIs REST
    path(
        "api/flashcards/<int:flashcard_id>/review/",
        SubmitFlashcardReviewView.as_view(),
        name="submit-flashcard-review",
    ),
]
