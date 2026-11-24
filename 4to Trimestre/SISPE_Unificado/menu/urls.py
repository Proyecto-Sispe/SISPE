from django.urls import path

from . import gestion, views

urlpatterns = [
    path("carta/", views.carta, name="carta"),
    path("roles/", views.roles, name="roles"),
    path("qr/<int:mesa>/", views.qr_mesa, name="qr_mesa"),
    path("qr/<int:mesa>/imagen.png", views.qr_imagen, name="qr_imagen"),
    # CRUD del menu dentro de la aplicacion
    path("gestion/<str:entidad>/", gestion.lista, name="gestion_lista"),
    path("gestion/<str:entidad>/nuevo/", gestion.crear, name="gestion_crear"),
    path("gestion/<str:entidad>/<int:pk>/editar/", gestion.editar, name="gestion_editar"),
    path("gestion/<str:entidad>/<int:pk>/borrar/", gestion.borrar, name="gestion_borrar"),
    path("gestion/combos/<int:pk>/partes/", gestion.combo_items, name="gestion_combo_items"),
]
