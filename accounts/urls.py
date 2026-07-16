from django.urls import path, include
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('campus/', views.student_dashboard_view, name='campus'),

    # Planejamento Acadêmico
    path('planejamento/', views.planejamento_view, name='planejamento'),

    # Academic Events API
    path('api/events/',                views.api_events_list,   name='api_events_list'),
    path('api/events/create/',         views.api_events_create, name='api_events_create'),
    path('api/events/<int:pk>/update/',views.api_events_update, name='api_events_update'),
    path('api/events/<int:pk>/delete/',views.api_events_delete, name='api_events_delete'),
    path('api/events/<int:pk>/status/',views.api_events_status, name='api_events_status'),
    path('api/events/<int:pk>/gcal/',  views.api_events_gcal,   name='api_events_gcal'),

    # Mis Cursos — redireciona direto para o Wix, sem pagina intermediaria
    path('mis-cursos/', RedirectView.as_view(
        url='https://www.alumedestudiantes.com/miscursos',
        permanent=False
    ), name='mis_cursos'),

    path('conecta/dashboard/', views.conecta_dashboard_view, name='conecta_dashboard'),
    path('accounts/gate/', views.auth_gate_view, name='auth_gate'),
    path('students/', views.students_list_view, name='students_list'),
    path('details/', views.account_details_view, name='account_details'),
    path('session-conflict/', views.session_conflict_view, name='session_conflict'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    
    # Store URL
    path('store/', views.alumed_store_view, name='alumed_store'),
    
    # Chatmed URLs
    path('chatmed/', views.chatmed_view, name='chatmed'),
    path('chatmed/get/<int:user_id>/', views.get_messages, name='get_messages'),
    path('chatmed/send/', views.send_message, name='send_message'),
    path('chatmed/check-unread/', views.check_unread_messages, name='check_unread_messages'),

    # Conecta FCM — Preferences API v2 (GET + POST)
    path('conecta/api/preferences/', views.conecta_preferences, name='conecta_preferences'),

    # Conecta Radar — Cartelera FCM ao vivo
    path('conecta/api/cartelera/', views.api_cartelera_live, name='api_cartelera_live'),

    # URLs de autenticação do Django
    path('', include('django.contrib.auth.urls')),
]

