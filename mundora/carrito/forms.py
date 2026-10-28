from django import forms


class FormularioAgregarCarrito(forms.Form):
    """Valida la cantidad que el usuario quiere agregar."""

    cantidad = forms.IntegerField(
        label="Cantidad",
        min_value=1,
        error_messages={
            "required": "Ingresá una cantidad.",
            "invalid": "Ingresá una cantidad entera.",
            "min_value": "La cantidad debe ser al menos 1.",
        },
    )