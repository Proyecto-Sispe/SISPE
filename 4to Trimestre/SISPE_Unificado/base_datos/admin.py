
from django.contrib import admin
from .models import (
    Menu,
    Categoria,
    Insumo,
    Mesa,
    Pedido,
    DetallePedido,
    Factura,
    Adicion,
    MetodoPago,
    Rol,
    TipoDoc,
    SesionMesa,
    Notificaciones,
)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = (
        'id_menu',
        'productos',
        'precio',
        'pkfk_id_categoria',
    )
    search_fields = ('productos', 'descripcion')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id_categoria', 'nom_categoria')
    search_fields = ('nom_categoria',)


@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = (
        'id_insumo',
        'nombre',
        'stock_actual',
        'stock_minimo',
        'unidad',
        'activo',
    )
    search_fields = ('nombre',)


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('id_mesa', 'capacidad', 'ubicacion', 'estado')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_pedido', 'id_mesa', 'fecha_pedido', 'estado')
    list_filter = ('estado',)


admin.site.register([
    DetallePedido,
    Factura,
    Adicion,
    MetodoPago,
    Rol,
    TipoDoc,
    SesionMesa,
    Notificaciones,
])
