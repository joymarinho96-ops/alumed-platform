from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('flashcards/', views.flashcards_dashboard, name='flashcards_dashboard'),
    path('flashcards/all/', views.deck_list, name='deck_list'), # Nova URL para ver todos
    path('flashcards/create-deck/', views.create_deck, name='create_deck'),
    path('flashcards/<int:deck_id>/', views.deck_detail, name='deck_detail'),
    path('flashcards/<int:deck_id>/delete/', views.delete_deck, name='delete_deck'),
    path('flashcards/<int:deck_id>/create-card/', views.create_flashcard, name='create_flashcard'),
    path('flashcards/card/<int:card_id>/delete/', views.delete_flashcard, name='delete_flashcard'),
    path('flashcards/<int:deck_id>/study/', views.study_deck, name='study_deck'),
    path('<int:course_id>/', views.course_dashboard, name='course_dashboard'),
    path('mark-lesson-complete/<int:lesson_id>/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('get_video_url/<int:lesson_id>/', views.get_video_url, name='get_video_url'),
    path('lesson/<int:lesson_id>/stream/', views.stream_media, name='stream_media'),
    path('lesson/<int:lesson_id>/comments/', views.lesson_comments, name='lesson_comments'),
    path('lesson/<int:lesson_id>/like/', views.toggle_like, name='toggle_like'),
]
