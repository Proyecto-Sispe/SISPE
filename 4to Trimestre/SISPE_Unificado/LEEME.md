# SISPE Unificado

Une las cuatro partes del proyecto en un solo servidor Django.

| Parte | Apps | Rutas |
|---|---|---|
| Parte Adriancho | `menu`, `pedidos`, `cocina` | `/` carta, `/carrito/`, `/seguimiento/<id>/`, `/cocina/`, `/gestion/...`, `/qr/<mesa>/` |
| Sistema_Victor | `mesas_pedidos` | `/servicio/`, `/servicio/mesas/`, `/servicio/mesa/<id>/pedir/`, `/servicio/pedidos/` |
| Sistema_sispe | `seguimiento_pedidos` | `/login/`, `/logout/`, `/recuperar-password/`, `/dashboard/<rol>/` |
| parte juan davisito | `base_datos`, `dashboard` | `/estadisticas/`, modelos en `/admin/` |

`/portal/` enlaza todos los módulos.

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
| `default` | `db.sqlite3` | usuarios Django, sesiones, carta/pedidos/cocina (Adriancho) |
| `mesas` | `db_mesas.sqlite3` | mesas, QR, sesiones y pedidos por mesa (Victor) |
| `sistema` | `db_sistema.sqlite3` | personas, roles, insumos, facturas (Juan / Sistema_sispe) |

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

## Correo

Sin configurar, los correos de recuperación se imprimen en la consola. Para Gmail:

```powershell
$env:SISPE_EMAIL_USER="cuenta@gmail.com"
$env:SISPE_EMAIL_PASS="clave de aplicacion"
```
