#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
crear_tablas.py  -  SISPE

Crea las tablas base del restaurante (Categoria, Menu, Pedido, Detalle_Pedido)
y carga las 11 categorias con sus 85 productos.

Solo hace falta en una instalacion nueva o si borraste db.sqlite3.
Es idempotente: usa CREATE TABLE IF NOT EXISTS y no duplica registros.

Uso:
    python crear_tablas.py
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
    print("No encuentro Django. Activa el entorno virtual primero.")
    sys.exit(1)

django.setup()

from django.db import connection  # noqa: E402

MOTOR = connection.vendor

CARTA = {
    "Hamburguesas": [
        ("Hamburguesa clásica", 16000, "Carne 120 g, lechuga, tomate y salsa de la casa"),
        ("Hamburguesa doble carne", 23000, "Dos carnes de 120 g con queso cheddar"),
        ("Hamburguesa de pollo", 17000, "Pechuga a la plancha, lechuga y mayonesa"),
        ("Hamburguesa BBQ", 19000, "Carne, tocineta, cebolla caramelizada y salsa BBQ"),
        ("Hamburguesa mexicana", 19500, "Carne, jalapeños, guacamole y pico de gallo"),
        ("Hamburguesa hawaiana", 18500, "Carne, piña asada y queso mozzarella"),
        ("Hamburguesa ranchera", 20000, "Carne, huevo frito, tocineta y papas"),
        ("Hamburguesa vegetariana", 16500, "Medallón de lentejas, vegetales y queso"),
        ("Hamburguesa de cerdo", 18000, "Carne de cerdo desmechada y chimichurri"),
        ("Hamburguesa triple", 27000, "Tres carnes, triple queso y tocineta"),
    ],
    "Perros Calientes": [
        ("Perro clásico", 9000, "Salchicha, papas ripio, queso y salsas"),
        ("Perro especial", 13000, "Salchicha, tocineta, queso y cebolla caramelizada"),
        ("Perro ranchero", 12500, "Salchicha, maíz, queso y salsa de la casa"),
        ("Perro hawaiano", 12000, "Salchicha, piña y queso mozzarella"),
        ("Perro mexicano", 12500, "Salchicha, jalapeños y guacamole"),
        ("Perro de pollo", 13500, "Pollo desmechado, queso y papas ripio"),
        ("Perro super", 15000, "Doble salchicha, tocineta, queso y huevo"),
        ("Perro vegetariano", 11000, "Salchicha vegetal, vegetales y salsas"),
    ],
    "Pizzas": [
        ("Pizza margarita", 22000, "Salsa de tomate, mozzarella y albahaca"),
        ("Pizza pepperoni", 26000, "Mozzarella y pepperoni en rodajas"),
        ("Pizza hawaiana", 25000, "Jamón, piña y mozzarella"),
        ("Pizza cuatro quesos", 28000, "Mozzarella, parmesano, azul y cheddar"),
        ("Pizza de pollo", 27000, "Pollo desmechado, champiñones y mozzarella"),
        ("Pizza carnes", 30000, "Carne, pollo, cerdo y pepperoni"),
        ("Pizza vegetariana", 24000, "Pimentón, cebolla, champiñones y aceitunas"),
        ("Pizza napolitana", 25500, "Tomate en rodajas, ajo y mozzarella"),
        ("Pizza BBQ", 27500, "Pollo, tocineta, cebolla y salsa BBQ"),
        ("Pizza mexicana", 27000, "Jalapeños, carne, maíz y guacamole"),
    ],
    "Salchipapas": [
        ("Salchipapa sencilla", 12000, "Papas a la francesa y salchicha"),
        ("Salchipapa especial", 16000, "Papas, salchicha, queso y tocineta"),
        ("Salchipapa ranchera", 17000, "Papas, salchicha, maíz y salsa de la casa"),
        ("Salchipapa de pollo", 18000, "Papas, pollo desmechado y queso"),
        ("Salchipapa mixta", 19000, "Papas, carne, pollo y salchicha"),
        ("Salchipapa hawaiana", 17500, "Papas, salchicha, piña y queso"),
        ("Salchipapa familiar", 32000, "Porción para compartir entre cuatro"),
    ],
    "Alitas": [
        ("Alitas BBQ x6", 18000, "Seis alitas bañadas en salsa BBQ"),
        ("Alitas BBQ x12", 32000, "Doce alitas bañadas en salsa BBQ"),
        ("Alitas picantes x6", 18000, "Seis alitas con salsa picante"),
        ("Alitas picantes x12", 32000, "Doce alitas con salsa picante"),
        ("Alitas miel mostaza x6", 19000, "Seis alitas con miel y mostaza"),
        ("Alitas miel mostaza x12", 34000, "Doce alitas con miel y mostaza"),
        ("Alitas mixtas x12", 34000, "Doce alitas en tres salsas"),
    ],
    "Nachos": [
        ("Nachos con queso", 14000, "Totopos con queso fundido"),
        ("Nachos rancheros", 17000, "Totopos, queso, carne y pico de gallo"),
        ("Nachos de pollo", 17500, "Totopos, pollo desmechado y queso"),
        ("Nachos mexicanos", 18000, "Totopos, jalapeños, guacamole y queso"),
        ("Nachos mixtos", 20000, "Totopos, carne, pollo y queso"),
        ("Nachos familiares", 29000, "Porción grande para compartir"),
    ],
    "Ensaladas": [
        ("Ensalada césar", 15000, "Lechuga, pollo, crutones y aderezo césar"),
        ("Ensalada de la casa", 13000, "Lechuga, tomate, zanahoria y vinagreta"),
        ("Ensalada de pollo", 16000, "Pollo a la plancha, vegetales y aderezo"),
        ("Ensalada tropical", 15500, "Piña, mango, lechuga y aderezo de la casa"),
        ("Ensalada de atún", 16500, "Atún, lechuga, maíz y aderezo"),
        ("Ensalada de quinoa", 17000, "Quinoa, vegetales y aderezo de limón"),
    ],
    "Bebidas": [
        ("Gaseosa personal", 3500, "Botella 400 ml"),
        ("Gaseosa 1.5 L", 7000, "Botella para compartir"),
        ("Agua sin gas", 3000, "Botella 600 ml"),
        ("Agua con gas", 3200, "Botella 600 ml"),
        ("Limonada natural", 5500, "Limón, agua y azúcar"),
        ("Limonada de coco", 7500, "Limón, coco y leche condensada"),
        ("Jugo de naranja", 6500, "Naranja recién exprimida"),
        ("Jugo de mora", 6500, "Mora natural con agua o leche"),
        ("Cerveza nacional", 6000, "Botella 330 ml"),
        ("Café americano", 4000, "Café de la casa"),
    ],
    "Postres": [
        ("Brownie con helado", 9500, "Brownie tibio con helado de vainilla"),
        ("Cheesecake de mora", 9000, "Porción con salsa de mora"),
        ("Torta de chocolate", 8500, "Porción con cubierta de chocolate"),
        ("Flan de caramelo", 7500, "Flan casero con caramelo"),
        ("Helado artesanal", 7000, "Dos bolas a elección"),
        ("Mazamorra", 6500, "Mazamorra con panela y leche"),
        ("Obleas con arequipe", 6000, "Oblea rellena de arequipe"),
    ],
    "Comidas Rápidas": [
        ("Papas a la francesa", 8000, "Porción individual con sal"),
        ("Papas con queso", 10500, "Papas cubiertas de queso fundido"),
        ("Aros de cebolla", 9500, "Ocho aros empanizados"),
        ("Nuggets de pollo", 12000, "Ocho nuggets con salsa"),
        ("Deditos de queso", 11000, "Seis deditos empanizados"),
        ("Sándwich de pollo", 14000, "Pan artesanal, pollo y vegetales"),
        ("Sándwich de carne", 15500, "Pan artesanal, carne y queso"),
    ],
    "Especiales": [
        ("Costillas BBQ", 32000, "Costillas de cerdo con salsa BBQ y papas"),
        ("Pechuga a la plancha", 26000, "Pechuga con vegetales y papas"),
        ("Churrasco", 38000, "Corte de res con papas y ensalada"),
        ("Punta de anca", 36000, "Corte de res con papas y ensalada"),
        ("Mojarra frita", 34000, "Pescado frito con patacón y ensalada"),
        ("Arroz con pollo", 24000, "Arroz con pollo desmechado y ensalada"),
        ("Bandeja de la casa", 30000, "Carne, pollo, arroz, frijoles y plátano"),
    ],
}


