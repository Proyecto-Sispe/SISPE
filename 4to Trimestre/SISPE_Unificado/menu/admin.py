"""Admin del menú: categorías, productos con foto, adiciones y combos."""

from django.contrib import admin
from django.utils.html import format_html

from .models import Adicion, Categoria, Combo, ComboItem, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id_categoria", "nom_categoria", "orden", "activa", "cuantos_productos")
    list_editable = ("orden", "activa")
    search_fields = ("nom_categoria",)
    ordering = ("orden", "nom_categoria")

    @admin.display(description="productos")
    def cuantos_productos(self, obj):
        return obj.productos.count()


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "miniatura",
        "id_menu",
        "nombre",
        "categoria",
        "precio",
        "disponible",
        "orden",
    )
    list_display_links = ("id_menu", "nombre")
    list_editable = ("precio", "disponible", "orden")
    list_filter = ("categoria", "disponible")
    search_fields = ("nombre", "descripcion")
    list_per_page = 25
    list_select_related = ("categoria",)
    fieldsets = (
        ("Datos del plato", {"fields": ("nombre", "descripcion", "categoria", "precio")}),
        ("Imagen y visibilidad", {"fields": ("foto", "disponible", "orden")}),
    )

    @admin.display(description="foto")
    def miniatura(self, obj):
        if obj.tiene_foto:
            return format_html(
                '<img src="{}" style="height:42px;width:42px;object-fit:cover;'
                'border-radius:8px;border:1px solid #3a322c;" />',
                obj.foto.url,
            )
        return format_html(
            '<span style="display:inline-flex;height:42px;width:42px;align-items:center;'
            'justify-content:center;border-radius:8px;background:#2a2320;color:#ff9a4d;'
            'font-weight:700;">{}</span>',
            obj.inicial,
        )


@admin.register(Adicion)
class AdicionAdmin(admin.ModelAdmin):
    list_display = ("id_adicion", "nombre", "precio", "categoria", "activa", "orden")
    list_editable = ("precio", "activa", "orden")
    list_filter = ("activa", "categoria")
    search_fields = ("nombre",)
    fieldsets = (
        (
            None,
            {
                "fields": ("nombre", "precio", "categoria", "activa", "orden"),
                "description": (
                    "Si dejas la categoría vacía, la adición se ofrece en todos los "
                    "productos. El precio se suma al del plato cuando el cliente la elige."
                ),
            },
        ),
    )


class ComboItemInline(admin.TabularInline):
    model = ComboItem
    extra = 1
    autocomplete_fields = ("producto",)
    fields = ("producto", "cantidad", "subtotal")
    readonly_fields = ("subtotal",)

    @admin.display(description="subtotal suelto")
    def subtotal(self, obj):
        if not obj.pk:
            return "—"
        return f"${obj.subtotal:,.0f}".replace(",", ".")


@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display = (
        "miniatura",
        "id_combo",
        "nombre",
        "precio",
        "precio_suelto",
        "activo",
        "orden",
    )
    list_display_links = ("id_combo", "nombre")
    list_editable = ("precio", "activo", "orden")
    list_filter = ("activo",)
    search_fields = ("nombre", "descripcion")
    inlines = [ComboItemInline]
    fieldsets = (
        ("Datos del combo", {"fields": ("nombre", "descripcion", "precio")}),
        ("Imagen y visibilidad", {"fields": ("foto", "activo", "orden")}),
    )

    @admin.display(description="foto")
    def miniatura(self, obj):
        if obj.tiene_foto:
            return format_html(
                '<img src="{}" style="height:42px;width:42px;object-fit:cover;'
                'border-radius:8px;border:1px solid #3a322c;" />',
                obj.foto.url,
            )
        return format_html(
            '<span style="display:inline-flex;height:42px;width:42px;align-items:center;'
            'justify-content:center;border-radius:8px;background:#2a2320;color:#ff9a4d;'
            'font-weight:700;">{}</span>',
            obj.inicial,
        )

    @admin.display(description="suma suelta")
    def precio_suelto(self, obj):
        return f"${obj.precio_suelto:,.0f}".replace(",", ".")
