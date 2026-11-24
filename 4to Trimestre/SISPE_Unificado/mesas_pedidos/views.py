from django.contrib import messages
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.http import url_has_allowed_host_and_scheme

from administracion.permisos import admin_required, obtener_rol_actual, rol_required
from menu import qr
from menu.views import _host_efectivo, _ips_locales

from .forms import IngresoClienteMesaForm, MesaForm
from .models import (
    Adicion,
    Categoria,
    DetallePedido,
    DetallePedidoAdicion,
    Menu,
    Mesa,
    Notificacion,
    Pedido,
    SesionMesa,
)
from pedidos.mesas_service import liberar_mesa_y_sesion


# Las tablas de esta app viven en la base "mesas" (ver config/routers.py)
BD = "mesas"
servicio_required = rol_required("Administrador", "Mesero")


def _calcular_total_pedido(pedido):
    subtotal_items = (
        pedido.detalles.aggregate(
            total=Sum(F("valor_venta") * F("cantidad"))
        )["total"]
        or 0
    )
    subtotal_adiciones = (
        DetallePedidoAdicion.objects.filter(detalle__pedido=pedido).aggregate(
            total=Sum(F("adicion__precio") * F("cantidad"))
        )["total"]
        or 0
    )
    return subtotal_items + subtotal_adiciones


def _mesas_con_qr(host, puede_gestionar_qr):
    """Prepara las mesas y genera sus QR solo para el rol administrador."""
    mesas = list(Mesa.objects.order_by("id"))
    for mesa in mesas:
        mesa.url_pedido = qr.url_carta(host, mesa.id) if puede_gestionar_qr else ""
        mesa.qr_url = qr.data_uri(mesa.url_pedido) if puede_gestionar_qr else None
    return mesas


# ==========================================
# 1. CRUD DE MESAS + QR
# ==========================================

@servicio_required
def mesas_list(request):
    puede_gestionar_qr = obtener_rol_actual(request) == "administrador"
    host = _host_efectivo(request)
    mesas = _mesas_con_qr(host, puede_gestionar_qr)
    desde = request.GET.get("desde", "").strip()
    hasta = request.GET.get("hasta", "").strip()
    rango_valido = True

    if desde or hasta:
        try:
            desde_num = int(desde) if desde else 1
            hasta_num = int(hasta) if hasta else 60
            if desde_num < 1 or hasta_num < desde_num:
                raise ValueError
        except ValueError:
            messages.error(
                request,
                "El rango debe usar mesas positivas y 'Hasta' no puede ser menor que 'Desde'.",
            )
            rango_valido = False
            desde_num = hasta_num = 0

    qr_count = 0
    for mesa in mesas:
        mesa.incluir_qr = (
            puede_gestionar_qr
            and rango_valido
            and (not desde or mesa.id >= desde_num)
            and (not hasta or mesa.id <= hasta_num)
        )
        qr_count += bool(mesa.incluir_qr and mesa.qr_url)

    return render(
        request,
        "mesas_pedidos/mesas_list.html",
        {
            "mesas": mesas,
            "puede_gestionar_qr": puede_gestionar_qr,
            "host": host,
            "ips": _ips_locales(),
            "motor": qr.motor(),
            "desde": desde,
            "hasta": hasta,
            "qr_count": qr_count,
        },
    )


@admin_required
def mesa_create(request):
    if request.method == "POST":
        form = MesaForm(request.POST)
        if form.is_valid():
            mesa = form.save()
            messages.success(request, f"Mesa #{mesa.id} creada y QR generado.")
            return redirect("mesas_list")
    else:
        form = MesaForm()
    return render(request, "mesas_pedidos/mesa_form.html", {"form": form, "accion": "Crear"})


@admin_required
def mesa_update(request, id_mesa):
    mesa = get_object_or_404(Mesa, pk=id_mesa)
    if request.method == "POST":
        form = MesaForm(request.POST, instance=mesa)
        if form.is_valid():
            mesa = form.save()
            messages.success(request, f"Mesa #{mesa.id} actualizada.")
            return redirect("mesas_list")
    else:
        form = MesaForm(instance=mesa)
    return render(
        request,
        "mesas_pedidos/mesa_form.html",
        {"form": form, "accion": "Editar", "mesa": mesa},
    )


