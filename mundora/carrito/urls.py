from django.urls import path

from . import views


# Identifica las rutas de la aplicación.
app_name = "carrito"

urlpatterns = [
    # Muestra el carrito del usuario autenticado.
    path(
        "",
        views.ver_carrito,
        name="detalle",
    ),

    # Agrega unidades de una variante.
    path(
        "agregar/<int:variante_id>/",
        views.agregar_variante,
        name="agregar",
    ),

    # Reemplaza la cantidad de un ítem propio.
    path(
        "items/<int:item_id>/actualizar/",
        views.actualizar_cantidad,
        name="actualizar",
    ),

    # Elimina un ítem del carrito propio.
    path(
        "items/<int:item_id>/quitar/",
        views.quitar_item,
        name="quitar",
    ),
]