from django.urls import path

from flashcards.api.views import (
    SubmitFlashcardReviewView,
)


urlpatterns = [
    path(
        "api/flashcards/<int:flashcard_id>/review/",
        SubmitFlashcardReviewView.as_view(),
        name="submit-flashcard-review",
    ),
]
