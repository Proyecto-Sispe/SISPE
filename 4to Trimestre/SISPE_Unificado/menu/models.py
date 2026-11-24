"""
Modelos del menu: categorias, productos, adiciones y combos.

Las tablas son managed = False porque el sistema nace de un esquema SQL ya
existente (sistema.sql de MariaDB). El script actualizar_bd.py se encarga de
crear las tablas que falten y de agregar las columnas nuevas sin borrar datos.
"""

from django.db import models


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nom_categoria = models.CharField("nombre", max_length=80)
    orden = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "Categoria"
        ordering = ["orden", "nom_categoria"]
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.nom_categoria


class Producto(models.Model):
    id_menu = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True, default="")
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    categoria = models.ForeignKey(
        Categoria,
        db_column="categoria_id",
        on_delete=models.PROTECT,
        related_name="productos",
    )
    disponible = models.BooleanField(default=True)
    foto = models.ImageField(upload_to="productos/", blank=True, null=True)
    orden = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = "Menu"
        ordering = ["categoria__orden", "categoria_id", "orden", "nombre"]
        verbose_name = "producto"
        verbose_name_plural = "productos"

    def __str__(self):
        return self.nombre

    @property
    def inicial(self):
        return (self.nombre or "?")[:1].upper()

    @property
    def tiene_foto(self):
        return bool(self.foto and getattr(self.foto, "name", ""))


class Adicion(models.Model):
    """Un extra que el cliente puede sumar a un plato (queso, tocineta...)."""

    id_adicion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    categoria = models.ForeignKey(
        Categoria,
        db_column="categoria_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="adiciones",
        help_text="Déjalo vacío para que la adición aplique a todos los productos.",
    )
    activa = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = "Adicion"
        ordering = ["orden", "nombre"]
        verbose_name = "adición"
        verbose_name_plural = "adiciones"

    def __str__(self):
        return f"{self.nombre} (+{self.precio})"


class Combo(models.Model):
    id_combo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True, default="")
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    foto = models.ImageField(upload_to="combos/", blank=True, null=True)
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = "Combo"
        ordering = ["orden", "nombre"]
        verbose_name = "combo"
        verbose_name_plural = "combos"

    def __str__(self):
        return self.nombre

    @property
    def inicial(self):
        return (self.nombre or "?")[:1].upper()

    @property
    def tiene_foto(self):
        return bool(self.foto and getattr(self.foto, "name", ""))

    @property
    def precio_suelto(self):
        total = sum(
            (item.producto.precio or 0) * item.cantidad
            for item in self.items.all()
            if item.producto_id
        )
        return total

    @property
    def ahorro(self):
        diferencia = self.precio_suelto - (self.precio or 0)
        return diferencia if diferencia > 0 else 0

    @property
    def resumen(self):
        partes = []
        for item in self.items.all():
            if item.producto_id:
                etiqueta = item.producto.nombre
                if item.cantidad > 1:
                    etiqueta = f"{item.cantidad}× {etiqueta}"
                partes.append(etiqueta)
        return partes


class ComboItem(models.Model):
    """Cada parte del combo. Se edita libremente desde el admin."""

    id_item = models.AutoField(primary_key=True)
    combo = models.ForeignKey(
        Combo, db_column="combo_id", on_delete=models.CASCADE, related_name="items"
    )
    producto = models.ForeignKey(
        Producto, db_column="producto_id", on_delete=models.PROTECT
    )
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        managed = False
        db_table = "Combo_Item"
        ordering = ["id_item"]
        verbose_name = "parte del combo"
        verbose_name_plural = "partes del combo"

    def __str__(self):
        return f"{self.cantidad}× {self.producto}"

    @property
    def subtotal(self):
        return (self.producto.precio or 0) * self.cantidad
