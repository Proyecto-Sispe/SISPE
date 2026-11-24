"""Vistas del carrito, la confirmacion del pedido y el seguimiento del cliente."""

from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_POST

from administracion import inventario
from administracion.facturacion import anular, facturar
from menu.models import Adicion, Combo, Producto

from . import carrito
from .mesas_service import liberar_mesa_y_sesion, ocupar_mesa
from .models import DetalleAdicion, DetallePedido, Pedido


def _mesa(request):
    mesa = request.POST.get("mesa") or request.GET.get("mesa") or request.session.get("mesa")
    if mesa:
        request.session["mesa"] = str(mesa).strip()
        return str(mesa).strip()
    return ""


def ver(request):
    lineas = carrito.lineas(request)
    return render(
        request,
        "pedidos/carrito.html",
        {
            "lineas": lineas,
            "total": carrito.total(request),
            "mesa": request.session.get("mesa", ""),
        },
    )


@require_POST
def agregar(request):
    tipo = request.POST.get("tipo", "producto")
    if tipo not in ("producto", "combo"):
        tipo = "producto"
    oid = request.POST.get("id") or request.POST.get("oid")
    if not oid:
        messages.error(request, "No se indicó qué producto agregar.")
        return redirect("carta")

    if tipo == "producto":
        if not Producto.objects.filter(pk=oid, disponible=True).exists():
            messages.error(request, "Ese producto ya no está disponible.")
            return redirect("carta")
    else:
        if not Combo.objects.filter(pk=oid, activo=True).exists():
            messages.error(request, "Ese combo ya no está disponible.")
            return redirect("carta")

    adiciones = request.POST.getlist("adiciones")
    cantidad = request.POST.get("cantidad", 1)
    notas = request.POST.get("notas", "")
    _mesa(request)

    carrito.agregar(request, tipo, oid, cantidad, adiciones, notas)
    messages.success(request, "Agregado al carrito.")
    destino = request.POST.get("volver") or "carrito"
    if destino == "carta":
        mesa = request.session.get("mesa", "")
        url = reverse("carta")
        if mesa:
            url = f"{url}?mesa={mesa}"
        return redirect(url)
    return redirect("carrito")


@require_POST
def actualizar(request, clave):
    accion = request.POST.get("accion", "")
    cantidad = request.POST.get("cantidad")
    if accion == "sumar":
        for linea in carrito.lineas(request):
            if linea["clave"] == clave:
                carrito.cambiar_cantidad(request, clave, linea["cantidad"] + 1)
                break
    elif accion == "restar":
        for linea in carrito.lineas(request):
            if linea["clave"] == clave:
                carrito.cambiar_cantidad(request, clave, linea["cantidad"] - 1)
                break
    elif cantidad is not None:
        carrito.cambiar_cantidad(request, clave, cantidad)
    return redirect("carrito")


@require_POST
def quitar(request, clave):
    carrito.quitar(request, clave)
    return redirect("carrito")


@require_POST
def vaciar(request):
    carrito.vaciar(request)
    return redirect("carrito")


@transaction.atomic
def confirmar(request):
    if request.method != "POST":
        return redirect("carrito")

    lineas = carrito.lineas(request)
    if not lineas:
        messages.warning(request, "El carrito está vacío.")
        return redirect("carta")

    mesa = _mesa(request)
    if not mesa:
        messages.error(request, "Falta indicar la mesa. Escanea el QR de tu mesa.")
        return redirect("carrito")

    requeridos = inventario.requerimientos(inventario.items_de_carrito(lineas))
    faltan = inventario.faltantes(requeridos)
    if faltan:
        nombres = ", ".join(insumo.nombre for insumo, _ in faltan)
        messages.error(
            request,
            f"No hay insumos suficientes para tu pedido ({nombres}). Quita esos platos o avisa al mesero.",
        )
        return redirect("carrito")

    observaciones = request.POST.get("observaciones", "").strip()
    total = carrito.total(request)

    pedido = Pedido.objects.create(
        id_mesa=int(mesa) if str(mesa).isdigit() else 0,
        estado="pendiente",
        prioridad=1,
        total=total,
        observaciones=observaciones,
    )

    for linea in lineas:
        detalle = DetallePedido.objects.create(
            pedido=pedido,
            producto=linea["objeto"] if linea["tipo"] == "producto" else None,
            combo=linea["objeto"] if linea["tipo"] == "combo" else None,
            cantidad=linea["cantidad"],
            precio_unitario=linea["unitario"],
            valor_venta=linea["subtotal"],
            notas=linea["notas"][:200],
        )
        for adicion in linea["adiciones"]:
            DetalleAdicion.objects.create(
                detalle=detalle, adicion=adicion, precio=adicion.precio
            )

    inventario.descontar(pedido, requeridos)
    cliente = request.session.get("cliente_mesa") or {}
    if str(cliente.get("mesa")) != str(mesa):
        cliente = {}
    facturar(pedido, cliente)
    request.session["ultimo_pedido_id"] = pedido.pk
    if str(mesa).isdigit():
        ocupar_mesa(int(mesa))

    carrito.vaciar(request)
    return redirect("seguimiento", pk=pedido.pk)


