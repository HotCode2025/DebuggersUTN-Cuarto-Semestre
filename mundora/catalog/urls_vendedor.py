from django.urls import path

from . import views_vendedor


# Identifica las rutas privadas del vendedor.
app_name = "vendedores"

urlpatterns = [
    # Muestra la tienda y sus publicaciones.
    path(
        "",
        views_vendedor.panel_vendedor,
        name="panel",
    ),

    # Muestra el detalle privado de un producto propio.
    path(
        "productos/<int:producto_id>/",
        views_vendedor.detalle_producto_vendedor,
        name="detalle_producto",
    ),
        # Permite preparar una publicación nueva.
    path(
        "productos/nuevo/",
        views_vendedor.crear_producto_vendedor,
        name="crear_producto",
    ),

    # Permite modificar únicamente un producto propio.
    path(
        "productos/<int:producto_id>/editar/",
        views_vendedor.editar_producto_vendedor,
        name="editar_producto",
    ),
    # Permite gestionar las variantes de un producto propio.
    path(  
        "productos/<int:producto_id>/variantes/",
        views_vendedor.gestionar_variantes_vendedor,
        name="gestionar_variantes",
    ),
    # Permite administrar la galería de un producto propio.
    path(
        "productos/<int:producto_id>/galeria/",
        views_vendedor.gestionar_galeria_vendedor,
        name="gestionar_galeria",
    ),
    # Cambia el estado de publicación mediante una solicitud POST.
    path(
        "productos/<int:producto_id>/publicacion/",
        views_vendedor.cambiar_publicacion_vendedor,
        name="cambiar_publicacion",
    ),
]