import re
from decimal import Decimal
from unicodedata import normalize


# Tarifas simuladas de MUNDORA, expresadas en pesos argentinos.
RETIRO_EN_TIENDA = Decimal("0.00")
ENVIO_LOCAL = Decimal("3000.00")
ENVIO_PROVINCIAL = Decimal("5500.00")
ENVIO_NACIONAL = Decimal("8500.00")


def _normalizar_provincia(valor):
    """Compara provincias sin distinguir tildes, espacios ni mayúsculas."""
    texto = normalize("NFD", " ".join((valor or "").split()).casefold())
    return "".join(letra for letra in texto if not 0x0300 <= ord(letra) <= 0x036F)


def _codigo_postal_base(valor):
    """Extrae los cuatro dígitos de un código postal argentino o CPA."""
    texto = "".join(str(valor or "").upper().split())
    coincidencia = re.fullmatch(r"(?:[A-Z]([0-9]{4})[A-Z]{3}|([0-9]{4}))", texto)
    if not coincidencia:
        raise ValueError("Ingresá un código postal válido, por ejemplo 5600 o M5600ABC.")
    return coincidencia.group(1) or coincidencia.group(2)


def cotizar_entrega(tienda, domicilio, *, es_retiro):
    """Calcula el costo de entrega de un pedido de una sola tienda."""
    if es_retiro:
        return RETIRO_EN_TIENDA

    provincia_origen = _normalizar_provincia(tienda.provincia)
    provincia_destino = _normalizar_provincia(domicilio.provincia)

    if not provincia_origen or not provincia_destino:
        raise ValueError("Falta la provincia de origen o de destino.")

    cp_origen = _codigo_postal_base(tienda.codigo_postal)
    cp_destino = _codigo_postal_base(domicilio.codigo_postal)

    if provincia_origen != provincia_destino:
        return ENVIO_NACIONAL
    if cp_origen == cp_destino:
        return ENVIO_LOCAL
    return ENVIO_PROVINCIAL