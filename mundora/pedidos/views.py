import uuid
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core import signing
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST,require_http_methods
from django.http import Http404
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone

from accounts.models import DomicilioEntrega
from carrito.models import ItemCarrito
from carrito.views import motivo_no_disponible
from catalog.views_publicas import productos_visibles


from .models import Compra, Pedido
from .services import crear_compra_pendiente, huella_revision, procesar_pago_simulado, cancelar_compra_pendiente, cancelar_pedido_pagado, solicitar_devolucion_pedido
from .forms import FormularioSolicitudDevolucion


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
@require_POST
def pagar_compra(request, codigo):
    """Procesa una simulación de pago para una compra propia."""

    if not request.user.is_authenticated:
        return redirect_to_login(
            reverse("pedidos:detalle", kwargs={"codigo": codigo}),
            login_url=reverse("accounts:iniciar_sesion"),
        )

    try:
        compra, procesada = procesar_pago_simulado(
            request.user,
            codigo,
            request.POST.get("resultado", ""),
        )
    except Compra.DoesNotExist:
        raise Http404("No se encontró la compra.")
    except ValidationError as error:
        for mensaje in error.messages:
            messages.error(request, mensaje)

        return redirect("pedidos:detalle", codigo=codigo)

    if not procesada:
        messages.info(
            request,
            "Esta compra ya no está pendiente. "
            "No se realizó ninguna operación adicional.",
        )
    elif compra.estado == Compra.Estado.CONFIRMADA:
        messages.success(
            request,
            "Pago simulado aprobado. Tu compra está confirmada "
            "y sus pedidos están en preparación.",
        )
    else:
        messages.error(request, compra.motivo_rechazo)

    return redirect("pedidos:detalle", codigo=compra.codigo)

@login_required
@require_GET
def mis_compras(request):
    """Lista únicamente las compras del usuario autenticado."""

    compras = (
        Compra.objects.filter(comprador=request.user)
        .prefetch_related("pedidos__detalles")
        .order_by("-fecha_creacion", "-pk")
    )

    paginador = Paginator(compras, 10)
    pagina = paginador.get_page(request.GET.get("pagina"))

    return render(
        request,
        "pedidos/mis_compras.html",
        {"pagina": pagina},
    )
@require_POST
@login_required
@transaction.atomic
def confirmar_recepcion(request, pedido_id):
    """Permite al comprador confirmar una sola vez la recepción."""

    # Busca únicamente pedidos de compras confirmadas del usuario.
    pedidos_propios = (
        Pedido.objects.select_for_update()
        .select_related("compra")
        .filter(
            compra__comprador=request.user,
            compra__estado=Compra.Estado.CONFIRMADA,
        )
    )

    pedido = get_object_or_404(
        pedidos_propios,
        pk=pedido_id,
    )

    # Conserva la fecha original si se repite la solicitud.
    if pedido.estado == Pedido.Estado.ENTREGADO:
        messages.info(
            request,
            "Ya habías confirmado la recepción de este pedido.",
        )

    elif pedido.estado != Pedido.Estado.ENVIADO:
        messages.error(
            request,
            "Solo podés confirmar la recepción de un pedido enviado.",
        )

    else:
        pedido.estado = Pedido.Estado.ENTREGADO
        pedido.fecha_entrega = timezone.now()

        pedido.save(
            update_fields=[
                "estado",
                "fecha_entrega",
                "fecha_actualizacion",
            ],
        )

        messages.success(
            request,
            f"Confirmaste la recepción del pedido {pedido.pk}.",
        )

    return redirect(
        "pedidos:detalle",
        codigo=pedido.compra.codigo,
    )