@admin_required
def mesa_delete(request, id_mesa):
    mesa = get_object_or_404(Mesa, pk=id_mesa)
    if request.method == "POST":
        if mesa.qr_imagen:
            mesa.qr_imagen.delete(save=False)
        mesa.delete()
        messages.success(request, "Mesa eliminada.")
        return redirect("mesas_list")
    return render(request, "mesas_pedidos/mesa_confirm_delete.html", {"mesa": mesa})


@servicio_required
def liberar_mesa(request, id_mesa):
    mesa = get_object_or_404(Mesa, pk=id_mesa)
    if request.method == "POST":
        with transaction.atomic(using=BD):
            SesionMesa.objects.filter(mesa=mesa, activa=True).update(
                activa=False, fecha_fin=timezone.now()
            )
            mesa.estado = Mesa.EstadoMesa.LIBRE
            mesa.save(update_fields=["estado"])
        liberar_mesa_y_sesion(mesa.id)
        messages.success(request, f"Mesa #{mesa.id} liberada.")
    siguiente = request.POST.get("next", "")
    if siguiente and url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
        return redirect(siguiente)
    return redirect("mesas_list")


# ==========================================
# 2. ESCANEO QR Y FLUJO DEL CLIENTE
# ==========================================

def _carta_de_mesa(request, mesa_id):
    request.session["mesa"] = str(mesa_id)
    return redirect(f"{reverse('carta')}?mesa={mesa_id}")


def escanear_mesa(request, id_mesa):
    """Bienvenida del QR: el cliente escribe nombre y documento y pasa a la carta."""
    mesa = Mesa.objects.filter(pk=id_mesa).first()
    if mesa is None:
        return _carta_de_mesa(request, id_mesa)

    cliente = request.session.get("cliente_mesa") or {}
    if cliente.get("mesa") == mesa.id and SesionMesa.objects.filter(
        pk=cliente.get("sesion"), mesa=mesa, activa=True
    ).exists():
        return _carta_de_mesa(request, mesa.id)

    if mesa.estado == Mesa.EstadoMesa.OCUPADA:
        return render(request, "mesas_pedidos/mesa_ocupada.html", {"mesa": mesa})

    form = IngresoClienteMesaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        nombre = form.cleaned_data["nombre_cliente"].strip()
        documento = form.cleaned_data["cedula_cliente"].strip()

        with transaction.atomic(using=BD):
            mesa_bloqueada = Mesa.objects.select_for_update().get(pk=mesa.pk)
            if mesa_bloqueada.estado == Mesa.EstadoMesa.OCUPADA:
                messages.error(request, "Esta mesa acaba de ser ocupada por otra persona.")
                return redirect("escanear_mesa", id_mesa=mesa.id)

            sesion = SesionMesa.objects.create(
                mesa=mesa_bloqueada,
                codigo_acceso=get_random_string(6).upper(),
                nombre_cliente=nombre,
                cedula_cliente=int(documento),
                activa=True,
            )
            mesa_bloqueada.estado = Mesa.EstadoMesa.OCUPADA
            mesa_bloqueada.save(update_fields=["estado"])

        request.session["cliente_mesa"] = {
            "mesa": mesa.id,
            "sesion": sesion.id,
            "nombre": nombre,
            "documento": documento,
        }
        messages.success(request, f"¡Bienvenido, {nombre}! Ya puedes hacer tu pedido.")
        return _carta_de_mesa(request, mesa.id)

    return render(request, "mesas_pedidos/bienvenida.html", {"mesa": mesa, "form": form})