def main():
    print("=" * 64)
    print(" SABOR URBANO · crear tablas base")
    print("=" * 64)
    print(" Motor:", MOTOR)

    entero_pk = (
        "INTEGER PRIMARY KEY AUTOINCREMENT" if MOTOR == "sqlite" else "INT AUTO_INCREMENT PRIMARY KEY"
    )
    texto = "TEXT" if MOTOR == "sqlite" else "LONGTEXT"
    booleano = "INTEGER" if MOTOR == "sqlite" else "TINYINT(1)"
    marca = "%s" if MOTOR == "mysql" else "?"

    sentencias = [
        f"""CREATE TABLE IF NOT EXISTS Categoria (
            id_categoria {entero_pk},
            nom_categoria VARCHAR(80) NOT NULL,
            orden INTEGER NOT NULL DEFAULT 0,
            activa {booleano} NOT NULL DEFAULT 1
        )""",
        f"""CREATE TABLE IF NOT EXISTS Menu (
            id_menu {entero_pk},
            nombre VARCHAR(120) NOT NULL,
            descripcion {texto} NULL,
            precio DECIMAL(10,2) NOT NULL DEFAULT 0,
            categoria_id INTEGER NOT NULL,
            disponible {booleano} NOT NULL DEFAULT 1,
            foto VARCHAR(255) NULL,
            orden INTEGER NOT NULL DEFAULT 0
        )""",
        f"""CREATE TABLE IF NOT EXISTS Pedido (
            id_pedido {entero_pk},
            id_mesa INTEGER NOT NULL DEFAULT 0,
            estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
            prioridad INTEGER NOT NULL DEFAULT 1,
            fecha_pedido DATETIME NULL,
            total DECIMAL(12,2) NOT NULL DEFAULT 0,
            observaciones {texto} NULL
        )""",
        f"""CREATE TABLE IF NOT EXISTS Detalle_Pedido (
            id_detalle {entero_pk},
            pedido_id INTEGER NOT NULL,
            producto_id INTEGER NULL,
            combo_id INTEGER NULL,
            cantidad INTEGER NOT NULL DEFAULT 1,
            precio_unitario DECIMAL(10,2) NOT NULL DEFAULT 0,
            valor_venta DECIMAL(12,2) NOT NULL DEFAULT 0,
            notas VARCHAR(200) NOT NULL DEFAULT ''
        )""",
    ]

    with connection.cursor() as cur:
        for sql in sentencias:
            cur.execute(sql)
    print("  + tablas base verificadas")

    with connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM Categoria")
        hay_categorias = cur.fetchone()[0]

    if hay_categorias:
        print(f"  = ya hay {hay_categorias} categorias, no se duplican")
    else:
        from menu.models import Categoria

        for orden, nombre in enumerate(CARTA.keys(), start=1):
            Categoria.objects.create(nom_categoria=nombre, orden=orden, activa=True)
        print(f"  + {len(CARTA)} categorias creadas")

    with connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM Menu")
        hay_productos = cur.fetchone()[0]

    if hay_productos:
        print(f"  = ya hay {hay_productos} productos, no se duplican")
    else:
        from menu.models import Categoria, Producto

        total = 0
        for nombre_cat, platos in CARTA.items():
            categoria = Categoria.objects.filter(nom_categoria=nombre_cat).first()
            if not categoria:
                continue
            for orden, (nombre, precio, descripcion) in enumerate(platos, start=1):
                Producto.objects.create(
                    nombre=nombre,
                    descripcion=descripcion,
                    precio=precio,
                    categoria=categoria,
                    disponible=True,
                    orden=orden,
                )
                total += 1
        print(f"  + {total} productos creados")

    print("-" * 64)
    with connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM Categoria")
        c = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM Menu")
        p = cur.fetchone()[0]
    print(f"  Categorias: {c}")
    print(f"  Productos : {p}")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    sys.exit(main())
