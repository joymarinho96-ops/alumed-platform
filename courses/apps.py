from django.apps import AppConfig

class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'

    def ready(self):
        # Importa os sinais para que sejam registrados
        # import courses.signals  <-- Removido pois o arquivo signals.py está vazio/depreciado
        pass
