from django.contrib import admin

from .models import Categoria, Tienda


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