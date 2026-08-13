from pathlib import Path
import os
import environ
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializa o environ
env = environ.Env()
# Lê o arquivo .env se ele existir
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# ======================
# CONFIGURAÇÕES BÁSICAS
# ======================
# Segurança: DEBUG deve ser False em produção
DEBUG = env.bool('DEBUG', default=True)

# Segurança: Nunca deixe uma chave padrão em produção
SECRET_KEY = env('SECRET_KEY', default='django-insecure-development-key-change-in-production')

# Chaves de API
ELEVENLABS_API_KEY = env('ELEVENLABS_API_KEY', default='')
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
MERCADOPAGO_ACCESS_TOKEN = env('MERCADOPAGO_ACCESS_TOKEN', default='')

ALLOWED_HOSTS = [
    '*',
    'alumedestudiantes.com',
    'www.alumedestudiantes.com',
    'localhost',
    '127.0.0.1',
    '.loca.lt',
    '.railway.app',
    '.up.railway.app',
    '.vercel.app',                 # Vercel preview e production
    env('RAILWAY_STATIC_URL', default='').replace('https://', '').rstrip('/'),
    env('VERCEL_URL', default='').replace('https://', '').rstrip('/'),
]
ALLOWED_HOSTS = [h for h in ALLOWED_HOSTS if h]  # remove vazios

CSRF_TRUSTED_ORIGINS = [
    'https://alumedestudiantes.com',
    'https://www.alumedestudiantes.com',
    'https://*.railway.app',
    'https://*.up.railway.app',
    'https://*.vercel.app',        # Vercel
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ======================
# BANCO DE DADOS
# ======================
DATABASES = {
    'default': dj_database_url.config(
        default=env('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ======================
# APPS
# ======================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_q',
    'django.contrib.humanize',
    'django.contrib.sites',

    # Seus apps
    'accounts',
    'courses',
    'core',
    'forum',
    'payments',
    'flashcards',
    'simulator',
    'rest_framework',



    # Allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

# ======================
# MIDDLEWARE
# ======================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve arquivos estáticos em produção
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.AutoLoginMiddleware', # Bypass de login para dev
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'accounts.middleware.OneSessionPerUserMiddleware',
]

# ======================
# URL / TEMPLATES
# ======================
ROOT_URLCONF = 'alumed.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.unread_messages',
                'accounts.context_processors.wix_urls',
            ],
        },
    },
]

WSGI_APPLICATION = 'alumed.wsgi.application'

# ======================
# AUTENTICAÇÃO
# ======================
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ======================
# STATIC / MEDIA / GCS
# ======================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configurações do Google Cloud Storage
GS_BUCKET_NAME = env('GS_BUCKET_NAME', default='alumed-storage-br')

# Credenciais do GCS
GS_CREDENTIALS_FILE = env('GS_CREDENTIALS_FILE', default=None)

if not GS_CREDENTIALS_FILE:
    # Fallback para desenvolvimento local se não estiver no .env
    possible_paths = [
        BASE_DIR / 'gcs_credentials.json',
        BASE_DIR / 'alumed' / 'gcs_credentials.json',
    ]
    for path in possible_paths:
        if path.exists():
            GS_CREDENTIALS_FILE = str(path)
            break

# ======================
# EMAIL (SMTP GMAIL)
# ======================
# Alterado de GmailApiEmailBackend para SMTP padrão para maior estabilidade em produção
if not env('EMAIL_HOST_USER', default=''):
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'no-reply@alumed.com'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    DEFAULT_FROM_EMAIL = env('EMAIL_HOST_USER', default='')
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')


# ======================
# INTERNACIONALIZAÇÃO
# ======================

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True

# ======================
# ALLAUTH SETTINGS
# ======================
SITE_ID = 1
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/biblioteca/'
LOGOUT_REDIRECT_URL = '/'

ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_EMAIL_VERIFICATION = 'none'

# ALLAUTH ACCOUNT CONFIGURATION


ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
LOGIN_REDIRECT_URL = '/biblioteca/'
LOGOUT_REDIRECT_URL = '/'

ACCOUNT_SIGNUP_FORM_CLASS = 'accounts.forms.CustomSignupForm'
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http' if DEBUG else 'https'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
            'https://www.googleapis.com/auth/calendar.events',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
            'prompt': 'consent',
        }
    }
}

