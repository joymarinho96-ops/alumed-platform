from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home, unlp, uba, barcelo, premed, grupos, microscopio_virtual, anatomia_3d, cronograma_finales, info_util, facultad, biblioteca, cronograma_tps, plan_estudios, apoyo_psicologico, comisiones, club, favoritos, cartelera_view, conecta_fcm_view, conecta_landing_view, mapa_facultad_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('accounts.urls')),
    path('cursos/', include('courses.urls', namespace='courses')),
    path('pagamento/', include('payments.urls', namespace='payments')),
    path('foro/', include('forum.urls', namespace='forum')),
    path('', home, name='home'),
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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
