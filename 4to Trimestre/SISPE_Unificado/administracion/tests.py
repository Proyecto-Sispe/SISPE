from decimal import Decimal
from types import SimpleNamespace

from django.test import TestCase

from . import inventario
from .models import Insumo, MovimientoInventario, ProductoInsumo


class DescuentoInventarioTests(TestCase):
    databases = {"default"}

    def setUp(self):
        self.carne = Insumo.objects.create(
            nombre="Carne de hamburguesa",
            unidad="Unidades",
            stock_actual=5,
        )
        self.pan = Insumo.objects.create(
            nombre="Pan de hamburguesa",
            unidad="Unidades",
            stock_actual=5,
        )
        self.producto_id = 987654
        ProductoInsumo.objects.create(
            producto_id=self.producto_id,
            insumo=self.carne,
            cantidad=1,
        )
        ProductoInsumo.objects.create(
            producto_id=self.producto_id,
            insumo=self.pan,
            cantidad=1,
        )

    def test_two_hamburgers_consume_two_meats_and_two_buns(self):
        requeridos = inventario.requerimientos([(self.producto_id, None, 2)])

        self.assertEqual(
            requeridos,
            {
                self.carne.pk: Decimal("2.000"),
                self.pan.pk: Decimal("2.000"),
            },
        )
        self.assertEqual(inventario.faltantes(requeridos), [])

        inventario.descontar(SimpleNamespace(pk=42), requeridos)

        self.carne.refresh_from_db()
        self.pan.refresh_from_db()
        self.assertEqual(self.carne.stock_actual, Decimal("3.000"))
        self.assertEqual(self.pan.stock_actual, Decimal("3.000"))
        self.assertEqual(
            MovimientoInventario.objects.filter(pedido_id=42, tipo="pedido").count(),
            2,
        )

    def test_insufficient_stock_is_reported_for_the_requested_quantity(self):
        requeridos = inventario.requerimientos([(self.producto_id, None, 6)])

        faltantes = inventario.faltantes(requeridos)

        self.assertEqual(
            {insumo.pk: cantidad for insumo, cantidad in faltantes},
            {
                self.carne.pk: Decimal("6.000"),
                self.pan.pk: Decimal("6.000"),
            },
        )
