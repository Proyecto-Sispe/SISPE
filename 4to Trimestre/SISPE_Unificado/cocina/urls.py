from django.urls import path

from . import views

urlpatterns = [
    path("", views.panel, name="cocina_panel"),
    path("pedido/<int:pk>/estado/", views.cambiar_estado, name="cocina_estado"),
    path("qr/", views.qr_mesas, name="cocina_qr"),
    path("reportes/", views.reportes, name="reportes"),
]
