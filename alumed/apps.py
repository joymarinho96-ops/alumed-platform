from django.apps import AppConfig

class AlumedConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "alumed"

    def ready(self):
        from django.core.files.storage import default_storage
        print("STORAGE ATIVO:", default_storage)
