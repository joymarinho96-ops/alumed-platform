from django.urls import path

from . import api, views


app_name = "medlatin"


urlpatterns = [
    path("", views.medlatin_home, name="home"),
    path("dictionary/", views.dictionary_search, name="dictionary"),
    path("terms/<slug:slug>/", views.term_detail, name="term-detail"),
    path("roots/", views.roots_explorer, name="roots"),
    path("roots/<int:root_id>/", views.root_detail, name="root-detail"),
    path("analyzer/", views.analyzer, name="analyzer"),
    path("favorites/", views.favorites, name="favorites"),
    path("favorites/<slug:slug>/toggle/", views.toggle_favorite, name="toggle-favorite"),
    path("progress/", views.progress_dashboard, name="progress"),
    path("flashcards/", views.flashcards, name="flashcards"),
    path("quizzes/", views.quizzes, name="quizzes"),
    path("quizzes/<int:quiz_id>/", views.quiz_detail, name="quiz-detail"),
    path("api/terms/", api.TermListAPIView.as_view(), name="api-terms"),
    path("api/terms/<slug:slug>/", api.TermDetailAPIView.as_view(), name="api-term-detail"),
    path("api/search/suggestions/", api.SearchSuggestionsAPIView.as_view(), name="api-search-suggestions"),
    path("api/roots/", api.RootListAPIView.as_view(), name="api-roots"),
    path("api/roots/<int:pk>/", api.RootDetailAPIView.as_view(), name="api-root-detail"),
    path("api/subjects/", api.SubjectsAPIView.as_view(), name="api-subjects"),
    path("api/anatomical-systems/", api.AnatomicalSystemsAPIView.as_view(), name="api-anatomical-systems"),
    path("api/analyze/", api.AnalyzerAPIView.as_view(), name="api-analyze"),
    path("api/favorites/", api.FavoriteListCreateAPIView.as_view(), name="api-favorites"),
    path("api/progress/", api.ProgressAPIView.as_view(), name="api-progress"),
    path("api/flashcards/", api.FlashcardListAPIView.as_view(), name="api-flashcards"),
    path("api/flashcards/<int:flashcard_id>/review/", api.FlashcardReviewAPIView.as_view(), name="api-flashcard-review"),
    path("api/quizzes/", api.QuizListAPIView.as_view(), name="api-quizzes"),
    path("api/quiz-attempts/", api.QuizAttemptAPIView.as_view(), name="api-quiz-attempts"),
    path("api/term-of-the-day/", api.TermOfTheDayAPIView.as_view(), name="api-term-of-the-day"),
]
