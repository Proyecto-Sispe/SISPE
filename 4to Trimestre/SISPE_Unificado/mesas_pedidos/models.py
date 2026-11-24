from django.db import models

from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone

try:
    import qrcode
except ImportError:  # Permite importar el módulo aunque qrcode aún no esté instalado
    qrcode = None


class Rol(models.Model):
    nombre = models.CharField(max_length=45, unique=True)

    class Meta:
        db_table = "rol"
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.nombre


class TipoDoc(models.Model):
    tipo_doc = models.CharField(max_length=45)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = "tipo_doc"
        verbose_name = "Tipo de documento"
        verbose_name_plural = "Tipos de documento"

    def __str__(self):
        return self.tipo_doc


class Persona(models.Model):
    id_usuario = models.IntegerField()
    tipo_doc = models.ForeignKey(
        TipoDoc,
        on_delete=models.PROTECT,
        related_name="personas",
    )
    nom1_usu = models.CharField(max_length=20)
    nom2_usu = models.CharField(max_length=20, blank=True, null=True)
    ape1_usu = models.CharField(max_length=20)
    ape2_usu = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.BigIntegerField()
    correo_usu = models.EmailField(max_length=45, unique=True, blank=True, null=True)
    password = models.CharField(max_length=255)
    estado = models.BooleanField(default=True)
    roles = models.ManyToManyField(
        Rol,
        through="PersonaRol",
        related_name="personas",
        blank=True,
    )

    class Meta:
        db_table = "persona"
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        constraints = [
            models.UniqueConstraint(
                fields=["id_usuario", "tipo_doc"],
                name="uq_persona_id_usuario_tipo_doc",
            )
        ]

    def __str__(self):
        nombres = " ".join(filter(None, [self.nom1_usu, self.nom2_usu]))
        apellidos = " ".join(filter(None, [self.ape1_usu, self.ape2_usu]))
        return f"{nombres} {apellidos}".strip()


class PersonaRol(models.Model):
    persona = models.ForeignKey(
        Persona,
        on_delete=models.CASCADE,
        related_name="asignaciones_rol",
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        related_name="asignaciones_persona",
    )

    class Meta:
        db_table = "persona_has_rol"
        verbose_name = "Asignación de rol"
        verbose_name_plural = "Asignaciones de roles"
        constraints = [
            models.UniqueConstraint(
                fields=["persona", "rol"],
                name="uq_persona_rol",
            )
        ]

    def __str__(self):
        return f"{self.persona} - {self.rol}"


class PasswordReset(models.Model):
    correo = models.EmailField(max_length=120, db_index=True)
    token = models.CharField(max_length=64, db_index=True)
    codigo = models.CharField(max_length=6)
    expira = models.DateTimeField()
    usado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "password_resets"
        verbose_name = "Restablecimiento de contraseña"
        verbose_name_plural = "Restablecimientos de contraseña"

    def __str__(self):
        return f"{self.correo} ({self.codigo})"


class Mesa(models.Model):
    class EstadoMesa(models.IntegerChoices):
        LIBRE = 0, "Libre"
        OCUPADA = 1, "Ocupada"

    capacidad = models.PositiveIntegerField()
    ubicacion = models.CharField(max_length=50)
    estado = models.IntegerField(
        choices=EstadoMesa.choices,
        default=EstadoMesa.LIBRE,
    )
    qr_imagen = models.ImageField(upload_to="qrs/", blank=True, null=True)

    class Meta:
        db_table = "mesa"
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"

    def __str__(self):
        return f"Mesa {self.pk} - {self.ubicacion} ({self.get_estado_display()})"

    def generar_qr_contenido(self):
        return f"mesa:{self.pk}"

    def save(self, *args, **kwargs):
        skip_qr = kwargs.pop("_skip_qr", False)
        super().save(*args, **kwargs)

        # Genera o actualiza el PNG del QR automáticamente al crear o editar la mesa
        if qrcode is not None and not skip_qr:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=8,
                border=4,
            )
            qr.add_data(self.generar_qr_contenido())
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            filename = f"mesa_{self.pk}.png"
            self.qr_imagen.save(filename, ContentFile(buffer.read()), save=False)
            super().save(update_fields=["qr_imagen"])


