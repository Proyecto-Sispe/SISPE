from django import forms
from .models import Mesa


class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ["capacidad", "ubicacion", "estado"]
        widgets = {
            "capacidad": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "ubicacion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Primer Piso, Terraza"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }


class IngresoClienteMesaForm(forms.Form):
    nombre_cliente = forms.CharField(
        max_length=100,
        label="Tu nombre",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Camilo Rojas"}),
    )
    cedula_cliente = forms.CharField(
        max_length=20,
        label="Número de documento",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 1031422939"}),
    )
    def clean_cedula_cliente(self):
        documento = self.cleaned_data["cedula_cliente"].strip().replace(".", "")
        if not documento.isdigit() or not 5 <= len(documento) <= 12:
            raise forms.ValidationError("Escribe solo números (entre 5 y 12 dígitos).")
        return documento
