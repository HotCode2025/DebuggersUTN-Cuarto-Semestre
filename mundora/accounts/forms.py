from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User


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