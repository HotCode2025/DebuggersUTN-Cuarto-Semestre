from django.urls import path

from . import views


# Identifica las rutas del proceso de compra.
app_name = "pedidos"

urlpatterns = [
    # Permite revisar la selección y el domicilio del comprador.
    path(
        "revisar/",
        views.revisar_compra,
        name="revisar",
    ),

        # Crea la compra pendiente mediante POST.
    path(
        "crear/",
        views.crear_compra,
        name="crear",
    ),

    # Muestra el detalle histórico de una compra propia.
    path(
        "<uuid:codigo>/",
        views.detalle_compra,
        name="detalle",
    ),
]