from __future__ import annotations

import difflib
import unicodedata
from datetime import timedelta
from typing import Any

from django.db.models import Avg, Count, Prefetch, Q
from django.utils import timezone

from .models import (
    Favorite,
    FlashcardRating,
    FlashcardReview,
    Relationship,
    RootEntry,
    Term,
    TermRootLink,
    Translation,
    UserTermProgress,
    WordPart,
)


SEARCH_RESULT_LIMIT = 200


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    return "".join(char for char in normalized if not unicodedata.combining(char)).lower().strip()


def build_term_queryset():
    return (
        Term.objects.all()
        .prefetch_related(
            "translations",
            "word_parts",
            "examples",
            "flashcards",
            Prefetch("root_links", queryset=TermRootLink.objects.select_related("root")),
            Prefetch("outgoing_relationships", queryset=Relationship.objects.select_related("target_term")),
        )
    )


def build_root_queryset():
    return RootEntry.objects.annotate(term_total=Count("term_links", distinct=True))


def get_term_of_the_day():
    terms = list(build_term_queryset().order_by("latin_name"))
    if not terms:
        return None
    today = timezone.localdate()
    return terms[today.toordinal() % len(terms)]


def get_medlatin_preview_context() -> dict[str, Any]:
    return {
        "medlatin_term_of_day": get_term_of_the_day(),
        "medlatin_featured_terms": list(build_term_queryset().order_by("latin_name")[:4]),
        "medlatin_popular_roots": list(build_root_queryset().order_by("-term_total", "form")[:6]),
        "medlatin_term_count": Term.objects.count(),
        "medlatin_root_count": RootEntry.objects.count(),
    }


def score_term(term: Term, query: str) -> int:
    norm_query = normalize_text(query)
    haystacks = [
        term.latin_name,
        term.standard_term,
        term.literal_translation,
        term.medical_definition,
        term.subject,
        term.specialty,
        term.anatomical_system,
        term.origin_language,
        term.naming_category,
        term.term_type,
    ]
    haystacks.extend(part.form for part in term.word_parts.all())
    haystacks.extend(trans.text for trans in term.translations.all())

    best = 0
    for haystack in filter(None, haystacks):
        norm_haystack = normalize_text(haystack)
        if norm_haystack == norm_query:
            best = max(best, 400)
        elif norm_haystack.startswith(norm_query):
            best = max(best, 270)
        elif norm_query in norm_haystack:
            best = max(best, 200)
        best = max(best, int(difflib.SequenceMatcher(a=norm_query, b=norm_haystack).ratio() * 100))
    return best


def apply_term_search(queryset, params: dict[str, Any]):
    query = (params.get("q") or "").strip()
    if query:
        db_filter = (
            Q(latin_name__icontains=query)
            | Q(standard_term__icontains=query)
            | Q(literal_translation__icontains=query)
            | Q(medical_definition__icontains=query)
            | Q(subject__icontains=query)
            | Q(specialty__icontains=query)
            | Q(anatomical_system__icontains=query)
            | Q(origin_language__icontains=query)
            | Q(word_parts__form__icontains=query)
            | Q(word_parts__meaning__icontains=query)
            | Q(root_links__root__form__icontains=query)
            | Q(root_links__root__core_meaning__icontains=query)
            | Q(translations__text__icontains=query)
        )
        results = list(queryset.filter(db_filter).distinct()[:SEARCH_RESULT_LIMIT])
        if len(results) < 12:
            fallback = list(build_term_queryset().order_by("latin_name")[:SEARCH_RESULT_LIMIT])
            seen_ids = {term.id for term in results}
            for term in fallback:
                if term.id in seen_ids:
                    continue
                if score_term(term, query) >= 72:
                    results.append(term)
        results.sort(key=lambda item: (-score_term(item, query), item.latin_name.lower()))
        return results

    subject = (params.get("subject") or "").strip()
    if subject:
        queryset = queryset.filter(subject__iexact=subject)

    anatomical_system = (params.get("anatomical_system") or "").strip()
    if anatomical_system:
        queryset = queryset.filter(anatomical_system__iexact=anatomical_system)

    origin_language = (params.get("origin_language") or "").strip()
    if origin_language:
        queryset = queryset.filter(origin_language__iexact=origin_language)

    grammatical_class = (params.get("grammatical_class") or "").strip()
    if grammatical_class:
        queryset = queryset.filter(grammatical_class__iexact=grammatical_class)

    term_type = (params.get("term_type") or "").strip()
    if term_type:
        queryset = queryset.filter(term_type__iexact=term_type)

    naming_category = (params.get("naming_category") or "").strip()
    if naming_category:
        queryset = queryset.filter(naming_category__iexact=naming_category)

    gender = (params.get("gender") or "").strip()
    if gender:
        queryset = queryset.filter(gender__iexact=gender)

    declension = (params.get("declension") or "").strip()
    if declension:
        queryset = queryset.filter(declension__iexact=declension)

    difficulty = (params.get("difficulty") or "").strip()
    if difficulty.isdigit():
        queryset = queryset.filter(difficulty=int(difficulty))

    ordering = (params.get("ordering") or "alphabetical").strip()
    if ordering == "most_studied":
        queryset = queryset.annotate(studied_total=Count("progress_records", distinct=True)).order_by("-studied_total", "latin_name")
    elif ordering == "most_favorited":
        queryset = queryset.annotate(favorite_total=Count("favorites", distinct=True)).order_by("-favorite_total", "latin_name")
    elif ordering == "recently_added":
        queryset = queryset.order_by("-created_at", "latin_name")
    elif ordering == "difficulty":
        queryset = queryset.order_by("difficulty", "latin_name")
    else:
        queryset = queryset.order_by("latin_name")
    return queryset


