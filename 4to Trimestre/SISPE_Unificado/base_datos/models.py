from django.db import models


# Modelos de las 19 tablas existentes en db.sqlite3.
# managed = False evita que Django intente crear o eliminar estas tablas.
# Los nombres de tablas y columnas conservan los de la base de datos original.


class Adicion(models.Model):
    id_adicion = models.AutoField(primary_key=True)
    nombre = models.TextField()
    precio = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = "Adicion"


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nom_categoria = models.TextField()

    class Meta:
        managed = False
        db_table = "Categoria"


class DetallePedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey("Pedido", models.DO_NOTHING, db_column="id_pedido")
    id_menu = models.ForeignKey("Menu", models.DO_NOTHING, db_column="id_menu")
    cantidad = models.IntegerField()
    valor_venta = models.FloatField()
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Detalle_Pedido"


class DetallePedidoAdicion(models.Model):
    id = models.AutoField(primary_key=True)
    id_detalle = models.ForeignKey(
        DetallePedido, models.DO_NOTHING, db_column="id_detalle"
    )
    id_adicion = models.ForeignKey(
        Adicion, models.DO_NOTHING, db_column="id_adicion"
    )
    cantidad = models.IntegerField()

    class Meta:
        managed = False
        db_table = "Detalle_Pedido_Adicion"


class Factura(models.Model):
    id_factura = models.AutoField(primary_key=True)
    id_pedido = models.OneToOneField(
        "Pedido", models.DO_NOTHING, db_column="id_pedido"
    )
    fecha_hora = models.TextField(db_column="Fecha_hora", blank=True, null=True)
    total = models.FloatField(db_column="Total")

    class Meta:
        managed = False
        db_table = "Factura"


class FacturaHasMetodoPago(models.Model):
    pk = models.CompositePrimaryKey("pkfk_n_factura", "pkfk_metodo_pago")
    # Se conservan como enteros porque forman una clave primaria compuesta.
    pkfk_n_factura = models.IntegerField()
    pkfk_metodo_pago = models.IntegerField()
    monto = models.FloatField()

    class Meta:
        managed = False
        db_table = "Factura_has_Metodo_pago"


class Insumo(models.Model):
    id_insumo = models.AutoField(primary_key=True)
    nombre = models.TextField()
    stock_actual = models.DecimalField(max_digits=12, decimal_places=3)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=3)
    unidad = models.TextField()
    activo = models.IntegerField()

    class Meta:
        managed = False
        db_table = "Insumo"


class Menu(models.Model):
    id_menu = models.AutoField(primary_key=True)
    productos = models.TextField(db_column="Productos")
    precio = models.FloatField(db_column="Precio")
    descripcion = models.TextField()
    pkfk_id_categoria = models.ForeignKey(
        Categoria, models.DO_NOTHING, db_column="pkfk_id_categoria"
    )
    foto = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Menu"


class MenuInsumo(models.Model):
    id_menu_insumo = models.AutoField(primary_key=True)
    id_menu = models.ForeignKey(Menu, models.DO_NOTHING, db_column="id_menu")
    id_insumo = models.ForeignKey(Insumo, models.DO_NOTHING, db_column="id_insumo")
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        managed = False
        db_table = "Menu_Insumo"


class Mesa(models.Model):
    id_mesa = models.AutoField(db_column="id_Mesa", primary_key=True)
    capacidad = models.IntegerField(db_column="Capacidad")
    ubicacion = models.TextField(db_column="Ubicacion")
    estado = models.IntegerField(db_column="Estado")

    class Meta:
        managed = False
        db_table = "Mesa"


class MetodoPago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    tipo_pago = models.TextField(db_column="Tipo_pago")

    class Meta:
        managed = False
        db_table = "Metodo_pago"


