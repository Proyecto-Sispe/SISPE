# SISPE · Sistema Integrado de Pedidos, Adiciones y Sala

SISPE reúne todas las partes del proyecto (Carta, pedidos, cocina, servicio en sala, control de accesos, roles, datos y reportes) en un solo servidor Django.

## Estructura de Módulos y Rutas Principales

| Parte | Apps de Django | Rutas Clave |
| ----- | ----- | ----- |
| **Carta, pedidos y cocina** | `menu`, `pedidos`, `cocina` | `/?mesa=5`, `/carrito/`, `/seguimiento/<id>/`, `/cocina/`, `/gestion/...` |
| **Servicio en sala** | `mesas_pedidos` | `/servicio/`, `/servicio/mesas/` (mesas + QR), `/servicio/mesa/<id>/pedir/`, `/servicio/pedidos/` |
| **Acceso y roles** | `seguimiento_pedidos` | `/login/`, `/logout/`, `/recuperar-password/`, `/dashboard/<rol>/` |
| **Datos y reportes** | `base_datos`, `dashboard` | Modelos en `/admin/`; estadísticas integradas en `/cocina/reportes/` |

> **Portal Principal:** Puedes acceder a la vista general que enlaza todos los módulos en `http://127.0.0.1:8000/portal/`

## Instalación y Puesta en Marcha (Windows)

1. Prepara el entorno virtual e instala las dependencias:

```powershell
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### Actualización y Sincronización de Base de Datos

* **Para actualizar o poblar datos iniciales de adiciones/combos:**

  ```powershell
  python actualizar_bd.py
  ```

  *(Crea las tablas `Adicion`, `Combo`, `Combo_Item`, `Detalle_Adicion`, agrega columnas faltantes y siembra 8 adiciones de ejemplo. Es idempotente).*

* **Si la base está completamente vacía:**

  ```powershell
  python manage.py migrate
  python crear_tablas.py
  python restablecer_acceso.py
  python actualizar_bd.py
  ```

* **Si aparece un error de columna (`OperationalError: no such column...`):**
  Ejecuta el script de sincronización para corregir la estructura sin perder datos:

  ```powershell
  python sincronizar_bd.py
  ```

  *(Usa `python sincronizar_bd.py --solo-ver` para revisar cambios sin modificar la base de datos).*

## Bases de Datos y Enrutamiento (`config/routers.py`)

El sistema utiliza múltiples bases de datos SQLite organizadas por contexto:

| Alias | Archivo SQLite | Contenido |
| ----- | ----- | ----- |
| `default` | `db.sqlite3` | Usuarios de Django, sesiones, carta, pedidos y cocina |
| `mesas` | `db_mesas.sqlite3` | Mesas, códigos QR, sesiones y pedidos por mesa |
| `sistema` | `db_sistema.sqlite3` | Personas, roles, insumos y datos del esquema SISPE |

### Configuración con MySQL (Opcional)

Para usar MySQL en la base de datos `sistema`, define las siguientes variables de entorno:

* `SISPE_SISTEMA_DB=mysql`
* `SISPE_DB_PASS=tu_contrasena`
* Variables opcionales: `SISPE_DB_NAME`, `SISPE_DB_USER`, `SISPE_DB_HOST`, `SISPE_DB_PORT`.

## Usuarios y Roles de Acceso

La pantalla de `/login/` admite dos tipos de credenciales:

1. **Correo de persona SISPE (Tabla `Persona`):** Entra a su panel por rol y sincroniza automáticamente un usuario Django con el grupo adecuado (ej. Cocinero -> `Chef`, Administrador -> Superusuario).
2. **Usuarios de Django:**

| Usuario / Correo | Contraseña | Vistas habilitadas / Rol |
| ----- | ----- | ----- |
| `admin` | `Admin12345` | `/admin/`, `/cocina/`, `/gestion/` |
| `chef` | `Chef12345` | `/cocina/`, `/cocina/qr/`, `/cocina/reportes/` |
| `admin@gmail.com` | `1234` | Administrador |
| `cocina1@gmail.com` | `1234` | Cocina |
| `mesero1@gmail.com` | `1234` | Mesero |
| `cliente@gmail.com` | `1234` | Cliente |

> **Nota:** El usuario Django `superadmin` es de tipo `staff` (no superusuario) y su clave debe asignársela un superusuario antes de iniciar sesión.

## Funcionalidades Destacadas

* **Adiciones:** Permite asociar extras a platos o categorías enteras. Sus precios se registran en `Detalle_Adicion` y se reflejan en la comanda y reportes.
* **Combos:** Permite estructurar paquetes con precio propio y componentes dinámicos (`Combo_Item`) desde `/gestion/combos/<id>/partes/`.
* **Imágenes:** Se cargan en `/gestion/productos/<id>/editar/` o desde `/admin/`, guardándose en `media/productos/`. Si un producto no tiene imagen, la interfaz muestra su inicial.
* **Mesas y Códigos QR:** Centralizados en `/servicio/mesas/`. Permite generar, descargar e imprimir códigos QR para las mesas.
* **Reportes:** Incluye métricas de venta filtrables y exportación a archivos Excel y PDF.

## Configuración de Envío de Correos

De manera predeterminada, los correos de restablecimiento de contraseña se imprimen en consola. Para habilitar el envío mediante Gmail, establece las siguientes variables de entorno:

```powershell
$env:SISPE_EMAIL_USER="tu_cuenta@gmail.com"
$env:SISPE_EMAIL_PASS="tu_clave_de_aplicacion"
$env:SISPE_EMAIL_FROM="tu_cuenta@gmail.com" # Opcional