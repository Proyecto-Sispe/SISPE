"""
Carrito de compras guardado en la sesion.

Reglas:
  * El precio NUNCA se toma de la sesion: siempre se recalcula contra la base.
  * Cada linea guarda tipo (producto/combo), id, cantidad, adiciones y notas.
  * Dos lineas del mismo producto con adiciones distintas son lineas distintas.
"""

from decimal import Decimal

from menu.models import Adicion, Combo, Producto

CLAVE_SESION = "carrito"


def _carrito(request):
    return request.session.setdefault(CLAVE_SESION, {})


def clave_linea(tipo, oid, adiciones=None, notas=""):
    ad = "-".join(str(int(a)) for a in sorted(adiciones or []))
    limpio = (notas or "").strip()[:40]
    return f"{tipo}:{int(oid)}:{ad}:{limpio}"


def _adiciones_validas(tipo, oid, ids):
    """Devuelve las adiciones que de verdad aplican a ese producto o combo."""
    if not ids:
        return []
    consulta = Adicion.objects.filter(activa=True, id_adicion__in=ids)
    if tipo == "producto":
        producto = Producto.objects.filter(pk=oid).first()
        if not producto:
            return []
        consulta = consulta.filter(categoria__isnull=True) | consulta.filter(
            categoria_id=producto.categoria_id
        )
    return list(consulta.distinct())


def agregar(request, tipo, oid, cantidad=1, adiciones=None, notas=""):
    cantidad = max(int(cantidad or 1), 1)
    adiciones = [int(a) for a in (adiciones or [])]
    clave = clave_linea(tipo, oid, adiciones, notas)
    carrito = _carrito(request)
    if clave in carrito:
        carrito[clave]["cantidad"] += cantidad
    else:
        carrito[clave] = {
            "tipo": tipo,
            "id": int(oid),
            "cantidad": cantidad,
            "adiciones": adiciones,
            "notas": (notas or "").strip()[:200],
        }
    request.session.modified = True
    return clave


def cambiar_cantidad(request, clave, cantidad):
    carrito = _carrito(request)
    if clave not in carrito:
        return
    cantidad = int(cantidad)
    if cantidad <= 0:
        carrito.pop(clave, None)
    else:
        carrito[clave]["cantidad"] = min(cantidad, 99)
    request.session.modified = True


def quitar(request, clave):
    carrito = _carrito(request)
    carrito.pop(clave, None)
    request.session.modified = True


def vaciar(request):
    request.session[CLAVE_SESION] = {}
    request.session.modified = True


def contar(request):
    return sum(item.get("cantidad", 0) for item in _carrito(request).values())


def lineas(request):
    """Lineas del carrito con precios recalculados desde la base."""
    carrito = _carrito(request)
    resultado = []
    ids_producto = [i["id"] for i in carrito.values() if i["tipo"] == "producto"]
    ids_combo = [i["id"] for i in carrito.values() if i["tipo"] == "combo"]

    productos = {p.pk: p for p in Producto.objects.filter(pk__in=ids_producto)}
    combos = {
        c.pk: c
        for c in Combo.objects.filter(pk__in=ids_combo).prefetch_related(
            "items__producto"
        )
    }

    for clave, item in carrito.items():
        cantidad = int(item.get("cantidad", 1))
        adiciones = _adiciones_validas(item["tipo"], item["id"], item.get("adiciones"))
        extra = sum((a.precio for a in adiciones), Decimal("0"))

        if item["tipo"] == "producto":
            objeto = productos.get(item["id"])
            if not objeto or not objeto.disponible:
                continue
            base = objeto.precio or Decimal("0")
            nombre = objeto.nombre
            detalle = objeto.descripcion
            foto = objeto.foto if objeto.tiene_foto else None
        else:
            objeto = combos.get(item["id"])
            if not objeto or not objeto.activo:
                continue
            base = objeto.precio or Decimal("0")
            nombre = objeto.nombre
            detalle = " + ".join(objeto.resumen)
            foto = objeto.foto if objeto.tiene_foto else None

        unitario = base + extra
        resultado.append(
            {
                "clave": clave,
                "tipo": item["tipo"],
                "objeto": objeto,
                "nombre": nombre,
                "detalle": detalle,
                "foto": foto,
                "cantidad": cantidad,
                "base": base,
                "adiciones": adiciones,
                "extra": extra,
                "unitario": unitario,
                "subtotal": unitario * cantidad,
                "notas": item.get("notas", ""),
            }
        )
    return resultado


def total(request):
    return sum((l["subtotal"] for l in lineas(request)), Decimal("0"))


def resumen_texto(linea):
    partes = [a.nombre for a in linea["adiciones"]]
    return ", ".join(partes)
