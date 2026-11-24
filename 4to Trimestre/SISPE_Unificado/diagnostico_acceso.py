#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
diagnostico_acceso.py  -  Sabor Urbano
======================================

Sirve cuando /admin/ responde:

    "Por favor ingrese el nombre de usuario y la clave correctos
     para obtener cuenta de personal."

Ese mensaje NO dice cual es el problema, solo que el par usuario/clave no
sirve. Este script revisa las cuatro causas posibles y arregla la que
encuentre:

    1. La base de datos que se esta usando no es la que crees
       (otra ruta, otro db.sqlite3, o MySQL en vez de SQLite).
    2. La base no tiene las tablas de usuarios (falta migrate).
    3. El usuario no existe, o existe pero esta inactivo / sin permiso
       de staff / con la clave vencida o inservible.
    4. La clave simplemente no coincide (distingue mayusculas).

Al final crea o restablece las cuentas y PRUEBA el login de verdad, con el
cliente de pruebas de Django, antes de decirte que quedo listo.

Uso (en la carpeta donde esta manage.py, con el entorno virtual activado):

    python diagnostico_acceso.py              # diagnostica y arregla
    python diagnostico_acceso.py --solo-ver   # solo diagnostica, no toca nada

Es idempotente: no borra productos, categorias, pedidos ni nada del menu.
"""

import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

SOLO_VER = "--solo-ver" in sys.argv or "--solo_ver" in sys.argv

LINEA = "=" * 68
SUB = "-" * 68


# --------------------------------------------------------------------------
# Arranque de Django (detecta el settings real leyendo manage.py)
# --------------------------------------------------------------------------
def detectar_settings():
    manage = BASE / "manage.py"
    if manage.exists():
        texto = manage.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"DJANGO_SETTINGS_MODULE['\"]\s*,\s*['\"]([\w\.]+)['\"]", texto)
        if m:
            return m.group(1)
    for candidato in ("config.settings", "sistema.settings", "settings"):
        if (BASE / (candidato.replace(".", "/") + ".py")).exists():
            return candidato
    return "config.settings"


os.environ.setdefault("DJANGO_SETTINGS_MODULE", detectar_settings())

try:
    import django
except ImportError:
    print("No encuentro Django en este Python.")
    print("Activa primero el entorno virtual del proyecto, por ejemplo:")
    print(r"    .\venv\Scripts\Activate.ps1")
    sys.exit(1)

try:
    django.setup()
except Exception as exc:
    print("No pude iniciar Django:", exc)
    print("Revisa que estes corriendo el script en la carpeta de manage.py.")
    sys.exit(1)

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connection
from django.test import Client

User = get_user_model()

CUENTAS = [
    ("admin", "Admin12345", True, "Administrador"),
    ("chef", "Chef12345", False, "Chef"),
]


# --------------------------------------------------------------------------
# 1. Que base de datos se esta usando de verdad
# --------------------------------------------------------------------------
def describir_base():
    db = settings.DATABASES["default"]
    engine = db.get("ENGINE", "?")
    nombre = str(db.get("NAME", "?"))
    if "sqlite" in engine:
        ruta = Path(nombre)
        if not ruta.is_absolute():
            ruta = (BASE / ruta).resolve()
        if ruta.exists():
            kb = ruta.stat().st_size / 1024
            return "SQLite  ->  {}  ({} KB)".format(ruta, round(kb))
        return "SQLite  ->  {}  (EL ARCHIVO NO EXISTE)".format(ruta)
    return "{}  ->  {} en {}:{}".format(
        engine.split(".")[-1],
        nombre,
        db.get("HOST") or "localhost",
        db.get("PORT") or "3306",
    )


def tablas_de_usuario():
    """Devuelve (ok, detalle). Comprueba que auth_user exista y se lea."""
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM auth_user")
            cur.fetchone()
        return True, ""
    except Exception as exc:
        return False, str(exc).strip()


def contar_menu():
    """Sirve para saber si estamos en la base buena o en una vacia."""
    try:
        from menu.models import Producto

        return Producto.objects.count()
    except Exception:
        return None


# --------------------------------------------------------------------------
# 2. Estado de las cuentas
# --------------------------------------------------------------------------
def listar_usuarios():
    total = User.objects.count()
    print("  Usuarios registrados: {}".format(total))
    if total == 0:
        print("  (ninguno: la tabla existe pero esta vacia)")
        return
    print()
    print("  {:<16} {:<8} {:<7} {:<7} {:<8} {}".format(
        "USUARIO", "ACTIVO", "STAFF", "SUPER", "CLAVE", "GRUPOS"))
    for u in User.objects.all().order_by("username"):
        grupos = ", ".join(u.groups.values_list("name", flat=True)) or "-"
        print("  {:<16} {:<8} {:<7} {:<7} {:<8} {}".format(
            u.username,
            "si" if u.is_active else "NO",
            "si" if u.is_staff else "NO",
            "si" if u.is_superuser else "NO",
            "si" if u.has_usable_password() else "NO",
            grupos,
        ))


def asegurar_grupos():
    for nombre in ("Cliente", "Chef", "Administrador"):
        Group.objects.get_or_create(name=nombre)


def arreglar_cuenta(username, password, superuser, grupo):
    usuario, creado = User.objects.get_or_create(username=username)
    usuario.is_active = True
    usuario.is_staff = True
    usuario.is_superuser = superuser
    if hasattr(usuario, "email") and not usuario.email:
        usuario.email = "{}@local.com".format(username)
    usuario.set_password(password)
    usuario.save()
    try:
        usuario.groups.add(Group.objects.get(name=grupo))
    except Group.DoesNotExist:
        pass
    return usuario, creado


# --------------------------------------------------------------------------
# 3. Prueba real del login contra /admin/
# --------------------------------------------------------------------------
def probar_admin(username, password):
    cliente = Client()
    try:
        resp = cliente.post(
            "/admin/login/",
            {"username": username, "password": password, "next": "/admin/"},
        )
    except Exception as exc:
        return False, "no se pudo abrir /admin/login/ ({})".format(exc)

    if resp.status_code == 302 and "/admin" in resp.get("Location", ""):
        panel = cliente.get("/admin/")
        if panel.status_code == 200:
            return True, "entra a /admin/ y el panel responde 200"
        return True, "login aceptado, pero /admin/ responde {}".format(panel.status_code)

    detalle = ""
    try:
        ctx = resp.context
        if ctx is not None:
            formulario = ctx.get("form") if hasattr(ctx, "get") else None
            if formulario is not None and formulario.errors:
                detalle = " | ".join(
                    "{}: {}".format(campo, " ".join(errs))
                    for campo, errs in formulario.errors.items()
                )
    except Exception:
        pass
    return False, "rechazado (HTTP {}) {}".format(resp.status_code, detalle).strip()


def probar_login_propio(username, password):
    """El login del sistema (/login/) manda al panel de cocina."""
    cliente = Client()
    try:
        resp = cliente.post("/login/", {"username": username, "password": password})
    except Exception as exc:
        return False, "no se pudo abrir /login/ ({})".format(exc)
    if resp.status_code == 302:
        return True, "redirige a {}".format(resp.get("Location", "?"))
    return False, "HTTP {}".format(resp.status_code)


# --------------------------------------------------------------------------
# 4. Programa principal
# --------------------------------------------------------------------------
def main():
    print(LINEA)
    print(" SABOR URBANO - diagnostico de acceso")
    print(LINEA)
    print(" Carpeta  :", BASE)
    print(" Settings :", os.environ["DJANGO_SETTINGS_MODULE"])
    print(" Base     :", describir_base())
    print(" Django   :", django.get_version())
    if os.environ.get("SABOR_DB", "").lower() == "mysql":
        print(" Aviso    : SABOR_DB=mysql, estas trabajando sobre MySQL,")
        print("            no sobre db.sqlite3. La cuenta debe existir ALLI.")
    print(SUB)

    ok, detalle = tablas_de_usuario()
    if not ok:
        print(" PROBLEMA 1: la base no tiene las tablas de usuarios de Django.")
        print(" Detalle:", detalle)
        print()
        print(" Solucion, en este orden:")
        print("     python manage.py migrate")
        print("     python crear_tablas.py        (si lo tienes)")
        print("     python diagnostico_acceso.py")
        print(LINEA)
        return 1

    productos = contar_menu()
    if productos is None:
        print(" No pude leer la tabla del menu (falta correr crear_tablas.py")
        print(" o la base no es la del proyecto).")
    else:
        print(" Productos en la base: {}".format(productos))
        if productos == 0:
            print(" Ojo: la base esta vacia de menu. Puede ser otro archivo")
            print("      db.sqlite3 distinto al que creias.")
    print(SUB)

    print(" Estado actual de las cuentas:")
    listar_usuarios()
    print(SUB)

    if SOLO_VER:
        print(" Modo --solo-ver: no modifique nada.")
        print(LINEA)
        return 0

    print(" Restableciendo cuentas...")
    asegurar_grupos()
    for username, password, superuser, grupo in CUENTAS:
        usuario, creado = arreglar_cuenta(username, password, superuser, grupo)
        print("   {:<8} clave {:<12} {}".format(
            username, password, "creada" if creado else "restablecida"))
    print(SUB)

    print(" Probando el login de verdad:")
    fallos = 0
    for username, password, superuser, grupo in CUENTAS:
        ok_admin, detalle_admin = probar_admin(username, password)
        print("   {:<8} /admin/  {}".format(username, "OK  - " + detalle_admin if ok_admin else "FALLA - " + detalle_admin))
        if not ok_admin:
            fallos += 1
        ok_propio, detalle_propio = probar_login_propio(username, password)
        print("   {:<8} /login/  {}".format(username, "OK  - " + detalle_propio if ok_propio else "FALLA - " + detalle_propio))
    print(LINEA)

    if fallos:
        print(" El login sigue fallando. Copiame esta salida completa y lo reviso.")
        print(LINEA)
        return 2

    print(" LISTO. Entra con:")
    print("     http://127.0.0.1:8000/admin/     usuario: admin   clave: Admin12345")
    print("     http://127.0.0.1:8000/login/     usuario: chef    clave: Chef12345")
    print()
    print(" La clave distingue mayusculas: Admin12345 lleva A mayuscula y")
    print(" no lleva espacios. Si el campo Contrasena queda vacio, el error")
    print(" que ves es exactamente el mismo.")
    print(LINEA)
    return 0


if __name__ == "__main__":
    sys.exit(main())
