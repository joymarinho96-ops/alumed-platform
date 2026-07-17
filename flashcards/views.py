from django.shortcuts import render, get_object_or_404, redirect

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q

from flashcards.models import Deck, Flashcard, StudentFlashcardProgress, StudyStreak
from flashcards.selectors import get_due_flashcards, get_subject_mastery
from flashcards.services.analytics import get_student_study_analytics
from flashcards.services.study_session import build_daily_session


@login_required
def flashcard_dashboard_view(request):
    """
    Exibe a central inteligente de flashcards (Joy Recall) do aluno.
    Mostra métricas, ofensiva atual e a lista de Decks de estudo.
    """
    student = request.user
    
    # Obtém métricas gerais do aluno
    analytics = get_student_study_analytics(student)
    
    # Obtém maestria agrupada por matéria para os gráficos
    subject_mastery = get_subject_mastery(student)
    
    # Carrega decks disponíveis (públicos ou com progresso do aluno)
    # Mostra a quantidade de cards totais e quantos estão vencidos (due) para o aluno
    decks = Deck.objects.annotate(
        total_cards=Count('flashcards'),
        due_cards_count=Count(
            'flashcards',
            filter=Q(
                flashcards__progress_records__student=student,
                flashcards__progress_records__next_review_at__lte=timezone.now()
            )
        )
    )

    # Verifica racha/ofensiva de estudos
    streak, _ = StudyStreak.objects.get_or_create(student=student)

    context = {
        "analytics": analytics,
        "subject_mastery": subject_mastery,
        "decks": decks,
        "streak": streak,
    }
    return render(request, "flashcards/dashboard.html", context)


@login_required
def deck_detail_view(request, deck_id: int):
    """
    Detalha um deck específico mostrando os cards cadastrados e o progresso do estudante.
    """
    student = request.user
    deck = get_object_or_404(Deck, id=deck_id)
    
    flashcards = deck.flashcards.all()
    total_cards = flashcards.count()
    
    # Progresso do aluno neste deck
    progress_qs = StudentFlashcardProgress.objects.filter(
        student=student,
        flashcard__deck=deck
    )
    
    studied_count = progress_qs.count()
    due_count = progress_qs.filter(next_review_at__lte=timezone.now()).count()
    
    context = {
        "deck": deck,
        "flashcards": flashcards,
        "total_cards": total_cards,
        "studied_count": studied_count,
        "due_count": due_count,
    }
    return render(request, "flashcards/deck_detail.html", context)


@login_required
def flashcard_study_view(request, deck_id: int = None):
    """
    Sessão de estudos ativa (interface de flashcards inteligente).
    Se deck_id for passado, estuda apenas aquele deck.
    Caso contrário, inicia a sessão diária geral com os cards vencidos ordenados por prioridade.
    """
    student = request.user
    
    if deck_id:
        deck = get_object_or_404(Deck, id=deck_id)
        # Seleciona cards do deck. Tenta trazer os vencidos primeiro.
        progress_records = StudentFlashcardProgress.objects.filter(
            student=student,
            flashcard__deck=deck,
            next_review_at__lte=timezone.now()
        ).select_related("flashcard")
        
        cards = [p.flashcard for p in progress_records]
        
        # Se não houver cards vencidos agendados, traz os cards novos/ainda não estudados
        if not cards:
            studied_ids = StudentFlashcardProgress.objects.filter(
                student=student,
                flashcard__deck=deck
            ).values_list("flashcard_id", flat=True)
            
            new_cards = deck.flashcards.exclude(id__in=studied_ids)
            cards = list(new_cards)[:20]
            
            # Se ainda assim não houver nada novo, traz os já estudados ordenados por domínio crescente
            if not cards:
                all_progress = StudentFlashcardProgress.objects.filter(
                    student=student,
                    flashcard__deck=deck
                ).select_related("flashcard").order_by("mastery_score")
                cards = [p.flashcard for p in all_progress][:20]
    else:
        deck = None
        # Carrega a sessão de estudos personalizada do dia baseada no seletor ordenado por prioridade!
        due_progress = build_daily_session(student, limit=30)
        cards = [p.flashcard for p in due_progress]

    context = {
        "deck": deck,
        "cards": cards,
        "total_count": len(cards),
    }
    return render(request, "flashcards/study.html", context)
