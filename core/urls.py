from django.urls import path
from . import views

urlpatterns = [
    path("conecta/dashboard/", views.dashboard_conecta_view, name="dashboard_conecta"),
    path("dashboard/simulados/", views.central_simulados_view, name="central_simulados"),
    path("en-vivo/", views.live_classroom_view, name="live_classroom"),
    path("dashboard/", views.student_dashboard, name="student_dashboard"),
    path("api/profile/materias/update/", views.update_materias, name="update_materias"),
    path("api/profile/whatsapp/update/", views.update_student_preferences, name="update_student_preferences"),
    path("biblioteca/", views.library_catalog, name="biblioteca_virtual"),
    path("api/biblioteca/download/", views.track_and_download_item, name="api_library_download"),
    path("calendar/sync/", views.sync_calendar_view, name="sync_calendar_bulk"),
    path("api/calendar/sync/", views.sync_calendar_event, name="sync_calendar"),
    path("api/calendar/unsync/", views.unsync_calendar_event, name="unsync_calendar"),
    path('', views.home, name='home'),
    path('becas/', views.becas_view, name='becas'),
]