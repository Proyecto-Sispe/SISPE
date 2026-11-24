# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Adicion(models.Model):
    id_adicion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'adicion'


class Categoria(models.Model):
    id_categoria = models.IntegerField(primary_key=True)
    nom_categoria = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'categoria'


class DetallePedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey('Pedido', models.CASCADE, db_column='id_pedido')
    id_menu = models.ForeignKey('Menu', models.DO_NOTHING, db_column='id_menu')
    cantidad = models.IntegerField()
    valor_venta = models.FloatField()
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'detalle_pedido'


class DetallePedidoAdicion(models.Model):
    id_detalle = models.ForeignKey(DetallePedido, models.CASCADE, db_column='id_detalle')
    id_adicion = models.ForeignKey(Adicion, models.DO_NOTHING, db_column='id_adicion')
    cantidad = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'detalle_pedido_adicion'


class Factura(models.Model):
    id_factura = models.AutoField(primary_key=True)
    id_pedido = models.OneToOneField('Pedido', models.CASCADE, db_column='id_pedido')
    fecha_hora = models.DateTimeField(db_column='Fecha_hora', blank=True, null=True)  # Field name made lowercase.
    total = models.FloatField(db_column='Total')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'factura'


class FacturaHasMetodoPago(models.Model):
    pk = models.CompositePrimaryKey('pkfk_n_factura', 'pkfk_metodo_pago')
    pkfk_n_factura = models.ForeignKey(Factura, models.DO_NOTHING, db_column='pkfk_n_factura')
    pkfk_metodo_pago = models.ForeignKey('MetodoPago', models.DO_NOTHING, db_column='pkfk_metodo_pago')
    monto = models.FloatField()

    class Meta:
        managed = False
        db_table = 'factura_has_metodo_pago'


class Insumo(models.Model):
    id_insumo = models.BigAutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=100)
    stock_actual = models.DecimalField(max_digits=12, decimal_places=3)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=3)
    unidad = models.CharField(max_length=20)
    activo = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'insumo'


class Menu(models.Model):
    id_menu = models.IntegerField(primary_key=True)
    productos = models.CharField(db_column='Productos', max_length=100)  # Field name made lowercase.
    precio = models.FloatField(db_column='Precio')  # Field name made lowercase.
    descripcion = models.TextField()
    pkfk_id_categoria = models.ForeignKey(Categoria, models.DO_NOTHING, db_column='pkfk_id_categoria')
    foto = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'menu'


class MenuInsumo(models.Model):
    id_menu_insumo = models.BigAutoField(primary_key=True)
    id_menu = models.ForeignKey(Menu, models.DO_NOTHING, db_column='id_menu')
    id_insumo = models.ForeignKey(Insumo, models.DO_NOTHING, db_column='id_insumo')
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        managed = False
        db_table = 'menu_insumo'
        unique_together = (('id_menu', 'id_insumo'),)


class Mesa(models.Model):
    id_mesa = models.IntegerField(db_column='id_Mesa', primary_key=True)  # Field name made lowercase.
    capacidad = models.IntegerField(db_column='Capacidad')  # Field name made lowercase.
    ubicacion = models.CharField(db_column='Ubicacion', max_length=50)  # Field name made lowercase.
    estado = models.IntegerField(db_column='Estado')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'mesa'


