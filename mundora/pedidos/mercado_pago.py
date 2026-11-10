import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.urls import reverse

from .models import Compra


def crear_orden_de_prueba(compra):
    """Crea una orden de Checkout Pro para una compra pendiente de MUNDORA."""
    if compra.estado != Compra.Estado.PENDIENTE:
        raise ValueError("Solo se puede iniciar el pago de una compra pendiente.")

    total = compra.total_con_entrega
    if total is None or total <= 0:
        raise ValueError("La compra no tiene un total válido con entrega.")

    token = settings.MP_ACCESS_TOKEN_PRUEBA.strip()
    if not token:
        raise ValueError("Falta el Access Token de prueba de Mercado Pago.")

    importe = f"{total:.2f}"
    codigo = str(compra.codigo)

    # El comprador vuelve al detalle protegido de la misma compra.
    dominio = settings.NGROK_HOST
    if not dominio:
        raise ValueError("Falta NGROK_HOST para configurar el retorno.")
    ruta = reverse("pedidos:detalle", kwargs={"codigo": compra.codigo})
    retorno = f"https://{dominio}{ruta}"

    # En esta primera prueba enviamos la compra completa como un único ítem.
    datos = {
        "type": "online",
        "processing_mode": "manual",
        "external_reference": codigo,
        "total_amount": importe,
        "config": {
            "online": {
                "success_url": retorno,
                "failure_url": retorno,
                "pending_url": retorno,
                "auto_return": "all",
            }
        },
        "items": [
            {
                "title": f"Compra MUNDORA #{compra.pk} con entrega incluida",
                "quantity": 1,
                "unit_price": importe,
            }
        ],
    }

    solicitud = Request(
        "https://api.mercadopago.com/v1/orders",
        data=json.dumps(datos).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            # Repetir esta prueba para la misma compra usa la misma clave.
            "X-Idempotency-Key": codigo,
        },
        method="POST",
    )

    try:
        with urlopen(solicitud, timeout=15) as respuesta:
            return json.load(respuesta)
    except HTTPError as error:
        detalle = error.read().decode("utf-8", errors="replace")
        raise ValueError(f"Mercado Pago respondió HTTP {error.code}: {detalle}") from error
    except (URLError, TimeoutError) as error:
        raise ConnectionError("No se pudo conectar con Mercado Pago.") from error

def consultar_orden(compra):
    """Consulta en Mercado Pago la orden guardada en esta compra."""
    if not compra.mp_orden_id:
        raise ValueError("La compra todavía no tiene una orden de Mercado Pago.")

    token = settings.MP_ACCESS_TOKEN_PRUEBA.strip()
    if not token:
        raise ValueError("Falta el Access Token de prueba de Mercado Pago.")

    solicitud = Request(
        f"https://api.mercadopago.com/v1/orders/{compra.mp_orden_id}",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )

    try:
        with urlopen(solicitud, timeout=15) as respuesta:
            return json.load(respuesta)
    except HTTPError as error:
        raise ValueError(
            f"Mercado Pago no pudo consultar la orden (HTTP {error.code})."
        ) from error
    except (URLError, TimeoutError) as error:
        raise ConnectionError("No se pudo conectar con Mercado Pago.") from error