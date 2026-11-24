#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
restablecer_acceso.py  -  Sabor Urbano

Crea (o restablece) las cuentas de acceso al sistema y los grupos de rol.
Es idempotente: puedes correrlo las veces que quieras, no duplica nada y
no toca los productos, las categorias ni los pedidos.

Uso:
    1) Copia este archivo al lado de manage.py
    2) Con el entorno virtual activado:
           python restablecer_acceso.py
"""

import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))


# --------------------------------------------------------------------------
# 1. Descubrir el modulo de settings del proyecto
# --------------------------------------------------------------------------
def detectar_settings():
    """Lee manage.py para saber cual es el settings real del proyecto."""
    manage = BASE / "manage.py"
    if manage.exists():
        texto = manage.read_text(encoding="utf-8", errors="ignore")
        m = re.search(
            r"DJANGO_SETTINGS_MODULE['\"]\s*,\s*['\"]([\w\.]+)['\"]", texto
        )
        if m:
            return m.group(1)

    for candidato in ("config.settings", "sistema.settings", "settings"):
        ruta = BASE / (candidato.replace(".", "/") + ".py")
        if ruta.exists():
            return candidato
    return "config.settings"


os.environ.setdefault("DJANGO_SETTINGS_MODULE", detectar_settings())

try:
    import django
except ImportError:
    print("No encuentro Django. Activa el entorno virtual primero:")
    print(r"    .\venv\Scripts\Activate.ps1")
    sys.exit(1)

try:
    django.setup()
except Exception as exc:  # settings mal escrito, app inexistente, etc.
    print("No pude iniciar Django:", exc)
    sys.exit(1)

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import OperationalError

User = get_user_model()


# --------------------------------------------------------------------------
# 2. Definicion de cuentas y roles
# --------------------------------------------------------------------------
CUENTAS = [
    {
        "username": "admin",
        "password": "Admin12345",
        "email": "admin@local.com",
        "nombre": "Administrador",
        "superuser": True,
        "grupo": "Administrador",
        "descripcion": "Admin de Django (/admin/) + panel de cocina",
    },
    {
        "username": "chef",
        "password": "Chef12345",
        "email": "chef@local.com",
        "nombre": "Chef",
        "superuser": False,
        "grupo": "Chef",
        "descripcion": "Panel de cocina (/cocina/)",
    },
]

# permisos por grupo: (app_label, codename)
PERMISOS_GRUPOS = {
    "Cliente": [
        ("menu", "view_categoria"),
        ("menu", "view_producto"),
        ("pedidos", "add_pedido"),
        ("pedidos", "add_detallepedido"),
        ("pedidos", "view_pedido"),
    ],
    "Chef": [
        ("pedidos", "view_pedido"),
        ("pedidos", "change_pedido"),
        ("pedidos", "view_detallepedido"),
        ("menu", "view_categoria"),
        ("menu", "view_producto"),
    ],
    "Administrador": [],  # el superusuario ya puede todo
}


def crear_grupos():
    creados = []
    for nombre, permisos in PERMISOS_GRUPOS.items():
        grupo, nuevo = Group.objects.get_or_create(name=nombre)
        if permisos:
            encontrados = []
            for app_label, codename in permisos:
                try:
                    p = Permission.objects.get(
                        content_type__app_label=app_label, codename=codename
                    )
                    encontrados.append(p)
                except Permission.DoesNotExist:
                    pass  # el modelo no existe en este proyecto: se ignora
            if encontrados:
                grupo.permissions.set(encontrados)
        creados.append((nombre, nuevo))
    return creados


def crear_cuenta(datos):
    usuario, nuevo = User.objects.get_or_create(
        username=datos["username"],
        defaults={"email": datos["email"]},
    )
    usuario.email = datos["email"]
    usuario.is_active = True
    usuario.is_staff = True
    usuario.is_superuser = datos["superuser"]
    if hasattr(usuario, "first_name"):
        usuario.first_name = datos["nombre"]
    usuario.set_password(datos["password"])
    usuario.save()

    try:
        grupo = Group.objects.get(name=datos["grupo"])
        usuario.groups.add(grupo)
    except Group.DoesNotExist:
        pass

    return usuario, nuevo


# --------------------------------------------------------------------------
# 3. Ejecucion
# --------------------------------------------------------------------------
def main():
    print("=" * 62)
    print(" SABOR URBANO - restablecer acceso")
    print("=" * 62)
    print(" Proyecto :", BASE)
    print(" Settings :", os.environ["DJANGO_SETTINGS_MODULE"])
    print(" Base     :", _motor())
    print("-" * 62)

    try:
        grupos = crear_grupos()
        for nombre, nuevo in grupos:
            print(("  + Grupo creado   : " if nuevo else "  = Grupo existente: ") + nombre)

        print("-" * 62)
        for datos in CUENTAS:
            usuario, nuevo = crear_cuenta(datos)
            estado = "creada" if nuevo else "clave restablecida"
            print("  {:<8} {:<22} {}".format(datos["username"], datos["password"], estado))
            print("           {}".format(datos["descripcion"]))
    except OperationalError as exc:
        print()
        print("La base de datos no tiene las tablas de Django todavia.")
        print("Detalle:", exc)
        print()
        print("Corrigelo asi, en este orden:")
        print("    python manage.py migrate")
        print("    python crear_tablas.py        (si lo tienes)")
        print("    python restablecer_acceso.py")
        return 1

    print("=" * 62)
    print(" Listo. Entra a http://127.0.0.1:8000/admin/")
    print("=" * 62)
    return 0


def _motor():
    try:
        from django.conf import settings

        db = settings.DATABASES["default"]
        return "{} ({})".format(db.get("ENGINE", "?").split(".")[-1], db.get("NAME", "?"))
    except Exception:
        return "desconocida"


if __name__ == "__main__":
    sys.exit(main())
