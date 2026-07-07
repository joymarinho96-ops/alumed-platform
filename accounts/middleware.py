from django.contrib.sessions.models import Session
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse

class OneSessionPerUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip static and media files to avoid multiple redirects/checks for assets
        if request.path.startswith(settings.STATIC_URL) or request.path.startswith(settings.MEDIA_URL):
            return self.get_response(request)

        # Se o usuário está autenticado
        if request.user.is_authenticated:
            # Verifica se o usuário é superusuário (admin)
            if request.user.is_superuser:
                # Se for admin, permite múltiplas sessões (não faz nada)
                pass
            else:
                cache_key = f"user_session_{request.user.id}"
                current_session_key = request.session.session_key
                
                # Tenta pegar a sessão salva no cache
                stored_session_key = cache.get(cache_key)

                # Se não tem sessão salva, salva a atual
                if not stored_session_key:
                    # Se não tem session key (pode acontecer em alguns backends de sessão antes do save), força o save
                    if not current_session_key:
                        request.session.save()
                        current_session_key = request.session.session_key
                    
                    cache.set(cache_key, current_session_key, timeout=None)
                
                # Se existe uma sessão salva e é diferente da atual
                elif stored_session_key != current_session_key:
                    # Verifica se a URL atual já é a de conflito ou logout para evitar loop
                    conflict_url = reverse('session_conflict')
                    logout_url = reverse('logout')
                    
                    if request.path != conflict_url and request.path != logout_url:
                         return redirect('session_conflict')

        response = self.get_response(request)
        return response
