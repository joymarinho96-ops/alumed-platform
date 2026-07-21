from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from medlatin.models import (
    Flashcard,
    MedicalExample,
    Quiz,
    QuizQuestion,
    Relationship,
    RootEntry,
    Term,
    TermRootLink,
    Translation,
    WordPart,
)
from medlatin.seed_data import ROOT_LIBRARY, SEED_QUIZZES, SEED_TERMS
from medlatin.services import normalize_text


class Command(BaseCommand):
    help = "Load the initial MedLatin dictionary dataset."

    @transaction.atomic
    def handle(self, *args, **options):
        root_map = {}
        for item in ROOT_LIBRARY:
            root, _ = RootEntry.objects.update_or_create(
                normalized_form=normalize_text(item["form"]).replace("-", ""),
                root_type=item["root_type"],
                defaults={
                    "form": item["form"],
                    "origin_language": item["origin_language"],
                    "original_script": item.get("original_script", ""),
                    "core_meaning": item["core_meaning"],
                    "explanation": item.get("explanation", ""),
                    "mnemonic": item.get("mnemonic", ""),
                    "variants": item.get("variants", ""),
                    "common_combinations": item.get("common_combinations", ""),
                    "subjects": item.get("subjects", ""),
                },
            )
            root_map[(root.normalized_form, root.root_type)] = root

        term_map = {}
        pending_relationships = []
        for item in SEED_TERMS:
            term, _ = Term.objects.update_or_create(
                latin_name=item["latin_name"],
                defaults={
                    key: value
                    for key, value in item.items()
                    if key
                    not in {"translations", "word_parts", "examples", "relationships"}
                },
            )
            term_map[item["latin_name"]] = term

            Translation.objects.filter(term=term).delete()
            for trans in item["translations"]:
                Translation.objects.create(term=term, **trans)

            WordPart.objects.filter(term=term).delete()
            for index, part in enumerate(item["word_parts"], start=1):
                WordPart.objects.create(term=term, display_order=index, confidence=1, **part)

            MedicalExample.objects.filter(term=term).delete()
            for sample in item.get("examples", []):
                MedicalExample.objects.create(term=term, **sample)

            pending_relationships.extend(
                (term.latin_name, target_name, relation_type, description)
                for target_name, relation_type, description in item.get("relationships", [])
            )

        TermRootLink.objects.all().delete()
        for term in Term.objects.prefetch_related("word_parts"):
            order = 1
            for part in term.word_parts.all():
                normalized_part = normalize_text(part.form).replace("-", "")
                root = self._match_root(root_map, normalized_part)
                if not root:
                    continue
                TermRootLink.objects.get_or_create(term=term, root=root, defaults={"display_order": order})
                order += 1

        Relationship.objects.all().delete()
        for source_name, target_name, relation_type, description in pending_relationships:
            source_term = term_map.get(source_name)
            target_term = term_map.get(target_name)
            if not source_term or not target_term:
                continue
            Relationship.objects.create(
                source_term=source_term,
                target_term=target_term,
                relationship_type=relation_type,
                description=description,
            )

        Flashcard.objects.all().delete()
        for term in Term.objects.prefetch_related("word_parts"):
            Flashcard.objects.create(
                term=term,
                card_type="term_to_meaning",
                question=f"What does '{term.latin_name}' mean in medical context?",
                answer=term.medical_definition,
                explanation=term.literal_translation,
            )
            if term.word_parts.count() > 1:
                decomposition = "; ".join(f"{item.form} = {item.meaning}" for item in term.word_parts.all())
                Flashcard.objects.create(
                    term=term,
                    card_type="term_to_decomposition",
                    question=f"Break down the term '{term.latin_name}'.",
                    answer=decomposition,
                    explanation=term.naming_logic,
                )

        Quiz.objects.all().delete()
        for quiz_data in SEED_QUIZZES:
            quiz = Quiz.objects.create(
                title=quiz_data["title"],
                subject=quiz_data["subject"],
                difficulty=quiz_data["difficulty"],
                description=quiz_data.get("description", ""),
                is_public=True,
            )
            for index, question_data in enumerate(quiz_data["questions"], start=1):
                term = term_map.get(question_data.get("term_slug", ""))
                QuizQuestion.objects.create(
                    quiz=quiz,
                    question_type=question_data["question_type"],
                    prompt=question_data["prompt"],
                    options=question_data.get("options", []),
                    correct_answer=question_data["correct_answer"],
                    explanation=question_data.get("explanation", ""),
                    term=term,
                    display_order=index,
                )

        self.stdout.write(self.style.SUCCESS(f"Seeded MedLatin with {Term.objects.count()} terms, {RootEntry.objects.count()} roots, and {Flashcard.objects.count()} flashcards."))

    def _match_root(self, root_map, normalized_part):
        exact = root_map.get((normalized_part, "root")) or root_map.get((normalized_part, "prefix")) or root_map.get((normalized_part, "suffix")) or root_map.get((normalized_part, "combining_form")) or root_map.get((normalized_part, "preposition"))
        if exact:
            return exact
        for key, root in root_map.items():
            root_form = key[0]
            if normalized_part.startswith(root_form) or root_form.startswith(normalized_part):
                return root
        return None
