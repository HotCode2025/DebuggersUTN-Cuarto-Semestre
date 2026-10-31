import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Compra(models.Model):
    """Agrupa los pedidos de una operación realizada por un comprador."""

    class Estado(models.TextChoices):
        """Define el resultado general de la compra."""

        PENDIENTE = "pendiente", "Pendiente de pago"
        CONFIRMADA = "confirmada", "Confirmada"
        RECHAZADA = "rechazada", "Rechazada"
        CANCELADA = "cancelada", "Cancelada"

    # Identificador público independiente del número interno de la tabla.
    codigo = models.UUIDField(
        "código de compra",
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
       
    # Identifica la selección y el domicilio utilizados al crear la compra.
    huella_revision = models.CharField(
        "huella de la revisión",
        max_length=64,
        blank=True,
        default="",
        editable=False,
    )

    comprador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="compras",
        verbose_name="comprador",
    )

    estado = models.CharField(
        "estado",
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )

    motivo_rechazo = models.CharField(
        "motivo del rechazo",
        max_length=250,
        blank=True,
    )

    # Copia del domicilio elegido: no depende de sus modificaciones futuras.
    destinatario = models.CharField(
        "nombre y apellido de quien recibe",
        max_length=150,
    )
    telefono_contacto = models.CharField(
        "teléfono de contacto",
        max_length=30,
    )
    provincia = models.CharField("provincia", max_length=100)
    localidad = models.CharField("localidad", max_length=100)
    codigo_postal = models.CharField("código postal", max_length=10)
    calle = models.CharField("calle", max_length=150)
    numero = models.CharField("número", max_length=20)
    detalle_direccion = models.CharField(
        "piso, departamento o referencias",
        max_length=200,
        blank=True,
    )

    fecha_creacion = models.DateTimeField(
        "fecha de creación",
        auto_now_add=True,
    )
    fecha_actualizacion = models.DateTimeField(
        "última modificación",
        auto_now=True,
    )
    fecha_confirmacion = models.DateTimeField(
        "fecha de confirmación",
        null=True,
        blank=True,
    )

    class Meta:
        """Define los nombres visibles y muestra primero lo más reciente."""

        verbose_name = "compra"
        verbose_name_plural = "compras"
        ordering = ["-fecha_creacion", "-pk"]

    @property
    def total_productos(self):
        """Suma los importes de los productos, sin incluir envíos."""

        return sum(
            (pedido.subtotal for pedido in self.pedidos.all()),
            Decimal("0.00"),
        )

    def __str__(self):
        """Identifica la compra mediante su código público."""

        return f"Compra {self.codigo}"


