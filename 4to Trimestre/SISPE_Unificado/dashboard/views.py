from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone

from administracion.permisos import admin_required
from base_datos.models import (
    Pedido,
    DetallePedido,
    Mesa,
    Factura,
)


@admin_required
def inicio(request):
    hoy = timezone.now().date()

    ventas_hoy = Factura.objects.filter(
        fecha_hora__startswith=hoy.strftime('%Y-%m-%d')
    ).aggregate(total=Sum('total'))['total'] or 0

    pedidos_completados = Pedido.objects.filter(
        estado='entregado'
    ).count()

    mesas_activas = Mesa.objects.filter(
        estado=1
    ).count()

    producto_mas_vendido = (
        DetallePedido.objects
        .values('id_menu__productos')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')
        .first()
    )

    nombre_producto = (
        producto_mas_vendido['id_menu__productos']
        if producto_mas_vendido else 'Sin ventas'
    )

    contexto = {
        'ventas_hoy': ventas_hoy,
        'pedidos_completados': pedidos_completados,
        'mesas_activas': mesas_activas,
        'producto_mas_vendido': nombre_producto,
    }

    return render(request, 'dashboard/inicio.html', contexto)