def seguimiento(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    request.session["ultimo_pedido_id"] = pedido.pk
    puede_cancelar = (pedido.estado == "pendiente")
    factura = getattr(pedido, "factura", None)
    return render(
        request,
        "pedidos/seguimiento.html",
        {
            "pedido": pedido,
            "puede_cancelar": puede_cancelar,
            "factura": factura,
            "detalles": pedido.detalles.select_related("producto", "combo").prefetch_related(
                "adiciones__adicion"
            ),
            "pasos": [
                ("pendiente", "Recibido"),
                ("en_preparacion", "En preparación"),
                ("listo", "Listo"),
                ("entregado", "Entregado"),
            ],
        },
    )


def estado_json(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    return JsonResponse(
        {
            "id": pedido.id_pedido,
            "estado": pedido.estado,
            "estado_display": pedido.get_estado_display(),
            "total": str(pedido.total),
            "minutos": pedido.minutos_espera,
            "avance": pedido.avance,
            "activo": pedido.activo,
            "puede_cancelar": pedido.estado == "pendiente",
        }
    )


BANCOS_PSE = [
    ("bancolombia", "Bancolombia"),
    ("bogota", "Banco de Bogotá"),
    ("davivienda", "Davivienda"),
    ("nequi", "Nequi"),
    ("daviplata", "Daviplata"),
    ("bbva", "BBVA Colombia"),
    ("occidente", "Banco de Occidente"),
    ("colpatria", "Scotiabank Colpatria"),
    ("popular", "Banco Popular"),
    ("cajasocial", "Banco Caja Social"),
    ("itau", "Itaú Corpbanca"),
    ("falabella", "Banco Falabella"),
]

METODOS_PAGO_PENDIENTES = {
    "pse": "PSE - Pendiente",
    "efectivo": "Efectivo - Pendiente en caja",
    "tarjeta": "Tarjeta - Pendiente en caja",
}


@require_POST
def cancelar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)

    # Validación de regla de negocio: solo antes de entrar en preparación
    if pedido.estado != "pendiente":
        messages.error(
            request,
            "El pedido ya entró en preparación en cocina y no puede ser cancelado.",
        )
        return redirect("seguimiento", pk=pedido.pk)

    with transaction.atomic():
        pedido.estado = "cancelado"
        pedido.save(update_fields=["estado"])
        inventario.devolver(pedido, "Cliente")
        anular(pedido)

    # Liberación automática de la mesa asociada
    if pedido.id_mesa:
        liberar_mesa_y_sesion(pedido.id_mesa)

    # Limpiar estado de mesa y pedido de la sesión
    request.session.pop("mesa", None)
    request.session.pop("cliente_mesa", None)
    request.session.pop("ultimo_pedido_id", None)

    return redirect("despedida_cliente")


def despedida_cliente(request):
    return render(request, "pedidos/despedida.html")


@require_POST
def finalizar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)

    # Al presionar Finalizar pedido, la mesa pasa a libre/disponible automáticamente
    if pedido.id_mesa:
        liberar_mesa_y_sesion(pedido.id_mesa)

    # Asegurar que la factura existe con sus cálculos
    cliente = request.session.get("cliente_mesa") or {}
    facturar(pedido, cliente)

    # Limpiar la mesa de la sesión del cliente para liberar su dispositivo
    request.session.pop("mesa", None)
    request.session.pop("cliente_mesa", None)

    messages.success(request, f"Mesa #{pedido.id_mesa} liberada. Aquí tienes tu factura detallada.")
    return redirect("factura_cliente", pk=pedido.pk)


