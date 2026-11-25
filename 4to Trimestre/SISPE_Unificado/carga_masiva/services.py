import csv
import io
from decimal import Decimal, InvalidOperation

from openpyxl import load_workbook

from menu.models import Categoria, Producto
from administracion.models import Insumo
def leer_archivo(archivo):

    nombre = archivo.name.lower()

    if nombre.endswith(".xlsx"):

        libro = load_workbook(
            archivo,
            read_only=True,
            data_only=True
        )

        hoja = libro.active

        filas = list(hoja.iter_rows(values_only=True))

        if not filas:
            raise ValueError("El archivo está vacío.")

        encabezados = [
            str(valor).strip().lower() if valor is not None else ""
            for valor in filas[0]
        ]

        return [
            dict(zip(encabezados, fila))
            for fila in filas[1:]
            if any(valor is not None for valor in fila)
        ]

    elif nombre.endswith(".csv"):

        contenido = archivo.read().decode("utf-8-sig")

        muestra = contenido[:2048]

        try:
            dialecto = csv.Sniffer().sniff(
                muestra,
                delimiters=",;"
            )
            separador = dialecto.delimiter
        except csv.Error:
            separador = ","

        lector = csv.DictReader(
            io.StringIO(contenido),
            delimiter=separador
        )

        return [
            {
                str(k).strip().lower(): v
                for k, v in fila.items()
            }
            for fila in lector
        ]

    raise ValueError("Formato de archivo no permitido.")

def validar_filas(tipo, filas):

    errores = []
    registros = []
    vistos = set()

    if not filas:
        return [], [{"fila": 1, "error": "El archivo no contiene registros."}]

    for numero, fila in enumerate(filas, start=2):

        try:

            if tipo == "categorias":

                nombre = str(
                    fila.get("nombre") or ""
                ).strip()

                if not nombre:
                    raise ValueError("Falta el nombre.")

                clave = nombre.casefold()
                if clave in vistos:
                    raise ValueError("La categoría está repetida en el archivo.")

                if Categoria.objects.using("default").filter(
                    nom_categoria__iexact=nombre
                ).exists():
                    raise ValueError("La categoría ya existe.")

                vistos.add(clave)
                registros.append({
                    "nombre": nombre
                })

            elif tipo == "productos":

                nombre = str(
                    fila.get("nombre") or ""
                ).strip()

                categoria_nombre = str(
                    fila.get("categoria") or ""
                ).strip()

                if not nombre:
                    raise ValueError("Falta el nombre del producto.")

                if not categoria_nombre:
                    raise ValueError("Falta la categoría.")

                precio = Decimal(str(fila["precio"]))

                if precio < 0:
                    raise ValueError("El precio no puede ser negativo.")

                categoria = Categoria.objects.using(
                    "default"
                ).filter(
                    nom_categoria__iexact=categoria_nombre
                ).first()

                if not categoria:
                    raise ValueError(
                        f"No existe la categoría {categoria_nombre}."
                    )

                clave = (nombre.casefold(), categoria.pk)
                if clave in vistos:
                    raise ValueError("El producto está repetido en el archivo.")

                disponible = str(
                    fila.get("disponible", "1")
                ).strip().lower()

                if disponible not in ("1", "0", "true", "false"):
                    raise ValueError("Disponibilidad inválida.")

                if Producto.objects.using("default").filter(
                    nombre__iexact=nombre,
                    categoria=categoria
                ).exists():
                    raise ValueError("El producto ya existe.")

                vistos.add(clave)
                registros.append({
                    "nombre": nombre,
                    "descripcion": str(
                        fila.get("descripcion") or ""
                    ).strip(),
                    "precio": precio,
                    "categoria": categoria,
                    "disponible": disponible in ("1", "true"),
                    "orden": int(fila.get("orden") or 0),
                })

            elif tipo == "insumos":

                nombre = str(
                    fila.get("nombre") or ""
                ).strip()

                if not nombre:
                    raise ValueError("Falta el nombre del insumo.")

                clave = nombre.casefold()
                if clave in vistos:
                    raise ValueError("El insumo está repetido en el archivo.")

                if Insumo.objects.using("default").filter(
                    nombre__iexact=nombre
                ).exists():
                    raise ValueError("El insumo ya existe.")

                stock = Decimal(str(
                    fila.get("stock_actual", 0) or 0
                ))

                minimo = Decimal(str(
                    fila.get("stock_minimo", 0) or 0
                ))

                if stock < 0 or minimo < 0:
                    raise ValueError("El stock no puede ser negativo.")

                vistos.add(clave)
                registros.append({
                    "nombre": nombre,
                    "unidad": str(
                        fila.get("unidad") or "Unidades"
                    ).strip(),
                    "stock_actual": stock,
                    "stock_minimo": minimo,
                    "activo": str(
                        fila.get("activo", "1")
                    ).strip().lower() in ("1", "true"),
                })

        except (ValueError, TypeError, KeyError, InvalidOperation) as error:

            errores.append({
                "fila": numero,
                "error": str(error)
            })

    return registros, errores