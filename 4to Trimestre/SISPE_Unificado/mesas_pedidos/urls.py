from django.urls import path
from . import views

urlpatterns = [
    # CRUD Mesas + QR
    path("mesas/", views.mesas_list, name="mesas_list"),
    path("mesas/nueva/", views.mesa_create, name="mesa_create"),
    path("mesas/<int:id_mesa>/editar/", views.mesa_update, name="mesa_update"),
    path("mesas/<int:id_mesa>/eliminar/", views.mesa_delete, name="mesa_delete"),
    path("mesas/<int:id_mesa>/liberar/", views.liberar_mesa, name="liberar_mesa"),

    # Escaneo QR y Pedido del Cliente
    path("mesa/<int:id_mesa>/pedir/", views.escanear_mesa, name="escanear_mesa"),
    path("pedido/<int:id_pedido>/menu/", views.ver_menu_pedido, name="ver_menu_pedido"),
    path("pedido/<int:id_pedido>/confirmar/", views.confirmar_pedido, name="confirmar_pedido"),
    path("pedido/<int:id_pedido>/resumen/", views.resumen_pedido, name="resumen_pedido"),

    # Panel de cocina / caja
    path("pedidos/", views.panel_pedidos, name="panel_pedidos"),
    path("pedido/<int:id_pedido>/despachar/", views.despachar_y_liberar, name="despachar_y_liberar"),
    path("", views.dashboard_visual, name="dashboard_visual"),
]