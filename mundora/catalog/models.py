from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Tienda(models.Model):
    """Representa el comercio de un usuario vendedor."""

    class Estado(models.TextChoices):
        """Define los posibles estados de aprobación de la tienda."""

        PENDIENTE = "pendiente", "Pendiente de aprobación"
        APROBADA = "aprobada", "Aprobada"
        RECHAZADA = "rechazada", "Rechazada"

    # Cada usuario puede ser propietario de una sola tienda.
    propietario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tienda",
        verbose_name="propietario",
    )

    # Datos comerciales y de contacto.
    nombre = models.CharField("nombre comercial", max_length=150)
    descripcion = models.TextField("descripción")
    correo_contacto = models.EmailField("correo de contacto")
    telefono = models.CharField("teléfono", max_length=30)

    # Única dirección desde la que la tienda despacha sus productos.
    provincia = models.CharField("provincia", max_length=100)
    localidad = models.CharField("localidad", max_length=100)
    codigo_postal = models.CharField("código postal", max_length=10)
    calle = models.CharField("calle", max_length=150)
    numero = models.CharField("número", max_length=20)
    detalle_direccion = models.CharField(
        "piso, departamento o referencia",
        max_length=200,
        blank=True,
    )

    # Resultado y observaciones de la revisión del administrador.
    estado = models.CharField(
        "estado",
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    observaciones_revision = models.TextField(
        "observaciones de la revisión",
        blank=True,
    )

    # Fechas registradas automáticamente.
    fecha_creacion = models.DateTimeField(
        "fecha de creación",
        auto_now_add=True,
    )
    fecha_actualizacion = models.DateTimeField(
        "última modificación",
        auto_now=True,
    )

    class Meta:
        """Configura los nombres visibles y el orden predeterminado."""

        verbose_name = "tienda"
        verbose_name_plural = "tiendas"
        ordering = ["nombre"]

    def __str__(self):
        """Identifica la tienda por su nombre comercial."""

        return self.nombre


class Categoria(models.Model):
    """Organiza los productos en categorías y subcategorías."""

    # Nombre, identificador para enlaces y descripción.
    nombre = models.CharField("nombre", max_length=100)
    identificador_url = models.SlugField(
        "identificador para URL",
        max_length=150,
        unique=True,
    )
    descripcion = models.TextField("descripción", blank=True)

    # Si no tiene categoría superior, es una categoría principal.
    categoria_superior = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="subcategorias",
        verbose_name="categoría superior",
        null=True,
        blank=True,
    )

    # Indica si la categoría está habilitada.
    activa = models.BooleanField("activa", default=True)

    class Meta:
        """Configura los nombres visibles y el orden predeterminado."""

        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["nombre"]

    def clean(self):
        """Valida que la jerarquía de categorías no tenga ciclos."""

        super().clean()

        categorias_visitadas = (
            {self.pk} if self.pk is not None else set()
        )
        antecesora = self.categoria_superior

        # Recorre las categorías superiores buscando repeticiones.
        while antecesora is not None:
            if antecesora.pk in categorias_visitadas:
                raise ValidationError({
                    "categoria_superior": (
                        "Esta relación genera un ciclo entre categorías."
                    )
                })

            categorias_visitadas.add(antecesora.pk)
            antecesora = antecesora.categoria_superior

    def __str__(self):
        """Identifica la categoría por su nombre."""

        return self.nombre