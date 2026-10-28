import uuid
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core import signing
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from accounts.models import DomicilioEntrega
from carrito.models import ItemCarrito
from carrito.views import motivo_no_disponible
from catalog.views_publicas import productos_visibles

from .models import Compra
from .services import crear_compra_pendiente, huella_revision


@login_required
@require_GET
def revisar_compra(request):
    """Muestra el domicilio y los productos antes de confirmar la compra."""

    # Solo consulta los productos del carrito del usuario autenticado.
    items = list(
        ItemCarrito.objects.filter(
            carrito__usuario=request.user,
        ).select_related(
            "variante__producto__tienda",
        )
    )

    domicilio = DomicilioEntrega.objects.filter(
        usuario=request.user,
    ).first()

    errores = []

    if not items:
        errores.append("Tu carrito está vacío.")

    if domicilio is None:
        errores.append(
            "Completá tu domicilio de entrega antes de continuar.",
        )

    # Reutiliza las reglas de visibilidad del catálogo.
    ids_productos = {
        item.variante.producto_id
        for item in items
    }

    ids_visibles = set(
        productos_visibles()
        .filter(pk__in=ids_productos)
        .values_list("pk", flat=True)
    )

    # Comprueba todas las selecciones; no omite productos silenciosamente.
    for item in items:
        variante = item.variante

        motivo = motivo_no_disponible(
            variante,
            variante.producto_id in ids_visibles,
            item.cantidad,
        )

        if motivo:
            errores.append(f"{variante}: {motivo}")

    # Los importes siempre se obtienen de los datos del servidor.
    total_productos = sum(
        (item.subtotal for item in items),
        Decimal("0.00"),
    )

        # Firma la revisión para detectar alteraciones y reconocer reenvíos.
    token_revision = ""

    if not errores:
        token_revision = signing.dumps(
            {
                "usuario": request.user.pk,
                "codigo": str(uuid.uuid4()),
                "huella": huella_revision(items, domicilio),
            },
            salt="pedidos.revision",
        )

    return render(
        request,
        "pedidos/revisar_compra.html",
        {
            "items": items,
            "domicilio": domicilio,
            "errores": errores,
            "total_productos": total_productos,
            "token_revision": token_revision,
        },
    )

@require_POST
def crear_compra(request):
    """Recibe una revisión válida y genera la compra pendiente."""

    if not request.user.is_authenticated:
        return redirect_to_login(
            reverse("pedidos:revisar"),
            login_url=reverse("accounts:iniciar_sesion"),
        )

    try:
        datos = signing.loads(
            request.POST.get("token_revision", ""),
            salt="pedidos.revision",
            max_age=3600,
        )

        if datos["usuario"] != request.user.pk:
            raise signing.BadSignature()

        codigo = uuid.UUID(datos["codigo"])
        huella = datos["huella"]

    except (
        signing.BadSignature,
        KeyError,
        TypeError,
        ValueError,
    ):
        messages.error(
            request,
            "La revisión venció o no es válida. Revisá nuevamente tu compra.",
        )
        return redirect("pedidos:revisar")

    try:
        compra, creada = crear_compra_pendiente(
            request.user,
            codigo,
            huella,
        )
    except ValidationError as error:
        for mensaje in error.messages:
            messages.error(request, mensaje)

        return redirect("pedidos:revisar")

    if creada:
        messages.success(
            request,
            "Tu compra quedó pendiente de pago. Todavía no se realizó ningún cargo.",
        )
    else:
        messages.info(
            request,
            "Esta solicitud ya había sido registrada. Mostramos la misma compra.",
        )

    return redirect(
        "pedidos:detalle",
        codigo=compra.codigo,
    )


@login_required
@require_GET
def detalle_compra(request, codigo):
    """Muestra una compra que pertenece al usuario autenticado."""

    compra = get_object_or_404(
        Compra.objects.prefetch_related(
            "pedidos__detalles",
        ),
        codigo=codigo,
        comprador=request.user,
    )

    return render(
        request,
        "pedidos/detalle_compra.html",
        {"compra": compra},
    )