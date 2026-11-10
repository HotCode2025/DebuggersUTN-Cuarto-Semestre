import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User, DomicilioEntrega


class FormularioRegistro(UserCreationForm):
    """Valida los datos necesarios para crear una cuenta."""

    first_name = forms.CharField(
        label="Nombre",
        max_length=150,
        required=True,
    )

    last_name = forms.CharField(
        label="Apellido",
        max_length=150,
        required=True,
    )

    email = forms.EmailField(
        label="Correo electrónico",
        required=True,
    )

    telefono = forms.CharField(
        label="Teléfono",
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"type": "tel"}),
    )

    class Meta:
        """Define el modelo y los campos disponibles en el registro."""

        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "telefono",
            "password1",
            "password2",
        )

        labels = {
            "username": "Nombre de usuario",
        }

        help_texts = {
            "username": (
                "Usá letras, números o los símbolos . + - _ "
                "sin espacios ni @."
            ),
        }

    def clean_username(self):
        """Valida el nombre de usuario y evita cuentas duplicadas."""

        nombre_usuario = self.cleaned_data["username"]

        if "@" in nombre_usuario:
            raise forms.ValidationError(
                "El nombre de usuario no puede contener @."
            )

        if User.objects.filter(
            username__iexact=nombre_usuario
        ).exists():
            raise forms.ValidationError(
                "Ya existe una cuenta con este nombre de usuario."
            )

        return nombre_usuario

    def clean_email(self):
        """Normaliza el correo y comprueba que no esté registrado."""

        correo = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=correo).exists():
            raise forms.ValidationError(
                "Ya existe una cuenta con este correo electrónico."
            )

        return correo

class FormularioInicioSesion(AuthenticationForm):
    """Solicita el identificador de la cuenta y su contraseña."""

    username = forms.CharField(
        label="Correo electrónico o nombre de usuario",
        max_length=254,
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "autocomplete": "username",
            }
        ),
    )

    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password"}
        ),
    )

    error_messages = {
        "invalid_login": (
            "No pudimos iniciar sesión. Revisá tu correo o nombre "
            "de usuario y tu contraseña."
        ),
        "inactive": "Esta cuenta está inactiva.",
    }

# Opciones disponibles para los domicilios dentro de Argentina.
PROVINCIAS_ARGENTINAS = (
    "Buenos Aires",
    "Ciudad Autónoma de Buenos Aires",
    "Catamarca",
    "Chaco",
    "Chubut",
    "Córdoba",
    "Corrientes",
    "Entre Ríos",
    "Formosa",
    "Jujuy",
    "La Pampa",
    "La Rioja",
    "Mendoza",
    "Misiones",
    "Neuquén",
    "Río Negro",
    "Salta",
    "San Juan",
    "San Luis",
    "Santa Cruz",
    "Santa Fe",
    "Santiago del Estero",
    "Tierra del Fuego, Antártida e Islas del Atlántico Sur",
    "Tucumán",
)


class FormularioDomicilioEntrega(forms.ModelForm):
    """Valida los datos del domicilio habitual de entrega."""

    provincia = forms.ChoiceField(
        label="Provincia",
        choices=[
            ("", "Seleccioná una provincia"),
            *[(provincia, provincia) for provincia in PROVINCIAS_ARGENTINAS],
        ],
    )

    class Meta:
        """Expone únicamente los datos que puede editar el comprador."""

        model = DomicilioEntrega

        # El propietario se asigna desde la sesión, nunca desde el formulario.
        fields = (
            "destinatario",
            "telefono_contacto",
            "provincia",
            "localidad",
            "codigo_postal",
            "calle",
            "numero",
            "detalle_direccion",
        )

        widgets = {
            "destinatario": forms.TextInput(
                attrs={"autocomplete": "shipping name"},
            ),
            "telefono_contacto": forms.TextInput(
                attrs={
                    "type": "tel",
                    "autocomplete": "shipping tel",
                },
            ),
            "localidad": forms.TextInput(
                attrs={"autocomplete": "shipping address-level2"},
            ),
            "codigo_postal": forms.TextInput(
                attrs={"autocomplete": "shipping postal-code"},
            ),
            "detalle_direccion": forms.Textarea(
                attrs={"rows": 3},
            ),
        }

        help_texts = {
            "codigo_postal": (
                "Ingresá 4 números o el CPA completo de 8 caracteres."
            ),
            "telefono_contacto": (
                "Podés incluir el código de país, espacios, guiones y paréntesis."
            ),
            "detalle_direccion": (
                "Opcional. Agregá piso, departamento o indicaciones para llegar."
            ),
        }

    def clean_codigo_postal(self):
        """Normaliza el código postal y comprueba su formato."""

        codigo = self.cleaned_data["codigo_postal"]
        codigo = "".join(codigo.split()).upper()

        if not re.fullmatch(
            r"(?:[0-9]{4}|[A-Z][0-9]{4}[A-Z]{3})",
            codigo,
        ):
            raise forms.ValidationError(
                "Ingresá 4 números o un CPA con una letra, "
                "4 números y 3 letras."
            )

        return codigo

    def clean_telefono_contacto(self):
        """Comprueba que el teléfono tenga un formato básico válido."""

        telefono = self.cleaned_data["telefono_contacto"].strip()

        if not re.fullmatch(r"[+0-9()\s-]+", telefono):
            raise forms.ValidationError(
                "El teléfono solo puede contener números, espacios, "
                "guiones, paréntesis y el signo +."
            )

        digitos = re.sub(r"[^0-9]", "", telefono)

        if not 7 <= len(digitos) <= 15:
            raise forms.ValidationError(
                "El teléfono debe contener entre 7 y 15 números."
            )

        return telefono