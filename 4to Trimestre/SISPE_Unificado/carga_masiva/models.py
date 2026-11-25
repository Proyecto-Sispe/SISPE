from django.db import models
from django.conf import settings


class HistorialCarga(models.Model):

    TIPOS = [
        ("categorias", "Categorías"),
        ("productos", "Productos"),
        ("insumos", "Insumos"),
    ]

    ESTADOS = [
        ("exitosa", "Exitosa"),
        ("fallida", "Fallida"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    tipo = models.CharField(
        max_length=30,
        choices=TIPOS
    )

    archivo_nombre = models.CharField(max_length=255)

    total_registros = models.PositiveIntegerField(default=0)

    registros_exitosos = models.PositiveIntegerField(default=0)

    registros_error = models.PositiveIntegerField(default=0)

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS
    )

    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.tipo} - {self.fecha}"