class MetodoPago(models.Model):
    id_pago = models.IntegerField(primary_key=True)
    tipo_pago = models.CharField(db_column='Tipo_pago', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'metodo_pago'


class Notificaciones(models.Model):
    id_notificacion = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=14)
    mensaje = models.TextField()
    id_mesa = models.ForeignKey(Mesa, models.DO_NOTHING, db_column='id_mesa', blank=True, null=True)
    id_pedido = models.ForeignKey('Pedido', models.DO_NOTHING, db_column='id_pedido', blank=True, null=True)
    leida = models.IntegerField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    destinatario_rol = models.ForeignKey('Rol', models.DO_NOTHING, db_column='destinatario_rol', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notificaciones'


class PasswordResets(models.Model):
    correo = models.CharField(max_length=120)
    token = models.CharField(max_length=64)
    codigo = models.CharField(max_length=6)
    expira = models.DateTimeField()
    usado = models.IntegerField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'password_resets'


class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    id_mesa = models.ForeignKey(Mesa, models.DO_NOTHING, db_column='id_mesa')
    mesero_tipo_doc = models.IntegerField(blank=True, null=True)
    mesero_id_usuario = models.IntegerField(blank=True, null=True)
    cliente_tipo_doc = models.IntegerField(blank=True, null=True)
    cliente_id_usuario = models.IntegerField(blank=True, null=True)
    id_sesion_qr = models.ForeignKey('SesionMesa', models.DO_NOTHING, db_column='id_sesion_qr', blank=True, null=True)
    fecha_pedido = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=14, blank=True, null=True)
    prioridad = models.CharField(max_length=7, blank=True, null=True)
    cocinero_asignado = models.IntegerField(blank=True, null=True)
    tiempo_estimado = models.IntegerField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    confirmado = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'pedido'


class Persona(models.Model):
  pk = models.CompositePrimaryKey("id_usuario", "pkfk_tipo_doc")
  id_usuario = models.IntegerField()
  pkfk_tipo_doc = models.ForeignKey(
      "TipoDoc", models.DO_NOTHING, db_column="pkfk_Tipo_doc"
  )
  nom1_usu = models.CharField(db_column="Nom1_usu", max_length=20)
  nom2_usu = models.CharField(
      db_column="Nom2_usu", max_length=20, blank=True, null=True
  )
  ape1_usu = models.CharField(db_column="Ape1_usu", max_length=20)
  ape2_usu = models.CharField(
      db_column="Ape2_usu", max_length=20, blank=True, null=True
  )
  telefono = models.BigIntegerField(db_column="Telefono")
  correo_usu = models.CharField(
      db_column="Correo_usu", unique=True, max_length=45, blank=True, null=True
  )
  password = models.CharField(db_column="Password", max_length=255)
  estado = models.IntegerField(blank=True, null=True)

  class Meta:
    managed = False
    db_table = "persona"


class PersonaHasRol(models.Model):
  pk = models.CompositePrimaryKey(
      "pkfk_id_usuario", "pkfk_tipo_doc", "pkfk_idrol"
  )
  persona = models.ForeignObject(
      Persona,
      models.DO_NOTHING,
      from_fields=("pkfk_id_usuario", "pkfk_tipo_doc"),
      to_fields=("id_usuario", "pkfk_tipo_doc"),
  )
  pkfk_id_usuario = models.IntegerField(db_column="pkfk_id_usuario")
  pkfk_tipo_doc = models.IntegerField(db_column="pkfk_Tipo_doc")
  pkfk_idrol = models.ForeignKey("Rol", models.DO_NOTHING, db_column="pkfk_idRol")

  class Meta:
    managed = False
    db_table = "persona_has_rol"


class Rol(models.Model):
    idrol = models.IntegerField(db_column='idRol', primary_key=True)  # Field name made lowercase.
    nom_rol = models.CharField(db_column='Nom_rol', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rol'


class SesionMesa(models.Model):
    id_sesion = models.AutoField(primary_key=True)
    id_mesa = models.ForeignKey(Mesa, models.DO_NOTHING, db_column='id_mesa')
    codigo_acceso = models.CharField(max_length=6)
    nombre_cliente = models.CharField(max_length=100)
    cedula_cliente = models.IntegerField()
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    activa = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sesion_mesa'


class TipoDoc(models.Model):
    id_doc = models.IntegerField(primary_key=True)
    tipo_doc = models.CharField(max_length=45)
    estado = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tipo_doc'

