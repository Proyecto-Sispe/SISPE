from django import forms


class CargaMasivaForm(forms.Form):

    TIPOS = [
        ("categorias", "Categorías"),
        ("productos", "Productos"),
        ("insumos", "Inventario e insumos"),
    ]

    tipo = forms.ChoiceField(
        choices=TIPOS,
        label="Tipo de información",
        widget=forms.Select(attrs={"class": "campo"}),
    )

    archivo = forms.FileField(
        label="Seleccionar archivo",
        help_text="Formatos permitidos: Excel .xlsx y CSV .csv",
        widget=forms.ClearableFileInput(
            attrs={"class": "campo-archivo", "accept": ".xlsx,.csv"}
        ),
    )

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]

        extensiones = (".xlsx", ".csv")

        if not archivo.name.lower().endswith(extensiones):
            raise forms.ValidationError(
                "Solo se permiten archivos Excel .xlsx o CSV."
            )

        if archivo.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "El archivo no puede superar los 5 MB."
            )

        return archivo