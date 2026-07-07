from django.urls import path
from . import views
from . import webhooks

app_name = 'payments'

urlpatterns = [
    path('iniciar/<int:course_id>/', views.create_payment, name='create_payment'),
    path('iniciar/club/<str:plan_type>/', views.create_club_payment, name='create_club_payment'),
    path('sucesso/', views.payment_success, name='payment_success'),
    path('falha/', views.payment_failure, name='payment_failure'),
    path('pendente/', views.payment_pending, name='payment_pending'),
    path('webhook/', views.webhook, name='webhook'),
    path('webhook-wix/', webhooks.wix_webhook_view, name='webhook_wix'),
    path('check_status/<int:course_id>/', views.check_payment_status, name='check_payment_status'),
    path('check_status_club/<str:plan_type>/', views.check_club_payment_status, name='check_club_payment_status'),
]
