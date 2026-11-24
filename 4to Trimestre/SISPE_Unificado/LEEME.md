# SISPE Unificado

Une las cuatro partes del proyecto en un solo servidor Django.

| Parte | Apps | Rutas |
|---|---|---|
| Carta, pedidos y cocina | `menu`, `pedidos`, `cocina` | `/`, `/carrito/`, `/seguimiento/<id>/`, `/cocina/`, `/gestion/...` |
| Servicio en sala | `mesas_pedidos` | `/servicio/`, `/servicio/mesas/` mesas + QR, `/servicio/mesa/<id>/pedir/`, `/servicio/pedidos/` |
| Acceso y roles | `seguimiento_pedidos` | `/login/`, `/logout/`, `/recuperar-password/`, `/dashboard/<rol>/` |
| Datos y reportes | `base_datos`, `dashboard` | modelos en `/admin/`; estadísticas integradas en `/cocina/reportes/` |

`/portal/` enlaza todos los módulos.
Los reportes incluyen métricas filtrables y exportación a Excel y PDF. La ruta
antigua `/estadisticas/` redirige al reporte integrado.

La gestión de mesas y la generación de QR están reunidas en `/servicio/mesas/`.
Administradores pueden generar, descargar e imprimir los QR de las mesas
registradas; meseros solo ven el estado y las acciones de servicio. Los accesos
QR antiguos redirigen a esta página y requieren el rol Administrador.

## Arrancar (Windows)

```powershell
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abrir http://127.0.0.1:8000/portal/

## Bases de datos

Las partes usan tablas con el mismo nombre pero columnas distintas, así que
cada una conserva su base (`config/routers.py`):

| Alias | Archivo | Contenido |
|---|---|---|
| `default` | `db.sqlite3` | usuarios Django, sesiones, carta, pedidos y cocina |
| `mesas` | `db_mesas.sqlite3` | mesas, QR, sesiones y pedidos por mesa |
| `sistema` | `db_sistema.sqlite3` | personas, roles, insumos y datos del esquema SISPE |

Para usar MySQL en `sistema`: definir `SISPE_SISTEMA_DB=mysql` y `SISPE_DB_PASS`
(opcionales `SISPE_DB_NAME`, `SISPE_DB_USER`, `SISPE_DB_HOST`, `SISPE_DB_PORT`).

## Acceso

`/login/` acepta:

- Correo de una persona SISPE (tabla `Persona`): entra a su panel por rol y
  se le crea un usuario Django con el grupo equivalente (Cocinero -> `Chef`,
  Administrador -> superusuario), así puede usar la cocina y el admin.
- Usuario de Django: `admin` / `Admin12345`, `chef` / `Chef12345`.

Personas de prueba (contraseña `1234`): `admin@gmail.com`, `cocina1@gmail.com`,
`mesero1@gmail.com`, `cliente@gmail.com`.

Son claves de desarrollo: cámbialas antes de publicar.

El usuario Django `superadmin` es de tipo `staff`, no es superusuario y no tiene
permisos sobre modelos; solo puede abrir el Centro de Gestión SISPE. Su contraseña
está sin configurar y un superusuario debe asignársela antes de iniciar sesión.

## Correo

Sin configurar, los correos de recuperación se imprimen en la consola. Para enviar
correos con Gmail, crea una contraseña de aplicación y configura estas variables
en la misma terminal antes de iniciar Django:

```powershell
$env:SISPE_EMAIL_USER="cuenta@gmail.com"
$env:SISPE_EMAIL_PASS="clave de aplicacion"
```

Opcionalmente, configura `SISPE_EMAIL_FROM` para la dirección remitente. No guardes
la contraseña de aplicación en los archivos del proyecto.
