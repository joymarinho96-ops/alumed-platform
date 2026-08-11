import os

file_path = r'C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\core\models.py'
content = """

# ==========================================
# MENU ARQUITETA - BACKEND ADMIN MODELS
# ==========================================

# 1. Conecta Radar 📡 (Monitoramento y Automatización)
class ConectaRadarSession(models.Model):
    session_name = models.CharField(max_length=100)
    auth_cookies = models.JSONField(help_text="Cookies serializadas de la sesión")
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '📡 Sesión Radar (Nodo Activo)'
        verbose_name_plural = '📡 Sesiones Radar'

class RadarSweepLog(models.Model):
    YEAR_CHOICES = [(0, 'Ingreso'), (1, '1º Año'), (2, '2º Año'), (3, '3º Año')]
    target_year = models.IntegerField(choices=YEAR_CHOICES)
    endpoint_scraped = models.URLField()
    status = models.CharField(max_length=50, choices=[('SUCCESS', 'Éxito'), ('BLOCKED', 'Bloqueado'), ('ERROR', 'Error')])
    items_found = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '🧿 Log de Varredura (Sweep)'
        verbose_name_plural = '🧿 Logs de Varredura'


# 2. PrimeiroBiblio 📚 (Ingestión RAG - Profe Joy)
class PrimeiroBiblioTome(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pendiente'), ('PROCESSING', 'Procesando'), ('COMPLETED', 'Completado')]
    file = models.FileField(upload_to='biblioteca_raw/')
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100, help_text="Ej: Anatomía, Histología")
    vectorization_status = models.CharField(max_length=20, default='PENDING', choices=STATUS_CHOICES)
    total_chunks = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '📚 Tomo de Biblioteca (RAG)'
        verbose_name_plural = '📚 Tomos de Biblioteca'


# 3. Motor Legal ⚖️ (Estatuto & Direitos)
class EstatutoCodex(models.Model):
    article_number = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    legal_text = models.TextField()
    keywords = models.CharField(max_length=255, help_text="Ej: recursante, extranjero, correlatividad")

    class Meta:
        verbose_name = '⚖️ Códice del Estatuto (Regla)'
        verbose_name_plural = '⚖️ Códices del Estatuto'

class AegisDefenseDraft(models.Model):
    student_identifier = models.CharField(max_length=100)
    related_rule = models.ForeignKey(EstatutoCodex, on_delete=models.SET_NULL, null=True)
    generated_document = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '🛡️ Escudo Legal (Borrador)'
        verbose_name_plural = '🛡️ Escudos Legales'


# 4. Club AluMed & Pagos 💳 (Gestión de Accesos)
class ClubAluMedAdept(models.Model):
    student_email = models.EmailField(unique=True)
    wix_subscription_id = models.CharField(max_length=100, blank=True)
    has_atlas_access = models.BooleanField(default=False)
    has_microscope_access = models.BooleanField(default=False)
    has_profe_joy_premium = models.BooleanField(default=False)
    expiration_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = '💎 Adepto del Club (Acceso)'
        verbose_name_plural = '💎 Adeptos del Club'


# 5. O Escudo / Firewall 🛡️ (Seguridad)
class FirewallSigil(models.Model):
    service_name = models.CharField(max_length=100)
    token_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    rate_limit_requests = models.IntegerField(default=100, help_text="Reqs por minuto")
    rotated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '🔥 Sello de Fuego (API Key)'
        verbose_name_plural = '🔥 Sellos de Fuego'
"""
with open(file_path, 'a', encoding='utf-8') as f:
    f.write(content)

print("Menu Arquiteta models appended successfully with improved names!")
