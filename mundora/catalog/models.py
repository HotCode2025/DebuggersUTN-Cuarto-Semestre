from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from decimal import Decimal
from django.db import models

from django.core.validators import MinValueValidator

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

class Producto(models.Model):
    """Representa una publicación del catálogo de una tienda."""

    class EstadoRevision(models.TextChoices):
        """Indica el resultado de la revisión administrativa."""

        PENDIENTE = "pendiente", "En revisión"
        APROBADO = "aprobado", "Verificado"
        RECHAZADO = "rechazado", "Rechazado"

    # Tienda propietaria y única categoría del producto.
    tienda = models.ForeignKey(
        Tienda,
        on_delete=models.PROTECT,
        related_name="productos",
        verbose_name="tienda",
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="productos",
        verbose_name="categoría",
    )

    # Información general de la publicación.
    nombre = models.CharField("nombre", max_length=150)
    identificador_url = models.SlugField(
        "identificador para URL",
        max_length=180,
        unique=True,
    )
    descripcion = models.TextField("descripción")
    marca = models.CharField(
        "marca",
        max_length=100,
        blank=True,
    )
    cuidados = models.TextField(
        "instrucciones de cuidado",
        blank=True,
    )
    provincia_origen = models.CharField(
        "provincia de origen",
        max_length=100,
    )

    # La publicación comienza sin estar visible.
    publicado = models.BooleanField(
        "publicado",
        default=False,
    )

    # La revisión es independiente de la decisión de publicar.
    estado_revision = models.CharField(
        "estado de revisión",
        max_length=20,
        choices=EstadoRevision.choices,
        default=EstadoRevision.PENDIENTE,
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
        """Define los nombres visibles y muestra primero lo más reciente."""

        verbose_name = "producto"
        verbose_name_plural = "productos"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        """Identifica el producto por su nombre."""

        return self.nombre


class Variante(models.Model):
    """Representa una versión del producto con precio y stock propios."""

    # Producto al que pertenece esta combinación.
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="variantes",
        verbose_name="producto",
    )

    # Características de un producto terminado, sin personalización.
    color = models.CharField(
        "color",
        max_length=60,
        blank=True,
    )
    medidas = models.CharField(
        "medidas",
        max_length=100,
        blank=True,
        help_text="Incluí la unidad. Ejemplo: 40 × 40 × 150 cm.",
    )
    material = models.CharField(
        "material",
        max_length=100,
        blank=True,
    )

    # Todos los precios del proyecto se expresan en pesos argentinos.
    precio = models.DecimalField(
        "precio en pesos argentinos",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    stock = models.PositiveIntegerField(
        "unidades disponibles",
        default=0,
    )

    # Imagen opcional para mostrar al seleccionar esta variante.
    imagen = models.ImageField(
        "imagen de la variante",
        upload_to="productos/variantes/",
        blank=True,
    )

    # Permite retirar una variante de la venta conservando su registro.
    activa = models.BooleanField(
        "activa",
        default=True,
    )

    class Meta:
        """Ordena las variantes y establece restricciones de datos."""

        verbose_name = "variante"
        verbose_name_plural = "variantes"
        ordering = ["pk"]

        constraints = [
            # Evita repetir una misma combinación dentro del producto.
            models.UniqueConstraint(
                fields=["producto", "color", "medidas", "material"],
                name="variante_combinacion_unica",
            ),
            # Impide guardar precios iguales o menores que cero.
            models.CheckConstraint(
                condition=models.Q(precio__gte=Decimal("0.01")),
                name="variante_precio_positivo",
            ),
        ]

    def __str__(self):
        """Describe la combinación o la identifica como estándar."""

        caracteristicas = [
            valor
            for valor in (self.color, self.medidas, self.material)
            if valor
        ]
        descripcion = " / ".join(caracteristicas) or "Estándar"

        return f"{self.producto.nombre} - {descripcion}"


class ImagenProducto(models.Model):
    """Guarda una fotografía de la galería del producto."""

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="imagenes",
        verbose_name="producto",
    )

    # Archivo de imagen y descripción para accesibilidad.
    imagen = models.ImageField(
        "imagen",
        upload_to="productos/galeria/",
    )
    texto_alternativo = models.CharField(
        "descripción de la imagen",
        max_length=180,
        help_text="Ejemplo: lámpara de pie verde vista de frente.",
    )

    # La imagen con el menor número será la principal.
    orden = models.PositiveIntegerField(
        "orden de presentación",
        default=0,
    )

    class Meta:
        """Ordena la galería y define sus nombres visibles."""

        verbose_name = "imagen del producto"
        verbose_name_plural = "imágenes de productos"
        ordering = ["orden", "pk"]

    def __str__(self):
        """Identifica la fotografía y su posición en la galería."""

        return f"{self.producto.nombre} - Imagen {self.orden}"


