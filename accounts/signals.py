from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.cache import cache

@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    # Quando o usuário faz login, salvamos a chave da sessão atual no cache
    if not request.session.session_key:
        request.session.save() # Garante que a sessão tenha uma chave
        
    cache_key = f"user_session_{user.id}"
    cache.set(cache_key, request.session.session_key, timeout=None)
