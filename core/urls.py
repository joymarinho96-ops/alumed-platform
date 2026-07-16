from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('becas/', views.becas_view, name='becas'),
]