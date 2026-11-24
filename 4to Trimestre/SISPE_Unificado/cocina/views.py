"""Panel de cocina, cambio de estado y reportes de ventas."""

from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.db.models import Count, DecimalField, F, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from administracion import inventario
from administracion.facturacion import anular

from menu.models import Categoria, Producto
from menu.views import _host_efectivo, _ips_locales
from pedidos.models import DetallePedido, Pedido

from .permisos import chef_required


@chef_required
def panel(request):
    activos = (
        Pedido.objects.filter(estado__in=["pendiente", "en_preparacion", "listo"])
        .prefetch_related("detalles__producto", "detalles__combo", "detalles__adiciones__adicion")
        .order_by("fecha_pedido")
    )
    columnas = [
        {
            "clave": "pendiente",
            "titulo": "Pendientes",
            "pedidos": [p for p in activos if p.estado == "pendiente"],
        },
        {
            "clave": "en_preparacion",
            "titulo": "En preparación",
            "pedidos": [p for p in activos if p.estado == "en_preparacion"],
        },
        {
            "clave": "listo",
            "titulo": "Listos",
            "pedidos": [p for p in activos if p.estado == "listo"],
        },
    ]
    hoy = date.today()
    del_dia = Pedido.objects.filter(fecha_pedido__date=hoy)
    contexto = {
        "columnas": columnas,
        "total_activos": activos.count() if hasattr(activos, "count") else len(activos),
        "pedidos_hoy": del_dia.count(),
        "ventas_hoy": del_dia.aggregate(
            t=Coalesce(Sum("total"), Value(Decimal("0")), output_field=DecimalField())
        )["t"],
    }
    return render(request, "cocina/panel.html", contexto)


@require_POST
@chef_required
def cambiar_estado(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    destino = request.POST.get("estado", "").strip()

    permitidos = set(pedido.SIGUIENTE.values()) | {"cancelado"}
    if destino not in permitidos:
        messages.error(request, "Ese cambio de estado no es válido.")
        return redirect("cocina_panel")

    pedido.estado = destino
    pedido.save(update_fields=["estado"])
    if destino == "cancelado":
        inventario.devolver(pedido, request.user.get_username())
        anular(pedido)
    messages.success(
        request, f"Pedido #{pedido.id_pedido}: {pedido.get_estado_display()}."
    )
    siguiente = request.POST.get("next", "")
    if siguiente and url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
        return redirect(siguiente)
    return redirect("cocina_panel")


@chef_required
def qr_mesas(request):
    desde = request.GET.get("desde", "1")
    hasta = request.GET.get("hasta", "12")
    host = _host_efectivo(request)

    try:
        desde_i = max(int(desde), 1)
    except (TypeError, ValueError):
        desde_i = 1
    try:
        hasta_i = min(int(hasta), 60)
    except (TypeError, ValueError):
        hasta_i = 12
    if hasta_i < desde_i:
        hasta_i = desde_i

    from menu import qr as qr_mod

    mesas = []
    for numero in range(desde_i, hasta_i + 1):
        destino = qr_mod.url_carta(host, numero)
        uri = qr_mod.data_uri(destino)
        mesas.append(
            {
                "numero": numero,
                "destino": destino,
                "imagen": uri,
                "respaldo": None if uri else qr_mod.url_respaldo(destino),
            }
        )

    return render(
        request,
        "menu/qr_mesas.html",
        {
            "mesas": mesas,
            "desde": desde_i,
            "hasta": hasta_i,
            "host": host,
            "ips": _ips_locales(),
            "motor": qr_mod.motor(),
        },
    )


@chef_required
def reportes(request):
    desde = request.GET.get("desde", "")
    hasta = request.GET.get("hasta", "")
    categoria = request.GET.get("categoria", "")
    estado = request.GET.get("estado", "")

    pedidos = Pedido.objects.all()
    if desde:
        pedidos = pedidos.filter(fecha_pedido__date__gte=desde)
    if hasta:
        pedidos = pedidos.filter(fecha_pedido__date__lte=hasta)
    if estado:
        pedidos = pedidos.filter(estado=estado)

    detalles = DetallePedido.objects.filter(pedido__in=pedidos)
    if categoria:
        detalles = detalles.filter(
            Q(producto__categoria_id=categoria) | Q(combo__items__producto__categoria_id=categoria)
        ).distinct()

    ventas = detalles.aggregate(
        t=Coalesce(Sum("valor_venta"), Value(Decimal("0")), output_field=DecimalField())
    )["t"]
    cantidad_pedidos = pedidos.count()
    ticket = (ventas / cantidad_pedidos) if cantidad_pedidos else Decimal("0")

    por_categoria = (
        detalles.filter(producto__isnull=False)
        .values("producto__categoria__nom_categoria")
        .annotate(total=Sum("valor_venta"), unidades=Sum("cantidad"))
        .order_by("-total")
    )

    top = (
        detalles.filter(producto__isnull=False)
        .values("producto__nombre")
        .annotate(total=Sum("valor_venta"), unidades=Sum("cantidad"))
        .order_by("-unidades")[:10]
    )

    combos_vendidos = (
        detalles.filter(combo__isnull=False)
        .values("combo__nombre")
        .annotate(total=Sum("valor_venta"), unidades=Sum("cantidad"))
        .order_by("-unidades")
    )

    por_estado = pedidos.values("estado").annotate(n=Count("id_pedido")).order_by("-n")

    maximo_categoria = max([c["total"] for c in por_categoria], default=Decimal("0")) or Decimal("1")
    for fila in por_categoria:
        fila["porcentaje"] = int((fila["total"] / maximo_categoria) * 100)

    contexto = {
        "desde": desde,
        "hasta": hasta,
        "categoria": categoria,
        "estado": estado,
        "categorias": Categoria.objects.filter(activa=True),
        "estados": Pedido.ESTADOS,
        "ventas": ventas,
        "cantidad_pedidos": cantidad_pedidos,
        "ticket": ticket,
        "por_categoria": por_categoria,
        "top": top,
        "combos_vendidos": combos_vendidos,
        "por_estado": por_estado,
    }
    return render(request, "cocina/reportes.html", contexto)