def get_search_suggestions(query: str, limit: int = 8) -> list[dict[str, Any]]:
    if not query.strip():
        return []
    terms = list(build_term_queryset().order_by("latin_name")[:SEARCH_RESULT_LIMIT])
    suggestions = []
    for term in terms:
        score = score_term(term, query)
        if score < 75:
            continue
        suggestions.append(
            {
                "slug": term.slug,
                "latin_name": term.latin_name,
                "literal_translation": term.literal_translation,
                "subject": term.subject,
                "score": score,
            }
        )
    suggestions.sort(key=lambda item: (-item["score"], item["latin_name"].lower()))
    return suggestions[:limit]


def get_recent_terms_for_session(request, limit: int = 4):
    recent_slugs = request.session.get("medlatin_recent_terms", [])
    if not recent_slugs:
        return []
    queryset = build_term_queryset().filter(slug__in=recent_slugs)
    term_map = {term.slug: term for term in queryset}
    return [term_map[slug] for slug in recent_slugs if slug in term_map][:limit]


def store_recent_term(request, term: Term) -> None:
    recent_slugs = request.session.get("medlatin_recent_terms", [])
    recent_slugs = [slug for slug in recent_slugs if slug != term.slug]
    recent_slugs.insert(0, term.slug)
    request.session["medlatin_recent_terms"] = recent_slugs[:8]
    request.session.modified = True


