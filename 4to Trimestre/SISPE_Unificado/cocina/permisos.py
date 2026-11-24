"""Control de acceso por rol para la zona de cocina."""

from functools import wraps

from administracion.permisos import cocinero_required, obtener_rol_actual


def es_chef(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=["Chef", "Cocinero"]).exists()


chef_required = cocinero_required
