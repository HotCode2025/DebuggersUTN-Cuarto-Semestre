from django.contrib import admin

from .models import Categoria, ImagenProducto, Producto, Tienda, Variante

from .forms import(
    ConjuntoImagenesProducto,
    ConjuntoVariantesProducto,
    FormularioProducto,
)


@admin.register(Tienda)
class AdministradorTienda(admin.ModelAdmin):
    """Configura la gestión de tiendas en el panel administrativo."""

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