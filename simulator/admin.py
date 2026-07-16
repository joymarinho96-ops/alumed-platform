import csv
import io
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import render
from .models import Subject, Topic, Question, Alternative, SimSession, UserAnswer


# ─── Inlines ─────────────────────────────────────────────────────────────────

class AlternativeInline(admin.TabularInline):
    model = Alternative
    extra = 4
    fields = ('text', 'is_correct', 'order')


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 2
    fields = ('name', 'active', 'order')


# ─── Subject ─────────────────────────────────────────────────────────────────

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display   = ('emoji', 'name', 'year', 'color', 'question_count', 'active', 'order')
    list_editable  = ('active', 'order')
    list_filter    = ('year', 'active')
    search_fields  = ('name',)
    inlines        = [TopicInline]

    def question_count(self, obj):
        return obj.questions.filter(active=True).count()
    question_count.short_description = 'Preguntas'


# ─── Topic ───────────────────────────────────────────────────────────────────

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display  = ('name', 'subject', 'active', 'order')
    list_editable = ('active', 'order')
    list_filter   = ('subject', 'active')
    search_fields = ('name',)


# ─── Question ────────────────────────────────────────────────────────────────

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display   = ('short_statement', 'subject', 'topic', 'q_type', 'difficulty', 'source', 'active')
    list_editable  = ('active',)
    list_filter    = ('subject', 'q_type', 'difficulty', 'source', 'active')
    search_fields  = ('statement', 'tags')
    inlines        = [AlternativeInline]
    readonly_fields = ('created_at',)
    change_list_template = 'admin/simulator/question/change_list.html'

    def short_statement(self, obj):
        return obj.statement[:80] + '…' if len(obj.statement) > 80 else obj.statement
    short_statement.short_description = 'Enunciado'

    def get_urls(self):
        urls = super().get_urls()
        custom = [path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name='simulator_question_import_csv')]
        return custom + urls

    def import_csv_view(self, request):
        """
        CSV format expected:
        subject,topic,q_type,difficulty,year,statement,explanation,tags,source,
        alt1,alt1_correct,alt2,alt2_correct,alt3,alt3_correct,alt4,alt4_correct,alt5,alt5_correct
        """
        if request.method == 'POST' and request.FILES.get('csv_file'):
            csv_file = request.FILES['csv_file']
            decoded  = csv_file.read().decode('utf-8-sig')
            reader   = csv.DictReader(io.StringIO(decoded))
            created  = 0
            errors   = []
            for i, row in enumerate(reader, start=2):
                try:
                    subj, _ = Subject.objects.get_or_create(
                        name=row['subject'].strip(),
                        defaults={'year': int(row.get('year_subject', 1) or 1)}
                    )
                    topic_obj = None
                    if row.get('topic', '').strip():
                        topic_obj, _ = Topic.objects.get_or_create(
                            subject=subj, name=row['topic'].strip()
                        )
                    q = Question.objects.create(
                        subject=subj, topic=topic_obj,
                        q_type=row.get('q_type', 'choice').strip() or 'choice',
                        difficulty=row.get('difficulty', 'medium').strip() or 'medium',
                        year=int(row['year']) if row.get('year', '').strip() else None,
                        statement=row['statement'].strip(),
                        explanation=row.get('explanation', '').strip(),
                        tags=row.get('tags', '').strip(),
                        source=row.get('source', 'alumed').strip() or 'alumed',
                    )
                    for n in range(1, 6):
                        txt = row.get(f'alt{n}', '').strip()
                        if txt:
                            Alternative.objects.create(
                                question=q, text=txt,
                                is_correct=str(row.get(f'alt{n}_correct', '')).strip().lower() in ('1','true','si','yes'),
                                order=n
                            )
                    created += 1
                except Exception as e:
                    errors.append(f'Fila {i}: {e}')
            if errors:
                self.message_user(request, f'{created} preguntas importadas. Errores: {"; ".join(errors[:5])}', messages.WARNING)
            else:
                self.message_user(request, f'✅ {created} preguntas importadas correctamente.', messages.SUCCESS)
            return HttpResponseRedirect(reverse('admin:simulator_question_changelist'))
        return render(request, 'admin/simulator/question/import_csv.html')


# ─── Alternative ─────────────────────────────────────────────────────────────

@admin.register(Alternative)
class AlternativeAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'question', 'is_correct', 'order')
    list_filter  = ('is_correct',)

    def short_text(self, obj):
        return obj.text[:60]
    short_text.short_description = 'Texto'


# ─── SimSession ───────────────────────────────────────────────────────────────

@admin.register(SimSession)
class SimSessionAdmin(admin.ModelAdmin):
    list_display  = ('user', 'mode', 'subject', 'score_display', 'total_q', 'status', 'started_at')
    list_filter   = ('mode', 'status', 'subject')
    search_fields = ('user__username',)
    readonly_fields = ('started_at', 'finished_at', 'score', 'correct', 'total_q', 'duration_s')

    def score_display(self, obj):
        color = '#10b981' if obj.score >= 60 else '#ef4444'
        return format_html('<span style="color:{};font-weight:700;">{:.0f}%</span>', color, obj.score)
    score_display.short_description = '% Acierto'


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('session', 'question', 'is_correct', 'time_spent_s')
    list_filter  = ('is_correct',)