def factura_cliente(request, pk):
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related(
            "detalles__producto", "detalles__combo", "detalles__adiciones__adicion"
        ),
        pk=pk,
    )
    factura = getattr(pedido, "factura", None)
    if not factura:
        factura = facturar(pedido, request.session.get("cliente_mesa") or {})

    if request.method == "POST":
        metodo = request.POST.get("metodo_pago", "").strip()
        if factura.estado == "pagada":
            messages.error(request, "Esta factura ya está pagada.")
        elif metodo not in METODOS_PAGO_PENDIENTES:
            messages.error(request, "Selecciona un método de pago válido.")
        else:
            factura.metodo_pago = METODOS_PAGO_PENDIENTES[metodo]
            factura.transaccion_id = ""
            factura.save(update_fields=["metodo_pago", "transaccion_id"])
            messages.success(
                request,
                "Método PSE seleccionado."
                if metodo == "pse"
                else f"Selección guardada. Acércate a caja para pagar en {metodo}.",
            )
        return redirect("factura_cliente", pk=pedido.pk)

    metodo_seleccionado = next(
        (
            codigo
            for codigo, etiqueta in METODOS_PAGO_PENDIENTES.items()
            if factura.metodo_pago == etiqueta
        ),
        "",
    )

    subtotal = Decimal(str(pedido.total or 0))
    impuesto = (subtotal * Decimal("0.08")).quantize(Decimal("0.01"))
    propina_sugerida = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
    total_con_impuesto = subtotal + impuesto
    total_con_propina = total_con_impuesto + propina_sugerida

    # Si ya está pagada, usar los montos almacenados
    if factura.estado == "pagada":
        total_a_pagar = factura.total
        propina_aplicada = factura.propina
    else:
        total_a_pagar = total_con_impuesto
        propina_aplicada = Decimal("0")

    return render(
        request,
        "pedidos/factura_cliente.html",
        {
            "pedido": pedido,
            "factura": factura,
            "subtotal": subtotal,
            "impuesto": impuesto,
            "propina_sugerida": propina_sugerida,
            "total_con_impuesto": total_con_impuesto,
            "total_con_propina": total_con_propina,
            "total_a_pagar": total_a_pagar,
            "propina_aplicada": propina_aplicada,
            "bancos_pse": BANCOS_PSE,
            "metodo_seleccionado": metodo_seleccionado,
        },
    )


@require_POST
def pagar_pse(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    factura = getattr(pedido, "factura", None)
    if not factura:
        factura = facturar(pedido, request.session.get("cliente_mesa") or {})
    if factura.estado == "pagada":
        messages.info(request, "Esta factura ya está pagada.")
        return redirect("factura_cliente", pk=pedido.pk)
    if factura.metodo_pago != METODOS_PAGO_PENDIENTES["pse"]:
        messages.error(request, "Selecciona PSE antes de continuar con el pago.")
        return redirect("factura_cliente", pk=pedido.pk)

    banco_codigo = request.POST.get("banco", "").strip()
    nombre_titular = request.POST.get("nombre", "").strip()
    documento = request.POST.get("documento", "").strip()
    email = request.POST.get("email", "").strip()
    incluir_propina = request.POST.get("incluir_propina") in ("1", "true", "on")

    banco_dict = dict(BANCOS_PSE)
    banco_nombre = banco_dict.get(banco_codigo, "Banco PSE")

    subtotal = Decimal(str(pedido.total or 0))
    impuesto = (subtotal * Decimal("0.08")).quantize(Decimal("0.01"))
    propina = (subtotal * Decimal("0.10")).quantize(Decimal("0.01")) if incluir_propina else Decimal("0")
    total_final = subtotal + impuesto + propina

    # Generación de número de transacción digital PSE
    ahora = timezone.now()
    fecha_str = ahora.strftime("%Y%m%d%H%M")
    aleatorio = get_random_string(6, allowed_chars="0123456789")
    cus = f"PSE-{fecha_str}-{aleatorio}"

    factura.estado = "pagada"
    factura.metodo_pago = f"PSE - {banco_nombre}"
    factura.transaccion_id = cus
    factura.subtotal = subtotal
    factura.impuesto = impuesto
    factura.propina = propina
    factura.total = total_final
    if nombre_titular:
        factura.cliente_nombre = nombre_titular[:100]
    if documento:
        factura.cliente_documento = documento[:20]
    factura.save()

    # Si el pedido estaba activo, se actualiza a entregado
    if pedido.estado in ("pendiente", "en_preparacion", "listo"):
        pedido.estado = "entregado"
        pedido.save(update_fields=["estado"])

    # Guardar comprobante digital en sesión para respaldo
    request.session["ultimo_pago_exitoso"] = {
        "pedido_id": pedido.pk,
        "factura_id": factura.pk,
        "numero_factura": factura.numero,
        "cus": cus,
        "banco": banco_nombre,
        "titular": nombre_titular or factura.cliente_nombre or "Cliente general",
        "documento": documento or factura.cliente_documento or "-",
        "email": email or "-",
        "fecha_hora": ahora.strftime("%d/%m/%Y %I:%M %p"),
        "subtotal": float(subtotal),
        "impuesto": float(impuesto),
        "propina": float(propina),
        "total": float(total_final),
    }

    messages.success(request, f"¡Pago PSE aprobado exitosamente! Transacción {cus}.")
    return redirect("comprobante_pago", pk=pedido.pk)


def comprobante_pago(request, pk):
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related(
            "detalles__producto", "detalles__combo", "detalles__adiciones__adicion"
        ),
        pk=pk,
    )
    factura = getattr(pedido, "factura", None)
    pago_info = request.session.get("ultimo_pago_exitoso") or {}

    return render(
        request,
        "pedidos/comprobante_pago.html",
        {
            "pedido": pedido,
            "factura": factura,
            "pago_info": pago_info,
        },
    )
