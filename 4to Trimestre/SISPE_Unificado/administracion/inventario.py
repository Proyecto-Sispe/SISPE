"""Descuento automático de insumos cuando se confirma un pedido."""

from collections import defaultdict
from decimal import Decimal

from django.db.models import F

from menu.models import ComboItem

from .models import Insumo, MovimientoInventario, ProductoInsumo


def _productos_de(producto_id, combo_id):
    if producto_id:
        return [(producto_id, 1)]
    if combo_id:
        return list(ComboItem.objects.filter(combo_id=combo_id).values_list("producto_id", "cantidad"))
    return []


def requerimientos(items):
    """items: [(producto_id, combo_id, cantidad)] -> {insumo_id: cantidad}"""
    total = defaultdict(Decimal)
    for producto_id, combo_id, cantidad in items:
        for pid, multiplo in _productos_de(producto_id, combo_id):
            for receta in ProductoInsumo.objects.filter(producto_id=pid, insumo__activo=True):
                total[receta.insumo_id] += receta.cantidad * multiplo * cantidad
    return dict(total)


def items_de_carrito(lineas):
    return [
        (
            linea["objeto"].pk if linea["tipo"] == "producto" else None,
            linea["objeto"].pk if linea["tipo"] == "combo" else None,
            int(linea["cantidad"]),
        )
        for linea in lineas
    ]


def faltantes(requeridos):
    """Insumos que no alcanzan: [(insumo, requerido)]"""
    insumos = Insumo.objects.select_for_update().filter(pk__in=requeridos)
    return [(i, requeridos[i.pk]) for i in insumos if i.stock_actual < requeridos[i.pk]]


def mover(insumo_id, cantidad, tipo, pedido_id=None, motivo="", usuario=""):
    """cantidad positiva suma stock, negativa resta."""
    Insumo.objects.filter(pk=insumo_id).update(stock_actual=F("stock_actual") + cantidad)
    MovimientoInventario.objects.create(
        insumo_id=insumo_id,
        tipo=tipo,
        cantidad=cantidad,
        pedido_id=pedido_id,
        motivo=motivo,
        usuario=usuario,
    )


def descontar(pedido, requeridos):
    for insumo_id, cantidad in requeridos.items():
        mover(insumo_id, -cantidad, "pedido", pedido.pk, f"Pedido #{pedido.pk}")


def devolver(pedido, usuario=""):
    """Repone lo consumido por un pedido cancelado (una sola vez)."""
    movimientos = MovimientoInventario.objects.filter(pedido_id=pedido.pk)
    if movimientos.filter(tipo="devolucion").exists():
        return
    for mov in list(movimientos.filter(tipo="pedido")):
        mover(mov.insumo_id, -mov.cantidad, "devolucion", pedido.pk, f"Cancelación pedido #{pedido.pk}", usuario)