@require_POST
@login_required
def cancelar_compra(request, codigo):
    """Recibe la cancelación de una compra pendiente del usuario."""

    try:
        compra, cancelada = cancelar_compra_pendiente(
            request.user,
            codigo,
        )
    except Compra.DoesNotExist:
        raise Http404("No se encontró la compra.")
    except ValidationError as error:
        for mensaje in error.messages:
            messages.error(request, mensaje)

        return redirect("pedidos:detalle", codigo=codigo)

    if cancelada:
        messages.success(
            request,
            "Cancelaste la compra pendiente. "
            "Los artículos permanecen en tu carrito.",
        )
    else:
        messages.info(
            request,
            "Esta compra ya estaba cancelada. No se realizaron cambios.",
        )

    return redirect(
        "pedidos:detalle",
        codigo=compra.codigo,
    )
@require_POST
@login_required
def cancelar_pedido(request, pedido_id):
    """Recibe la cancelación de un pedido pagado del comprador."""

    # Obtiene una dirección de regreso sin permitir consultar pedidos ajenos.
    pedido_propio = get_object_or_404(
        Pedido.objects.select_related("compra"),
        pk=pedido_id,
        compra__comprador=request.user,
        compra__estado=Compra.Estado.CONFIRMADA,
    )

    try:
        pedido, cancelado = cancelar_pedido_pagado(
            request.user,
            pedido_id,
        )
    except Pedido.DoesNotExist:
        raise Http404("No se encontró el pedido.")
    except ValidationError as error:
        for mensaje in error.messages:
            messages.error(request, mensaje)

        return redirect(
            "pedidos:detalle",
            codigo=pedido_propio.compra.codigo,
        )

    if cancelado:
        messages.success(
            request,
            "Pedido cancelado. Se repusieron sus unidades "
            "y se registró el reembolso simulado.",
        )
    else:
        messages.info(
            request,
            "Este pedido ya estaba cancelado y reembolsado. "
            "No se realizaron cambios.",
        )

    return redirect(
        "pedidos:detalle",
        codigo=pedido.compra.codigo,
    )
@login_required
@require_http_methods(["GET", "POST"])
def solicitar_devolucion(request, pedido_id):
    """Muestra y procesa la solicitud de devolución del comprador."""

    pedido = get_object_or_404(
        Pedido.objects.select_related("compra"),
        pk=pedido_id,
        compra__comprador=request.user,
        compra__estado=Compra.Estado.CONFIRMADA,
    )

    if pedido.estado_devolucion != Pedido.EstadoDevolucion.SIN_SOLICITUD:
        messages.info(
            request,
            "Este pedido ya tiene una solicitud de devolución registrada.",
        )
        return redirect("pedidos:detalle", codigo=pedido.compra.codigo)

    if pedido.estado not in {
        Pedido.Estado.ENVIADO,
        Pedido.Estado.ENTREGADO,
    }:
        messages.error(
            request,
            "Solo podés solicitar devoluciones de pedidos enviados "
            "o entregados.",
        )
        return redirect("pedidos:detalle", codigo=pedido.compra.codigo)

    if request.method == "POST":
        formulario = FormularioSolicitudDevolucion(request.POST)

        if formulario.is_valid():
            try:
                pedido, creada = solicitar_devolucion_pedido(
                    request.user,
                    pedido.pk,
                    formulario.cleaned_data["motivo"],
                )
            except Pedido.DoesNotExist:
                raise Http404("No se encontró el pedido.")
            except ValidationError as error:
                formulario.add_error(None, error)
            else:
                if creada:
                    messages.success(
                        request,
                        "Solicitud registrada. La tienda debe revisarla. "
                        "Todavía no se realizó ningún reembolso.",
                    )
                else:
                    messages.info(
                        request,
                        "La solicitud ya estaba registrada. "
                        "No se realizaron cambios.",
                    )

                return redirect(
                    "pedidos:detalle",
                    codigo=pedido.compra.codigo,
                )
    else:
        formulario = FormularioSolicitudDevolucion()

    return render(
        request,
        "pedidos/solicitar_devolucion.html",
        {
            "pedido": pedido,
            "formulario": formulario,
        },
    )