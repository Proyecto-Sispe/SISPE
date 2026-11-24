from django.apps import AppConfig


class BaseDatosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base_datos'
    verbose_name = "Base de datos SISPE (Juan)"
