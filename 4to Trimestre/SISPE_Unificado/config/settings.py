"""
Configuracion unificada de SISPE.

Une las cuatro partes del proyecto en un solo servidor Django:
  - Parte Adriancho   -> menu, pedidos, cocina   (carta, carrito, cocina, gestion)
  - Sistema_Victor    -> mesas_pedidos            (mesas, QR, pedido por mesa)
  - Sistema_sispe     -> seguimiento_pedidos      (login por rol, recuperar contrasena)
  - parte juan davisito -> base_datos, dashboard  (modelos del esquema SISPE y estadisticas)

Cada parte conserva su base de datos porque sus tablas tienen el mismo nombre
con columnas distintas. config/routers.py decide a que base va cada app.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "SISPE_SECRET", "django-insecure-sispe-unificado-cambia-esta-clave-en-produccion"
)
DEBUG = os.environ.get("SISPE_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Parte Adriancho
    "menu",
    "pedidos",
    "cocina",
    # Sistema_Victor
    "mesas_pedidos",
    # Sistema_sispe
    "seguimiento_pedidos",
    # parte juan davisito
    "base_datos",
    "dashboard",
    # Modulo de administracion (inventario, facturas, usuarios)
    "administracion",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "pedidos.context.carrito_contador",
                "seguimiento_pedidos.context_processors.rol_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# default -> usuarios de Django, sesiones, admin y la carta (Parte Adriancho)
# mesas   -> mesas, QR y pedidos por mesa (Sistema_Victor)
# sistema -> esquema SISPE original: personas, roles, insumos... (juan davisito + Sistema_sispe)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "mesas": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_mesas.sqlite3",
    },
    "sistema": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_sistema.sqlite3",
    },
}

# Para usar la base MySQL/MariaDB "sistema" del script sistema.sql:
#   $env:SISPE_SISTEMA_DB="mysql"; $env:SISPE_DB_PASS="tu_clave"
if os.environ.get("SISPE_SISTEMA_DB", "").lower() in ("mysql", "mariadb"):
    try:
        import pymysql

        pymysql.install_as_MySQLdb()
    except ImportError:
        pass
    DATABASES["sistema"] = {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("SISPE_DB_NAME", "sistema"),
        "USER": os.environ.get("SISPE_DB_USER", "root"),
        "PASSWORD": os.environ.get("SISPE_DB_PASS", ""),
        "HOST": os.environ.get("SISPE_DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("SISPE_DB_PORT", "3306"),
        "OPTIONS": {"charset": "utf8mb4", "init_command": "SET sql_mode='STRICT_TRANS_TABLES'"},
    }

DATABASE_ROUTERS = ["config.routers.SispeRouter"]

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = False

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/portal/"
LOGOUT_REDIRECT_URL = "/"

SABOR_MONEDA = "$"

# Correo (recuperar contrasena). Sin variables de entorno, los correos se
# imprimen en la consola. Para Gmail:
#   $env:SISPE_EMAIL_USER="cuenta@gmail.com"; $env:SISPE_EMAIL_PASS="clave de aplicacion"
EMAIL_HOST_USER = os.environ.get("SISPE_EMAIL_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("SISPE_EMAIL_PASS", "")
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    DEFAULT_FROM_EMAIL = "sispe@localhost"
