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
from .cotizador import cotizar_entrega
from .mercado_pago import crear_orden_de_prueba, consultar_orden

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

    # Muestra una sola opción de entrega por tienda del carrito.
    tiendas_por_id = {
        item.variante.producto.tienda_id: item.variante.producto.tienda
        for item in items
    }

    tiendas = sorted(
        tiendas_por_id.values(),
        key=lambda tienda: tienda.pk,
    )

        # Calcula una cotización por tienda para mostrarla en la revisión.
    for tienda in tiendas:
        tienda.costo_envio_estimado = None

        if domicilio is not None:
            try:
                tienda.costo_envio_estimado = cotizar_entrega(
                    tienda,
                    domicilio,
                    es_retiro=False,
                )
            except ValueError:
                # La plantilla avisa si faltan datos para cotizar.
                pass


    return render(
        request,
        "pedidos/revisar_compra.html",
        {
            "items": items,
            "domicilio": domicilio,
            "errores": errores,
            "total_productos": total_productos,
            "token_revision": token_revision,
            "tiendas": tiendas,
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
        # Recoge las elecciones y rechaza campos enviados más de una vez.
        modalidades = {}

        for nombre in request.POST:
            if not nombre.startswith("entrega_"):
                continue

            valores = request.POST.getlist(nombre)

            if len(valores) != 1:
                raise ValidationError(
                    "Se recibió más de una modalidad para una tienda."
                )

            tienda_id = nombre.removeprefix("entrega_")
            modalidades[tienda_id] = valores[0]

        compra, creada = crear_compra_pendiente(
            request.user,
            codigo,
            huella,
            modalidades,
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

@login_required
@require_POST
def pagar_compra(request, codigo):
    """Abre el checkout de Mercado Pago de una compra propia y pendiente."""
    try:
        with transaction.atomic():
            # Evita que dos clics simultáneos creen dos órdenes locales.
            compra = get_object_or_404(
                Compra.objects.select_for_update(),
                codigo=codigo,
                comprador=request.user,
            )

            if compra.estado != Compra.Estado.PENDIENTE:
                messages.info(request, "Esta compra ya no está pendiente de pago.")
                return redirect("pedidos:detalle", codigo=codigo)

            if not compra.mp_checkout_url:
                orden = crear_orden_de_prueba(compra)
                orden_id = orden.get("id")
                enlace = orden.get("checkout_url")

                if not orden_id or not enlace:
                    raise ValueError("La respuesta de Mercado Pago está incompleta.")

                compra.mp_orden_id = orden_id
                compra.mp_checkout_url = enlace
                compra.save(update_fields=["mp_orden_id", "mp_checkout_url"])

            enlace = compra.mp_checkout_url

    except (ValueError, ConnectionError):
        messages.error(
            request,
            "No pudimos abrir Mercado Pago. Tu compra sigue pendiente. "
            "Volvé a intentarlo.",
        )
        return redirect("pedidos:detalle", codigo=codigo)

    return redirect(enlace)

@login_required
@require_POST
def verificar_pago(request, codigo):
    """Verifica el pago de una compra propia antes de descontar stock."""
    compra = get_object_or_404(Compra, comprador=request.user, codigo=codigo)
    destino = redirect("pedidos:detalle", codigo=codigo)

    if compra.estado != Compra.Estado.PENDIENTE:
        messages.info(request, "Esta compra ya fue procesada.")
        return destino

    try:
        orden = consultar_orden(compra)
    except (ValueError, ConnectionError):
        messages.error(request, "No pudimos consultar el pago. Intentá nuevamente.")
        return destino

    if (
        orden.get("id") != compra.mp_orden_id
        or orden.get("external_reference") != str(compra.codigo)
    ):
        messages.error(request, "La orden recibida no corresponde a esta compra.")
        return destino

    if (orden.get("status"), orden.get("status_detail")) != ("processed", "accredited"):
        messages.info(request, "Mercado Pago todavía no informa un pago acreditado.")
        return destino

    # Compara el dinero acreditado con el total de productos y entrega.
    from decimal import InvalidOperation

    try:
        pagado = Decimal(str(orden.get("total_paid_amount")))
        importe_orden = Decimal(str(orden.get("total_amount")))
    except InvalidOperation:
        messages.error(request, "No se pudo verificar el importe del pago.")
        return destino

    if (
        orden.get("currency") != "ARS"
        or not pagado.is_finite()
        or not importe_orden.is_finite()
        or pagado != compra.total_con_entrega
        or importe_orden != pagado
    ):
        messages.error(request, "La moneda o el importe no coincide. Revisá la operación.")
        return destino

    with transaction.atomic():
        # El servicio vuelve a comprobar el stock y evita descontarlo dos veces.
        compra, modificada = procesar_pago_simulado(request.user, codigo, "aprobado")

        if modificada and compra.estado == Compra.Estado.RECHAZADA:
            # La compra no se pudo preparar, pero el pago sí fue acreditado.
            compra.motivo_rechazo = (
                "Pago acreditado en Mercado Pago. Requiere revisión y eventual "
                f"reembolso. {compra.motivo_rechazo}"
            )[:250]
            compra.save(update_fields=["motivo_rechazo"])

    if compra.estado == Compra.Estado.CONFIRMADA:
        messages.success(request, "Pago acreditado. Tu compra está confirmada.")
    else:
        messages.warning(
            request,
            "El pago fue acreditado, pero la compra no pudo confirmarse. "
            "La operación requiere revisión.",
        )

    return destino 

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
    elif not (
        (
            pedido.modalidad_entrega == Pedido.ModalidadEntrega.ENVIO
            and pedido.estado == Pedido.Estado.ENVIADO
        )
        or (
            pedido.modalidad_entrega == Pedido.ModalidadEntrega.RETIRO
            and pedido.estado == Pedido.Estado.LISTO_RETIRO
        )
    ):
        messages.error(
            request,
            "Solo podés confirmar un envío despachado "
            "o un retiro que la tienda haya marcado como listo.",
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