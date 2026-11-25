"""Módulo de administración: usuarios, menú, inventario, facturas y pedidos activos."""

from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from menu.models import Categoria, Producto
from pedidos.models import Pedido
from seguimiento_pedidos.models import Persona, PersonaHasRol, Rol

from . import inventario
from .forms import InsumoForm, PersonaForm, RecetaForm
from .models import Factura, Insumo, MovimientoInventario, ProductoInsumo
from .permisos import admin_required, cajero_required

POR_PAGINA = 25


def _decimal(valor):
    try:
        return Decimal(str(valor).replace(",", ".").strip())
    except (InvalidOperation, AttributeError):
        return None


def _paginar(request, objetos, por_pagina=POR_PAGINA):
    pagina = Paginator(objetos, por_pagina).get_page(request.GET.get("page"))
    filtros = request.GET.copy()
    filtros.pop("page", None)
    return pagina, filtros.urlencode()


def _volver(request, defecto):
    destino = request.POST.get("next") or request.GET.get("next")
    if destino and url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}):
        return redirect(destino)
    return redirect(defecto)


# --------------------------------------------------------------------------
# Usuarios (tabla Persona del esquema SISPE)
# --------------------------------------------------------------------------
def _roles_por_persona():
    return {
        (r.pkfk_id_usuario, r.pkfk_tipo_doc): r.pkfk_idrol
        for r in PersonaHasRol.objects.select_related("pkfk_idrol")
    }


@admin_required
def usuarios(request):
    q = request.GET.get("q", "").strip()
    rol = request.GET.get("rol", "")
    estado = request.GET.get("estado", "")

    personas = Persona.objects.select_related("pkfk_tipo_doc").order_by("nom1_usu", "ape1_usu")
    if q:
        filtro = (
            Q(nom1_usu__icontains=q)
            | Q(nom2_usu__icontains=q)
            | Q(ape1_usu__icontains=q)
            | Q(ape2_usu__icontains=q)
            | Q(correo_usu__icontains=q)
        )
        if q.isdigit():
            filtro |= Q(id_usuario=int(q)) | Q(telefono=int(q))
        personas = personas.filter(filtro)
    if estado == "activo":
        personas = personas.filter(estado=1)
    elif estado == "inactivo":
        personas = personas.exclude(estado=1)

    roles = _roles_por_persona()
    filas = []
    for p in personas:
        r = roles.get((p.id_usuario, p.pkfk_tipo_doc_id))
        if rol and (not r or str(r.idrol) != rol):
            continue
        filas.append({"persona": p, "rol": r})

    return render(
        request,
        "administracion/usuarios.html",
        {"filas": filas, "q": q, "rol": rol, "estado": estado, "roles": Rol.objects.order_by("idrol")},
    )


def _sincronizar_usuario_django(
    correo_anterior, persona, rol_nombre, password_actualizada=False
):
    """Mantiene al día el usuario Django creado en el login (grupo, nombre, activo)."""
    from seguimiento_pedidos.views import _usuario_django

    User = get_user_model()
    usuario = User.objects.filter(username=(correo_anterior or "").lower()).first()
    if not usuario:
        return
    usuario.username = persona.correo_usu.lower()
    usuario.is_active = persona.estado == 1
    if password_actualizada:
        usuario.password = persona.password
    usuario.save()
    _usuario_django(persona, rol_nombre.lower())


@admin_required
def usuario_crear(request):
    form = PersonaForm(request.POST or None, creando=True)
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        if Persona.objects.filter(id_usuario=d["numero"], pkfk_tipo_doc_id=d["tipo_doc"]).exists():
            form.add_error("numero", "Ya existe una persona con ese documento.")
        elif Persona.objects.filter(correo_usu__iexact=d["correo"]).exists():
            form.add_error("correo", "Ese correo ya está registrado.")
        else:
            with transaction.atomic(using="sistema"):
                Persona.objects.create(
                    id_usuario=d["numero"],
                    pkfk_tipo_doc_id=int(d["tipo_doc"]),
                    nom1_usu=d["nom1"],
                    nom2_usu=d["nom2"] or None,
                    ape1_usu=d["ape1"],
                    ape2_usu=d["ape2"] or None,
                    telefono=d["telefono"],
                    correo_usu=d["correo"],
                    password=make_password(d["password"]),
                    estado=1 if d["activo"] else 0,
                )
                PersonaHasRol.objects.create(
                    pkfk_id_usuario=d["numero"],
                    pkfk_tipo_doc=int(d["tipo_doc"]),
                    pkfk_idrol_id=int(d["rol"]),
                )
            messages.success(request, f"Usuario {d['nom1']} {d['ape1']} registrado.")
            return redirect("adm_usuarios")
    return render(request, "administracion/usuario_form.html", {"form": form, "modo": "crear"})


