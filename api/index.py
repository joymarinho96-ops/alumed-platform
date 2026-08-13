import os
import sys

# Garante que o diretório raiz está no path do Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumed.settings')

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
