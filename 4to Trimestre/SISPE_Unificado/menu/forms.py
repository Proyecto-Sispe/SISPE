"""Formularios de la CRUD del menú: categorías, productos, adiciones y combos."""

from django import forms

from .models import Adicion, Categoria, Combo, ComboItem, Producto


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nom_categoria", "orden", "activa"]
        widgets = {
            "nom_categoria": forms.TextInput(
                attrs={"class": "campo", "placeholder": "Ej. Hamburguesas"}
            ),
            "orden": forms.NumberInput(attrs={"class": "campo", "min": 0}),
        }
        labels = {
            "nom_categoria": "Nombre de la categoría",
            "orden": "Orden en la carta",
            "activa": "Visible en la carta",
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre",
            "descripcion",
            "categoria",
            "precio",
            "foto",
            "disponible",
            "orden",
        ]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "campo", "placeholder": "Ej. Hamburguesa clásica"}
            ),
            "descripcion": forms.Textarea(
                attrs={"class": "campo", "rows": 3, "placeholder": "Ingredientes, tamaño…"}
            ),
            "categoria": forms.Select(attrs={"class": "campo"}),
            "precio": forms.NumberInput(attrs={"class": "campo", "step": "100", "min": 0}),
            "foto": forms.ClearableFileInput(
                attrs={"class": "campo-archivo", "accept": "image/*"}
            ),
            "orden": forms.NumberInput(attrs={"class": "campo", "min": 0}),
        }
        labels = {
            "nombre": "Nombre del plato",
            "descripcion": "Descripción",
            "categoria": "Categoría",
            "precio": "Precio",
            "foto": "Imagen del producto",
            "disponible": "Disponible para pedir",
            "orden": "Orden dentro de la categoría",
        }

    def clean_precio(self):
        precio = self.cleaned_data.get("precio")
        if precio is None or precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio


class AdicionForm(forms.ModelForm):
    class Meta:
        model = Adicion
        fields = ["nombre", "precio", "categoria", "activa", "orden"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "campo", "placeholder": "Ej. Queso extra"}
            ),
            "precio": forms.NumberInput(attrs={"class": "campo", "step": "100", "min": 0}),
            "categoria": forms.Select(attrs={"class": "campo"}),
            "orden": forms.NumberInput(attrs={"class": "campo", "min": 0}),
        }
        labels = {
            "nombre": "Nombre de la adición",
            "precio": "Precio que se suma",
            "categoria": "Aplica solo a esta categoría",
            "activa": "Disponible en la carta",
            "orden": "Orden",
        }
        help_texts = {
            "categoria": "Déjala vacía para ofrecerla en todos los productos.",
        }

    def clean_precio(self):
        precio = self.cleaned_data.get("precio")
        if precio is None or precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio


class ComboForm(forms.ModelForm):
    class Meta:
        model = Combo
        fields = ["nombre", "descripcion", "precio", "foto", "activo", "orden"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "campo", "placeholder": "Ej. Combo familiar"}
            ),
            "descripcion": forms.Textarea(
                attrs={"class": "campo", "rows": 3, "placeholder": "Qué incluye el combo…"}
            ),
            "precio": forms.NumberInput(attrs={"class": "campo", "step": "100", "min": 0}),
            "foto": forms.ClearableFileInput(
                attrs={"class": "campo-archivo", "accept": "image/*"}
            ),
            "orden": forms.NumberInput(attrs={"class": "campo", "min": 0}),
        }
        labels = {
            "nombre": "Nombre del combo",
            "descripcion": "Descripción",
            "precio": "Precio del combo",
            "foto": "Imagen del combo",
            "activo": "Visible en la carta",
            "orden": "Orden",
        }


class ComboItemForm(forms.ModelForm):
    class Meta:
        model = ComboItem
        fields = ["producto", "cantidad"]
        widgets = {
            "producto": forms.Select(attrs={"class": "campo"}),
            "cantidad": forms.NumberInput(attrs={"class": "campo", "min": 1, "max": 20}),
        }
        labels = {"producto": "Producto", "cantidad": "Cantidad"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["producto"].queryset = Producto.objects.filter(
            disponible=True
        ).select_related("categoria")
        self.fields["producto"].label_from_instance = (
            lambda p: f"{p.nombre} · ${p.precio:,.0f}".replace(",", ".")
        )
