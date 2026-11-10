"""Ejecutar desde manage.py shell. Solo lee el aviso local; no procesa pagos."""
import hashlib
import hmac
import json
from urllib.parse import parse_qs, urlsplit
from urllib.request import urlopen
from importlib.metadata import version

from django.conf import settings


def diagnosticar():
    objetivo = "ORDTST01M6HR58EVSJX3PN4QCK5HSFZ6"
    try:
        with urlopen("http://127.0.0.1:4040/api/requests/http?limit=100", timeout=5) as respuesta:
            avisos = json.load(respuesta)["requests"]
    except OSError:
        print("No se pudo abrir el inspector local de ngrok.")
        return

    for aviso in sorted(avisos, key=lambda a: a.get("start", ""), reverse=True):
        req = aviso["request"]
        url = urlsplit(req["uri"])
        identificador = parse_qs(url.query).get("data.id", [""])[0]
        if (req.get("method") != "POST" or url.path != "/compras/mercado-pago/webhook/"
                or identificador.upper() != objetivo or aviso.get("response", {}).get("status_code") != 401):
            continue
        headers = {k.lower(): (v[0] if isinstance(v, list) else v) for k, v in req["headers"].items()}
        clave = settings.MP_WEBHOOK_SECRETO_PRUEBA.strip()
        firma = headers.get("x-signature", "")
        rid = headers.get("x-request-id", "")
        partes = dict(x.strip().split("=", 1) for x in firma.split(",") if "=" in x)
        ts, v1 = partes.get("ts"), partes.get("v1")
        if not all((clave, rid, ts, v1)):
            print("La captura no contiene todos los campos de firma necesarios.")
            return
        print("SDK:", version("mercadopago"))
        for nombre, valor in (("original", identificador), ("minusculas", identificador.lower())):
            mensaje = f"id:{valor};request-id:{rid};ts:{ts};"
            calculada = hmac.new(clave.encode(), mensaje.encode(), hashlib.sha256).hexdigest()
            print("HMAC con ID", nombre, ":", hmac.compare_digest(calculada, v1))
        return
    print("No se encontro el POST 401 de esa orden en el historial actual de ngrok.")


diagnosticar()
