from django.urls import path, include
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.student_dashboard_view, name='student_dashboard'),
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

    # URLs de autenticação do Django
    path('', include('django.contrib.auth.urls')),
]
