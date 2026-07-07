from .models import ChatMessage

def unread_messages(request):
    if request.user.is_authenticated:
        count = ChatMessage.objects.filter(receiver=request.user, is_read=False).count()
        return {'unread_messages_count': count}
    return {'unread_messages_count': 0}

def wix_urls(request):
    return {
        'WIX_URLS': {
            'registrarme': 'https://alumed.wixsite.com/alumed/registro',
            'iniciar_sesion': 'https://alumed.wixsite.com/alumed/login',
            'comprar_curso': 'https://alumed.wixsite.com/alumed/cursos',
            'comprar_intensivo': 'https://alumed.wixsite.com/alumed/intensivos',
            'ver_curso': 'https://alumed.wixsite.com/alumed/aula',
            'continuar_cursando': 'https://alumed.wixsite.com/alumed/aula',
            'mi_panel': 'https://alumed.wixsite.com/alumed/mi-panel',
            'mis_clases': 'https://alumed.wixsite.com/alumed/mis-clases',
            'pagar_cuota': 'https://alumed.wixsite.com/alumed/pagos',
            'checkout': 'https://alumed.wixsite.com/alumed/checkout',
            'renovar_acceso': 'https://alumed.wixsite.com/alumed/renovacion',
            'mi_biblioteca_adquirida': 'https://alumed.wixsite.com/alumed/biblioteca-adquirida',
        }
    }
