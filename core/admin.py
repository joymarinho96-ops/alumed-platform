from django.contrib import admin
from .models import Announcement, Event, LibraryResource, Product, Popup, Testimonial, TestimonialVideo, DigitalBook
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content')
    actions = ['delete_old_announcements']

    def delete_old_announcements(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} avisos foram deletados.")
    delete_old_announcements.short_description = "Deletar avisos selecionados"

@admin.register(Popup)
class PopupAdmin(admin.ModelAdmin):
    list_display = ('message', 'is_active')
    list_editable = ('is_active',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'event_type')
    list_filter = ('event_type', 'start_date')
    search_fields = ('title',)
    actions = ['delete_past_events']

    def delete_past_events(self, request, queryset):
        """Deleta eventos selecionados."""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} eventos foram deletados.")
    delete_past_events.short_description = "Deletar eventos selecionados"

    change_list_template = "admin/core/event/change_list.html"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('cleanup-past-events/', self.admin_site.admin_view(self.cleanup_past_events_view), name='event_cleanup'),
            path('delete-all-events/', self.admin_site.admin_view(self.delete_all_events_view), name='event_delete_all'),
        ]
        return custom_urls + urls

    def cleanup_past_events_view(self, request):
        from django.shortcuts import redirect
        from django.contrib import messages
        today = timezone.now().date()
        deleted_count, _ = Event.objects.filter(end_date__lt=today).delete()
        self.message_user(request, f"Calendário limpo: {deleted_count} eventos passados removidos.", level=messages.SUCCESS)
        return redirect('admin:core_event_changelist')

    def delete_all_events_view(self, request):
        from django.shortcuts import redirect
        from django.contrib import messages
        # Deleta TODOS os eventos
        deleted_count, _ = Event.objects.all().delete()
        self.message_user(request, f"Calendário ZERADO: {deleted_count} eventos foram removidos permanentemente.", level=messages.WARNING)
        return redirect('admin:core_event_changelist')

@admin.register(LibraryResource)
class LibraryResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'image_preview')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                f'<img src="{obj.image.url}" style="height:60px;border-radius:4px;"/>'
            )
        return "Sin imagen"
    image_preview.short_description = "Vista Previa"

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'created_at')
    search_fields = ('name', 'text')

@admin.register(TestimonialVideo)
class TestimonialVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)


@admin.register(DigitalBook)
class DigitalBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'year', 'category', 'created_at')
    list_filter = ('subject', 'year', 'category')
    search_fields = ('title', 'description', 'tags')

