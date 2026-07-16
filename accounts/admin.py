from django.contrib import admin
from .models import (Profile, ChatMessage, AccessProduct, UserAccess,
                     ConectaPreference, ConectaSubscription, ConectaConsentEvent)
from django.utils import timezone
from datetime import timedelta

@admin.register(ConectaPreference)
class ConectaPreferenceAdmin(admin.ModelAdmin):
    list_display    = ('user','whatsapp_number','alert_email',
                       'whatsapp_active','email_active','calendar_active',
                       'consent_granted','updated_at')
    list_filter     = ('whatsapp_active','email_active','calendar_active','consent_granted')
    search_fields   = ('user__username','user__email','whatsapp_number','alert_email')
    readonly_fields = ('consent_at','consent_version','consent_channels','updated_at')

@admin.register(ConectaSubscription)
class ConectaSubscriptionAdmin(admin.ModelAdmin):
    list_display  = ('user','type','key','enabled','updated_at')
    list_filter   = ('type','enabled')
    search_fields = ('user__username','key')

@admin.register(ConectaConsentEvent)
class ConectaConsentEventAdmin(admin.ModelAdmin):
    list_display  = ('user','action','version','channels','whatsapp','email','ip_address','created_at')
    list_filter   = ('action','version')
    search_fields = ('user__username','email','whatsapp')
    readonly_fields = ('user','action','version','channels','whatsapp','email',
                       'ip_address','user_agent','created_at')
    # Inmutable — sin botón add ni delete
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo')
    search_fields = ('user__username', 'user__email')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'is_read')
    list_filter = ('timestamp', 'is_read')
    search_fields = ('content', 'sender__username', 'receiver__username')
    actions = ['delete_old_messages']

    def delete_old_messages(self, request, queryset):
        """Ação para deletar mensagens com mais de 30 dias (ou outro período)"""
        # Exemplo: deletar mensagens selecionadas que são mais antigas que 30 dias
        # Se quiser deletar TODAS as antigas independente da seleção, a lógica seria diferente.
        # Aqui, vamos deletar as selecionadas.
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} mensagens foram deletadas com sucesso.")
    delete_old_messages.short_description = "Deletar mensagens selecionadas"

    # Se quiser um botão global para limpar histórico antigo:
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('cleanup-history/', self.admin_site.admin_view(self.cleanup_history_view), name='chatmessage_cleanup'),
        ]
        return custom_urls + urls

    def cleanup_history_view(self, request):
        from django.shortcuts import redirect
        from django.contrib import messages
        # Deleta mensagens com mais de 30 dias
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_count, _ = ChatMessage.objects.filter(timestamp__lt=cutoff_date).delete()
        self.message_user(request, f"Histórico limpo: {deleted_count} mensagens antigas removidas.", level=messages.SUCCESS)
        return redirect('admin:accounts_chatmessage_changelist')

    change_list_template = "admin/accounts/chatmessage/change_list.html"


@admin.register(AccessProduct)
class AccessProductAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('slug', 'name')


@admin.register(UserAccess)
class UserAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'is_active', 'source', 'granted_at', 'expires_at')
    list_filter = ('is_active', 'source', 'product')
    search_fields = ('user__username', 'user__email', 'product__slug')
    raw_id_fields = ('user',)
    date_hierarchy = 'granted_at'
