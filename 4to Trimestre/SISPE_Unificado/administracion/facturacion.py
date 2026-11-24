from decimal import Decimal
from .models import Factura


def facturar(pedido, cliente=None):
    cliente = cliente or {}
    subtotal = Decimal(str(pedido.total or 0))
    impuesto = (subtotal * Decimal("0.08")).quantize(Decimal("0.01"))
    total = subtotal + impuesto
    factura, creada = Factura.objects.get_or_create(
        pedido=pedido,
        defaults={
            "fecha": pedido.fecha_pedido,
            "mesa": pedido.id_mesa,
            "cliente_nombre": cliente.get("nombre", "")[:100],
            "cliente_documento": str(cliente.get("documento", ""))[:20],
            "subtotal": subtotal,
            "impuesto": impuesto,
            "propina": Decimal("0"),
            "total": total,
        },
    )
    if not creada and factura.subtotal == 0 and subtotal > 0:
        factura.subtotal = subtotal
        factura.impuesto = impuesto
        if factura.estado != "pagada":
            factura.total = total + factura.propina
        factura.save(update_fields=["subtotal", "impuesto", "total"])
    return factura


def anular(pedido):
    Factura.objects.filter(pedido=pedido).update(estado="anulada")
