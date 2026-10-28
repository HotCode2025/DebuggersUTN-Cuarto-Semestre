from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Carrito(models.Model):
    """Conserva la selección de compra de un usuario."""

    # Cada usuario puede tener un único carrito.
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carrito",
        verbose_name="usuario",
    )

    fecha_creacion = models.DateTimeField(
        "fecha de creación",
        auto_now_add=True,
    )

    class Meta:
        """Define los nombres visibles del carrito."""

        verbose_name = "carrito"
        verbose_name_plural = "carritos"

    def __str__(self):
        """Identifica el carrito mediante su propietario."""

        return f"Carrito del usuario {self.usuario_id}"


class ItemCarrito(models.Model):
    """Guarda una variante y la cantidad elegida en el carrito."""

    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="carrito",
    )

    # Se referencia la variante para obtener su precio y stock actuales.
    variante = models.ForeignKey(
        "catalog.Variante",
        on_delete=models.CASCADE,
        related_name="items_carrito",
        verbose_name="variante",
    )

    cantidad = models.PositiveIntegerField(
        "cantidad",
        default=1,
        validators=[MinValueValidator(1)],
    )

    fecha_agregado = models.DateTimeField(
        "fecha de incorporación",
        auto_now_add=True,
    )

    fecha_actualizacion = models.DateTimeField(
        "última modificación",
        auto_now=True,
    )

    class Meta:
        """Ordena los ítems e impide duplicados y cantidades inválidas."""

        verbose_name = "ítem del carrito"
        verbose_name_plural = "ítems del carrito"
        ordering = ["fecha_agregado", "pk"]

        constraints = [
            models.UniqueConstraint(
                fields=["carrito", "variante"],
                name="carrito_variante_unica",
            ),
            models.CheckConstraint(
                condition=models.Q(cantidad__gte=1),
                name="carrito_cantidad_positiva",
            ),
        ]

    @property
    def subtotal(self):
        """Calcula el importe con el precio vigente de la variante."""

        return self.variante.precio * self.cantidad

    def __str__(self):
        """Identifica la variante y la cantidad seleccionada."""

        return f"{self.variante} × {self.cantidad}"