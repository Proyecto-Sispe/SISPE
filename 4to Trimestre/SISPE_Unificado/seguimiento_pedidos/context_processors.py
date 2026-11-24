from administracion.permisos import obtener_rol_actual


def rol_context(request):
    """
    Context processor que inyecta en todas las plantillas la información
    del rol del usuario autenticado para el renderizado dinámico del navbar.
    """
    rol = obtener_rol_actual(request)

    # Buscar pedido en sesión para acceso directo desde el navbar
    pedido_id = request.session.get("ultimo_pedido_id")
    if not pedido_id and request.session.get("mesa"):
        try:
            from pedidos.models import Pedido
            m = str(request.session.get("mesa")).strip()
            if m.isdigit():
                p = (
                    Pedido.objects.filter(id_mesa=int(m), estado__in=["pendiente", "en_preparacion", "listo"])
                    .order_by("-fecha_pedido")
                    .first()
                )
                if p:
                    pedido_id = p.pk
        except Exception:
            pass

    return {
        "rol_actual": rol,
        "es_admin": rol == "administrador",
        "es_django_admin": rol == "admin_django",
        "es_cocinero": rol == "cocinero",
        "es_cajero": rol == "cajero",
        "es_mesero": rol == "mesero",
        "es_cliente": rol == "cliente",
        "es_anonimo": rol == "anonimo",
        "rol_nombre_display": {
            "administrador": "Administrador",
            "admin_django": "Admin Django",
            "cocinero": "Cocinero",
            "cajero": "Cajero",
            "mesero": "Mesero",
            "cliente": "Cliente",
            "anonimo": "Invitado",
        }.get(rol, "Invitado"),
        "pedido_activo_id": pedido_id,
        "mesa_sesion": request.session.get("mesa", ""),
    }
