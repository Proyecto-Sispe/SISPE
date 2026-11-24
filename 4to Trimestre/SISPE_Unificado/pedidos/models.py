"""Modelos de pedidos: comanda, lineas de detalle y adiciones por linea."""

from django.db import models
from django.utils import timezone

from menu.models import Adicion, Combo, Producto


class Pedido(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("en_preparacion", "En preparación"),
        ("listo", "Listo"),
        ("entregado", "Entregado"),
        ("cancelado", "Cancelado"),
    ]

    SIGUIENTE = {
        "pendiente": "en_preparacion",
        "en_preparacion": "listo",
        "listo": "entregado",
    }

    PRIORIDADES = [(1, "Normal"), (2, "Alta"), (3, "Urgente")]

    id_pedido = models.AutoField(primary_key=True)
    id_mesa = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    prioridad = models.IntegerField(choices=PRIORIDADES, default=1)
    fecha_pedido = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True, default="")

    class Meta:
        managed = False
        db_table = "Pedido"
        ordering = ["-fecha_pedido"]
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"

    def __str__(self):
        return f"Pedido #{self.id_pedido} · mesa {self.id_mesa}"

    # -- ayudas para la pantalla de cocina ---------------------------------
    @property
    def minutos_espera(self):
        if not self.fecha_pedido:
            return 0
        ahora = timezone.now()
        referencia = self.fecha_pedido
        if timezone.is_aware(referencia) and timezone.is_naive(ahora):
            referencia = timezone.make_naive(referencia, timezone.get_current_timezone())
        delta = ahora - referencia
        return max(int(delta.total_seconds() // 60), 0)

    @property
    def avance(self):
        return {
            "pendiente": 15,
            "en_preparacion": 55,
            "listo": 90,
            "entregado": 100,
            "cancelado": 100,
        }.get(self.estado, 0)

    @property
    def siguiente_estado(self):
        return self.SIGUIENTE.get(self.estado)

    @property
    def siguiente_etiqueta(self):
        return {
            "en_preparacion": "Empezar preparación",
            "listo": "Marcar listo",
            "entregado": "Entregado",
        }.get(self.siguiente_estado, "")

    @property
    def activo(self):
        return self.estado in ("pendiente", "en_preparacion", "listo")

    @property
    def total_unidades(self):
        return sum(d.cantidad for d in self.detalles.all())


class DetallePedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(
        Pedido, db_column="pedido_id", on_delete=models.CASCADE, related_name="detalles"
    )
    producto = models.ForeignKey(
        Producto,
        db_column="producto_id",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="detalles",
    )
    combo = models.ForeignKey(
        Combo,
        db_column="combo_id",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="detalles",
    )
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_venta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notas = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        managed = False
        db_table = "Detalle_Pedido"
        ordering = ["id_detalle"]
        verbose_name = "detalle de pedido"
        verbose_name_plural = "detalles de pedido"

    def __str__(self):
        return f"{self.cantidad}× {self.descripcion}"

    @property
    def descripcion(self):
        if self.combo_id:
            return self.combo.nombre
        if self.producto_id:
            return self.producto.nombre
        return "Ítem"

    @property
    def es_combo(self):
        return bool(self.combo_id)


class DetalleAdicion(models.Model):
    id_detalle_adicion = models.AutoField(primary_key=True)
    detalle = models.ForeignKey(
        DetallePedido,
        db_column="detalle_id",
        on_delete=models.CASCADE,
        related_name="adiciones",
    )
    adicion = models.ForeignKey(
        Adicion, db_column="adicion_id", on_delete=models.PROTECT
    )
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        managed = False
        db_table = "Detalle_Adicion"
        ordering = ["id_detalle_adicion"]
        verbose_name = "adición del pedido"
        verbose_name_plural = "adiciones del pedido"

    def __str__(self):
        return f"{self.adicion.nombre} (+{self.precio})"
