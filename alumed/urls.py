from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home, unlp, uba, barcelo, premed, grupos, microscopio_virtual, anatomia_3d, cronograma_finales, info_util, facultad, biblioteca, cronograma_tps, plan_estudios, apoyo_psicologico, comisiones, club, favoritos, cartelera_view, conecta_fcm_view, conecta_landing_view, mapa_facultad_view, becas_view, simulacros_view, api_get_simulacro_questions, checkout_intensivo
from core.telegram_views import telegram_webhook, setup_webhook
from core.library_views import conecta_biblioteca_view, conecta_biblioteca_lector_view
from core.profe_joy_views import profe_joy_chat, profe_joy_page, profe_joy_stats

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('accounts.urls')),
    path('cursos/', include('courses.urls', namespace='courses')),
    path('pagamento/', include('payments.urls', namespace='payments')),
    path('foro/', include('forum.urls', namespace='forum')),
    path('', include('flashcards.urls', namespace='flashcards')), # <- Rotas e API do Joy Recall
    path('medlatin/', include('medlatin.urls', namespace='medlatin')),

    path('', home, name='home'),
    path('simulacros/', simulacros_view, name='simulacros'),
    path('simulacros/<slug:materia>/', simulacros_view, name='simulacro_materia'),
    path('api/simulacros/<str:subject>/', api_get_simulacro_questions, name='api_get_simulacro_questions'),
    path('checkout/<slug:curso>/', checkout_intensivo, name='checkout_intensivo'),

    path('unlp/', unlp, name='unlp'),
    path('uba/', uba, name='uba'),
    path('barcelo/', barcelo, name='barcelo'),
    path('premed/', premed, name='premed'),
    path('grupos/', grupos, name='grupos'),
    path('groups/', grupos, name='groups'),

    path('microscopio-virtual/', microscopio_virtual, name='microscopio_virtual'),
    path('anatomia-3d/', anatomia_3d, name='anatomia_3d'),
    path('cronograma-finales/', cronograma_finales, name='cronograma_finales'),
    path('cartelera/', cartelera_view, name='cartelera_view'),

    # Conecta FCM — /conecta/ landing publica, /conecta-fcm/ legado
    path('conecta/', conecta_landing_view, name='conecta_landing'),
    path('conecta-fcm/', conecta_fcm_view, name='conecta_fcm'),
    path('conecta/biblioteca/', conecta_biblioteca_view, name='conecta_biblioteca'),
    path('conecta/biblioteca/lector/<int:book_id>/', conecta_biblioteca_lector_view, name='conecta_biblioteca_lector'),

    path('info-util/', info_util, name='info_util'),
    path('facultad/', facultad, name='facultad'),
    path('biblioteca/', biblioteca, name='biblioteca'),
    path('cronograma-tps/', cronograma_tps, name='cronograma_tps'),
    path('plan-estudios/', plan_estudios, name='plan_estudios'),
    path('apoyo-psicologico/', apoyo_psicologico, name='apoyo_psicologico'),
    path('comisiones/', comisiones, name='comisiones'),
    path('club/', club, name='club'),
    path('favoritos/', favoritos, name='favoritos'),
    path('mapa-facultad/', mapa_facultad_view, name='mapa_facultad'),
    path('becas/', becas_view, name='becas'),

    # Telegram Bot Webhook
    path('telegram/webhook/', telegram_webhook, name='telegram_webhook'),
    path('telegram/setup-webhook/', setup_webhook, name='telegram_setup_webhook'),

    # ── Profe Joy IA ──
    path('profe-joy/', profe_joy_page, name='profe_joy'),
    path('profe-joy/chat/', profe_joy_chat, name='profe_joy_chat'),
    path('profe-joy/stats/', profe_joy_stats, name='profe_joy_stats'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

