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
]