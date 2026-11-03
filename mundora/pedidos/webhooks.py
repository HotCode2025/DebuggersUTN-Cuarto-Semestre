import logging

from .models import Compra
from .verificacion import verificar_pago_de_compra

logger = logging.getLogger(__name__)

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from mercadopago.webhook import (
    InvalidWebhookSignatureError,
    WebhookSignatureValidator,
)


@csrf_exempt
@require_POST
def webhook_mercado_pago(request):
    """Comprueba que Mercado Pago firmó el aviso recibido por el túnel."""
    secreto = settings.MP_WEBHOOK_SECRETO_PRUEBA.strip()
    if not secreto:
        return HttpResponse("Falta configurar la firma de prueba.", status=503)

    firma = request.headers.get("x-signature")
    solicitud_id = request.headers.get("x-request-id")
    orden_id = request.GET.get("data.id")

    if not all((firma, solicitud_id, orden_id)):
        return HttpResponse("Faltan datos de la firma.", status=401)

    try:
        # Mercado Pago firmó el aviso con el ID de la orden en minúsculas.
        WebhookSignatureValidator.validate(firma, solicitud_id, orden_id.lower(), secreto)
    except InvalidWebhookSignatureError as error:
        # Registra el motivo en la terminal sin exponer claves ni firmas.
        detalle = str(error).lower()
        if any(palabra in detalle for palabra in ("timestamp", "expired", "tolerance")):
            motivo = "marca de tiempo o tolerancia"        
        elif any(palabra in detalle for palabra in ("malformed", "format", "missing")):
            motivo = "formato de la firma o dato faltante"
        elif any(palabra in detalle for palabra in ("mismatch", "does not match")):
            motivo = "la firma calculada no coincide"
        else:
            motivo = "el SDK no distingue la causa en el mensaje"

        logger.warning("Webhook rechazado para la orden %s: %s", orden_id, motivo)
        return HttpResponse("Firma no válida.", status=401)

    compra = Compra.objects.filter(mp_orden_id=orden_id).first()
    if compra is None:
        return HttpResponse("Orden sin compra asociada.", status=200)

    try:
        resultado = verificar_pago_de_compra(compra)
    except (ValueError, ConnectionError):
        logger.warning("No se pudo consultar la orden de la compra %s.", compra.pk)
        return HttpResponse("No se pudo consultar la orden.", status=503)

    if resultado in {"datos_incorrectos", "requiere_revision"}:
        logger.warning("Revisar pago de la compra %s: %s", compra.pk, resultado)

    return HttpResponse(resultado, status=200)