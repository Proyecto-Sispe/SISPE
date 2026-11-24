"""Vistas publicas: carta del cliente, portada de roles y codigos QR."""

import json
import socket
from decimal import Decimal

from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from . import qr
from .models import Adicion, Categoria, Combo, Producto


def _ips_locales():
    """IPs de la red del equipo, para el selector de host de los QR."""
    ips = []
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = info[4][0]
            if ip not in ips and not ip.startswith("127."):
                ips.append(ip)
    except Exception:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip not in ips and not ip.startswith("127."):
            ips.insert(0, ip)
    except Exception:
        pass
    return ips


def _host_efectivo(request):
    host = request.GET.get("host", "").strip()
    if host:
        return host
    return request.get_host()


def _sin_registro_en_mesa(request, mesa):
    """True si un cliente anónimo llega a una mesa real sin pasar por la bienvenida."""
    if not mesa.isdigit() or request.user.is_authenticated:
        return False
    from mesas_pedidos.models import Mesa, SesionMesa

    cliente = request.session.get("cliente_mesa") or {}
    if cliente.get("mesa") == int(mesa) and SesionMesa.objects.filter(
        pk=cliente.get("sesion"), activa=True
    ).exists():
        return False
    return Mesa.objects.filter(pk=int(mesa)).exists()


def carta(request):
    mesa = request.GET.get("mesa", "").strip()
    if _sin_registro_en_mesa(request, mesa):
        return redirect("escanear_mesa", id_mesa=int(mesa))
    if mesa:
        request.session["mesa"] = mesa
    else:
        mesa = request.session.get("mesa", "")

    busqueda = request.GET.get("q", "").strip()
    cat_filtro = request.GET.get("cat", "").strip()

    categorias = list(Categoria.objects.filter(activa=True))
    productos = list(
        Producto.objects.filter(disponible=True).select_related("categoria")
    )

    if busqueda:
        texto = busqueda.lower()
        productos = [
            p
            for p in productos
            if texto in (p.nombre or "").lower()
            or texto in (p.descripcion or "").lower()
        ]
    if cat_filtro:
        productos = [p for p in productos if str(p.categoria_id) == cat_filtro]

    # agrupados por categoria, en el orden de la categoria
    grupos = []
    for categoria in categorias:
        suyos = [p for p in productos if p.categoria_id == categoria.id_categoria]
        if suyos:
            grupos.append({"categoria": categoria, "productos": suyos})

    combos = list(
        Combo.objects.filter(activo=True).prefetch_related("items__producto")
    )
    if busqueda:
        texto = busqueda.lower()
        combos = [
            c
            for c in combos
            if texto in (c.nombre or "").lower()
            or texto in (c.descripcion or "").lower()
        ]
    if cat_filtro:
        combos = []

    # adiciones por producto, en JSON para el panel de personalizacion
    adiciones = list(Adicion.objects.filter(activa=True))
    mapa_adiciones = {}
    for producto in productos:
        aplicables = [
            a
            for a in adiciones
            if a.categoria_id in (None, producto.categoria_id)
        ]
        if aplicables:
            mapa_adiciones[producto.pk] = [
                {
                    "id": a.id_adicion,
                    "nombre": a.nombre,
                    "precio": float(a.precio or 0),
                }
                for a in aplicables
            ]

    adiciones_combo = [
        {"id": a.id_adicion, "nombre": a.nombre, "precio": float(a.precio or 0)}
        for a in adiciones
    ]

    contexto = {
        "mesa": mesa,
        "categorias": categorias,
        "grupos": grupos,
        "combos": combos,
        "busqueda": busqueda,
        "cat_filtro": cat_filtro,
        "total_productos": len(productos),
        "adiciones_json": json.dumps(mapa_adiciones),
        "adiciones_combo_json": json.dumps(adiciones_combo),
        "hay_adiciones": bool(adiciones),
        "host": _host_efectivo(request),
    }
    return render(request, "menu/carta.html", contexto)


def roles(request):
    return render(request, "roles.html", {"ips": _ips_locales()})


# --------------------------------------------------------------------------
# Codigos QR de las mesas
# --------------------------------------------------------------------------
def qr_mesa(request, mesa):
    host = _host_efectivo(request)
    destino = qr.url_carta(host, mesa)
    uri = qr.data_uri(destino)
    contexto = {
        "mesa": mesa,
        "destino": destino,
        "host": host,
        "imagen": uri,
        "respaldo": None if uri else qr.url_respaldo(destino),
        "motor": qr.motor(),
        "ips": _ips_locales(),
    }
    return render(request, "menu/qr.html", contexto)


def qr_imagen(request, mesa):
    host = _host_efectivo(request)
    destino = qr.url_carta(host, mesa)
    png = qr.generar_png(destino)
    if not png:
        raise Http404("No hay generador de QR instalado (pip install segno)")
    respuesta = HttpResponse(png, content_type="image/png")
    respuesta["Content-Disposition"] = f'inline; filename="qr_mesa_{mesa}.png"'
    return respuesta
