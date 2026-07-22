from __future__ import annotations

from collections import defaultdict
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.utils import timezone

from .models import Favorite, FlashcardReview, ProgressStatus, Quiz, QuizAttempt, RootEntry, Term, UserTermProgress
from .services import (
    analyze_term_text,
    apply_term_search,
    build_progress_snapshot,
    build_root_queryset,
    build_term_queryset,
    get_medlatin_preview_context,
    get_recent_terms_for_session,
    store_recent_term,
)


def medlatin_home(request: HttpRequest) -> HttpResponse:
    context = get_medlatin_preview_context()
    context["recent_terms"] = get_recent_terms_for_session(request)
    context["featured_subjects"] = [
        "Anatomy",
        "Histology",
        "Embryology",
        "Physiology",
        "Pathology",
        "Radiology",
        "Neurology",
        "Cardiology",
    ]
    context["naming_logic_categories"] = [
        "Shape",
        "Position",
        "Direction",
        "Function",
        "Size",
        "Number",
        "Color",
        "Pathological process",
    ]
    context["disclaimer"] = (
        "MedLatin is an educational terminology platform and does not replace medical textbooks, official anatomical nomenclature, professional instruction, diagnosis, or clinical advice."
    )
    return render(request, "medlatin/home.html", context)


def dictionary_search(request: HttpRequest) -> HttpResponse:
    raw_results = apply_term_search(build_term_queryset(), request.GET)
    results = raw_results if isinstance(raw_results, list) else list(raw_results)
    paginator = Paginator(results, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "page_obj": page_obj,
        "result_count": len(results),
        "subjects": list(Term.objects.exclude(subject="").values_list("subject", flat=True).distinct().order_by("subject")),
        "anatomical_systems": list(
            Term.objects.exclude(anatomical_system="").values_list("anatomical_system", flat=True).distinct().order_by("anatomical_system")
        ),
        "origin_languages": list(
            Term.objects.exclude(origin_language="").values_list("origin_language", flat=True).distinct().order_by("origin_language")
        ),
        "request_get": request.GET,
    }
    return render(request, "medlatin/dictionary.html", context)


def term_detail(request: HttpRequest, slug: str) -> HttpResponse:
    term = get_object_or_404(build_term_queryset(), slug=slug)
    store_recent_term(request, term)

    progress = None
    is_favorited = False
    if request.user.is_authenticated:
        progress, _ = UserTermProgress.objects.get_or_create(user=request.user, term=term)
        progress.last_viewed = timezone.now()
        progress.study_count += 1
        if not progress.status:
            progress.status = ProgressStatus.LEARNING
        progress.save()
        is_favorited = Favorite.objects.filter(user=request.user, term=term).exists()

    translations = {translation.language: translation for translation in term.translations.all()}
    examples_by_context = defaultdict(list)
    for example in term.examples.all():
        examples_by_context[example.context].append(example)

    relationships_by_type = defaultdict(list)
    for relation in term.outgoing_relationships.all():
        relationships_by_type[relation.get_relationship_type_display()].append(relation)

    context = {
        "term": term,
        "translations": translations,
        "examples_by_context": dict(examples_by_context),
        "relationships_by_type": dict(relationships_by_type),
        "progress": progress,
        "is_favorited": is_favorited,
        "related_roots": [link.root for link in term.root_links.all()],
        "recent_terms": get_recent_terms_for_session(request),
        "term_of_day": get_medlatin_preview_context()["medlatin_term_of_day"],
    }
    return render(request, "medlatin/term_detail.html", context)


def roots_explorer(request: HttpRequest) -> HttpResponse:
    roots = build_root_queryset().order_by("form")
    query = (request.GET.get("q") or "").strip()
    if query:
        roots = roots.filter(form__icontains=query) | roots.filter(core_meaning__icontains=query)
    context = {"roots": roots, "request_get": request.GET}
    return render(request, "medlatin/roots.html", context)


def root_detail(request: HttpRequest, root_id: int) -> HttpResponse:
    root = get_object_or_404(build_root_queryset(), pk=root_id)
    related_terms = (
        Term.objects.filter(root_links__root=root)
        .distinct()
        .order_by("latin_name")
    )
    context = {"root": root, "related_terms": related_terms}
    return render(request, "medlatin/root_detail.html", context)