@admin_required
def usuario_editar(request, tipo, numero):
    persona = get_object_or_404(Persona, id_usuario=numero, pkfk_tipo_doc_id=tipo)
    rol_actual = _roles_por_persona().get((persona.id_usuario, persona.pkfk_tipo_doc_id))
    inicial = {
        "tipo_doc": persona.pkfk_tipo_doc_id,
        "numero": persona.id_usuario,
        "nom1": persona.nom1_usu,
        "nom2": persona.nom2_usu,
        "ape1": persona.ape1_usu,
        "ape2": persona.ape2_usu,
        "telefono": persona.telefono,
        "correo": persona.correo_usu,
        "rol": rol_actual.idrol if rol_actual else None,
        "activo": persona.estado == 1,
    }
    form = PersonaForm(request.POST or None, initial=inicial, creando=False)
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        repetido = (
            Persona.objects.filter(correo_usu__iexact=d["correo"])
            .exclude(id_usuario=numero, pkfk_tipo_doc_id=tipo)
            .exists()
        )
        if repetido:
            form.add_error("correo", "Ese correo ya está registrado.")
        else:
            cambios = {
                "nom1_usu": d["nom1"],
                "nom2_usu": d["nom2"] or None,
                "ape1_usu": d["ape1"],
                "ape2_usu": d["ape2"] or None,
                "telefono": d["telefono"],
                "correo_usu": d["correo"],
                "estado": 1 if d["activo"] else 0,
            }
            if d["password"]:
                cambios["password"] = make_password(d["password"])
            with transaction.atomic(using="sistema"):
                Persona.objects.filter(id_usuario=numero, pkfk_tipo_doc_id=tipo).update(**cambios)
                PersonaHasRol.objects.filter(pkfk_id_usuario=numero, pkfk_tipo_doc=tipo).delete()
                PersonaHasRol.objects.create(
                    pkfk_id_usuario=numero, pkfk_tipo_doc=tipo, pkfk_idrol_id=int(d["rol"])
                )
            persona = Persona.objects.get(id_usuario=numero, pkfk_tipo_doc_id=tipo)
            _sincronizar_usuario_django(
                inicial["correo"],
                persona,
                Rol.objects.get(pk=d["rol"]).nom_rol,
                password_actualizada=bool(d["password"]),
            )
            messages.success(request, "Cambios guardados.")
            return redirect("adm_usuarios")
    return render(
        request,
        "administracion/usuario_form.html",
        {"form": form, "modo": "editar", "persona": persona},
    )


# --------------------------------------------------------------------------
# Menú
# --------------------------------------------------------------------------
@admin_required
def menu(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "")
    disp = request.GET.get("disp", "")
    pmin = _decimal(request.GET.get("pmin", ""))
    pmax = _decimal(request.GET.get("pmax", ""))
    receta = request.GET.get("receta", "")
    orden = request.GET.get("orden", "nombre")

    productos = Producto.objects.select_related("categoria").annotate(n_insumos=Count("receta"))
    if q:
        filtro = Q(nombre__icontains=q) | Q(descripcion__icontains=q) | Q(categoria__nom_categoria__icontains=q)
        if q.isdigit():
            filtro |= Q(pk=int(q))
        productos = productos.filter(filtro)
    if cat:
        productos = productos.filter(categoria_id=cat)
    if disp == "si":
        productos = productos.filter(disponible=True)
    elif disp == "no":
        productos = productos.filter(disponible=False)
    if pmin is not None:
        productos = productos.filter(precio__gte=pmin)
    if pmax is not None:
        productos = productos.filter(precio__lte=pmax)
    if receta == "con":
        productos = productos.filter(n_insumos__gt=0)
    elif receta == "sin":
        productos = productos.filter(n_insumos=0)
    ordenes = {"nombre": "nombre", "precio": "precio", "-precio": "-precio", "categoria": "categoria__nom_categoria"}
    productos = productos.order_by(ordenes.get(orden, "nombre"), "nombre")

    pagina, filtros = _paginar(request, productos)
    return render(
        request,
        "administracion/menu.html",
        {
            "pagina": pagina,
            "filtros": filtros,
            "categorias": Categoria.objects.order_by("orden", "nom_categoria"),
            "q": q,
            "cat": cat,
            "disp": disp,
            "pmin": request.GET.get("pmin", ""),
            "pmax": request.GET.get("pmax", ""),
            "receta": receta,
            "orden": orden,
            "total": productos.count(),
        },
    )


