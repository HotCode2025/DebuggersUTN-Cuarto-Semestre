from django import forms


class FormularioDespacho(forms.Form):
    """Solicita los datos necesarios para registrar un envío."""

    empresa_transporte = forms.CharField(
        label="Empresa de transporte",
        max_length=100,
        strip=True,
        help_text="Para las pruebas podés usar una empresa ficticia.",
    )
    codigo_seguimiento = forms.CharField(
        label="Código de seguimiento",
        max_length=100,
        strip=True,
        help_text="Ingresá el código que identifica este envío.",
    )
class FormularioSolicitudDevolucion(forms.Form):
    """Solicita el motivo para devolver todos los artículos del pedido."""

    motivo = forms.CharField(
        label="Motivo de la devolución",
        max_length=1000,
        strip=True,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Explicá por qué querés devolver este pedido completo.",
    )