from . import carrito


def carrito_contador(request):
    """Deja disponible {{ carrito_items }} en todas las plantillas."""
    try:
        return {"carrito_items": carrito.contar(request)}
    except Exception:
        return {"carrito_items": 0}