@require_POST
@admin_required
def menu_disponible(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.disponible = not producto.disponible
    producto.save(update_fields=["disponible"])
    estado = "disponible" if producto.disponible else "no disponible"
    messages.success(request, f"{producto.nombre}: {estado}.")
    return _volver(request, "adm_menu")


# --------------------------------------------------------------------------
# Inventario
# --------------------------------------------------------------------------
@admin_required
def inventario_lista(request):
    q = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "")
    unidad = request.GET.get("unidad", "")

    insumos = Insumo.objects.annotate(n_productos=Count("recetas"))
    if q:
        insumos = insumos.filter(Q(nombre__icontains=q) | Q(recetas__producto__nombre__icontains=q)).distinct()
    if unidad:
        insumos = insumos.filter(unidad=unidad)
    insumos = list(insumos)
    if estado:
        insumos = [i for i in insumos if i.estado_stock == estado]

    todos = list(Insumo.objects.all())
    return render(
        request,
        "administracion/inventario.html",
        {
            "insumos": insumos,
            "q": q,
            "estado": estado,
            "unidad": unidad,
            "unidades": sorted({i.unidad for i in todos}),
            "resumen": {
                "total": len(todos),
                "bajo": sum(1 for i in todos if i.estado_stock == "bajo"),
                "agotado": sum(1 for i in todos if i.estado_stock == "agotado"),
            },
            "movimientos": MovimientoInventario.objects.select_related("insumo")[:15],
        },
    )


@require_POST
@admin_required
def inventario_mover(request, pk):
    insumo = get_object_or_404(Insumo, pk=pk)
    cantidad = _decimal(request.POST.get("cantidad", ""))
    accion = request.POST.get("accion")
    if cantidad is None or cantidad <= 0:
        messages.error(request, "Escribe una cantidad mayor que cero.")
    elif accion == "descontar" and cantidad > insumo.stock_actual:
        messages.error(request, f"No hay suficiente {insumo.nombre}: quedan {insumo.stock_actual:g}.")
    else:
        signo = 1 if accion == "agregar" else -1
        with transaction.atomic():
            inventario.mover(
                insumo.pk,
                signo * cantidad,
                "entrada" if signo > 0 else "salida",
                motivo=request.POST.get("motivo", "")[:200],
                usuario=request.user.get_username(),
            )
        verbo = "Agregaste" if signo > 0 else "Descontaste"
        messages.success(request, f"{verbo} {cantidad:g} {insumo.unidad} de {insumo.nombre}.")
    return _volver(request, "adm_inventario")


@admin_required
def insumo_form(request, pk=None):
    insumo = get_object_or_404(Insumo, pk=pk) if pk else None
    form = InsumoForm(request.POST or None, instance=insumo)
    if request.method == "POST" and form.is_valid():
        nuevo = form.save()
        messages.success(request, f"Insumo {nuevo.nombre} guardado.")
        return redirect("adm_inventario")
    return render(request, "administracion/insumo_form.html", {"form": form, "insumo": insumo})


@admin_required
def recetas(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "")
    sin_receta = request.GET.get("sin_receta") == "1"
    productos = Producto.objects.select_related("categoria").prefetch_related("receta__insumo").order_by("nombre")
    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(receta__insumo__nombre__icontains=q)).distinct()
    if cat:
        productos = productos.filter(categoria_id=cat)
    if sin_receta:
        productos = productos.annotate(n_insumos=Count("receta")).filter(n_insumos=0)
    pagina, filtros = _paginar(request, productos, 20)
    return render(
        request,
        "administracion/recetas.html",
        {
            "pagina": pagina,
            "filtros": filtros,
            "q": q,
            "cat": cat,
            "sin_receta": sin_receta,
            "productos_sin_receta": Producto.objects.filter(disponible=True)
            .annotate(n_insumos=Count("receta"))
            .filter(n_insumos=0)
            .count(),
            "categorias": Categoria.objects.order_by("orden", "nom_categoria"),
        },
    )


