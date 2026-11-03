from decimal import Decimal, InvalidOperation

from django.db import transaction

from .mercado_pago import consultar_orden
from .models import Compra
from .services import procesar_pago_simulado


def verificar_pago_de_compra(compra):
    """Consulta la orden y confirma la compra solo si el pago coincide."""
    orden = consultar_orden(compra)

    if (
        orden.get("id") != compra.mp_orden_id
        or orden.get("external_reference") != str(compra.codigo)
    ):
        return "datos_incorrectos"

    if (orden.get("status"), orden.get("status_detail")) != (
        "processed", "accredited"
    ):
        return "sin_acreditar"

    try:
        pagado = Decimal(str(orden.get("total_paid_amount")))
        importe_orden = Decimal(str(orden.get("total_amount")))
    except InvalidOperation:
        return "datos_incorrectos"

    if (
        orden.get("currency") != "ARS"
        or not pagado.is_finite()
        or not importe_orden.is_finite()
        or pagado != compra.total_con_entrega
        or importe_orden != pagado
    ):
        return "datos_incorrectos"

    # El servicio existente bloquea la compra y las variantes.
    # Si otro aviso ya la confirmó, no vuelve a descontar stock.
    with transaction.atomic():
        compra, modificada = procesar_pago_simulado(
            compra.comprador, compra.codigo, "aprobado"
        )

        if compra.estado == Compra.Estado.CONFIRMADA:
            return "confirmada"

        if modificada and compra.estado == Compra.Estado.RECHAZADA:
            compra.motivo_rechazo = (
                "Pago acreditado en Mercado Pago. Revisar posible reembolso. "
                + compra.motivo_rechazo
            )[:250]
            compra.save(update_fields=["motivo_rechazo"])

        return "requiere_revision"