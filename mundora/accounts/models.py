from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    """Representa una cuenta que puede comprar y solicitar una tienda."""

    # Cada cuenta debe tener un correo diferente.
    email = models.EmailField(
        "correo electrónico",
        unique=True,
        blank=False,
        error_messages={
            "unique": "Ya existe una cuenta con este correo electrónico.",
        },
    )

    # Permite conservar las cuentas existentes sin inventarles un teléfono.
    telefono = models.CharField(
        "teléfono",
        max_length=30,
        blank=True,
    )

    