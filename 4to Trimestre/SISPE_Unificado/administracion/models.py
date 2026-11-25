"""Inventario y facturación. Viven en la base default, junto a la carta y los pedidos."""

from decimal import Decimal

from django.db import models
from django.utils import timezone

from menu.models import Producto
from pedidos.models import Pedido


class LoginThrottle(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    window_started = models.DateTimeField()
    blocked_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "sispe_login_throttle"
        indexes = [
            models.Index(fields=["window_started"], name="login_window_idx"),
        ]


class Insumo(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    unidad = models.CharField(max_length=20, default="Unidades")
    stock_actual = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "insumo"
        verbose_name_plural = "insumos"

    def __str__(self):
        return f"{self.nombre} ({self.unidad})"

    @property
    def estado_stock(self):
        if self.stock_actual <= 0:
            return "agotado"
        if self.stock_actual <= self.stock_minimo:
            return "bajo"
        return "ok"


class ProductoInsumo(models.Model):
    """Receta: cuánto de cada insumo gasta una unidad del producto."""

    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, db_constraint=False, related_name="receta"
    )
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name="recetas")
    cantidad = models.DecimalField(max_digits=10, decimal_places=3, default=1)

    class Meta:
        unique_together = [("producto", "insumo")]
        ordering = ["insumo__nombre"]
        verbose_name = "insumo del producto"
        verbose_name_plural = "insumos por producto"

    def __str__(self):
        return f"{self.producto} → {self.cantidad} {self.insumo}"


class MovimientoInventario(models.Model):
    TIPOS = [
        ("entrada", "Entrada manual"),
        ("salida", "Salida manual"),
        ("pedido", "Consumo por pedido"),
        ("devolucion", "Devolución por cancelación"),
    ]

    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name="movimientos")
    tipo = models.CharField(max_length=12, choices=TIPOS)
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)
    pedido_id = models.IntegerField(null=True, blank=True, db_index=True)
    motivo = models.CharField(max_length=200, blank=True, default="")
    usuario = models.CharField(max_length=150, blank=True, default="")
    fecha = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-fecha", "-id"]
        verbose_name = "movimiento de inventario"
        verbose_name_plural = "movimientos de inventario"


class Factura(models.Model):
    ESTADOS = [("emitida", "Emitida"), ("pagada", "Pagada"), ("anulada", "Anulada")]

    pedido = models.OneToOneField(
        Pedido, on_delete=models.DO_NOTHING, db_constraint=False, related_name="factura"
    )
    fecha = models.DateTimeField(default=timezone.now, db_index=True)
    mesa = models.IntegerField(default=0, db_index=True)
    cliente_nombre = models.CharField(max_length=100, blank=True, default="")
    cliente_documento = models.CharField(max_length=20, blank=True, default="")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    impuesto = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    propina = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    estado = models.CharField(max_length=10, choices=ESTADOS, default="emitida")
    metodo_pago = models.CharField(max_length=50, blank=True, default="")
    transaccion_id = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        ordering = ["-fecha", "-id"]
        verbose_name = "factura"
        verbose_name_plural = "facturas"

    def __str__(self):
        return self.numero

    @property
    def numero(self):
        return f"F-{self.pk:06d}" if self.pk else "F-nueva"
