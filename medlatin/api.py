from __future__ import annotations

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Favorite, Flashcard, FlashcardReview, Quiz, QuizAttempt, RootEntry, Term, UserTermProgress
from .serializers import (
    FavoriteSerializer,
    FlashcardReviewSerializer,
    FlashcardSerializer,
    QuizAttemptSerializer,
    QuizSerializer,
    RootEntrySerializer,
    TermDetailSerializer,
    TermListSerializer,
    UserTermProgressSerializer,
)
from .services import (
    analyze_term_text,
    apply_term_search,
    build_progress_snapshot,
    build_root_queryset,
    build_term_queryset,
    get_search_suggestions,
    get_term_of_the_day,
    update_flashcard_review,
)


class MedLatinPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class TermListAPIView(generics.ListAPIView):
    serializer_class = TermListSerializer
    pagination_class = MedLatinPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        result = apply_term_search(build_term_queryset(), self.request.query_params)
        if isinstance(result, list):
            ids = [term.id for term in result]
            preserved = {term.id: index for index, term in enumerate(result)}
            queryset = list(build_term_queryset().filter(id__in=ids))
            queryset.sort(key=lambda item: preserved[item.id])
            return queryset
        return result


class TermDetailAPIView(generics.RetrieveAPIView):
    serializer_class = TermDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return build_term_queryset()


class SearchSuggestionsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get("q", "")
        return Response({"results": get_search_suggestions(query)})


class RootListAPIView(generics.ListAPIView):
    serializer_class = RootEntrySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = MedLatinPagination

    def get_queryset(self):
        queryset = build_root_queryset().order_by("form")
        query = (self.request.query_params.get("q") or "").strip()
        if query:
            queryset = queryset.filter(form__icontains=query) | queryset.filter(core_meaning__icontains=query)
        return queryset


class RootDetailAPIView(generics.RetrieveAPIView):
    serializer_class = RootEntrySerializer
    permission_classes = [permissions.AllowAny]
    queryset = build_root_queryset()


class SubjectsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        subjects = list(Term.objects.exclude(subject="").values_list("subject", flat=True).distinct().order_by("subject"))
        return Response({"results": subjects})


class AnatomicalSystemsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        systems = list(
            Term.objects.exclude(anatomical_system="").values_list("anatomical_system", flat=True).distinct().order_by("anatomical_system")
        )
        return Response({"results": systems})


class AnalyzerAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(analyze_term_text(request.query_params.get("q", "")))


class FavoriteListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Favorite.objects.filter(user=request.user).select_related("term")
        return Response(FavoriteSerializer(queryset, many=True, context={"request": request}).data)

    def post(self, request):
        slug = request.data.get("slug")
        term = get_object_or_404(Term, slug=slug)
        favorite, created = Favorite.objects.get_or_create(user=request.user, term=term)
        if not created:
            favorite.delete()
            return Response({"favorited": False}, status=status.HTTP_200_OK)
        return Response({"favorited": True}, status=status.HTTP_201_CREATED)


class ProgressAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = UserTermProgress.objects.filter(user=request.user).select_related("term")
        return Response(
            {
                "snapshot": build_progress_snapshot(request.user),
                "records": UserTermProgressSerializer(queryset, many=True, context={"request": request}).data,
            }
        )

    def post(self, request):
        slug = request.data.get("slug")
        term = get_object_or_404(Term, slug=slug)
        progress, _ = UserTermProgress.objects.get_or_create(user=request.user, term=term)
        progress.status = request.data.get("status", progress.status)
        progress.private_notes = request.data.get("private_notes", progress.private_notes)
        progress.last_viewed = timezone.now()
        progress.study_count += 1
        progress.save()
        return Response(UserTermProgressSerializer(progress, context={"request": request}).data)


class FlashcardListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        due_only = request.query_params.get("due") == "1"
        queryset = Flashcard.objects.filter(is_active=True).select_related("term")
        if due_only:
            queryset = queryset.filter(reviews__user=request.user, reviews__next_review__lte=timezone.now()).distinct()
        return Response(FlashcardSerializer(queryset, many=True).data)


class FlashcardReviewAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, flashcard_id: int):
        flashcard = get_object_or_404(Flashcard, pk=flashcard_id)
        review, _ = FlashcardReview.objects.get_or_create(user=request.user, flashcard=flashcard)
        review = update_flashcard_review(review, request.data.get("rating", "good"))
        return Response(FlashcardReviewSerializer(review).data)


class QuizListAPIView(generics.ListAPIView):
    serializer_class = QuizSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Quiz.objects.filter(is_public=True).prefetch_related("questions")
        subject = (self.request.query_params.get("subject") or "").strip()
        if subject:
            queryset = queryset.filter(subject__iexact=subject)
        difficulty = (self.request.query_params.get("difficulty") or "").strip()
        if difficulty.isdigit():
            queryset = queryset.filter(difficulty=int(difficulty))
        return queryset.order_by("title")


class QuizAttemptAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = QuizAttempt.objects.filter(user=request.user).select_related("quiz")
        return Response(QuizAttemptSerializer(queryset, many=True).data)

    def post(self, request):
        quiz = get_object_or_404(Quiz.objects.prefetch_related("questions"), pk=request.data.get("quiz_id"))
        answers = request.data.get("answers", {})
        correct = 0
        total = quiz.questions.count()
        for question in quiz.questions.all():
            submitted = str(answers.get(str(question.id), "")).strip().lower()
            expected = question.correct_answer.get("value") if isinstance(question.correct_answer, dict) else question.correct_answer
            if submitted == str(expected).strip().lower():
                correct += 1
        accuracy = (correct / total * 100) if total else 0
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=correct,
            accuracy=accuracy,
            completed_at=timezone.now(),
            answers=answers,
        )
        return Response(QuizAttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)


class TermOfTheDayAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        term = get_term_of_the_day()
        if not term:
            return Response({"detail": "No terms available."}, status=status.HTTP_404_NOT_FOUND)
        return Response(TermDetailSerializer(term, context={"request": request}).data)
