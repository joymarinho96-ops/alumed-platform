from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from .models import Course, Module, Lesson, LessonCompletion, Enrollment, EnrollmentHistory, Comment, Like, PaymentHistory, PodcastEpisode

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    autocomplete_fields = ['user']
    readonly_fields = ('enrollment_date', 'expiration_date',)

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'lesson_type', 'video_provider', 'file', 'video_url', 'html_content', 'html_url', 'simulacro_url', 'special_content_url', 'duration_in_minutes', 'order')
    ordering = ('order',)

class PodcastEpisodeInline(admin.TabularInline): # Mudado para TabularInline para ficar mais compacto (estilo lista)
    model = PodcastEpisode
    extra = 1
    fields = ('title', 'audio_url', 'duration', 'order')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "duration_days")
    readonly_fields = ("image_preview",)
    inlines = [ModuleInline] # Removido EnrollmentInline para evitar redundância
    search_fields = ['title']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                f'<img src="{obj.image.url}" style="height:120px;border-radius:6px;border:1px solid #444"/>'
            )
        return "Sem imagem"

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('title', 'course', 'order')
    list_editable = ('order',)
    ordering = ('course', 'order')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "lesson_type", "duration_in_minutes", "order")
    list_editable = ("order",) # Permite editar a ordem diretamente na lista
    list_filter = ('module__course', 'lesson_type')
    search_fields = ('title', 'module__title')
    inlines = [PodcastEpisodeInline] # Adicionado Inline para Podcasts
    ordering = ('module', 'order')

    fieldsets = (
        (None, {
            'fields': ('module', 'title', 'description', 'lesson_type', 'duration_in_minutes', 'order')
        }),
        ('Conteúdo da Aula', {
            'description': "Preencha apenas o campo correspondente ao 'Tipo de Aula' selecionado.",
            'fields': ('file', 'video_provider', 'video_url', 'html_content', 'html_url', 'simulacro_url', 'special_content_url'),
        }),
    )

@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed_at")
    search_fields = ('user__username', 'lesson__title')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'start_date', 'expiration_date', 'access_source', 'is_active', 'is_expired')
    list_filter = ('course', 'access_source', 'is_active', 'enrollment_date', 'expiration_date')
    search_fields = ('user__username', 'course__title', 'internal_notes')
    readonly_fields = ('enrollment_date', 'revoked_at', 'revoked_by', 'created_by')
    list_per_page = 25
    fieldsets = (
        (None, {
            'fields': ('user', 'course', 'start_date', 'expiration_date', 'is_active')
        }),
        ('Información de Acceso y Auditoría', {
            'fields': ('access_source', 'created_by', 'internal_notes')
        }),
        ('Control de Revocaciones', {
            'fields': ('revoked_at', 'revoked_by'),
            'classes': ('collapse',),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['expiration_date'].required = False
        return form

    def save_model(self, request, obj, form, change):
        from django.utils import timezone
        from datetime import timedelta
        
        is_new = not obj.pk
        
        if is_new:
            obj.created_by = request.user
            if not obj.expiration_date:
                days = obj.course.duration_days if obj.course else 30
                obj.expiration_date = obj.start_date + timedelta(days=days)
        
        # Si se desactiva manualmente, registrar revocación
        if change and 'is_active' in form.changed_data and not obj.is_active:
            obj.revoked_by = request.user
            obj.revoked_at = timezone.now()
        elif change and 'is_active' in form.changed_data and obj.is_active:
            # Si se reactiva, limpiar revocación
            obj.revoked_by = None
            obj.revoked_at = None
            
        super().save_model(request, obj, form, change)
        
        # Crear entrada en el historial de auditoría
        action = 'extend' if change else 'create'
        if change and 'is_active' in form.changed_data and not obj.is_active:
            action = 'revoke'
            
        EnrollmentHistory.objects.create(
            enrollment=obj,
            user=obj.user,
            course=obj.course,
            action=action,
            access_source=obj.access_source,
            amount_paid=0.00,
            performed_by=request.user,
            notes=obj.internal_notes or f"Acción realizada vía Django Admin por {request.user.username}."
        )

    @admin.display(boolean=True, description='¿Expirado?')
    def is_expired(self, obj):
        from django.utils import timezone
        return obj.expiration_date < timezone.now()

@admin.register(EnrollmentHistory)
class EnrollmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'action', 'performed_by', 'timestamp')
    readonly_fields = ('enrollment', 'user', 'course', 'action', 'access_source', 'amount_paid', 'performed_by', 'notes', 'timestamp')
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'payment_date', 'amount_paid', 'days_added')
    list_filter = ('course', 'payment_date')
    search_fields = ('user__username', 'course__title')
    readonly_fields = ('payment_date',)
    list_per_page = 25

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'created_at', 'parent')
    list_filter = ('lesson__module__course',)
    search_fields = ('user__username', 'lesson__title', 'text')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'created_at')
    list_filter = ('lesson__module__course',)
    search_fields = ('user__username', 'lesson__title')