def analyze_term_text(raw_term: str) -> dict[str, Any]:
    query = (raw_term or "").strip()
    if not query:
        return {
            "query": "",
            "confidence": "uncertain",
            "parts": [],
            "warning": "Type a medical term to analyze it.",
            "related_terms": [],
        }

    exact_term = (
        build_term_queryset()
        .filter(Q(latin_name__iexact=query) | Q(standard_term__iexact=query) | Q(translations__text__iexact=query))
        .distinct()
        .first()
    )
    if exact_term:
        root_ids = [link.root_id for link in exact_term.root_links.all()]
        related_terms = (
            Term.objects.filter(root_links__root_id__in=root_ids)
            .exclude(pk=exact_term.pk)
            .distinct()
            .order_by("latin_name")[:6]
        )
        return {
            "query": query,
            "confidence": "high",
            "parts": [
                {
                    "form": part.form,
                    "part_type": part.get_part_type_display(),
                    "meaning": part.meaning,
                    "origin_language": part.origin_language,
                    "confidence": float(part.confidence),
                }
                for part in exact_term.word_parts.all()
            ],
            "literal_construction": exact_term.literal_translation,
            "possible_meaning": exact_term.medical_definition,
            "warning": "Exact entry found. This decomposition comes from the MedLatin dataset.",
            "matched_term": exact_term,
            "related_terms": list(related_terms),
        }

    normalized = normalize_text(query).replace(" ", "").replace("-", "")
    roots = list(build_root_queryset())
    prefix_matches = []
    suffix_matches = []
    internal_matches = []

    for root in roots:
        form = root.normalized_form.replace("-", "")
        if not form or len(form) < 2:
            continue
        if normalized.startswith(form):
            prefix_matches.append(root)
        elif normalized.endswith(form):
            suffix_matches.append(root)
        elif form in normalized:
            internal_matches.append(root)

    prefix_matches.sort(key=lambda item: len(item.normalized_form), reverse=True)
    suffix_matches.sort(key=lambda item: len(item.normalized_form), reverse=True)
    internal_matches.sort(key=lambda item: len(item.normalized_form), reverse=True)

    selected = []
    seen_ids = set()
    for collection in (prefix_matches[:2], internal_matches[:3], suffix_matches[:2]):
        for root in collection:
            if root.id in seen_ids:
                continue
            seen_ids.add(root.id)
            selected.append(root)

    if not selected:
        return {
            "query": query,
            "confidence": "uncertain",
            "parts": [],
            "warning": "No reliable decomposition was found in the current root bank. Expert review is recommended.",
            "related_terms": [],
        }

    related_terms = (
        Term.objects.filter(root_links__root__in=selected)
        .distinct()
        .order_by("latin_name")[:8]
    )
    meanings = " + ".join(root.core_meaning for root in selected)
    return {
        "query": query,
        "confidence": "moderate" if len(selected) >= 2 else "uncertain",
        "parts": [
            {
                "form": root.form,
                "part_type": root.get_root_type_display(),
                "meaning": root.core_meaning,
                "origin_language": root.origin_language,
                "confidence": 0.68 if index == 0 else 0.58,
            }
            for index, root in enumerate(selected)
        ],
        "literal_construction": meanings,
        "possible_meaning": f"Possible semantic field: {meanings}.",
        "warning": "Automated decomposition based on attested roots. Expert review is recommended for disputed analyses.",
        "related_terms": list(related_terms),
    }


def update_flashcard_review(review: FlashcardReview, rating: str) -> FlashcardReview:
    now = timezone.now()
    ease_factor = float(review.ease_factor)
    interval = int(review.interval or 0)

    if rating == FlashcardRating.AGAIN:
        interval = 1
        ease_factor = max(1.30, ease_factor - 0.25)
        review.mistake_count += 1
    elif rating == FlashcardRating.HARD:
        interval = 2 if interval < 2 else max(2, round(interval * 1.2))
        ease_factor = max(1.30, ease_factor - 0.15)
    elif rating == FlashcardRating.EASY:
        interval = 4 if review.review_count < 2 else max(4, round(interval * (ease_factor + 0.25)))
        ease_factor += 0.15
    else:
        if review.review_count == 0:
            interval = 1
        elif review.review_count == 1:
            interval = 3
        else:
            interval = max(3, round(interval * ease_factor))

    review.rating = rating
    review.review_count += 1
    review.interval = interval
    review.ease_factor = round(ease_factor, 2)
    review.next_review = now + timedelta(days=interval)
    review.reviewed_at = now
    review.save()
    return review


def build_progress_snapshot(user) -> dict[str, Any]:
    progress_qs = UserTermProgress.objects.filter(user=user).select_related("term")
    mastered = progress_qs.filter(status="mastered").count()
    learning = progress_qs.filter(status="learning").count()
    due_reviews = FlashcardReview.objects.filter(user=user, next_review__lte=timezone.now()).count()
    avg_accuracy = user.medlatin_quiz_attempts.aggregate(avg=Avg("accuracy"))["avg"] or 0
    return {
        "terms_studied": progress_qs.count(),
        "terms_mastered": mastered,
        "terms_learning": learning,
        "flashcards_due": due_reviews,
        "flashcard_reviews_total": FlashcardReview.objects.filter(user=user).count(),
        "quiz_accuracy": round(float(avg_accuracy), 1),
        "favorite_total": Favorite.objects.filter(user=user).count(),
    }
