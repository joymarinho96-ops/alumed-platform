from django.contrib.auth import login
from django.contrib.auth.models import User

class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            user = User.objects.filter(is_superuser=True).first() or User.objects.first()
            if user:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return self.get_response(request)
