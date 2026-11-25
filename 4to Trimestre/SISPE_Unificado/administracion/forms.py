from django import forms
from django.contrib.auth.password_validation import validate_password

from seguimiento_pedidos.models import Rol, TipoDoc

from .models import Insumo, ProductoInsumo


class PersonaForm(forms.Form):
    tipo_doc = forms.ChoiceField(label="Tipo de documento")
    numero = forms.IntegerField(label="Número de documento", min_value=1)
    nom1 = forms.CharField(label="Primer nombre", max_length=20)
    nom2 = forms.CharField(label="Segundo nombre", max_length=20, required=False)
    ape1 = forms.CharField(label="Primer apellido", max_length=20)
    ape2 = forms.CharField(label="Segundo apellido", max_length=20, required=False)
    telefono = forms.IntegerField(label="Teléfono", min_value=0)
    correo = forms.EmailField(label="Correo", max_length=45)
    rol = forms.ChoiceField(label="Rol")
    password = forms.CharField(
        label="Contraseña", required=False, widget=forms.PasswordInput(render_value=False)
    )
    activo = forms.BooleanField(label="Usuario activo", required=False, initial=True)

    def __init__(self, *args, creando=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.creando = creando
        self.fields["tipo_doc"].choices = [
            (t.id_doc, t.tipo_doc) for t in TipoDoc.objects.filter(estado=1).order_by("id_doc")
        ]
        self.fields["rol"].choices = [(r.idrol, r.nom_rol) for r in Rol.objects.order_by("idrol")]
        if creando:
            self.fields["password"].required = True
        else:
            self.fields["tipo_doc"].disabled = True
            self.fields["numero"].disabled = True
            self.fields["password"].help_text = "Déjala vacía para conservar la actual."

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            validate_password(password)
        return password


class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ["nombre", "unidad", "stock_actual", "stock_minimo", "activo"]
        labels = {"stock_actual": "Stock actual", "stock_minimo": "Stock mínimo"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["stock_actual"].disabled = True
            self.fields["stock_actual"].help_text = "Usa Agregar / Descontar en el inventario para moverlo."


class RecetaForm(forms.ModelForm):
    class Meta:
        model = ProductoInsumo
        fields = ["insumo", "cantidad"]
        labels = {"cantidad": "Cantidad por unidad del plato"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["insumo"].queryset = Insumo.objects.filter(activo=True)
