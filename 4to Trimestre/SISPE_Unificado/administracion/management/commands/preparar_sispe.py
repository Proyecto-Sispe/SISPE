"""Carga los datos iniciales del módulo de administración (se puede repetir sin duplicar)."""

from decimal import Decimal

from django.core.management.base import BaseCommand

from administracion.facturacion import facturar
from administracion.models import Insumo, ProductoInsumo
from menu.models import Producto
from pedidos.models import Pedido

# palabra en el nombre del plato -> [(palabra del insumo, cantidad por unidad)]
RECETAS = {
    "hamburguesa": [("carne de hamburguesa", 1), ("pan de hamburguesa", 1), ("queso en tajadas", 1), ("lechuga", "0.02"), ("tomate", "0.03")],
    "perro": [("salchicha", 1), ("queso mozzarella", "0.03"), ("papa chip", "0.02")],
    "pizza": [("base de pizza", 1), ("queso mozzarella", "0.12")],
    "burrito": [("tortilla", 1), ("frijol", "0.05")],
    "quesadilla": [("tortilla", 1), ("queso mozzarella", "0.08")],
    "arepa": [("arepa blanca", 1)],
    "nugget": [("nuggets", 6)],
    "papas": [("papa a la francesa", "0.2")],
    "lasagna": [("lasagna", 3), ("bechamel", "0.1")],
    "patac": [("canastillas", 1)],
}


class Command(BaseCommand):
    help = "Importa insumos, crea recetas de ejemplo, facturas de pedidos previos y mesas 1-12."

    def handle(self, *args, **opciones):
        self._insumos()
        self._recetas()
        self._facturas()
        self._mesas()

    def _insumos(self):
        from base_datos.models import Insumo as InsumoSistema

        nuevos = 0
        try:
            origen = list(InsumoSistema.objects.using("sistema").all())
        except Exception as error:  # base sistema no disponible
            self.stdout.write(self.style.WARNING(f"No se pudo leer la base sistema: {error}"))
            origen = []
        for i in origen:
            _, creado = Insumo.objects.get_or_create(
                nombre=i.nombre,
                defaults={
                    "unidad": i.unidad,
                    "stock_actual": i.stock_actual,
                    "stock_minimo": i.stock_minimo,
                    "activo": bool(i.activo),
                },
            )
            nuevos += creado
        self.stdout.write(f"Insumos nuevos: {nuevos} (total {Insumo.objects.count()})")

    def _recetas(self):
        nuevas = 0
        insumos = list(Insumo.objects.all())
        for producto in Producto.objects.all():
            nombre = producto.nombre.lower()
            for clave, partes in RECETAS.items():
                if clave not in nombre:
                    continue
                for palabra, cantidad in partes:
                    insumo = next((i for i in insumos if palabra in i.nombre.lower()), None)
                    if insumo:
                        _, creado = ProductoInsumo.objects.get_or_create(
                            producto=producto, insumo=insumo, defaults={"cantidad": Decimal(str(cantidad))}
                        )
                        nuevas += creado
                break
        self.stdout.write(f"Recetas nuevas: {nuevas} (total {ProductoInsumo.objects.count()})")

    def _facturas(self):
        creadas = 0
        from administracion.models import Factura

        con_factura = set(Factura.objects.values_list("pedido_id", flat=True))
        for pedido in Pedido.objects.exclude(estado="cancelado"):
            if pedido.pk not in con_factura:
                facturar(pedido)
                creadas += 1
        self.stdout.write(f"Facturas nuevas: {creadas}")

    def _mesas(self):
        from mesas_pedidos.models import Mesa

        creadas = 0
        for numero in range(1, 13):
            if not Mesa.objects.filter(pk=numero).exists():
                Mesa.objects.create(id=numero, capacidad=4, ubicacion="Salón principal")
                creadas += 1
        self.stdout.write(f"Mesas nuevas: {creadas} (total {Mesa.objects.count()})")
