from django.contrib import admin

from .models import Factura, Insumo, MovimientoInventario, ProductoInsumo


@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "unidad", "stock_actual", "stock_minimo", "activo")
    search_fields = ("nombre",)


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ("numero", "fecha", "mesa", "cliente_nombre", "total", "estado")
    list_filter = ("estado", "mesa")


admin.site.register(ProductoInsumo)
admin.site.register(MovimientoInventario)
