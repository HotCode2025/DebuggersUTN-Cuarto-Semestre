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

        # Procesa el pago simulado mediante una solicitud POST.
    path(
        "<uuid:codigo>/pagar/",
        views.pagar_compra,
        name="pagar",
    ),

        # Muestra el historial del comprador autenticado.
    path(
        "mis-compras/",
        views.mis_compras,
        name="mis_compras",
    ),
        # Confirma la recepción de un pedido del comprador autenticado.
    path(
        "pedidos/<int:pedido_id>/confirmar-recepcion/",
        views.confirmar_recepcion,
        name="confirmar_recepcion",
    ),
        # Cancela una compra pendiente mediante una solicitud POST.
    path(
        "<uuid:codigo>/cancelar/",
        views.cancelar_compra,
        name="cancelar_compra",
    ),
        # Cancela un pedido pagado que todavía está en preparación.
    path(
        "pedidos/<int:pedido_id>/cancelar/",
        views.cancelar_pedido,
        name="cancelar_pedido",
    ),
        # Permite solicitar la devolución de un pedido propio.
    path(
        "pedidos/<int:pedido_id>/devolucion/",
        views.solicitar_devolucion,
        name="solicitar_devolucion",
    ),
]