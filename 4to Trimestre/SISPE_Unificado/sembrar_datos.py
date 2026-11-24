#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sembrar_datos.py - Sabor Urbano
================================

Llena la base con datos de ejemplo adicionales (categorías, productos,
adiciones, combos y pedidos demo), usando solo ORM de Django.

Uso:
    python sembrar_datos.py
    python sembrar_datos.py --solo-ver

Es idempotente: al correrlo dos veces no duplica registros.
"""

import argparse
import os
import random
import re
import sys
import unicodedata
from datetime import timedelta
from decimal import Decimal
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
    print("No encuentro Django. Activa el entorno virtual y corre de nuevo.")
    sys.exit(1)

try:
    django.setup()
except Exception as exc:
    print(f"No pude iniciar Django: {exc}")
    sys.exit(1)

from django.db import DatabaseError, OperationalError, ProgrammingError, connection, transaction  # noqa: E402
from django.utils import timezone  # noqa: E402

from menu.models import Adicion, Categoria, Combo, ComboItem, Producto  # noqa: E402
from pedidos.models import DetalleAdicion, DetallePedido, Pedido  # noqa: E402

LINEA = "=" * 72
SUB = "-" * 72
MOTOR = connection.vendor
RNG = random.Random(20261120)


CATEGORIAS_BASE = [
    "Hamburguesas",
    "Perros Calientes",
    "Pizzas",
    "Salchipapas",
    "Alitas",
    "Nachos",
    "Ensaladas",
    "Bebidas",
    "Postres",
    "Comidas Rápidas",
    "Especiales",
]

NUEVAS_CATEGORIAS = [
    "Sopas y Cremas",
    "Carnes y Parrilla",
    "Desayunos",
    "Smoothies y Jugos Naturales",
    "Menú Infantil",
]


PLANTILLAS_PRODUCTOS = {
    "Hamburguesas": {
        "base": "Hamburguesa",
        "sabores": ["Parrillera", "Criolla", "Andina", "Costeña", "Callejera", "Campesina", "Quesuda", "Santafereña"],
        "extras": ["ahumada", "con tocineta", "con maíz tierno", "con cebolla crispy", "con pepinillos", "con salsa burger", "con piña asada", "con doble queso"],
        "rango": (15000, 30000),
    },
    "Perros Calientes": {
        "base": "Perro",
        "sabores": ["Bacano", "Ranchero", "Monteriano", "Pacífico", "Paisa", "Sabanero", "Candelaria", "Supremo"],
        "extras": ["con queso gratinado", "con ripio crocante", "con maíz y tocineta", "con salsa tártara", "con guacamole", "con cebolla caramelizada", "con jalapeños", "con salsa de piña"],
        "rango": (9000, 20000),
    },
    "Pizzas": {
        "base": "Pizza",
        "sabores": ["Artesanal", "Mediterránea", "Campestre", "Sabrosa", "Familiar", "Tradicional", "Especial", "Urbana"],
        "extras": ["de pollo bbq", "de jamón serrano", "de chorizo y maíz", "de vegetales al wok", "de tres carnes", "de queso costeño", "de tocineta miel", "de champiñón al ajillo"],
        "rango": (18000, 38000),
    },
    "Salchipapas": {
        "base": "Salchipapa",
        "sabores": ["Suprema", "Urbana", "Aplastada", "Monstruo", "Picantica", "Mixta", "Paisa", "Parrandera"],
        "extras": ["con salchicha premium", "con queso fundido", "con maíz y tocineta", "con pollo desmechado", "con carne mechada", "con chorizo santarrosano", "con hogao", "con doble salsa"],
        "rango": (12000, 28000),
    },
    "Alitas": {
        "base": "Alitas",
        "sabores": ["Crocantes", "BBQ", "Miel Mostaza", "Ajo Parmesano", "Picantes", "Tropicales", "Ahumadas", "Cítricas"],
        "extras": ["con papas francesas", "con dip ranch", "con dip de queso", "con limón y pimienta", "con salsa búfalo", "con salsa teriyaki", "con ajonjolí", "con chimichurri"],
        "rango": (16000, 32000),
    },
    "Nachos": {
        "base": "Nachos",
        "sabores": ["Tex Mex", "Criollos", "Urbano", "Del Chef", "Fiesta", "Mexicano", "Brutal", "Compartir"],
        "extras": ["con queso cheddar", "con chili de carne", "con pico de gallo", "con frijol refrito", "con pollo mechado", "con guacamole", "con jalapeños", "con crema agria"],
        "rango": (13000, 26000),
    },
    "Ensaladas": {
        "base": "Ensalada",
        "sabores": ["Fresca", "Andina", "De la Huerta", "Proteica", "Fit", "Tropical", "Verde", "Ligera"],
        "extras": ["con pollo grillé", "con atún", "con aguacate", "con queso campesino", "con frutos secos", "con quinoa", "con vinagreta cítrica", "con aderezo de yogurt"],
        "rango": (12000, 24000),
    },
    "Bebidas": {
        "base": "Bebida",
        "sabores": ["Refrescante", "Fría", "Burbujeante", "Natural", "Energizante", "Dulce", "Cítrica", "Artesanal"],
        "extras": ["de maracuyá", "de frutos rojos", "de mango biche", "de limón hierbabuena", "de tamarindo", "de corozo", "de lulo", "de guanábana"],
        "rango": (3000, 11000),
    },
    "Postres": {
        "base": "Postre",
        "sabores": ["Casero", "Cremoso", "Dulce", "Tentación", "Especial", "Delicia", "Suave", "Frutal"],
        "extras": ["de arequipe", "de chocolate", "de maracuyá", "de mora", "de limón", "de tres leches", "de coco", "de café"],
        "rango": (6000, 17000),
    },
    "Comidas Rápidas": {
        "base": "Wrap",
        "sabores": ["Crujiente", "Especial", "Ahumado", "Criollo", "Ranchero", "Picante", "Mixto", "Urbano"],
        "extras": ["de pollo", "de carne", "de cerdo", "de pollo bbq", "de atún", "de vegetales", "de jamón y queso", "de chorizo"],
        "rango": (11000, 23000),
    },
    "Especiales": {
        "base": "Plato",
        "sabores": ["Parrillero", "Criollo", "Urbano", "Costeño", "Andino", "Del Puerto", "Montañero", "Gourmet"],
        "extras": ["con papas rústicas", "con ensalada fresca", "con arroz de la casa", "con yuca crocante", "con hogao artesanal", "con chimichurri", "con salsa de la casa", "con vegetales salteados"],
        "rango": (22000, 45000),
    },
    "Sopas y Cremas": {
        "base": "Crema",
        "sabores": ["de Tomate", "de Pollo", "de Champiñón", "de Ahuyama", "de Maíz", "de Brócoli", "de Cebolla", "de Papa"],
        "extras": ["con crotones", "con queso gratinado", "con pan campesino", "con tocineta", "con cilantro fresco", "con crema de leche", "con aceite de oliva", "con topping de maíz"],
        "rango": (9000, 19000),
    },
    "Carnes y Parrilla": {
        "base": "Parrilla",
        "sabores": ["de Res", "de Cerdo", "de Pollo", "Mixta", "Montañera", "Criolla", "Costeña", "Especial"],
        "extras": ["con papa criolla", "con yuca frita", "con ensalada", "con arepa asada", "con guacamole", "con chimichurri", "con plátano maduro", "con hogao"],
        "rango": (26000, 45000),
    },
    "Desayunos": {
        "base": "Desayuno",
        "sabores": ["Paisa", "Santandereano", "Ligero", "Energético", "Criollo", "Costeño", "Campesino", "Completo"],
        "extras": ["con arepa y queso", "con chocolate caliente", "con jugo natural", "con huevos al gusto", "con pan artesanal", "con fruta fresca", "con avena", "con café recién hecho"],
        "rango": (10000, 23000),
    },
    "Smoothies y Jugos Naturales": {
        "base": "Smoothie",
        "sabores": ["Tropical", "Verde", "Energía", "Antioxidante", "Playero", "Nutritivo", "Detox", "Andino"],
        "extras": ["de mango y banano", "de fresa y mora", "de piña y coco", "de maracuyá", "de guanábana", "de frutos amarillos", "de lulo y naranja", "de banano y avena"],
        "rango": (7000, 17000),
    },
    "Menú Infantil": {
        "base": "Mini",
        "sabores": ["Burger", "Pizza", "Perrito", "Nuggets", "Salchipapa", "Quesadilla", "Alitas", "Combo"],
        "extras": ["con jugo de cajita", "con sorpresa", "con papitas", "con galleta", "con fruta", "con heladito", "con salsa suave", "con yogur"],
        "rango": (9000, 19000),
    },
}


ADICIONES_NUEVAS = [
    ("Extra pepperoni", 3500, "Pizzas"),
    ("Doble salchicha", 3000, "Perros Calientes"),
    ("Queso cheddar extra", 2500, None),
    ("Tocineta crocante", 3500, None),
    ("Aguacate fresco", 3000, None),
    ("Cebolla crispy", 2000, "Hamburguesas"),
    ("Jalapeños", 1500, None),
    ("Salsa tártara", 1000, None),
    ("Salsa BBQ ahumada", 1500, None),
    ("Salsa de ajo", 1000, None),
    ("Queso mozzarella", 2500, "Pizzas"),
    ("Borde de queso", 4000, "Pizzas"),
    ("Pollo desmechado extra", 4000, "Salchipapas"),
    ("Carne mechada extra", 4500, "Salchipapas"),
    ("Maíz tierno", 1500, None),
    ("Huevo frito", 2000, "Desayunos"),
    ("Arepa extra", 1500, "Desayunos"),
    ("Pan tostado", 1000, "Desayunos"),
    ("Papas rústicas", 3000, "Carnes y Parrilla"),
    ("Guacamole casero", 2500, None),
    ("Crema agria", 1500, "Nachos"),
    ("Dip de queso", 2000, "Alitas"),
    ("Top de fruta fresca", 2000, "Postres"),
    ("Malteada mini", 5000, "Menú Infantil"),
]


COMBOS_ESPEC = [
    {
        "nombre": "Combo Urbano Burger",
        "descripcion": "Hamburguesa contundente + papas + bebida con precio especial.",
        "partes": [("Hamburguesas", 1), ("Salchipapas", 1), ("Bebidas", 1)],
        "descuento": Decimal("4500"),
    },
    {
        "nombre": "Combo Perro Full",
        "descripcion": "Perro caliente cargado con acompañante y bebida.",
        "partes": [("Perros Calientes", 1), ("Nachos", 1), ("Bebidas", 1)],
        "descuento": Decimal("4000"),
    },
    {
        "nombre": "Combo Pizza en Pareja",
        "descripcion": "Pizza mediana con dos bebidas para compartir.",
        "partes": [("Pizzas", 1), ("Bebidas", 2)],
        "descuento": Decimal("5000"),
    },
    {
        "nombre": "Combo Alitas + Nachos",
        "descripcion": "Alitas salseadas y nachos para antojo completo.",
        "partes": [("Alitas", 1), ("Nachos", 1), ("Bebidas", 1)],
        "descuento": Decimal("4500"),
    },
    {
        "nombre": "Combo Ligero Fit",
        "descripcion": "Ensalada fresca acompañada de smoothie natural.",
        "partes": [("Ensaladas", 1), ("Smoothies y Jugos Naturales", 1)],
        "descuento": Decimal("3000"),
    },
    {
        "nombre": "Combo Parrilla Doble",
        "descripcion": "Parrilla para dos con bebida y postre para cerrar.",
        "partes": [("Carnes y Parrilla", 1), ("Bebidas", 2), ("Postres", 1)],
        "descuento": Decimal("7000"),
    },
    {
        "nombre": "Combo Desayuno Activo",
        "descripcion": "Desayuno completo con smoothie energético.",
        "partes": [("Desayunos", 1), ("Smoothies y Jugos Naturales", 1)],
        "descuento": Decimal("3000"),
    },
    {
        "nombre": "Combo Infantil Feliz",
        "descripcion": "Menú infantil con bebida y postre mini.",
        "partes": [("Menú Infantil", 1), ("Bebidas", 1), ("Postres", 1)],
        "descuento": Decimal("3500"),
    },
    {
        "nombre": "Combo Cremita + Wrap",
        "descripcion": "Crema del día con wrap recién hecho.",
        "partes": [("Sopas y Cremas", 1), ("Comidas Rápidas", 1)],
        "descuento": Decimal("3500"),
    },
    {
        "nombre": "Combo Antojo Nocturno",
        "descripcion": "Burger, alitas y bebida para compartir en grande.",
        "partes": [("Hamburguesas", 1), ("Alitas", 1), ("Bebidas", 1)],
        "descuento": Decimal("6000"),
    },
    {
        "nombre": "Combo Sabor Colombiano",
        "descripcion": "Plato especial con sopa y bebida de la casa.",
        "partes": [("Especiales", 1), ("Sopas y Cremas", 1), ("Bebidas", 1)],
        "descuento": Decimal("6500"),
    },
    {
        "nombre": "Combo Súper Compartir",
        "descripcion": "Pizza, salchipapa y dos bebidas con descuento real.",
        "partes": [("Pizzas", 1), ("Salchipapas", 1), ("Bebidas", 2)],
        "descuento": Decimal("7500"),
    },
]


def quitar_tildes(texto):
    if texto is None:
        return ""
    nfkd = unicodedata.normalize("NFD", str(texto))
    return "".join(ch for ch in nfkd if unicodedata.category(ch) != "Mn")


def normalizar_nombre(texto):
    base = quitar_tildes(texto).lower().strip()
    return " ".join(base.split())


def redondear_500(valor):
    valor_int = int(Decimal(valor))
    return int(round(valor_int / 500.0) * 500)


def contar_tablas():
    return {
        "categorias": Categoria.objects.count(),
        "productos": Producto.objects.count(),
        "adiciones": Adicion.objects.count(),
        "combos": Combo.objects.count(),
        "pedidos": Pedido.objects.count(),
    }


def imprimir_conteos(titulo, conteos):
    print(titulo)
    print(f"  Categorías : {conteos['categorias']}")
    print(f"  Productos  : {conteos['productos']}")
    print(f"  Adiciones  : {conteos['adiciones']}")
    print(f"  Combos     : {conteos['combos']}")
    print(f"  Pedidos    : {conteos['pedidos']}")


def verificar_esquema():
    faltantes = []
    existentes = set(connection.introspection.table_names())
    for tabla in ("Categoria", "Menu", "Adicion", "Combo", "Combo_Item", "Pedido", "Detalle_Pedido", "Detalle_Adicion"):
        if tabla not in existentes:
            faltantes.append(f"tabla {tabla}")

    if faltantes:
        print("La base de datos no está lista para sembrar datos.")
        print("Faltan elementos de esquema:")
        for item in faltantes:
            print(f"  - {item}")
        print("\nEjecuta primero: python sincronizar_bd.py")
        return False

    pruebas = [
        lambda: list(Categoria.objects.values_list("id_categoria", "nom_categoria", "orden", "activa")[:1]),
        lambda: list(Producto.objects.values_list("id_menu", "nombre", "descripcion", "precio", "categoria_id", "disponible", "orden")[:1]),
        lambda: list(Adicion.objects.values_list("id_adicion", "nombre", "precio", "categoria_id", "activa", "orden")[:1]),
        lambda: list(Combo.objects.values_list("id_combo", "nombre", "descripcion", "precio", "activo", "orden")[:1]),
        lambda: list(ComboItem.objects.values_list("id_item", "combo_id", "producto_id", "cantidad")[:1]),
        lambda: list(Pedido.objects.values_list("id_pedido", "id_mesa", "estado", "prioridad", "fecha_pedido", "total", "observaciones")[:1]),
        lambda: list(DetallePedido.objects.values_list("id_detalle", "pedido_id", "producto_id", "combo_id", "cantidad", "precio_unitario", "valor_venta", "notas")[:1]),
        lambda: list(DetalleAdicion.objects.values_list("id_detalle_adicion", "detalle_id", "adicion_id", "precio")[:1]),
    ]

    try:
        for prueba in pruebas:
            prueba()
    except (OperationalError, ProgrammingError, DatabaseError) as exc:
        print("La base tiene tablas, pero faltan columnas o hay estructura desactualizada.")
        print(f"Detalle técnico: {type(exc).__name__}: {exc}")
        print("\nEjecuta primero: python sincronizar_bd.py")
        return False

    return True


def obtener_o_crear_categorias():
    creadas = 0
    omitidas = 0

    existentes = list(Categoria.objects.all().order_by("orden", "id_categoria"))
    por_normalizado = {normalizar_nombre(c.nom_categoria): c for c in existentes}
    max_orden = max([c.orden for c in existentes], default=0)

    todas = CATEGORIAS_BASE + NUEVAS_CATEGORIAS
    for nombre in todas:
        clave = normalizar_nombre(nombre)
        categoria = por_normalizado.get(clave)
        if categoria:
            omitidas += 1
            if not categoria.activa:
                categoria.activa = True
                categoria.save(update_fields=["activa"])
            continue
        max_orden += 1
        categoria = Categoria.objects.create(nom_categoria=nombre, orden=max_orden, activa=True)
        por_normalizado[clave] = categoria
        creadas += 1

    return creadas, omitidas


def generar_productos_plan(categorias, ciclo):
    plan = []
    sellos = ["de autor", "de la casa", "receta especial", "edición urbana", "sabor premium"]

    for categoria in categorias:
        plantilla = PLANTILLAS_PRODUCTOS.get(categoria.nom_categoria)
        if not plantilla:
            continue

        base = plantilla["base"]
        sabores = plantilla["sabores"]
        extras = plantilla["extras"]
        pmin, pmax = plantilla["rango"]
        precios = list(range(pmin, pmax + 1, 500)) or [pmin]

        for i in range(16):
            idx = (ciclo * 16) + i
            sabor = sabores[idx % len(sabores)]
            extra = extras[(idx * 3 + ciclo) % len(extras)]

            nombre = f"{base} {sabor} {extra}".strip()
            if ciclo > 0:
                nombre = f"{nombre} {sellos[(idx + ciclo) % len(sellos)]}"

            descripcion = (
                f"{nombre} preparada al momento, con ingredientes frescos y toque colombiano."
            )
            precio = precios[(idx * 2 + ciclo) % len(precios)]
            precio = max(3000, min(45000, redondear_500(precio)))

            plan.append(
                {
                    "categoria": categoria,
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "precio": precio,
                }
            )

    return plan


def sembrar_productos():
    existentes = list(Producto.objects.all().values("id_menu", "nombre", "categoria_id", "orden"))
    nombres_existentes = {normalizar_nombre(p["nombre"]) for p in existentes}

    categorias = list(Categoria.objects.filter(activa=True).order_by("orden", "id_categoria"))

    orden_por_categoria = {}
    for p in existentes:
        cid = p["categoria_id"]
        orden_por_categoria[cid] = max(orden_por_categoria.get(cid, 0), p["orden"] or 0)

    total_inicial = len(existentes)
    objetivo_total = 285
    meta_nuevos = max(0, objetivo_total - total_inicial)

    creados = 0
    omitidos = 0
    ciclo = 0

    while creados < meta_nuevos and ciclo < 25:
        plan = generar_productos_plan(categorias, ciclo=ciclo)
        ciclo += 1

        for item in plan:
            if creados >= meta_nuevos:
                break

            nombre = item["nombre"]
            clave = normalizar_nombre(nombre)

            if clave in nombres_existentes:
                omitidos += 1
                continue

            cat = item["categoria"]
            orden_por_categoria[cat.id_categoria] = orden_por_categoria.get(cat.id_categoria, 0) + 1

            Producto.objects.create(
                nombre=nombre,
                descripcion=item["descripcion"],
                precio=Decimal(item["precio"]),
                categoria=cat,
                disponible=True,
                orden=orden_por_categoria[cat.id_categoria],
            )
            nombres_existentes.add(clave)
            creados += 1

    return creados, omitidos


def sembrar_adiciones():
    categorias = list(Categoria.objects.all())
    cat_por_nombre = {normalizar_nombre(c.nom_categoria): c for c in categorias}

    existentes = list(Adicion.objects.all())
    nombres_existentes = {normalizar_nombre(a.nombre): a for a in existentes}
    max_orden = max([a.orden for a in existentes], default=0)

    creadas = 0
    omitidas = 0

    for nombre, precio, categoria_nombre in ADICIONES_NUEVAS:
        clave = normalizar_nombre(nombre)
        if clave in nombres_existentes:
            omitidas += 1
            continue

        categoria = None
        if categoria_nombre:
            categoria = cat_por_nombre.get(normalizar_nombre(categoria_nombre))

        max_orden += 1
        ad = Adicion.objects.create(
            nombre=nombre,
            precio=Decimal(precio),
            categoria=categoria,
            activa=True,
            orden=max_orden,
        )
        nombres_existentes[clave] = ad
        creadas += 1

    return creadas, omitidas


def crear_combos():
    categorias = {normalizar_nombre(c.nom_categoria): c for c in Categoria.objects.filter(activa=True)}
    productos_por_cat = {}
    for cat in categorias.values():
        prods = list(
            Producto.objects.filter(categoria=cat, disponible=True).order_by("orden", "id_menu")
        )
        if prods:
            productos_por_cat[cat.id_categoria] = prods

    existentes = {normalizar_nombre(c.nombre): c for c in Combo.objects.all()}
    max_orden = max([c.orden for c in Combo.objects.all()], default=0)
    creados = 0
    omitidos = 0

    for i, spec in enumerate(COMBOS_ESPEC, start=1):
        clave = normalizar_nombre(spec["nombre"])
        if clave in existentes:
            omitidos += 1
            continue

        partes = []
        valido = True
        for j, (cat_nombre, cantidad) in enumerate(spec["partes"]):
            cat = categorias.get(normalizar_nombre(cat_nombre))
            if not cat:
                valido = False
                break
            lista = productos_por_cat.get(cat.id_categoria, [])
            if not lista:
                valido = False
                break
            prod = lista[(i + j) % len(lista)]
            partes.append((prod, int(cantidad)))

        if not valido or len(partes) < 2:
            omitidos += 1
            continue

        suma_suelta = sum((p.precio or Decimal("0")) * cant for p, cant in partes)
        precio_combo = suma_suelta - spec["descuento"]
        precio_combo = Decimal(redondear_500(precio_combo))
        if precio_combo >= suma_suelta:
            precio_combo = Decimal(redondear_500(suma_suelta - Decimal("500")))
        if precio_combo <= 0:
            precio_combo = Decimal("3000")
        if precio_combo >= suma_suelta:
            precio_combo = suma_suelta - Decimal("500")
        if precio_combo <= 0:
            omitidos += 1
            continue

        max_orden += 1
        combo = Combo.objects.create(
            nombre=spec["nombre"],
            descripcion=spec["descripcion"],
            precio=precio_combo,
            activo=True,
            orden=max_orden,
        )
        for prod, cant in partes:
            ComboItem.objects.create(combo=combo, producto=prod, cantidad=cant)

        existentes[clave] = combo
        creados += 1

    return creados, omitidos


def adiciones_aplicables_para_producto(producto):
    consulta = Adicion.objects.filter(activa=True)
    consulta = consulta.filter(categoria__isnull=True) | consulta.filter(categoria_id=producto.categoria_id)
    return list(consulta.order_by("orden", "id_adicion").distinct())


def adiciones_globales():
    return list(Adicion.objects.filter(activa=True, categoria__isnull=True).order_by("orden", "id_adicion"))


def sembrar_pedidos_demo(cantidad=40):
    demo_existentes = Pedido.objects.filter(observaciones__istartswith="[demo]").count()
    if demo_existentes:
        return 0, cantidad

    productos = list(Producto.objects.filter(disponible=True).order_by("id_menu"))
    combos = list(Combo.objects.filter(activo=True).order_by("id_combo"))
    if not productos:
        return 0, cantidad

    globales = adiciones_globales()
    estados = [
        "pendiente",
        "en_preparacion",
        "listo",
        "entregado",
        "entregado",
        "cancelado",
    ]

    creados = 0
    base = timezone.now()

    for i in range(cantidad):
        fecha = base - timedelta(days=(i % 30), hours=((i * 3) % 24), minutes=((i * 11) % 60))
        mesa = (i % 12) + 1
        estado = estados[i % len(estados)]
        prioridad = (i % 3) + 1

        observacion = "[demo] Pedido de ejemplo"
        if i % 4 == 0:
            observacion = "[demo] Sin cebolla, por favor."
        elif i % 5 == 0:
            observacion = "[demo] Empacar para llevar."

        pedido = Pedido.objects.create(
            id_mesa=mesa,
            estado=estado,
            prioridad=prioridad,
            fecha_pedido=fecha,
            total=Decimal("0"),
            observaciones=observacion,
        )

        lineas = (i % 4) + 1
        total_pedido = Decimal("0")

        for j in range(lineas):
            usar_combo = bool(combos) and ((i + j) % 3 == 0)
            cantidad_linea = ((i + j) % 3) + 1

            producto = None
            combo = None
            precio_unitario = Decimal("0")
            adiciones = []

            if usar_combo:
                combo = combos[(i + j) % len(combos)]
                precio_unitario = Decimal(combo.precio or 0)
                if globales and (i + j) % 2 == 0:
                    adiciones = [globales[(i + j) % len(globales)]]
            else:
                producto = productos[(i * 2 + j) % len(productos)]
                precio_unitario = Decimal(producto.precio or 0)
                aplicables = adiciones_aplicables_para_producto(producto)
                if aplicables and (i + j) % 2 == 0:
                    adiciones = [aplicables[(i + j) % len(aplicables)]]
                    if len(aplicables) > 2 and (i + j) % 5 == 0:
                        adiciones.append(aplicables[(i + j + 1) % len(aplicables)])

            suma_adiciones = sum((Decimal(a.precio or 0) for a in adiciones), Decimal("0"))
            valor_venta = (precio_unitario + suma_adiciones) * Decimal(cantidad_linea)

            detalle = DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                combo=combo,
                cantidad=cantidad_linea,
                precio_unitario=precio_unitario,
                valor_venta=valor_venta,
                notas="sin picante" if (i + j) % 6 == 0 else "",
            )

            for ad in adiciones:
                DetalleAdicion.objects.create(
                    detalle=detalle,
                    adicion=ad,
                    precio=Decimal(ad.precio or 0),
                )

            total_pedido += valor_venta

        pedido.total = total_pedido
        pedido.save(update_fields=["total"])
        creados += 1

    return creados, 0


def resumen_final(resultados):
    conteos = contar_tablas()
    print(LINEA)
    print("RESUMEN DE SIEMBRA")
    print(LINEA)
    print(
        "Categorías: creadas {creadas}, omitidas {omitidas}".format(
            creadas=resultados["categorias"]["creadas"],
            omitidas=resultados["categorias"]["omitidas"],
        )
    )
    print(
        "Productos : creados {creados}, omitidos {omitidos}".format(
            creados=resultados["productos"]["creados"],
            omitidos=resultados["productos"]["omitidos"],
        )
    )
    print(
        "Adiciones : creadas {creadas}, omitidas {omitidas}".format(
            creadas=resultados["adiciones"]["creadas"],
            omitidas=resultados["adiciones"]["omitidas"],
        )
    )
    print(
        "Combos    : creados {creados}, omitidos {omitidos}".format(
            creados=resultados["combos"]["creados"],
            omitidos=resultados["combos"]["omitidos"],
        )
    )
    print(
        "Pedidos   : creados {creados}, omitidos {omitidos}".format(
            creados=resultados["pedidos"]["creados"],
            omitidos=resultados["pedidos"]["omitidos"],
        )
    )
    print(SUB)
    imprimir_conteos("Totales finales:", conteos)


def main():
    parser = argparse.ArgumentParser(
        description="Siembra datos de ejemplo para Sabor Urbano usando ORM de Django."
    )
    parser.add_argument(
        "--solo-ver",
        action="store_true",
        help="Muestra conteos actuales sin escribir datos.",
    )
    args = parser.parse_args()

    print(LINEA)
    print(" SABOR URBANO · siembra de datos demo")
    print(LINEA)
    print(f" Carpeta  : {BASE}")
    print(f" Settings : {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f" Django   : {django.get_version()} · {MOTOR}")
    print(SUB)

    if not verificar_esquema():
        return 1

    inicial = contar_tablas()
    imprimir_conteos("Conteos actuales:", inicial)

    if args.solo_ver:
        print(SUB)
        print("Modo --solo-ver: no se escribió ningún registro.")
        print(LINEA)
        return 0

    resultados = {
        "categorias": {"creadas": 0, "omitidas": 0},
        "productos": {"creados": 0, "omitidos": 0},
        "adiciones": {"creadas": 0, "omitidas": 0},
        "combos": {"creados": 0, "omitidos": 0},
        "pedidos": {"creados": 0, "omitidos": 0},
    }

    try:
        with transaction.atomic():
            cat_creadas, cat_omit = obtener_o_crear_categorias()
            prod_creados, prod_omit = sembrar_productos()
            adi_creadas, adi_omit = sembrar_adiciones()
            comb_creados, comb_omit = crear_combos()
            ped_creados, ped_omit = sembrar_pedidos_demo(cantidad=40)

            resultados["categorias"] = {"creadas": cat_creadas, "omitidas": cat_omit}
            resultados["productos"] = {"creados": prod_creados, "omitidos": prod_omit}
            resultados["adiciones"] = {"creadas": adi_creadas, "omitidas": adi_omit}
            resultados["combos"] = {"creados": comb_creados, "omitidos": comb_omit}
            resultados["pedidos"] = {"creados": ped_creados, "omitidos": ped_omit}
    except Exception as exc:
        print("\nOcurrió un error durante la siembra. No se guardaron cambios parciales.")
        print(f"Detalle: {type(exc).__name__}: {exc}")
        print("Si sospechas de estructura incompleta, corre primero: python sincronizar_bd.py")
        print(LINEA)
        return 2

    resumen_final(resultados)
    print(LINEA)
    return 0


if __name__ == "__main__":
    sys.exit(main())
