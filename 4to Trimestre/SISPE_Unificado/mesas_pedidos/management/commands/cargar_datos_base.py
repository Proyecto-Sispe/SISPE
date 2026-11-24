from decimal import Decimal
from django.core.management.base import BaseCommand
from mesas_pedidos.models import Adicion, Categoria, Menu, Mesa


class Command(BaseCommand):
    help = "Carga mesas, categorías, productos y adiciones iniciales en SQLite"

    def handle(self, *args, **options):
        estado_libre = getattr(Mesa, "ESTADO_LIBRE", 0)

        mesas_data = [
            (1, 4, "Primer Piso"),
            (2, 2, "Primer Piso"),
            (3, 6, "Segundo Piso"),
            (4, 4, "Terraza"),
        ]
        for num, cap, ubi in mesas_data:
            Mesa.objects.get_or_create(
                id=num,
                defaults={"capacidad": cap, "ubicacion": ubi, "estado": estado_libre},
            )

        cat_hamburguesas, _ = Categoria.objects.get_or_create(nom_categoria="Hamburguesas")
        cat_salchipapas, _ = Categoria.objects.get_or_create(nom_categoria="Salchipapas")
        cat_pizzas, _ = Categoria.objects.get_or_create(nom_categoria="Pizza")

        productos_data = [
            (cat_hamburguesas, "Hamburguesa Clásica", 16000, "Carne, queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas"),
            (cat_hamburguesas, "Hamburguesa Crispy Bacon", 19000, "Carne, doble tocineta, queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas"),
            (cat_salchipapas, "Salchipapa Tentación", 12000, "Papas fritas, rodajas de salchicha americana y dos huevos de codorniz"),
            (cat_pizzas, "Pizza Pepperoni", 17000, "Queso mozzarella y rodajas de pepperoni"),
        ]
        for cat, prod, precio, desc in productos_data:
            Menu.objects.get_or_create(
                productos=prod,
                defaults={"precio": Decimal(str(precio)), "descripcion": desc, "categoria": cat},
            )

        adiciones_data = [
            ("Queso extra", 3000),
            ("Tocineta extra", 4000),
            ("Sin cebolla", 0),
            ("Papas grandes", 5000),
            ("Salsa BBQ extra", 1500),
        ]
        for nombre, precio in adiciones_data:
            Adicion.objects.get_or_create(nombre=nombre, defaults={"precio": Decimal(str(precio))})

        self.stdout.write(self.style.SUCCESS("Datos base cargados correctamente en SQLite."))