def analyzer(request: HttpRequest) -> HttpResponse:
    query = (request.GET.get("q") or "").strip()
    analysis = analyze_term_text(query) if query else None
    context = {
        "query": query,
        "analysis": analysis,
        "examples": ["sternocleidomastoideus", "gastrocnemius", "endocardium", "pericarditis", "adenocarcinoma"],
    }
    return render(request, "medlatin/analyzer.html", context)


def favorites(request: HttpRequest) -> HttpResponse:
    items = []
    if request.user.is_authenticated:
        items = Favorite.objects.filter(user=request.user).select_related("term").order_by("-created_at")
    return render(request, "medlatin/favorites.html", {"favorites": items})


def toggle_favorite(request: HttpRequest, slug: str) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("medlatin:term-detail", slug=slug)
    term = get_object_or_404(Term, slug=slug)
    favorite = Favorite.objects.filter(user=request.user, term=term)
    if favorite.exists():
        favorite.delete()
    else:
        Favorite.objects.create(user=request.user, term=term)
    next_url = request.POST.get("next") or request.GET.get("next") or request.META.get("HTTP_REFERER") or "medlatin:term-detail"
    if next_url == "medlatin:term-detail":
        return redirect("medlatin:term-detail", slug=slug)
    return redirect(next_url)


def progress_dashboard(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("medlatin:home")
    snapshot = build_progress_snapshot(request.user)
    recent_progress = (
        UserTermProgress.objects.filter(user=request.user)
        .select_related("term")
        .order_by("-updated_at")[:8]
    )
    due_reviews = (
        FlashcardReview.objects.filter(user=request.user, next_review__lte=timezone.now())
        .select_related("flashcard__term")
        .order_by("next_review")[:8]
    )
    quiz_attempts = request.user.medlatin_quiz_attempts.select_related("quiz").order_by("-started_at")[:8]
    context = {
        "snapshot": snapshot,
        "recent_progress": recent_progress,
        "due_reviews": due_reviews,
        "quiz_attempts": quiz_attempts,
    }
    return render(request, "medlatin/progress.html", context)


def flashcards(request: HttpRequest) -> HttpResponse:
    due_reviews = []
    new_cards = Term.objects.filter(flashcards__is_active=True).distinct()[:12]
    if request.user.is_authenticated:
        due_reviews = (
            FlashcardReview.objects.filter(user=request.user, next_review__lte=timezone.now())
            .select_related("flashcard__term")
            .order_by("next_review")
        )
        new_cards = Term.objects.filter(flashcards__is_active=True).exclude(
            flashcards__reviews__user=request.user
        ).distinct()[:12]
    context = {"due_reviews": due_reviews, "new_cards": new_cards}
    return render(request, "medlatin/flashcards.html", context)


def quizzes(request: HttpRequest) -> HttpResponse:
    public_quizzes = Quiz.objects.filter(is_public=True).annotate(question_total=Count("questions")).order_by("title")
    return render(request, "medlatin/quizzes.html", {"quizzes": public_quizzes})


def quiz_detail(request: HttpRequest, quiz_id: int) -> HttpResponse:
    quiz = get_object_or_404(Quiz.objects.prefetch_related("questions__term"), pk=quiz_id)
    result = None
    if request.method == "POST":
        answers = {}
        correct = 0
        total = quiz.questions.count()
        for question in quiz.questions.all():
            answer = request.POST.get(f"question_{question.id}", "").strip()
            answers[str(question.id)] = answer
            expected = question.correct_answer.get("value") if isinstance(question.correct_answer, dict) else question.correct_answer
            if str(answer).strip().lower() == str(expected).strip().lower():
                correct += 1
        accuracy = (correct / total * 100) if total else 0
        result = {"correct": correct, "total": total, "accuracy": round(accuracy, 1), "answers": answers}
        if request.user.is_authenticated:
            QuizAttempt.objects.create(
                user=request.user,
                quiz=quiz,
                score=correct,
                accuracy=accuracy,
                completed_at=timezone.now(),
                answers=answers,
            )
    return render(request, "medlatin/quiz_detail.html", {"quiz": quiz, "result": result})
