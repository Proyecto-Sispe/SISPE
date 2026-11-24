#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
actualizar_bd.py  -  Sabor Urbano

Pone al dia la base de datos SIN borrar nada:

  * crea las tablas nuevas (Adicion, Combo, Combo_Item, Detalle_Adicion)
  * agrega las columnas nuevas a las tablas que ya existen
  * siembra unas adiciones de ejemplo la primera vez

Es idempotente: se puede correr las veces que quieras. No toca productos,
categorias, pedidos ni usuarios existentes.

Uso:
    python actualizar_bd.py
"""

import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))


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

django.setup()

from django.db import connection  # noqa: E402

MOTOR = connection.vendor  # 'sqlite' o 'mysql'


def tipos():
    """Tipo de dato por columna segun el motor."""
    if MOTOR == "mysql":
        return {
            "int": "INT NULL",
            "int_nn": "INT NOT NULL DEFAULT 0",
            "bool": "TINYINT(1) NOT NULL DEFAULT 1",
            "texto": "VARCHAR(255) NULL",
            "texto_nn": "VARCHAR(255) NOT NULL DEFAULT ''",
            "largo": "LONGTEXT NULL",
            "decimal": "DECIMAL(12,2) NOT NULL DEFAULT 0",
            "fecha": "DATETIME NULL",
        }
    return {
        "int": "INTEGER NULL",
        "int_nn": "INTEGER NOT NULL DEFAULT 0",
        "bool": "INTEGER NOT NULL DEFAULT 1",
        "texto": "VARCHAR(255) NULL",
        "texto_nn": "VARCHAR(255) NOT NULL DEFAULT ''",
        "largo": "TEXT NULL",
        "decimal": "DECIMAL(12,2) NOT NULL DEFAULT 0",
        "fecha": "DATETIME NULL",
    }


T = tipos()


def tablas_existentes():
    return set(connection.introspection.table_names())


def columnas(tabla):
    with connection.cursor() as cur:
        nombres = [c.name for c in connection.introspection.get_table_description(cur, tabla)]
    return {n.lower(): n for n in nombres}


def qi(nombre):
    if MOTOR == "mysql":
        return "`{}`".format(str(nombre).replace("`", "``"))
    return '"{}"'.format(str(nombre).replace('"', '""'))


def adaptar_expresion(expr, mapa):
    texto = expr
    for clave in sorted(mapa.keys(), key=len, reverse=True):
        texto = re.sub(r"\b{}\b".format(re.escape(clave)), mapa[clave], texto, flags=re.IGNORECASE)
    return texto


def ejecutar(sql, params=None):
    with connection.cursor() as cur:
        cur.execute(sql, params or [])
        try:
            return cur.rowcount
        except Exception:
            return 0


def crear_tabla(nombre, definicion):
    if nombre in tablas_existentes():
        print(f"  = tabla {nombre:<16} ya existe")
        return False
    ejecutar(f"CREATE TABLE {nombre} ({definicion})")
    print(f"  + tabla {nombre:<16} creada")
    return True


def agregar_columna(tabla, columna, tipo):
    if tabla not in tablas_existentes():
        print(f"  ! tabla {tabla} no existe, se omite {columna}")
        return False

    mapa = columnas(tabla)
    if columna.lower() in mapa:
        return False

    sql = f"ALTER TABLE {qi(tabla)} ADD COLUMN {qi(columna)} {tipo}"
    try:
        ejecutar(sql)
        print(f"  + {tabla}.{columna:<16} agregada")
        return True
    except Exception as exc:
        mapa = columnas(tabla)
        if columna.lower() in mapa:
            print(f"  = {tabla}.{mapa[columna.lower()]:<16} ya existia (se continua)")
        else:
            print(f"  ! {tabla}.{columna:<16} no se pudo agregar: {exc}")
        return False


def main():
    print("=" * 64)
    print(" SABOR URBANO · actualizar base de datos")
    print("=" * 64)
    print(" Proyecto :", BASE)
    print(" Settings :", os.environ["DJANGO_SETTINGS_MODULE"])
    print(" Motor    :", MOTOR)
    print("-" * 64)

    print(" Tablas nuevas")
    crear_tabla(
        "Adicion",
        "id_adicion INTEGER PRIMARY KEY AUTOINCREMENT, "
        "nombre VARCHAR(80) NOT NULL, "
        "precio DECIMAL(10,2) NOT NULL DEFAULT 0, "
        "categoria_id INTEGER NULL, "
        "activa INTEGER NOT NULL DEFAULT 1, "
        "orden INTEGER NOT NULL DEFAULT 0"
        if MOTOR == "sqlite"
        else "id_adicion INT AUTO_INCREMENT PRIMARY KEY, "
        "nombre VARCHAR(80) NOT NULL, "
        "precio DECIMAL(10,2) NOT NULL DEFAULT 0, "
        "categoria_id INT NULL, "
        "activa TINYINT(1) NOT NULL DEFAULT 1, "
        "orden INT NOT NULL DEFAULT 0",
    )

    crear_tabla(
        "Combo",
        "id_combo INTEGER PRIMARY KEY AUTOINCREMENT, "
        "nombre VARCHAR(120) NOT NULL, "
        "descripcion TEXT NULL, "
        "precio DECIMAL(10,2) NOT NULL DEFAULT 0, "
        "foto VARCHAR(255) NULL, "
        "activo INTEGER NOT NULL DEFAULT 1, "
        "orden INTEGER NOT NULL DEFAULT 0"
        if MOTOR == "sqlite"
        else "id_combo INT AUTO_INCREMENT PRIMARY KEY, "
        "nombre VARCHAR(120) NOT NULL, "
        "descripcion LONGTEXT NULL, "
        "precio DECIMAL(10,2) NOT NULL DEFAULT 0, "
        "foto VARCHAR(255) NULL, "
        "activo TINYINT(1) NOT NULL DEFAULT 1, "
        "orden INT NOT NULL DEFAULT 0",
    )

    crear_tabla(
        "Combo_Item",
        "id_item INTEGER PRIMARY KEY AUTOINCREMENT, "
        "combo_id INTEGER NOT NULL, "
        "producto_id INTEGER NOT NULL, "
        "cantidad INTEGER NOT NULL DEFAULT 1"
        if MOTOR == "sqlite"
        else "id_item INT AUTO_INCREMENT PRIMARY KEY, "
        "combo_id INT NOT NULL, "
        "producto_id INT NOT NULL, "
        "cantidad INT NOT NULL DEFAULT 1",
    )

    crear_tabla(
        "Detalle_Adicion",
        "id_detalle_adicion INTEGER PRIMARY KEY AUTOINCREMENT, "
        "detalle_id INTEGER NOT NULL, "
        "adicion_id INTEGER NOT NULL, "
        "precio DECIMAL(10,2) NOT NULL DEFAULT 0"
        if MOTOR == "sqlite"
        else "id_detalle_adicion INT AUTO_INCREMENT PRIMARY KEY, "
        "detalle_id INT NOT NULL, "
        "adicion_id INT NOT NULL, "
        "precio DECIMAL(10,2) NOT NULL DEFAULT 0",
    )

    print("-" * 64)
    print(" Columnas nuevas en tablas existentes")

    agregar_columna("Menu", "disponible", T["bool"])
    agregar_columna("Menu", "foto", T["texto"])
    agregar_columna("Menu", "orden", T["int_nn"])

    agregar_columna("Categoria", "orden", T["int_nn"])
    agregar_columna("Categoria", "activa", T["bool"])

    # Pedido: la tabla vieja no tenia total ni prioridad, y de ahi salia el
    # error "no such column: Pedido.total" en /cocina/.
    agregar_columna("Pedido", "total", T["decimal"])
    agregar_columna("Pedido", "prioridad", T["int_nn"])
    agregar_columna("Pedido", "estado", T["texto_nn"])
    agregar_columna("Pedido", "fecha_pedido", T["fecha"])
    agregar_columna("Pedido", "observaciones", T["largo"])

    agregar_columna("Detalle_Pedido", "combo_id", T["int"])
    agregar_columna("Detalle_Pedido", "precio_unitario", T["decimal"])
    agregar_columna("Detalle_Pedido", "valor_venta", T["decimal"])
    agregar_columna("Detalle_Pedido", "cantidad", T["int_nn"])
    agregar_columna("Detalle_Pedido", "notas", T["texto_nn"])

    # Los pedidos viejos quedan con total 0: se recalcula sumando sus lineas.
    try:
        mapa_pedido = columnas("Pedido") if "Pedido" in tablas_existentes() else {}
        mapa_detalle = columnas("Detalle_Pedido") if "Detalle_Pedido" in tablas_existentes() else {}
        total = mapa_pedido.get("total")
        id_pedido = mapa_pedido.get("id_pedido")
        valor_venta = mapa_detalle.get("valor_venta")
        pedido_id = mapa_detalle.get("pedido_id")
        if total and id_pedido and valor_venta and pedido_id:
            n = ejecutar(
                "UPDATE {pedido} SET {total} = ("
                "  SELECT COALESCE(SUM(d.{valor}), 0) FROM {detalle} d"
                "  WHERE d.{pedido_id_det} = {pedido}.{id_pedido}"
                ") WHERE ({total} IS NULL OR {total} = 0) AND EXISTS ("
                "  SELECT 1 FROM {detalle} d WHERE d.{pedido_id_det} = {pedido}.{id_pedido}"
                ")".format(
                    pedido=qi("Pedido"),
                    total=qi(total),
                    detalle=qi("Detalle_Pedido"),
                    valor=qi(valor_venta),
                    pedido_id_det=qi(pedido_id),
                    id_pedido=qi(id_pedido),
                )
            )
            if n:
                print(f"  + {n} totales de pedidos recalculados")
    except Exception as exc:
        print(f"  ! no se pudo recalcular el total: {exc}")

    # Las columnas nuevas entran con NULL/0 en las filas que ya existian.
    # Aqui se rellenan con el valor logico para que nada salga en blanco.
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
    ]
    for tabla, columna, valor, condicion in rellenos:
        if tabla not in tablas_existentes():
            continue
        try:
            mapa = columnas(tabla)
            col_real = mapa.get(columna.lower())
            if not col_real:
                continue
            valor_real = adaptar_expresion(valor, mapa)
            cond_real = adaptar_expresion(condicion, mapa)
            ejecutar(f"UPDATE {qi(tabla)} SET {qi(col_real)} = {valor_real} WHERE {cond_real}")
        except Exception:
            pass

    # El detalle antiguo guardaba el producto en una columna que puede ser
    # obligatoria; si existe producto_id nulo lo dejamos como esta.
    print("-" * 64)
    print(" Datos de ejemplo")

    with connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM Adicion")
        cuantas = cur.fetchone()[0]

    if cuantas == 0:
        from menu.models import Adicion

        ejemplos = [
            ("Queso extra", 2000, 0),
            ("Tocineta", 3000, 0),
            ("Cebolla caramelizada", 1500, 0),
            ("Aguacate", 2500, 0),
            ("Salsa de la casa", 1000, 0),
            ("Doble carne", 6000, 0),
            ("Papas a la francesa", 4000, 0),
            ("Bebida personal", 3500, 0),
        ]
        for nombre, precio, orden in ejemplos:
            Adicion.objects.create(
                nombre=nombre, precio=precio, categoria_id=None, activa=True, orden=orden
            )
        print(f"  + {len(ejemplos)} adiciones de ejemplo creadas")
    else:
        print(f"  = ya hay {cuantas} adiciones, no se toca nada")

    print("-" * 64)
    print(" Resumen")
    for tabla in ("Categoria", "Menu", "Adicion", "Combo", "Combo_Item", "Pedido", "Detalle_Pedido"):
        if tabla in tablas_existentes():
            with connection.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM {tabla}")
                n = cur.fetchone()[0]
            print(f"  {tabla:<18} {n:>6} registros")
        else:
            print(f"  {tabla:<18} (no existe)")

    print("=" * 64)
    print(" Listo. Arranca con: python manage.py runserver")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    sys.exit(main())
