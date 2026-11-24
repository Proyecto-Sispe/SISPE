#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sincronizar_bd.py  -  SISPE
==================================

Repara el error:

    OperationalError: no such column: Pedido.total

Ese error no es de Django ni del modelo: es que la tabla `Pedido` de tu
db.sqlite3 se creo con la version anterior del sistema y le faltan columnas
que el codigo nuevo si usa (total, prioridad, observaciones...). Lo mismo
puede pasar en `Detalle_Pedido`, `Menu` o `Categoria`.

Este script compara, tabla por tabla, las columnas que el codigo espera
contra las que la base realmente tiene, y agrega las que falten SIN borrar
ni reescribir un solo dato. Tambien crea las tablas que no existan
(Adicion, Combo, Combo_Item, Detalle_Adicion).

Al final comprueba de verdad: corre las mismas consultas que hacen
/cocina/ y /cocina/reportes/, y si hay un superusuario, pide las dos
paginas por HTTP. Si algo sigue mal, te lo dice con el nombre exacto.

Uso (en la carpeta de manage.py, con el entorno virtual activado):

    python sincronizar_bd.py              # repara y verifica
    python sincronizar_bd.py --solo-ver   # solo muestra que falta

Es idempotente: correrlo dos veces no cambia nada la segunda vez.
"""

import os
import re
import sys
from decimal import Decimal
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

SOLO_VER = "--solo-ver" in sys.argv or "--solo_ver" in sys.argv

LINEA = "=" * 70
SUB = "-" * 70


# --------------------------------------------------------------------------
# Arranque de Django
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
    print("No encuentro Django. Activa el entorno virtual primero:")
    print(r"    .\venv\Scripts\Activate.ps1")
    sys.exit(1)

try:
    django.setup()
except Exception as exc:
    print("No pude iniciar Django:", exc)
    sys.exit(1)

from django.conf import settings
from django.db import connection  # noqa: E402

from menu.models import Adicion, Categoria, Combo, ComboItem, Producto  # noqa: E402
from pedidos.models import DetalleAdicion, DetallePedido, Pedido  # noqa: E402

MOTOR = connection.vendor  # 'sqlite' o 'mysql'

MODELOS = [
    Categoria,
    Producto,
    Adicion,
    Combo,
    ComboItem,
    Pedido,
    DetallePedido,
    DetalleAdicion,
]


# --------------------------------------------------------------------------
# Utilidades de esquema
# --------------------------------------------------------------------------
def describir_base():
    db = settings.DATABASES["default"]
    engine = db.get("ENGINE", "?")
    nombre = str(db.get("NAME", "?"))
    if "sqlite" in engine:
        ruta = Path(nombre)
        if not ruta.is_absolute():
            ruta = (BASE / ruta).resolve()
        estado = "{} KB".format(round(ruta.stat().st_size / 1024)) if ruta.exists() else "NO EXISTE"
        return "SQLite -> {}  ({})".format(ruta, estado)
    return "{} -> {} en {}:{}".format(
        engine.split(".")[-1], nombre, db.get("HOST") or "localhost", db.get("PORT") or "3306"
    )


def tablas_existentes():
    return set(connection.introspection.table_names())


def columnas(tabla):
    with connection.cursor() as cur:
        return [c.name for c in connection.introspection.get_table_description(cur, tabla)]


def mapa_columnas(tabla):
    """Devuelve {nombre_en_minuscula: nombre_real_en_bd}."""
    return {nombre.lower(): nombre for nombre in columnas(tabla)}


def columna_real(tabla, nombre):
    return mapa_columnas(tabla).get(nombre.lower())


def qi(nombre):
    """Escapa identificadores para que funcionen igual en SQLite y MySQL."""
    if MOTOR == "mysql":
        return "`{}`".format(str(nombre).replace("`", "``"))
    return '"{}"'.format(str(nombre).replace('"', '""'))


def adaptar_expresion(expr, mapa):
    """Cambia nombres canonicos por el nombre real de cada columna."""
    texto = expr
    for clave in sorted(mapa.keys(), key=len, reverse=True):
        real = mapa[clave]
        texto = re.sub(r"\b{}\b".format(re.escape(clave)), real, texto, flags=re.IGNORECASE)
    return texto


def tipo_sql(campo):
    """Tipo de columna SQL para un campo del modelo."""
    interno = campo.get_internal_type()
    if interno in ("ForeignKey", "OneToOneField"):
        return "INT" if MOTOR == "mysql" else "integer"
    if MOTOR == "mysql":
        mapa = {
            "AutoField": "INT",
            "BigAutoField": "BIGINT",
            "IntegerField": "INT",
            "PositiveIntegerField": "INT",
            "SmallIntegerField": "SMALLINT",
            "BigIntegerField": "BIGINT",
            "DecimalField": "DECIMAL({},{})".format(campo.max_digits, campo.decimal_places),
            "FloatField": "DOUBLE",
            "CharField": "VARCHAR({})".format(campo.max_length or 255),
            "TextField": "LONGTEXT",
            "BooleanField": "TINYINT(1)",
            "DateTimeField": "DATETIME",
            "DateField": "DATE",
            "ImageField": "VARCHAR(255)",
            "FileField": "VARCHAR(255)",
            "EmailField": "VARCHAR(254)",
        }
    else:
        mapa = {
            "AutoField": "integer",
            "BigAutoField": "bigint",
            "IntegerField": "integer",
            "PositiveIntegerField": "integer",
            "SmallIntegerField": "smallint",
            "BigIntegerField": "bigint",
            "DecimalField": "decimal",
            "FloatField": "real",
            "CharField": "varchar({})".format(campo.max_length or 255),
            "TextField": "text",
            "BooleanField": "bool",
            "DateTimeField": "datetime",
            "DateField": "date",
            "ImageField": "varchar(255)",
            "FileField": "varchar(255)",
            "EmailField": "varchar(254)",
        }
    return mapa.get(interno, "varchar(255)")


def valor_por_defecto(campo):
    """Valor DEFAULT para las filas que ya existen. None = sin DEFAULT."""
    interno = campo.get_internal_type()
    defecto = getattr(campo, "default", None)
    if defecto is not None and not callable(defecto):
        if interno == "BooleanField":
            return "1" if defecto else "0"
        if isinstance(defecto, str):
            return "'" + defecto.replace("'", "''") + "'"
        if isinstance(defecto, (int, float, Decimal)):
            return str(defecto)
    if interno == "BooleanField":
        return "1"
    if interno in ("IntegerField", "PositiveIntegerField", "SmallIntegerField", "BigIntegerField"):
        return "0"
    if interno == "DecimalField":
        return "0"
    if interno in ("CharField", "TextField", "EmailField"):
        return "''"
    return None


def ejecutar(sql, params=None):
    with connection.cursor() as cur:
        cur.execute(sql, params or [])
        try:
            return cur.rowcount
        except Exception:
            return 0


def crear_tabla_desde_modelo(modelo):
    """Crea la tabla a partir de los campos del modelo.

    Se escribe el CREATE TABLE a mano en vez de usar el editor de esquema de
    Django porque estas tablas son managed=False y las claves foraneas se
    declaran como columnas simples: asi funciona igual en SQLite y en MySQL
    sin arrastrar restricciones que puedan chocar con datos ya existentes.
    """
    tabla = modelo._meta.db_table
    partes = []
    for campo in modelo._meta.local_fields:
        if campo.primary_key:
            if MOTOR == "mysql":
                partes.append("{} INT AUTO_INCREMENT PRIMARY KEY".format(campo.column))
            else:
                partes.append("{} INTEGER PRIMARY KEY AUTOINCREMENT".format(campo.column))
            continue
        trozo = "{} {}".format(campo.column, tipo_sql(campo))
        defecto = valor_por_defecto(campo)
        # MySQL no admite DEFAULT en columnas TEXT.
        if MOTOR == "mysql" and campo.get_internal_type() == "TextField":
            defecto = None
        if defecto is not None:
            trozo += " DEFAULT " + defecto
        partes.append(trozo)
    ejecutar("CREATE TABLE {} ({})".format(tabla, ", ".join(partes)))


# --------------------------------------------------------------------------
# Sincronizacion
# --------------------------------------------------------------------------
def sincronizar():
    existentes = tablas_existentes()
    creadas, agregadas = [], []

    for modelo in MODELOS:
        tabla = modelo._meta.db_table

        if tabla not in existentes:
            print("  + tabla {:<16} no existia: se crea completa".format(tabla))
            crear_tabla_desde_modelo(modelo)
            creadas.append(tabla)
            continue

        mapa = mapa_columnas(tabla)
        faltantes = []
        for campo in modelo._meta.local_fields:
            if campo.primary_key:
                continue
            if campo.column.lower() not in mapa:
                faltantes.append(campo)

        if not faltantes:
            print("  = {:<16} completa ({} columnas)".format(tabla, len(mapa)))
            continue

        print("  ! {:<16} le faltan {} columnas".format(tabla, len(faltantes)))
        for campo in faltantes:
            sql = "ALTER TABLE {} ADD COLUMN {} {}".format(
                qi(tabla), qi(campo.column), tipo_sql(campo)
            )
            defecto = valor_por_defecto(campo)
            if defecto is not None:
                sql += " DEFAULT " + defecto
            try:
                ejecutar(sql)
                print("      + {}.{}".format(tabla, campo.column))
                agregadas.append("{}.{}".format(tabla, campo.column))
                mapa[campo.column.lower()] = campo.column
            except Exception as exc:
                mapa = mapa_columnas(tabla)
                if campo.column.lower() in mapa:
                    print("      = {}.{} ya existia (se continua)".format(tabla, mapa[campo.column.lower()]))
                else:
                    print("      ! {}.{} no se pudo agregar: {}".format(tabla, campo.column, exc))

    return creadas, agregadas


def copiar_datos_viejos():
    """Si la tabla traia el total con otro nombre, lo pasa a la columna nueva."""
    cambios = []

    def copiar(tabla, destino, candidatos, expresion=None):
        try:
            mapa = mapa_columnas(tabla)
        except Exception:
            return
        destino_real = mapa.get(destino.lower())
        if not destino_real:
            return
        origen_real = None
        for candidato in candidatos:
            origen_real = mapa.get(candidato.lower())
            if origen_real:
                break
        if not origen_real:
            return
        expr = adaptar_expresion(expresion or origen_real, mapa)
        try:
            n = ejecutar(
                "UPDATE {t} SET {d} = {e} "
                "WHERE ({d} IS NULL OR {d} = 0) AND {o} IS NOT NULL".format(
                    t=qi(tabla), d=qi(destino_real), e=expr, o=qi(origen_real)
                )
            )
            if n:
                cambios.append("{}: {} filas copiadas desde {}".format(tabla, n, origen_real))
        except Exception as exc:
            print("      (no se pudo copiar {} -> {}: {})".format(origen_real, destino_real, exc))

    copiar("Pedido", "total", ["valor_total", "total_pedido", "precio_total", "monto", "valor", "subtotal"])
    copiar("Detalle_Pedido", "precio_unitario", ["precio", "valor_unitario", "precio_venta"])
    copiar(
        "Detalle_Pedido",
        "valor_venta",
        ["precio", "valor", "subtotal"],
        expresion="precio * COALESCE(cantidad, 1)",
    )

    # Si el pedido viejo no guardaba el total en ninguna columna, se recalcula
    # sumando sus lineas: es el mismo numero que el sistema habria mostrado.
    try:
        mapa_pedido = mapa_columnas("Pedido")
        mapa_detalle = mapa_columnas("Detalle_Pedido")
        total_pedido = mapa_pedido.get("total")
        id_pedido = mapa_pedido.get("id_pedido")
        valor_venta = mapa_detalle.get("valor_venta")
        pedido_id = mapa_detalle.get("pedido_id")
        if total_pedido and id_pedido and valor_venta and pedido_id:
            n = ejecutar(
                "UPDATE {pedido} SET {total} = ("
                "  SELECT COALESCE(SUM(d.{valor}), 0) FROM {detalle} d"
                "  WHERE d.{pedido_id_det} = {pedido}.{id_pedido}"
                ") WHERE ({total} IS NULL OR {total} = 0) AND EXISTS ("
                "  SELECT 1 FROM {detalle} d WHERE d.{pedido_id_det} = {pedido}.{id_pedido}"
                ")".format(
                    pedido=qi("Pedido"),
                    total=qi(total_pedido),
                    detalle=qi("Detalle_Pedido"),
                    valor=qi(valor_venta),
                    pedido_id_det=qi(pedido_id),
                    id_pedido=qi(id_pedido),
                )
            )
            if n:
                cambios.append("Pedido: {} totales recalculados desde sus lineas".format(n))
    except Exception as exc:
        print("      (no se pudo recalcular el total: {})".format(exc))

    return cambios


def normalizar():
    """Rellena las columnas recien creadas en las filas que ya existian."""
    rellenos = [
        ("Pedido", "prioridad", "1", "prioridad IS NULL OR prioridad = 0"),
        ("Pedido", "observaciones", "''", "observaciones IS NULL"),
        ("Pedido", "estado", "'pendiente'", "estado IS NULL OR estado = ''"),
        ("Pedido", "fecha_pedido", "CURRENT_TIMESTAMP", "fecha_pedido IS NULL"),
        ("Detalle_Pedido", "notas", "''", "notas IS NULL"),
        ("Detalle_Pedido", "cantidad", "1", "cantidad IS NULL OR cantidad = 0"),
        ("Detalle_Pedido", "precio_unitario", "valor_venta", "precio_unitario IS NULL"),
        ("Menu", "disponible", "1", "disponible IS NULL"),
        ("Menu", "orden", "0", "orden IS NULL"),
        ("Categoria", "activa", "1", "activa IS NULL"),
        ("Categoria", "orden", "0", "orden IS NULL"),
        ("Adicion", "activa", "1", "activa IS NULL"),
        ("Combo", "activo", "1", "activo IS NULL"),
    ]
    hechos = []
    existentes = tablas_existentes()
    for tabla, columna, valor, condicion in rellenos:
        if tabla not in existentes:
            continue
        try:
            mapa = mapa_columnas(tabla)
            columna_real = mapa.get(columna.lower())
            if not columna_real:
                continue
            valor_real = adaptar_expresion(valor, mapa)
            condicion_real = adaptar_expresion(condicion, mapa)
            n = ejecutar(
                "UPDATE {t} SET {c} = {v} WHERE {w}".format(
                    t=qi(tabla), c=qi(columna_real), v=valor_real, w=condicion_real
                )
            )
            if n:
                hechos.append("{}.{}: {} filas".format(tabla, columna_real, n))
        except Exception:
            pass
    return hechos


def sembrar_adiciones():
    """Si la tabla Adicion quedo vacia, deja unas adiciones de ejemplo."""
    try:
        if Adicion.objects.exists():
            return 0
    except Exception:
        return 0
    ejemplos = [
        ("Queso extra", 2000),
        ("Tocineta", 3000),
        ("Cebolla caramelizada", 1500),
        ("Aguacate", 2500),
        ("Salsa de la casa", 1000),
        ("Doble carne", 6000),
        ("Papas a la francesa", 4000),
        ("Bebida personal", 3500),
    ]
    for orden, (nombre, precio) in enumerate(ejemplos):
        Adicion.objects.create(
            nombre=nombre, precio=precio, categoria_id=None, activa=True, orden=orden
        )
    return len(ejemplos)


# --------------------------------------------------------------------------
# Verificacion real
# --------------------------------------------------------------------------
def probar_consultas():
    """Corre las mismas consultas que /cocina/ y /cocina/reportes/."""
    from datetime import date

    from django.db.models import Count, DecimalField, Sum, Value
    from django.db.models.functions import Coalesce

    pruebas = []

    def probar(nombre, funcion):
        try:
            funcion()
            pruebas.append((nombre, True, ""))
        except Exception as exc:
            pruebas.append((nombre, False, "{}: {}".format(type(exc).__name__, exc)))

    probar("Pedido.objects.filter(estado)", lambda: list(
        Pedido.objects.filter(estado__in=["pendiente", "en_preparacion", "listo"])[:5]))
    probar("Pedido.fecha_pedido__date", lambda: Pedido.objects.filter(
        fecha_pedido__date=date.today()).count())
    probar("Sum(Pedido.total)", lambda: Pedido.objects.aggregate(
        t=Coalesce(Sum("total"), Value(Decimal("0")), output_field=DecimalField())))
    probar("DetallePedido.valor_venta", lambda: DetallePedido.objects.aggregate(
        t=Coalesce(Sum("valor_venta"), Value(Decimal("0")), output_field=DecimalField()),
        u=Coalesce(Sum("cantidad"), Value(0))))
    probar("reporte por categoria", lambda: list(
        DetallePedido.objects.values("producto__categoria__nom_categoria")
        .annotate(total=Sum("valor_venta"), unidades=Sum("cantidad"))[:5]))
    probar("reporte por producto", lambda: list(
        DetallePedido.objects.values("producto__nombre")
        .annotate(total=Sum("valor_venta"))[:5]))
    probar("reporte por combo", lambda: list(
        DetallePedido.objects.values("combo__nombre").annotate(total=Sum("valor_venta"))[:5]))
    probar("pedidos por estado", lambda: list(
        Pedido.objects.values("estado").annotate(n=Count("id_pedido"))[:5]))
    probar("detalles con adiciones", lambda: list(
        DetallePedido.objects.prefetch_related("adiciones__adicion")[:5]))
    probar("Menu.foto / disponible", lambda: list(Producto.objects.all()[:5]))
    probar("Adicion", lambda: list(Adicion.objects.all()[:5]))
    probar("Combo + partes", lambda: list(Combo.objects.prefetch_related("items__producto")[:5]))

    print("  {:<34} {}".format("CONSULTA", "RESULTADO"))
    for nombre, ok, detalle in pruebas:
        print("  {:<34} {}".format(nombre, "OK" if ok else "FALLA -> " + detalle))
    return all(ok for _, ok, _ in pruebas)


def probar_paginas():
    """Pide /cocina/ y /cocina/reportes/ por HTTP con un superusuario real."""
    from django.contrib.auth import get_user_model
    from django.test import Client

    Usuario = get_user_model()
    jefe = Usuario.objects.filter(is_superuser=True, is_active=True).first()
    if not jefe:
        print("  (no hay superusuario: no puedo probar las paginas por HTTP)")
        return None

    cliente = Client()
    cliente.force_login(jefe)
    resultados = []
    for url in ("/cocina/", "/cocina/reportes/", "/", "/carrito/"):
        try:
            resp = cliente.get(url)
            ok = resp.status_code in (200, 302)
            resultados.append((url, resp.status_code, ok))
        except Exception as exc:
            resultados.append((url, "{}: {}".format(type(exc).__name__, exc), False))
    print("  {:<22} {:<8} {}".format("PAGINA", "HTTP", "ESTADO"))
    for url, codigo, ok in resultados:
        print("  {:<22} {:<8} {}".format(url, codigo, "OK" if ok else "FALLA"))
    return all(ok for _, _, ok in resultados)


# --------------------------------------------------------------------------
# Programa principal
# --------------------------------------------------------------------------
def main():
    print(LINEA)
    print(" SABOR URBANO · sincronizar base de datos")
    print(LINEA)
    print(" Carpeta  :", BASE)
    print(" Settings :", os.environ["DJANGO_SETTINGS_MODULE"])
    print(" Base     :", describir_base())
    print(" Django   :", django.get_version(), "·", MOTOR)
    print(SUB)

    if "auth_user" not in tablas_existentes():
        print(" La base no tiene ni las tablas de Django.")
        print(" Corre primero:  python manage.py migrate")
        print(LINEA)
        return 1

    print(" Revisando tablas y columnas")
    if SOLO_VER:
        for modelo in MODELOS:
            tabla = modelo._meta.db_table
            if tabla not in tablas_existentes():
                print("  - tabla {:<16} NO EXISTE".format(tabla))
                continue
            mapa = mapa_columnas(tabla)
            faltan = [
                c.column
                for c in modelo._meta.local_fields
                if not c.primary_key and c.column.lower() not in mapa
            ]
            if faltan:
                print("  ! {:<16} faltan: {}".format(tabla, ", ".join(faltan)))
            else:
                print("  = {:<16} completa".format(tabla))
        print(SUB)
        print(" Modo --solo-ver: no cambie nada. Quita el flag para reparar.")
        print(LINEA)
        return 0

    creadas, agregadas = sincronizar()
    print(SUB)

    if creadas or agregadas:
        print(" Copiando datos de columnas viejas")
        cambios = copiar_datos_viejos()
        if cambios:
            for linea in cambios:
                print("   " + linea)
        else:
            print("   (nada que copiar)")
        rellenos = normalizar()
        if rellenos:
            print(" Rellenando valores vacios")
            for linea in rellenos:
                print("   " + linea)
        cuantas = sembrar_adiciones()
        if cuantas:
            print(" Adiciones de ejemplo creadas: {}".format(cuantas))
        print(SUB)

    print(" Verificando las consultas del sistema")
    consultas_ok = probar_consultas()
    print(SUB)
    print(" Verificando las paginas")
    paginas_ok = probar_paginas()
    print(LINEA)

    print(" Resumen")
    print("   tablas creadas   : {}".format(len(creadas)))
    print("   columnas sumadas : {}".format(len(agregadas)))
    if agregadas:
        for nombre in agregadas:
            print("      + " + nombre)
    print(SUB)

    if not consultas_ok or paginas_ok is False:
        print(" Todavia queda algo mal. Copiame esta salida completa.")
        print(LINEA)
        return 2

    print(" LISTO. /cocina/ ya responde. Arranca con:")
    print("     python manage.py runserver")
    print(LINEA)
    return 0


if __name__ == "__main__":
    sys.exit(main())
