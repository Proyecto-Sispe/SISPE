"""Admin de pedidos: comandas con sus líneas y las adiciones de cada línea."""

from django.contrib import admin
from django.utils.html import format_html

from .models import DetalleAdicion, DetallePedido, Pedido


class DetalleAdicionInline(admin.TabularInline):
    model = DetalleAdicion
    extra = 0
    autocomplete_fields = ("adicion",)


class DetalleInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    autocomplete_fields = ("producto", "combo")
    fields = ("producto", "combo", "cantidad", "precio_unitario", "valor_venta", "notas")
    readonly_fields = ("valor_venta",)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "id_pedido",
        "id_mesa",
        "estado_badge",
        "prioridad",
        "fecha_pedido",
        "total",
        "unidades",
    )
    list_filter = ("estado", "prioridad", "fecha_pedido")
    search_fields = ("id_pedido", "id_mesa")
    date_hierarchy = "fecha_pedido"
    inlines = [DetalleInline]
    list_per_page = 30
    readonly_fields = ("fecha_pedido",)
    fieldsets = (
        ("Comanda", {"fields": ("id_mesa", "estado", "prioridad", "total")}),
        ("Notas", {"fields": ("observaciones", "fecha_pedido")}),
    )

    @admin.display(description="estado", ordering="estado")
    def estado_badge(self, obj):
        colores = {
            "pendiente": "#b45309",
            "en_preparacion": "#1d4ed8",
            "listo": "#15803d",
            "entregado": "#3f3f46",
            "cancelado": "#b91c1c",
        }
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 9px;border-radius:999px;'
            'font-size:11px;font-weight:600;">{}</span>',
            colores.get(obj.estado, "#3f3f46"),
            obj.get_estado_display(),
        )

    @admin.display(description="ítems")
    def unidades(self, obj):
        return obj.total_unidades


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = (
        "id_detalle",
        "pedido",
        "descripcion",
        "cantidad",
        "precio_unitario",
        "valor_venta",
        "adiciones_texto",
    )
    list_filter = ("producto__categoria",)
    search_fields = ("pedido__id_pedido", "producto__nombre", "combo__nombre")
    inlines = [DetalleAdicionInline]
    autocomplete_fields = ("producto", "combo")

    @admin.display(description="adiciones")
    def adiciones_texto(self, obj):
        nombres = [a.adicion.nombre for a in obj.adiciones.all()]
        return ", ".join(nombres) if nombres else "—"


@admin.register(DetalleAdicion)
class DetalleAdicionAdmin(admin.ModelAdmin):
    list_display = ("id_detalle_adicion", "detalle", "adicion", "precio")
    autocomplete_fields = ("adicion",)