class Notificaciones(models.Model):
    id_notificacion = models.AutoField(primary_key=True)
    tipo = models.TextField()
    mensaje = models.TextField()
    id_mesa = models.ForeignKey(
        Mesa, models.DO_NOTHING, db_column="id_mesa", blank=True, null=True
    )
    id_pedido = models.ForeignKey(
        "Pedido", models.DO_NOTHING, db_column="id_pedido", blank=True, null=True
    )
    leida = models.IntegerField(blank=True, null=True)
    fecha_creacion = models.TextField(blank=True, null=True)
    destinatario_rol = models.ForeignKey(
        "Rol", models.DO_NOTHING, db_column="destinatario_rol", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "Notificaciones"


class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    id_mesa = models.ForeignKey(Mesa, models.DO_NOTHING, db_column="id_mesa")
    mesero_tipo_doc = models.IntegerField(blank=True, null=True)
    mesero_id_usuario = models.IntegerField(blank=True, null=True)
    cliente_tipo_doc = models.IntegerField(blank=True, null=True)
    cliente_id_usuario = models.IntegerField(blank=True, null=True)
    id_sesion_qr = models.ForeignKey(
        "SesionMesa", models.DO_NOTHING, db_column="id_sesion_qr", blank=True, null=True
    )
    fecha_pedido = models.TextField(blank=True, null=True)
    estado = models.TextField(blank=True, null=True)
    prioridad = models.TextField(blank=True, null=True)
    cocinero_asignado = models.IntegerField(blank=True, null=True)
    tiempo_estimado = models.IntegerField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    confirmado = models.IntegerField()

    class Meta:
        managed = False
        db_table = "Pedido"


class Persona(models.Model):
    pk = models.CompositePrimaryKey("id_usuario", "pkfk_tipo_doc")
    id_usuario = models.IntegerField()
    # Es parte de la clave primaria compuesta; la FK física permanece en SQLite.
    pkfk_tipo_doc = models.IntegerField(db_column="pkfk_Tipo_doc")
    nom1_usu = models.TextField(db_column="Nom1_usu")
    nom2_usu = models.TextField(db_column="Nom2_usu", blank=True, null=True)
    ape1_usu = models.TextField(db_column="Ape1_usu")
    ape2_usu = models.TextField(db_column="Ape2_usu", blank=True, null=True)
    telefono = models.IntegerField(db_column="Telefono")
    correo_usu = models.TextField(db_column="Correo_usu", blank=True, null=True)
    password = models.TextField(db_column="Password")
    estado = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Persona"


class PersonaHasRol(models.Model):
    # Django no puede representar como ForeignKey normal la FK compuesta
    # hacia Persona; por eso se conservan sus dos columnas como enteros.
    pk = models.CompositePrimaryKey(
        "pkfk_id_usuario", "pkfk_tipo_doc", "pkfk_idrol"
    )
    pkfk_tipo_doc = models.IntegerField(db_column="pkfk_Tipo_doc")
    pkfk_id_usuario = models.IntegerField()
    pkfk_idrol = models.IntegerField(db_column="pkfk_idRol")

    class Meta:
        managed = False
        db_table = "Persona_has_Rol"


class Rol(models.Model):
    idrol = models.AutoField(db_column="idRol", primary_key=True)
    nom_rol = models.TextField(db_column="Nom_rol")

    class Meta:
        managed = False
        db_table = "Rol"


class SesionMesa(models.Model):
    id_sesion = models.AutoField(primary_key=True)
    id_mesa = models.ForeignKey(Mesa, models.DO_NOTHING, db_column="id_mesa")
    codigo_acceso = models.TextField()
    nombre_cliente = models.TextField()
    cedula_cliente = models.IntegerField()
    fecha_inicio = models.TextField(blank=True, null=True)
    fecha_fin = models.TextField(blank=True, null=True)
    activa = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Sesion_Mesa"


class TipoDoc(models.Model):
    id_doc = models.AutoField(primary_key=True)
    tipo_doc = models.TextField()
    estado = models.IntegerField()

    class Meta:
        managed = False
        db_table = "Tipo_doc"


class PasswordResets(models.Model):
    id = models.AutoField(primary_key=True)
    correo = models.TextField()
    token = models.TextField()
    codigo = models.TextField()
    expira = models.TextField()
    usado = models.IntegerField()
    created_at = models.TextField()

    class Meta:
        managed = False
        db_table = "password_resets"
