"""
Configuracion unificada de SISPE.

Une los módulos funcionales de SISPE en un solo servidor Django:
  - menu, pedidos y cocina       (carta, carrito y preparación)
  - mesas_pedidos                (mesas, QR y pedidos en sala)
  - seguimiento_pedidos          (acceso por rol y recuperación de cuenta)
  - base_datos y dashboard       (datos SISPE; estadísticas en reportes)

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
    # Carta, pedidos y cocina
    "menu",
    "pedidos",
    "cocina",
    # Mesas y pedidos en sala
    "mesas_pedidos",
    # Acceso y roles
    "seguimiento_pedidos",
    # Datos del sistema y compatibilidad de rutas
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

# default -> usuarios de Django, sesiones, administración y carta
# mesas   -> mesas, QR y pedidos por mesa
# sistema -> personas, roles, insumos y datos del esquema SISPE
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

# settings.py

# --------------------------------------------------------------------
# EMAIL (Recuperación de contraseña)
# --------------------------------------------------------------------
# Configura aquí tu cuenta SMTP. Para Gmail debes generar una
# "Contraseña de aplicación" (https://myaccount.google.com/apppasswords)
# y usarla en EMAIL_HOST_PASSWORD (NO tu contraseña normal).

EMAIL_HOST = os.environ.get("SISPE_EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("SISPE_EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("SISPE_EMAIL_USE_TLS", "1") == "1"
EMAIL_HOST_USER = os.environ.get("SISPE_EMAIL_USER", "proyecto.sispe@gmail.com")
EMAIL_HOST_PASSWORD = os.environ.get("SISPE_EMAIL_PASS", "jeyo jvgk nmin nlps")
DEFAULT_FROM_EMAIL = os.environ.get(
    "SISPE_EMAIL_FROM", EMAIL_HOST_USER or "proyecto.sispe@gmail.com"
)
EMAIL_BACKEND = os.environ.get(
    "SISPE_EMAIL_BACKEND",
    (
        "django.core.mail.backends.console.EmailBackend"
        if DEBUG and not EMAIL_HOST_USER
        else "django.core.mail.backends.smtp.EmailBackend"
    ),
)
