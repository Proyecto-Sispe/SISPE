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

from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("SISPE_DEBUG", "0") == "1"
SECRET_KEY = os.environ.get("SISPE_SECRET")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = get_random_secret_key()
    else:
        raise ImproperlyConfigured("Set SISPE_SECRET before running with DEBUG disabled.")
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "SISPE_ALLOWED_HOSTS", "127.0.0.1,localhost,testserver"
    ).split(",")
    if host.strip()
]

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
    # Modulo de carga masiva de datos
    "carga_masiva",
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

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

PASSWORD_RESET_TIMEOUT = 60 * 15
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

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
EMAIL_HOST_USER = os.environ.get("SISPE_EMAIL_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("SISPE_EMAIL_PASS", "")
DEFAULT_FROM_EMAIL = os.environ.get(
    "SISPE_EMAIL_FROM", EMAIL_HOST_USER or "no-reply@localhost"
)
EMAIL_BACKEND = os.environ.get(
    "SISPE_EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend",
)
