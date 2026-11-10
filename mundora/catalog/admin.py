from django.contrib import admin
from django.utils import timezone

from .models import Categoria, ImagenProducto, Producto, Tienda, Variante

from .forms import(
    ConjuntoImagenesProducto,
    ConjuntoVariantesProducto,
    FormularioProducto,
    FormularioTienda,
)


@admin.register(Tienda)
class AdministradorTienda(admin.ModelAdmin):
    """Configura la gestión de tiendas en el panel administrativo."""
        # Aplica las validaciones de revisión de tiendas.
    form = FormularioTienda

    # Columnas del listado de tiendas.
    list_display = (
        "nombre",
        "propietario",
        "provincia",
        "localidad",
        "estado",
    )

    # Filtros disponibles en el listado.
    list_filter = ("estado", "provincia")

    # Campos utilizados por el buscador.
    search_fields = (
        "nombre",
        "propietario__username",
        "correo_contacto",
    )

    # Fechas visibles que no pueden editarse manualmente.
    readonly_fields = (
        "fecha_creacion",
        "fecha_actualizacion",
    )
    
    def save_model(self, request, obj, form, change):
        """Guarda la tienda y pausa productos si no está aprobada."""

        super().save_model(request, obj, form, change)

        if obj.estado != Tienda.Estado.APROBADA:
            cantidad = obj.productos.filter(
                publicado=True,
            ).update(
                publicado=False,
                fecha_actualizacion=timezone.now(),
            )

            if cantidad:
                self.message_user(
                    request,
                    f"Se pausaron {cantidad} publicaciones porque "
                    "la tienda no está aprobada.",
                )

@admin.register(Categoria)
class AdministradorCategoria(admin.ModelAdmin):
    """Configura la gestión de categorías en el panel administrativo."""

    # Columnas del listado de categorías.
    list_display = ("nombre", "categoria_superior", "activa")

    # Permite filtrar por categorías activas o inactivas.
    list_filter = ("activa",)

    # Permite buscar categorías por su nombre.
    search_fields = ("nombre",)

    # Sugiere un identificador para URL a partir del nombre.
    prepopulated_fields = {
        "identificador_url": ("nombre",),
    }

class VarianteEnLinea(admin.StackedInline):
    """Permite cargar variantes dentro del formulario del producto."""

    model = Variante
    #Solo muestra una nueva fila cuando se solicita agregar una variante.
    formset = ConjuntoVariantesProducto
    extra = 0

    #Permite eliminar variantes desde el formulario
    can_delete = True

    # Campos de cada combinación disponible.
    fields = (
        "color",
        "medidas",
        "material",
        "precio",
        "stock",
        "imagen",
        "activa",
    )


class ImagenProductoEnLinea(admin.TabularInline):
    """Permite administrar la galería desde el producto."""

    model = ImagenProducto

    #Comprueba que una publicacion conserve imagenes en su galeria.
    formset = ConjuntoImagenesProducto

    extra = 1

    # Datos y posición de cada fotografía.
    fields = (
        "imagen",
        "texto_alternativo",
        "orden",
    )


@admin.register(Producto)
class AdministradorProducto(admin.ModelAdmin):
    """Configura la carga de productos, variantes e imágenes."""

    #aplica las condiciones generales para publicar
    form = FormularioProducto

    # Columnas del listado de productos.
    list_display = (
        "nombre",
        "tienda",
        "categoria",
        "publicado",
        "estado_revision",
    )

    # Filtros disponibles en el panel.
    list_filter = (
        "publicado",
        "estado_revision",
        "categoria",
    )

    # Permite buscar por producto, marca o tienda.
    search_fields = (
        "nombre",
        "marca",
        "tienda__nombre",
    )

    # Sugiere el identificador para los enlaces del producto.
    prepopulated_fields = {
        "identificador_url": ("nombre",),
    }

    # Impide modificar manualmente las fechas automáticas.
    readonly_fields = (
        "fecha_creacion",
        "fecha_actualizacion",
    )

    # Agrupa los campos para facilitar la carga.
    fieldsets = (
        (
            "Información del producto",
            {
                "fields": (
                    "tienda",
                    "categoria",
                    "nombre",
                    "identificador_url",
                    "descripcion",
                    "marca",
                    "cuidados",
                    "provincia_origen",
                )
            },
        ),
        (
            "Publicación y revisión",
            {
                "fields": (
                    "publicado",
                    "estado_revision",
                    "observaciones_revision",
                )
            },
        ),
        (
            "Fechas",
            {
                "fields": (
                    "fecha_creacion",
                    "fecha_actualizacion",
                )
            },
        ),
    )

    # Incorpora variantes y fotografías en la misma pantalla.
    inlines = (
        VarianteEnLinea,
        ImagenProductoEnLinea,
    )