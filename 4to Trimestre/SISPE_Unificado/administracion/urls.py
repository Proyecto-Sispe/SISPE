from django.urls import path

from . import views

urlpatterns = [
    path("usuarios/", views.usuarios, name="adm_usuarios"),
    path("usuarios/nuevo/", views.usuario_crear, name="adm_usuario_crear"),
    path("usuarios/<int:tipo>/<int:numero>/editar/", views.usuario_editar, name="adm_usuario_editar"),
    path("menu/", views.menu, name="adm_menu"),
    path("menu/<int:pk>/disponible/", views.menu_disponible, name="adm_menu_disponible"),
    path("inventario/", views.inventario_lista, name="adm_inventario"),
    path("inventario/nuevo/", views.insumo_form, name="adm_insumo_crear"),
    path("inventario/<int:pk>/editar/", views.insumo_form, name="adm_insumo_editar"),
    path("inventario/<int:pk>/mover/", views.inventario_mover, name="adm_inventario_mover"),
    path("inventario/recetas/", views.recetas, name="adm_recetas"),
    path("inventario/recetas/<int:pk>/", views.receta_producto, name="adm_receta"),
    path("inventario/recetas/quitar/<int:pk>/", views.receta_quitar, name="adm_receta_quitar"),
    path("facturas/", views.facturas, name="adm_facturas"),
    path("facturas/<int:pk>/", views.factura_detalle, name="adm_factura"),
    path("pedidos/", views.pedidos_activos, name="adm_pedidos"),
]