def ver_menu_pedido(request, id_pedido):
    pedido = get_object_or_404(
        Pedido.objects.select_related("mesa", "sesion_qr"), pk=id_pedido
    )
    categorias = Categoria.objects.prefetch_related("productos").all()
    adiciones = Adicion.objects.all()

    if request.method == "POST" and not pedido.confirmado:
        id_menu = request.POST.get("id_menu")
        try:
            cantidad = max(1, int(request.POST.get("cantidad", 1)))
        except (TypeError, ValueError):
            cantidad = 1
        obs_item = request.POST.get("observaciones_item", "").strip()
        ids_adiciones = request.POST.getlist("adiciones")

        producto = get_object_or_404(Menu, pk=id_menu)

        with transaction.atomic(using=BD):
            detalle = DetallePedido.objects.create(
                pedido=pedido,
                menu=producto,
                cantidad=cantidad,
                valor_venta=producto.precio,
                observaciones=obs_item or None,
            )
            for id_ad in ids_adiciones:
                adicion = Adicion.objects.filter(pk=id_ad).first()
                if adicion:
                    DetallePedidoAdicion.objects.create(
                        detalle=detalle,
                        adicion=adicion,
                        cantidad=1,
                    )

        messages.success(request, f"Agregaste {cantidad}x {producto.productos} al pedido.")
        return redirect("ver_menu_pedido", id_pedido=pedido.id)

    total_actual = _calcular_total_pedido(pedido)
    return render(
        request,
        "mesas_pedidos/menu_pedido.html",
        {
            "pedido": pedido,
            "categorias": categorias,
            "adiciones": adiciones,
            "total_actual": total_actual,
        },
    )


def confirmar_pedido(request, id_pedido):
    pedido = get_object_or_404(Pedido.objects.select_related("mesa"), pk=id_pedido)
    if request.method == "POST":
        pedido.observaciones = request.POST.get("observaciones_pedido", "").strip() or None
        pedido.confirmado = True
        pedido.estado = Pedido.EstadoPedido.EN_PREPARACION
        pedido.save(update_fields=["observaciones", "confirmado", "estado"])

        Notificacion.objects.create(
            tipo=(
                Notificacion.TipoNotificacion.PEDIDO_URGENTE
                if pedido.prioridad == Pedido.PrioridadPedido.URGENTE
                else Notificacion.TipoNotificacion.NUEVO_PEDIDO
            ),
            mensaje=f"Pedido #{pedido.id} confirmado en Mesa #{pedido.mesa.id}",
            mesa=pedido.mesa,
            pedido=pedido,
        )
        messages.success(request, "¡Pedido enviado a cocina!")
    return redirect("resumen_pedido", id_pedido=pedido.id)


def resumen_pedido(request, id_pedido):
    pedido = get_object_or_404(
        Pedido.objects.select_related("mesa", "sesion_qr").prefetch_related(
            "detalles__menu",
            "detalles__adiciones_detalle__adicion",
        ),
        pk=id_pedido,
    )
    return render(
        request,
        "mesas_pedidos/resumen_pedido.html",
        {"pedido": pedido, "total": _calcular_total_pedido(pedido)},
    )


# ==========================================
# 3. GESTIÓN RÁPIDA DE PEDIDOS / LIBERAR
# ==========================================

@servicio_required
def panel_pedidos(request):
    pedidos = Pedido.objects.select_related("mesa", "sesion_qr").order_by("-fecha_pedido")
    return render(request, "mesas_pedidos/panel_pedidos.html", {"pedidos": pedidos})


@servicio_required
def despachar_y_liberar(request, id_pedido):
    pedido = get_object_or_404(
        Pedido.objects.select_related("mesa", "sesion_qr"), pk=id_pedido
    )
    if request.method == "POST":
        with transaction.atomic(using=BD):
            pedido.estado = Pedido.EstadoPedido.ENTREGADO
            pedido.save(update_fields=["estado"])

            if pedido.sesion_qr:
                pedido.sesion_qr.activa = False
                pedido.sesion_qr.fecha_fin = timezone.now()
                pedido.sesion_qr.save(update_fields=["activa", "fecha_fin"])

            mesa = pedido.mesa
            mesa.estado = Mesa.EstadoMesa.LIBRE
            mesa.save(update_fields=["estado"])
        liberar_mesa_y_sesion(mesa.id)

        messages.success(
            request, f"Pedido #{pedido.id} entregado y Mesa #{mesa.id} liberada."
        )
    return redirect("panel_pedidos")


@servicio_required
def dashboard_visual(request):
    if obtener_rol_actual(request) == "administrador":
        return redirect("dashboard_admin")
    return redirect("mesas_list")
