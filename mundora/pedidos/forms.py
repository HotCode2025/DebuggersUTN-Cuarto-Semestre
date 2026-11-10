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

class FormularioRespuestaDevolucion(forms.Form):
    """Solicita la decisión y su explicación para el comprador."""

    decision = forms.ChoiceField(
        label="Decisión",
        choices=[
            ("", "Seleccioná una opción"),
            ("aceptar", "Aceptar devolución"),
            ("rechazar", "Rechazar devolución"),
        ],
    )
    respuesta = forms.CharField(
        label="Respuesta al comprador",
        max_length=1500,
        strip=True,
        widget=forms.Textarea(attrs={"rows": 5}),
        help_text=(
            "Explicá tu decisión. Si aceptás, incluí las instrucciones "
            "para devolver los artículos."
        ),
    )

class FormularioRecepcionDevolucion(forms.Form):
    """Confirma la recepción completa y define si se repone stock."""

    recepcion_completa = forms.BooleanField(
        label="Confirmo que recibí todos los artículos del pedido", 
        required=True,
        )
    reposicion = forms.ChoiceField(
        label="Reposición de stock",
        choices=[
            ("", "Seleccioná una opción"),
            ("si", "Reponer todas las unidades: están aptas para vender"),
            ("no", "No reponer unidades"),
        ],
        )
    observaciones = forms.CharField(
        label="Estado de los artículos recibidos",
        max_length=1500,
        strip=True,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Describí su estado y explicá la decisión sobre el stock.",
    )