class Categoria(models.Model):
    nom_categoria = models.CharField(max_length=100)

    class Meta:
        db_table = "categoria"
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nom_categoria


class Insumo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    stock_actual = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    unidad = models.CharField(max_length=20)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "insumo"
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"

    def __str__(self):
        return f"{self.nombre} ({self.stock_actual} {self.unidad})"


class Menu(models.Model):
    productos = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="productos",
    )
    foto = models.ImageField(upload_to="menu/", blank=True, null=True)
    insumos = models.ManyToManyField(
        Insumo,
        through="MenuInsumo",
        related_name="menus",
        blank=True,
    )

    class Meta:
        db_table = "menu"
        verbose_name = "Producto del menú"
        verbose_name_plural = "Productos del menú"

    def __str__(self):
        return f"{self.productos} (${self.precio})"


class MenuInsumo(models.Model):
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name="receta_insumos",
    )
    insumo = models.ForeignKey(
        Insumo,
        on_delete=models.PROTECT,
        related_name="recetas_menu",
    )
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        db_table = "menu_insumo"
        verbose_name = "Insumo por producto"
        verbose_name_plural = "Insumos por producto"
        constraints = [
            models.UniqueConstraint(
                fields=["menu", "insumo"],
                name="uq_menu_insumo",
            )
        ]

    def __str__(self):
        return f"{self.menu.productos} -> {self.insumo.nombre} ({self.cantidad})"


class Adicion(models.Model):
    nombre = models.CharField(max_length=80)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = "adicion"
        verbose_name = "Adición"
        verbose_name_plural = "Adiciones"

    def __str__(self):
        return f"{self.nombre} (+${self.precio})"


class SesionMesa(models.Model):
    mesa = models.ForeignKey(
        Mesa,
        on_delete=models.PROTECT,
        related_name="sesiones",
    )
    codigo_acceso = models.CharField(max_length=6)
    nombre_cliente = models.CharField(max_length=100)
    cedula_cliente = models.IntegerField()
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = "sesion_mesa"
        verbose_name = "Sesión de mesa"
        verbose_name_plural = "Sesiones de mesa"

    def __str__(self):
        return f"Sesión #{self.pk} - Mesa {self.mesa_id} ({self.nombre_cliente})"


class Pedido(models.Model):
    class EstadoPedido(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_PREPARACION = "en_preparacion", "En preparación"
        EN_CAMINO = "en_camino", "En camino"
        ENTREGADO = "entregado", "Entregado"

    class PrioridadPedido(models.TextChoices):
        NORMAL = "normal", "Normal"
        URGENTE = "urgente", "Urgente"

    mesa = models.ForeignKey(
        Mesa,
        on_delete=models.PROTECT,
        related_name="pedidos",
    )
    mesero = models.ForeignKey(
        Persona,
        on_delete=models.SET_NULL,
        related_name="pedidos_atendidos",
        blank=True,
        null=True,
    )
    cliente = models.ForeignKey(
        Persona,
        on_delete=models.SET_NULL,
        related_name="pedidos_realizados",
        blank=True,
        null=True,
    )
    sesion_qr = models.ForeignKey(
        SesionMesa,
        on_delete=models.SET_NULL,
        related_name="pedidos",
        blank=True,
        null=True,
    )
    cocinero_asignado = models.ForeignKey(
        Persona,
        on_delete=models.SET_NULL,
        related_name="pedidos_cocina",
        blank=True,
        null=True,
    )
    fecha_pedido = models.DateTimeField(default=timezone.now)
    estado = models.CharField(
        max_length=20,
        choices=EstadoPedido.choices,
        default=EstadoPedido.PENDIENTE,
    )
    prioridad = models.CharField(
        max_length=10,
        choices=PrioridadPedido.choices,
        default=PrioridadPedido.NORMAL,
    )
    tiempo_estimado = models.IntegerField(default=15)
    observaciones = models.TextField(blank=True, null=True)
    confirmado = models.BooleanField(default=False)

    class Meta:
        db_table = "pedido"
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido #{self.pk} - Mesa {self.mesa_id} ({self.get_estado_display()})"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.PROTECT,
        related_name="detalles_pedido",
    )
    cantidad = models.IntegerField()
    valor_venta = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.TextField(blank=True, null=True)
    adiciones = models.ManyToManyField(
        Adicion,
        through="DetallePedidoAdicion",
        related_name="detalles_pedido",
        blank=True,
    )

    class Meta:
        db_table = "detalle_pedido"
        verbose_name = "Detalle de pedido"
        verbose_name_plural = "Detalles de pedido"

    def __str__(self):
        return f"{self.cantidad}x {self.menu.productos} (Pedido #{self.pedido_id})"


