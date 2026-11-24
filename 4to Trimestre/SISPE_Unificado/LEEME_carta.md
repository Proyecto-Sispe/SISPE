# Sabor Urbano · adiciones, combos e imágenes

## Instalación

1. Descomprime el ZIP encima de `Sistema_Python`, aceptando reemplazar.
   El ZIP **no incluye** `db.sqlite3`, así que tus usuarios, productos y pedidos se conservan.
2. Con el entorno virtual activo:

```powershell
pip install -r requirements.txt
python actualizar_bd.py
python manage.py runserver 0.0.0.0:8000
```

`actualizar_bd.py` crea las tablas nuevas (`Adicion`, `Combo`, `Combo_Item`,
`Detalle_Adicion`), agrega las columnas que falten y siembra 8 adiciones de ejemplo.
Es idempotente: puedes correrlo varias veces.

Si la base está vacía o borraste `db.sqlite3`:

```powershell
python manage.py migrate
python crear_tablas.py
python restablecer_acceso.py
python actualizar_bd.py
```

## Usuarios

| Usuario | Contraseña | Entra a |
|---|---|---|
| `admin` | `Admin12345` | `/admin/`, `/cocina/`, `/gestion/` |
| `chef` | `Chef12345` | `/cocina/`, `/cocina/qr/`, `/cocina/reportes/` |

## Rutas

| Ruta | Qué hace |
|---|---|
| `/?mesa=5` | Carta del cliente con imágenes, adiciones y combos |
| `/carrito/` | Carrito con adiciones y total |
| `/seguimiento/<id>/` | Estado del pedido en vivo |
| `/cocina/` | Panel del chef |
| `/cocina/qr/` | Hoja de QR de mesas con selector de IP |
| `/cocina/reportes/` | Reportes de ventas |
| `/gestion/productos/` | CRUD de productos (crear, modificar, eliminar) |
| `/gestion/adiciones/` | CRUD de adiciones |
| `/gestion/combos/` | CRUD de combos y sus partes |

## Adiciones

Cada adición tiene nombre y precio. Al elegirla en la carta, su precio se suma al
del plato y se guarda en `Detalle_Adicion`, así que la comanda y el reporte
muestran el extra. Si dejas la categoría vacía, la adición se ofrece en todos los
productos; si la llenas, solo en esa categoría.

## Combos

Un combo tiene precio propio y una lista de partes (`Combo_Item`), cada una con
producto y cantidad. Las partes se agregan, modifican y quitan desde
`/gestion/combos/<id>/partes/`. El admin muestra la suma suelta para comparar.

## Imágenes

Se suben desde `/gestion/productos/<id>/editar/` o desde el admin, campo **foto**.
Se guardan en `media/productos/` y aparecen en la carta y en el carrito. Si un
plato no tiene imagen, la carta muestra su inicial.


---

## Si ya tenías el sistema instalado y sale un error de columna

Mensajes como:

```
OperationalError at /cocina/
no such column: Pedido.total
```

significan que tu `db.sqlite3` se creó con la versión anterior y le faltan
columnas que el código nuevo sí usa. No hay que borrar la base: se arregla
en el sitio, sin perder productos, pedidos ni usuarios.

Copia `sincronizar_bd.py` al lado de `manage.py` y córrelo:

```
python sincronizar_bd.py
```

Qué hace, en orden:

1. Compara cada tabla con lo que el código espera y **agrega solo las
   columnas que faltan** (`Pedido.total`, `Pedido.prioridad`,
   `Menu.foto`, `Detalle_Pedido.precio_unitario`, etc.).
2. Crea las tablas que no existan (`Adicion`, `Combo`, `Combo_Item`,
   `Detalle_Adicion`).
3. Recupera los totales de los pedidos viejos sumando sus líneas, y rellena
   los campos que quedaron vacíos.
4. **Verifica de verdad**: corre las mismas consultas de `/cocina/` y
   `/cocina/reportes/` y pide las páginas por HTTP. Si algo sigue mal, te
   dice exactamente qué.

Es idempotente: la segunda corrida no cambia nada.

Si solo quieres ver qué falta sin tocar nada:

```
python sincronizar_bd.py --solo-ver
```

`actualizar_bd.py` también quedó corregido con las mismas columnas, así que
cualquiera de los dos scripts deja la base al día.
