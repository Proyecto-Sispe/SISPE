"""Panel de cocina, cambio de estado y reportes de ventas."""

from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.db.models import Count, DecimalField, F, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from administracion import inventario
from administracion.facturacion import anular
from administracion.permisos import admin_required
from mesas_pedidos.models import Mesa

from menu.models import Categoria, Producto
from pedidos.models import DetallePedido, Pedido

from .permisos import chef_required
from .reportes import exportar_excel, exportar_pdf


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


@admin_required
def qr_mesas(request):
    query = request.GET.urlencode()
    destino = reverse("mesas_list")
    return redirect(f"{destino}?{query}" if query else destino)


@chef_required
def reportes(request):
    desde = request.GET.get("desde", "").strip()
    hasta = request.GET.get("hasta", "").strip()
    categoria = request.GET.get("categoria", "").strip()
    estado = request.GET.get("estado", "").strip()
    export = request.GET.get("export", "").strip()

    if export not in ("", "excel", "pdf"):
        return HttpResponseBadRequest("Formato de exportación no válido.")

    fecha_desde = parse_date(desde) if desde else None
    fecha_hasta = parse_date(hasta) if hasta else None
    if desde and fecha_desde is None:
        return HttpResponseBadRequest("La fecha inicial no es válida.")
    if hasta and fecha_hasta is None:
        return HttpResponseBadRequest("La fecha final no es válida.")
    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        return HttpResponseBadRequest("La fecha inicial no puede ser posterior a la fecha final.")

    if categoria:
        try:
            categoria_id = int(categoria)
        except ValueError:
            return HttpResponseBadRequest("La categoría seleccionada no es válida.")
        if not Categoria.objects.filter(pk=categoria_id, activa=True).exists():
            return HttpResponseBadRequest("La categoría seleccionada no está disponible.")
        categoria = str(categoria_id)

    nombres_estados = dict(Pedido.ESTADOS)
    if estado and estado not in nombres_estados:
        return HttpResponseBadRequest("El estado seleccionado no es válido.")

    pedidos = Pedido.objects.all()
    if fecha_desde:
        pedidos = pedidos.filter(fecha_pedido__date__gte=fecha_desde)
    if fecha_hasta:
        pedidos = pedidos.filter(fecha_pedido__date__lte=fecha_hasta)
    if estado:
        pedidos = pedidos.filter(estado=estado)

    detalles = DetallePedido.objects.filter(pedido__in=pedidos).select_related(
        "pedido", "producto", "combo"
    )
    if categoria:
        detalles = detalles.filter(
            Q(producto__categoria_id=categoria) | Q(combo__items__producto__categoria_id=categoria)
        ).distinct()

    pedidos_reporte = pedidos
    if categoria:
        pedidos_reporte = pedidos.filter(pk__in=detalles.values("pedido_id").distinct())

    ventas = detalles.aggregate(
        t=Coalesce(Sum("valor_venta"), Value(Decimal("0")), output_field=DecimalField())
    )["t"]
    cantidad_pedidos = pedidos_reporte.count()
    ticket = (ventas / cantidad_pedidos) if cantidad_pedidos else Decimal("0")
    pedidos_entregados = pedidos_reporte.filter(estado="entregado").count()
    mesas_ocupadas = Mesa.objects.filter(estado=Mesa.EstadoMesa.OCUPADA).count()

    por_categoria = (
        detalles.filter(producto__isnull=False)
        .values("producto__categoria__nom_categoria")
        .annotate(total=Sum("valor_venta"), unidades=Sum("cantidad"))
        .order_by("-total")
    )

    top = list(
        detalles.filter(producto__isnull=False)
        .values("producto__nombre")
        .annotate(total=Sum("valor_venta"), unidades=Sum("cantidad"))
        .order_by("-unidades", "producto__nombre")[:10]
    )

    combos_vendidos = list(
        detalles.filter(combo__isnull=False)
        .values("combo__nombre")
        .annotate(total=Sum("valor_venta"), unidades=Sum("cantidad"))
        .order_by("-unidades", "combo__nombre")
    )

    por_estado = list(
        pedidos_reporte.values("estado").annotate(n=Count("id_pedido")).order_by("-n")
    )

    por_categoria = list(por_categoria)
    maximo_categoria = max(
        (fila["total"] or Decimal("0") for fila in por_categoria),
        default=Decimal("0"),
    ) or Decimal("1")
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
        "pedidos_entregados": pedidos_entregados,
        "mesas_ocupadas": mesas_ocupadas,
        "ticket": ticket,
        "por_categoria": por_categoria,
        "top": top,
        "producto_mas_vendido": top[0]["producto__nombre"] if top else "Sin ventas",
        "combos_vendidos": combos_vendidos,
        "por_estado": por_estado,
        "categoria_nombre": (
            Categoria.objects.filter(pk=categoria).values_list("nom_categoria", flat=True).first()
            if categoria
            else "Todas"
        ),
        "estado_nombre": nombres_estados.get(estado, "Todos"),
        "detalle_export": detalles,
    }

    if export == "excel":
        return exportar_excel(contexto)
    if export == "pdf":
        return exportar_pdf(contexto)

    return render(request, "cocina/reportes.html", contexto)