class DetallePedidoAdicion(models.Model):
    detalle = models.ForeignKey(
        DetallePedido,
        on_delete=models.CASCADE,
        related_name="adiciones_detalle",
    )
    adicion = models.ForeignKey(
        Adicion,
        on_delete=models.PROTECT,
        related_name="en_detalles",
    )
    cantidad = models.IntegerField(default=1)

    class Meta:
        db_table = "detalle_pedido_adicion"
        verbose_name = "Adición en detalle de pedido"
        verbose_name_plural = "Adiciones en detalles de pedido"

    def __str__(self):
        return f"{self.cantidad}x {self.adicion.nombre}"


class MetodoPago(models.Model):
    tipo_pago = models.CharField(max_length=45, unique=True)

    class Meta:
        db_table = "metodo_pago"
        verbose_name = "Método de pago"
        verbose_name_plural = "Métodos de pago"

    def __str__(self):
        return self.tipo_pago


class Factura(models.Model):
    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.CASCADE,
        related_name="factura",
    )
    fecha_hora = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    metodos_pago = models.ManyToManyField(
        MetodoPago,
        through="FacturaMetodoPago",
        related_name="facturas",
        blank=True,
    )

    class Meta:
        db_table = "factura"
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"

    def __str__(self):
        return f"Factura #{self.pk} - Pedido #{self.pedido_id}"

    def calcular_total(self):
        subtotal_items = (
            self.pedido.detalles.aggregate(
                total=Sum(F("valor_venta") * F("cantidad"))
            )["total"]
            or 0
        )
        subtotal_adiciones = (
            DetallePedidoAdicion.objects.filter(detalle__pedido=self.pedido).aggregate(
                total=Sum(F("adicion__precio") * F("cantidad"))
            )["total"]
            or 0
        )
        return subtotal_items + subtotal_adiciones


class FacturaMetodoPago(models.Model):
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name="pagos",
    )
    metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        related_name="pagos_factura",
    )
    monto = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "factura_has_metodo_pago"
        verbose_name = "Pago de factura"
        verbose_name_plural = "Pagos de factura"
        constraints = [
            models.UniqueConstraint(
                fields=["factura", "metodo_pago"],
                name="uq_factura_metodo_pago",
            )
        ]

    def __str__(self):
        return f"Factura #{self.factura_id} - {self.metodo_pago.tipo_pago}: ${self.monto}"


class Notificacion(models.Model):
    class TipoNotificacion(models.TextChoices):
        PEDIDO_LISTO = "pedido_listo", "Pedido listo"
        NUEVO_PEDIDO = "nuevo_pedido", "Nuevo pedido"
        PEDIDO_URGENTE = "pedido_urgente", "Pedido urgente"

    tipo = models.CharField(
        max_length=20,
        choices=TipoNotificacion.choices,
    )
    mensaje = models.TextField()
    mesa = models.ForeignKey(
        Mesa,
        on_delete=models.SET_NULL,
        related_name="notificaciones",
        blank=True,
        null=True,
    )
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.SET_NULL,
        related_name="notificaciones",
        blank=True,
        null=True,
    )
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    destinatario_rol = models.ForeignKey(
        Rol,
        on_delete=models.SET_NULL,
        related_name="notificaciones",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "notificaciones"
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.mensaje[:40]}"
