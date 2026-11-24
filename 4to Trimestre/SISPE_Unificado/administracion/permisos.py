from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render


DJANGO_DASHBOARD_GROUP = "Django Dashboard Only"


def obtener_rol_actual(request):
    """
    Retorna el rol normalizado, incluido el acceso limitado al Centro de Gestión.
    """
    if not request.user.is_authenticated:
        if request.session.get("cliente_mesa") or request.session.get("mesa"):
            return "cliente"
        return "anonimo"

    # 1. Sesión explícita asignada en el login
    rol_session = request.session.get("usuario_rol")
    if rol_session:
        r = str(rol_session).strip().lower()
        if r in ("administrador", "admin"):
            return "administrador"
        if r in ("cocinero", "chef"):
            return "cocinero"
        if r in ("cajero", "caja"):
            return "cajero"
        if r in ("mesero", "meseros"):
            return "mesero"
        if r in ("cliente", "clientes"):
            return "cliente"

    # 2. Superusuario de Django
    if request.user.is_superuser or request.user.groups.filter(name__in=["Administrador", "Admin"]).exists():
        return "administrador"
    if request.user.groups.filter(name=DJANGO_DASHBOARD_GROUP).exists():
        return "admin_django"

    # 3. Grupos de Django
    if request.user.groups.filter(name__in=["Chef", "Cocinero"]).exists():
        return "cocinero"
    if request.user.groups.filter(name__in=["Cajero", "Caja"]).exists():
        return "cajero"
    if request.user.groups.filter(name__in=["Mesero", "Meseros"]).exists():
        return "mesero"
    if request.user.groups.filter(name__in=["Cliente", "Clientes"]).exists():
        return "cliente"

    # 4. Consulta a Persona / PersonaHasRol en 'sistema'
    try:
        from seguimiento_pedidos.models import Persona, PersonaHasRol
        persona = Persona.objects.filter(correo_usu__iexact=request.user.email).first()
        if persona:
            rel = PersonaHasRol.objects.select_related("pkfk_idrol").filter(
                pkfk_id_usuario=persona.id_usuario,
                pkfk_tipo_doc=persona.pkfk_tipo_doc_id,
            ).first()
            if rel and rel.pkfk_idrol:
                nom = rel.pkfk_idrol.nom_rol.strip().lower()
                if "admin" in nom:
                    return "administrador"
                if "cocin" in nom or "chef" in nom:
                    return "cocinero"
                if "cajer" in nom:
                    return "cajero"
                if "meser" in nom:
                    return "mesero"
                if "client" in nom:
                    return "cliente"
    except Exception:
        pass

    return "cliente"


def tiene_rol(user, *grupos):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    grupos_normalizados = set()
    for g in grupos:
        gn = str(g).strip().lower()
        if gn in ("administrador", "admin"):
            grupos_normalizados.update(["administrador", "admin", "Administrador", "Admin"])
        elif gn in ("cocinero", "chef"):
            grupos_normalizados.update(["cocinero", "chef", "Cocinero", "Chef"])
        elif gn in ("cajero", "caja"):
            grupos_normalizados.update(["cajero", "caja", "Cajero", "Caja"])
        elif gn in ("mesero", "meseros"):
            grupos_normalizados.update(["mesero", "meseros", "Mesero", "Meseros"])
        elif gn in ("cliente", "clientes"):
            grupos_normalizados.update(["cliente", "clientes", "Cliente", "Clientes"])
        else:
            grupos_normalizados.add(g)
    return user.groups.filter(name__in=grupos_normalizados).exists()


def rol_required(*grupos):
    """
    Superusuario siempre pasa.
    Comprueba si el rol actual del usuario está incluido en los grupos permitidos.
    """
    grupos_normalizados = set()
    for g in grupos:
        gn = str(g).strip().lower()
        if gn in ("administrador", "admin"):
            grupos_normalizados.add("administrador")
        elif gn in ("cocinero", "chef"):
            grupos_normalizados.add("cocinero")
        elif gn in ("cajero", "caja"):
            grupos_normalizados.add("cajero")
        elif gn in ("mesero", "meseros"):
            grupos_normalizados.add("mesero")
        elif gn in ("cliente", "clientes"):
            grupos_normalizados.add("cliente")
        else:
            grupos_normalizados.add(gn)

    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if request.user.is_superuser:
                return vista(request, *args, **kwargs)

            rol_actual = obtener_rol_actual(request)
            if rol_actual in grupos_normalizados:
                return vista(request, *args, **kwargs)

            return render(
                request,
                "administracion/sin_permiso.html",
                {"grupos": list(grupos), "rol_usuario": rol_actual},
                status=403,
            )

        return envoltura

    return decorador


admin_required = rol_required("Administrador")
cajero_required = rol_required("Cajero", "Administrador")
cocinero_required = rol_required("Cocinero", "Administrador")
mesero_required = rol_required("Mesero", "Administrador")
