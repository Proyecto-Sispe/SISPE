from django.urls import path
from . import views

urlpatterns = [
    path('recuperar-password/', views.recuperar_password_page, name='recuperar_password'),
    path('api/auth/recuperar-password/', views.api_enviar_recuperacion, name='api_recuperar_password'),

    # Dashboards de ejemplo por rol
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/cocinero/', views.dashboard_cocinero, name='dashboard_cocinero'),
    path('dashboard/cajero/', views.dashboard_cajero, name='dashboard_cajero'),
    path('dashboard/mesero/', views.dashboard_mesero, name='dashboard_mesero'),
    path('dashboard/cliente/', views.dashboard_cliente, name='dashboard_cliente'),
]