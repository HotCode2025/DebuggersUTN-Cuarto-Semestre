from django.urls import path

from . import views_publicas


# Identifica las rutas del catálogo público.
app_name = "catalogo"

urlpatterns = [
    # Muestra el listado de productos visibles.
    path(
        "",
        views_publicas.listado_productos,
        name="listado",
    ),

    # Muestra el detalle utilizando el identificador del producto.
    path(
        "productos/<slug:identificador_url>/",
        views_publicas.detalle_producto_publico,
        name="detalle",
    ),
]