"""
WSGI config for alumed project.

It exposes the WSGI callable as a module-level variable named ``application``.
Vercel requer o alias ``app`` apontando para o mesmo callable.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumed.settings')

application = get_wsgi_application()

# Alias necessario para o Vercel (@vercel/python busca `app` por padrao)
app = application
