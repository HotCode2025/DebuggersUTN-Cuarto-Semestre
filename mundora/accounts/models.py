from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

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

class DomicilioEntrega(models.Model):
    """Guarda el domicilio habitual de entrega de un usuario."""

    # Cada cuenta puede guardar un único domicilio habitual.
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="domicilio_entrega",
        verbose_name="usuario",
    )

    # La persona que recibe puede ser distinta del titular de la cuenta.
    destinatario = models.CharField(
        "nombre y apellido de quien recibe",
        max_length=150,
    )

    telefono_contacto = models.CharField(
        "teléfono de contacto para la entrega",
        max_length=30,
    )

    # Dirección de entrega dentro de Argentina.
    provincia = models.CharField(
        "provincia",
        max_length=100,
    )

    localidad = models.CharField(
        "localidad",
        max_length=100,
    )

    codigo_postal = models.CharField(
        "código postal",
        max_length=10,
    )

    calle = models.CharField(
        "calle",
        max_length=150,
    )

    numero = models.CharField(
        "número",
        max_length=20,
        help_text="Si el domicilio no tiene numeración, indicá S/N.",
    )

    detalle_direccion = models.CharField(
        "piso, departamento o referencias",
        max_length=200,
        blank=True,
    )

    # Registra cuándo se creó y cuándo se modificó la dirección.
    fecha_creacion = models.DateTimeField(
        "fecha de creación",
        auto_now_add=True,
    )

    fecha_actualizacion = models.DateTimeField(
        "última modificación",
        auto_now=True,
    )

    class Meta:
        """Define los nombres visibles del domicilio."""

        verbose_name = "domicilio de entrega"
        verbose_name_plural = "domicilios de entrega"

    def __str__(self):
        """Identifica el domicilio por su dirección y localidad."""

        return f"{self.calle} {self.numero}, {self.localidad}"

    