# ======================
# PADRÃO
# ======================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ======================
# X-FRAME-OPTIONS
# ======================
# Permite que o site seja carregado em iframes da mesma origem (necessário para o chat popup)
X_FRAME_OPTIONS = 'SAMEORIGIN'

# ======================
# WIX INTEGRATION SETTINGS
# ======================
ALUMED_WEBHOOK_SECRET = env('ALUMED_WEBHOOK_SECRET', default='miClaveSecretaAlumed2026')
ALUMED_SSO_SECRET = env('ALUMED_SSO_SECRET', default='miClaveSecretaAlumed2026')

WIX_PLAN_COURSE_MAPPING = {
    "wix-plan-anual-histo-2026": [1],
    "wix-plan-premium-anual": [1, 2, 3, 4, 5],
    "wix-plan-biologia-2026": [2],
    "wix-plan-anatomia-cat-c": [5],
}


# ======================
# DJANGO Q2 CONFIGURATION
# ======================
Q_CLUSTER = {
    'name': 'alumed_q2',
    'workers': 4,
    'recycle': 500,
    'timeout': 60,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default'  # Usar Django ORM como broker
}


# ======================
# WHATSAPP INTEGRATION
# ======================
WHATSAPP_API_URL = os.environ.get('WHATSAPP_API_URL', 'https://api.whatsapp.com/v1/')
WHATSAPP_TOKEN = os.environ.get('WHATSAPP_TOKEN', 'YOUR_WHATSAPP_TOKEN')
WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', 'YOUR_PHONE_ID')
ALUMED_SUPPORT_WHATSAPP_NUMBER = os.environ.get('ALUMED_SUPPORT_WHATSAPP_NUMBER', '+5492210000000')


# ======================
# WIX HEADLESS CMS
# ======================
WIX_HEADLESS_CLIENT_ID = os.environ.get('WIX_HEADLESS_CLIENT_ID', '78772f94-8bde-45fb-b768-190b2c98204f')
WIX_SITE_ID = os.environ.get('WIX_SITE_ID', '4e135cc0-cb21-4dd6-ab13-33e1dd20bda3')
WIX_API_KEY = os.environ.get('WIX_API_KEY', 'IST.eyJraWQiOiJQb3pIX2FDMiIsImFsZyI6IlJTMjU2In0.eyJkYXRhIjoie1wiaWRcIjpcImI5N2JlOTE0LTUzYmEtNDk1My1hN2Y4LWJmY2E3OWUwMGQyNlwiLFwiaWRlbnRpdHlcIjp7XCJ0eXBlXCI6XCJhcHBsaWNhdGlvblwiLFwiaWRcIjpcIjFmOGQ5Y2UwLTM3NjgtNDI1OC04ODk2LWUyNjNmZDEyMWIzNVwifSxcInRlbmFudFwiOntcInR5cGVcIjpcImFjY291bnRcIixcImlkXCI6XCI0ZTEzNWNjMC1jYjIxLTRkZDYtYWIxZC1hODk3ZjExMjU1YjhcIn19IiwiaWF0IjoxNzg2MTI0MDUyfQ.Zoh6ekxP4oEkbDQvBj_MtGvnj_Hzs8WCRg_6v6KPE6NOMzaIwPEuz3qjr7e1E-0tU4a8axwzODoL5estK4HmXNVxS6aGaTaLOGPN_Fodt8PybHyefdaWJbezPS1KTmxbHLQ2rWAMuphxbZfnvV85UxVYf0l_7FFKHj7Kk0K2zTfIx1_JF-dZEtnCuIYVWXvjpYfQV7vDTOmV5W56no4lIywzWCeayG_8yqko-xDCrFVEIXF2v_LDXCGCAYcqrHa_qE8FgYj8ll-pl2FSsrazQDOBfLbhh0pr1Bgq04-Bf096k_qPD3ILqxi1KCp8L6ktZFdRzcRAwv795Y0HToJUlg')
WIX_LIBRARY_COLLECTION_ID = os.environ.get('WIX_LIBRARY_COLLECTION_ID', 'SharedFiles')