class Pedido(models.Model):
    """Agrupa los productos que una tienda debe entregar en una compra."""

    class Estado(models.TextChoices):
        """Define las etapas de preparación y entrega del pedido."""

        PENDIENTE = "pendiente", "Pendiente de confirmación"
        PREPARACION = "preparacion", "En preparación"
        ENVIADO = "enviado", "Enviado"
        ENTREGADO = "entregado", "Entregado"
        CANCELADO = "cancelado", "Cancelado"

    class EstadoDevolucion(models.TextChoices):
        """Define el avance de la devolución del pedido completo."""

        SIN_SOLICITUD = "sin_solicitud", "Sin solicitud"
        SOLICITADA = "solicitada", "Solicitada"
        ACEPTADA = "aceptada", "Aceptada: pendiente de recepción"
        RECHAZADA = "rechazada", "Rechazada"
        COMPLETADA = "completada", "Completada"

    compra = models.ForeignKey(
        Compra,
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name="compra",
    )

    tienda = models.ForeignKey(
        "catalog.Tienda",
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name="tienda",
    )

    # Conserva el nombre comercial utilizado al realizar la compra.
    nombre_tienda = models.CharField(
        "nombre de la tienda al comprar",
        max_length=150,
    )

    estado = models.CharField(
        "estado",
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )

    fecha_creacion = models.DateTimeField(
        "fecha de creación",
        auto_now_add=True,
    )
    fecha_actualizacion = models.DateTimeField(
        "última modificación",
        auto_now=True,
    )

        # Datos de seguimiento correspondientes a este pedido.
    empresa_transporte = models.CharField(
        "empresa de transporte",
        max_length=100,
        blank=True,
    )
    codigo_seguimiento = models.CharField(
        "código de seguimiento",
        max_length=100,
        blank=True,
    )
    fecha_despacho = models.DateTimeField(
        "fecha de despacho",
        null=True,
        blank=True,
    )
        # Registra cuándo el comprador confirma la recepción.
    fecha_entrega = models.DateTimeField(
        "fecha de confirmación de recepción",
        null=True,
        blank=True,
    )
    # Conserva el resultado de una cancelación posterior al pago.
    fecha_cancelacion = models.DateTimeField(
        "fecha de cancelación",
        null=True,
        blank=True,
    )
    importe_reembolso_simulado = models.DecimalField(
        "importe del reembolso simulado",
        max_digits=18,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        editable=False,
    )
    fecha_reembolso_simulado = models.DateTimeField(
        "fecha del reembolso simulado",
        null=True,
        blank=True,
        editable=False,
    )

        # Registra una devolución independiente del estado de entrega.
    estado_devolucion = models.CharField(
        "estado de devolución",
        max_length=20,
        choices=EstadoDevolucion.choices,
        default=EstadoDevolucion.SIN_SOLICITUD,
    )
    motivo_devolucion = models.TextField(
        "motivo de devolución",
        max_length=1000,
        blank=True,
    )
    fecha_solicitud_devolucion = models.DateTimeField(
        "fecha de solicitud de devolución",
        null=True,
        blank=True,
    )
    class Meta:
        """Impide generar dos pedidos de la misma tienda en una compra."""

        verbose_name = "pedido"
        verbose_name_plural = "pedidos"
        ordering = ["pk"]

        constraints = [
            models.UniqueConstraint(
                fields=["compra", "tienda"],
                name="pedido_tienda_unica_por_compra",
            ),
        ]

    @property
    def subtotal(self):
        """Suma los importes históricos de los productos del pedido."""

        return sum(
            (detalle.subtotal for detalle in self.detalles.all()),
            Decimal("0.00"),
        )

    def __str__(self):
        """Identifica el pedido y la tienda que debe prepararlo."""

        return f"Pedido {self.pk} — {self.nombre_tienda}"


class DetallePedido(models.Model):
    """Conserva una variante comprada con su cantidad y precio acordado."""

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.PROTECT,
        related_name="detalles",
        verbose_name="pedido",
    )

    # Conserva el historial aunque la variante se elimine del catálogo.
    variante = models.ForeignKey(
        "catalog.Variante",
        on_delete=models.SET_NULL,
        related_name="detalles_pedido",
        verbose_name="variante",
        null=True,
        blank=True,
    )

    # Copias de los datos del producto y de su combinación.
    nombre_producto = models.CharField(
        "nombre del producto al comprar",
        max_length=150,
    )
    marca = models.CharField("marca", max_length=100, blank=True)
    color = models.CharField("color", max_length=60, blank=True)
    medidas = models.CharField("medidas", max_length=100, blank=True)
    material = models.CharField("material", max_length=100, blank=True)

    cantidad = models.PositiveIntegerField(
        "cantidad",
        validators=[MinValueValidator(1)],
    )

    # Este precio no se obtiene nuevamente del catálogo al consultar la compra.
    precio_unitario = models.DecimalField(
        "precio unitario en pesos argentinos",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    class Meta:
        """Evita variantes repetidas y valores numéricos inválidos."""

        verbose_name = "detalle del pedido"
        verbose_name_plural = "detalles de pedidos"
        ordering = ["pk"]

        constraints = [
            models.UniqueConstraint(
                fields=["pedido", "variante"],
                name="detalle_variante_unica_por_pedido",
            ),
            models.CheckConstraint(
                condition=models.Q(cantidad__gte=1),
                name="detalle_pedido_cantidad_positiva",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    precio_unitario__gte=Decimal("0.01"),
                ),
                name="detalle_pedido_precio_positivo",
            ),
        ]

    @property
    def subtotal(self):
        """Calcula el importe utilizando el precio guardado en el pedido."""

        return self.precio_unitario * self.cantidad

    def __str__(self):
        """Describe el producto y la cantidad comprada."""

        return f"{self.nombre_producto} × {self.cantidad}"