@admin_required
def receta_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = RecetaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        receta, creada = ProductoInsumo.objects.update_or_create(
            producto=producto,
            insumo=form.cleaned_data["insumo"],
            defaults={"cantidad": form.cleaned_data["cantidad"]},
        )
        messages.success(request, f"{'Agregado' if creada else 'Actualizado'}: {receta.insumo.nombre}.")
        return redirect("adm_receta", pk=producto.pk)
    return render(
        request,
        "administracion/receta_producto.html",
        {"producto": producto, "receta": producto.receta.select_related("insumo"), "form": form},
    )


@require_POST
@admin_required
def receta_quitar(request, pk):
    receta = get_object_or_404(ProductoInsumo, pk=pk)
    producto_id = receta.producto_id
    receta.delete()
    messages.success(request, "Insumo quitado de la receta.")
    return redirect("adm_receta", pk=producto_id)


# --------------------------------------------------------------------------
# Facturas
# --------------------------------------------------------------------------
def _rango(periodo, desde, hasta):
    hoy = date.today()
    if periodo == "hoy":
        return hoy, hoy
    if periodo == "ayer":
        return hoy - timedelta(days=1), hoy - timedelta(days=1)
    if periodo == "semana":
        return hoy - timedelta(days=hoy.weekday()), hoy
    if periodo == "mes":
        return hoy.replace(day=1), hoy
    if periodo == "anio":
        return hoy.replace(month=1, day=1), hoy
    return desde or None, hasta or None


@cajero_required
def facturas(request):
    q = request.GET.get("q", "").strip()
    mesa = request.GET.get("mesa", "")
    periodo = request.GET.get("periodo", "")
    estado = request.GET.get("estado", "")
    tmin = _decimal(request.GET.get("tmin", ""))
    tmax = _decimal(request.GET.get("tmax", ""))
    desde, hasta = _rango(periodo, request.GET.get("desde", ""), request.GET.get("hasta", ""))

    lista = Factura.objects.all()
    if q:
        numero = q.upper().replace("F-", "").lstrip("0")
        filtro = Q(cliente_nombre__icontains=q) | Q(cliente_documento__icontains=q)
        if numero.isdigit():
            filtro |= Q(pk=int(numero)) | Q(pedido_id=int(numero))
        lista = lista.filter(filtro)
    if mesa:
        lista = lista.filter(mesa=mesa)
    if desde:
        lista = lista.filter(fecha__date__gte=desde)
    if hasta:
        lista = lista.filter(fecha__date__lte=hasta)
    if estado:
        lista = lista.filter(estado=estado)
    if tmin is not None:
        lista = lista.filter(total__gte=tmin)
    if tmax is not None:
        lista = lista.filter(total__lte=tmax)

    resumen = lista.filter(estado="emitida").aggregate(total=Sum("total"), n=Count("id"))
    pagina, filtros = _paginar(request, lista)
    return render(
        request,
        "administracion/facturas.html",
        {
            "pagina": pagina,
            "filtros": filtros,
            "q": q,
            "mesa": mesa,
            "periodo": periodo,
            "estado": estado,
            "desde": request.GET.get("desde", ""),
            "hasta": request.GET.get("hasta", ""),
            "tmin": request.GET.get("tmin", ""),
            "tmax": request.GET.get("tmax", ""),
            "mesas": Factura.objects.order_by("mesa").values_list("mesa", flat=True).distinct(),
            "suma": resumen["total"] or 0,
            "emitidas": resumen["n"],
            "rango": (desde, hasta),
        },
    )


@cajero_required
def factura_detalle(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    pedido = (
        Pedido.objects.filter(pk=factura.pedido_id)
        .prefetch_related("detalles__producto", "detalles__combo", "detalles__adiciones__adicion")
        .first()
    )
    return render(request, "administracion/factura_detalle.html", {"factura": factura, "pedido": pedido})


# --------------------------------------------------------------------------
# Pedidos activos
# --------------------------------------------------------------------------
@cajero_required
def pedidos_activos(request):
    activos = list(
        Pedido.objects.filter(estado__in=["pendiente", "en_preparacion", "listo"])
        .prefetch_related("detalles__producto", "detalles__combo", "detalles__adiciones__adicion")
        .order_by("fecha_pedido")
    )
    clientes = {
        f.pedido_id: f for f in Factura.objects.filter(pedido_id__in=[p.pk for p in activos])
    }
    for p in activos:
        p.factura_info = clientes.get(p.pk)
    return render(request, "administracion/pedidos_activos.html", {"pedidos": activos})
