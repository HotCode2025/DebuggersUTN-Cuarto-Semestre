from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.core.paginator import Paginator
from pedidos.models import Compra, Pedido
from django.utils import timezone
from pedidos.forms import FormularioDespacho, FormularioRespuestaDevolucion, FormularioRecepcionDevolucion
from .forms_vendedor import (FormularioProductoVendedor, FormularioVariantesVendedor, FormularioGaleriaVendedor)
from .models import Producto, Tienda
from django.core.exceptions import ValidationError
from django.http import Http404

from pedidos.services import completar_devolucion_pedido

@login_required
@require_GET
def panel_vendedor(request):
    """Muestra la tienda y los productos del usuario autenticado."""

    tienda = Tienda.objects.filter(
        propietario=request.user,
    ).first()

    productos = Producto.objects.none()

    if tienda is not None:
        productos = Producto.objects.filter(
            tienda=tienda,
        ).select_related("categoria")

    return render(
        request,
        "catalog/vendedor/panel.html",
        {
            "tienda": tienda,
            "productos": productos,
        },
    )


@login_required
@require_GET
def detalle_producto_vendedor(request, producto_id):
    """Muestra una publicación privada únicamente a su propietario."""

    productos_propios = Producto.objects.filter(
        tienda__propietario=request.user,
    ).select_related(
        "tienda",
        "categoria",
    ).prefetch_related(
        "variantes",
        "imagenes",
    )

    producto = get_object_or_404(
        productos_propios,
        pk=producto_id,
    )

    return render(
        request,
        "catalog/vendedor/detalle_producto.html",
        {"producto": producto},
    )
@login_required
@require_http_methods(["GET", "POST"])
def crear_producto_vendedor(request):
    """Crea un borrador asociado a la tienda del usuario."""

    tienda = get_object_or_404(
        Tienda,
        propietario=request.user,
    )

    # La tienda y los estados los determina el servidor.
    producto = Producto(
        tienda=tienda,
        publicado=False,
        estado_revision=Producto.EstadoRevision.PENDIENTE,
    )

    if request.method == "POST":
        formulario = FormularioProductoVendedor(
            request.POST,
            instance=producto,
        )

        if formulario.is_valid():
            producto = formulario.save()

            messages.success(
                request,
                "El producto se creó como borrador.",
            )

            return redirect(
                "vendedores:detalle_producto",
                producto_id=producto.pk,
            )
    else:
        formulario = FormularioProductoVendedor(
            instance=producto,
        )

    return render(
        request,
        "catalog/vendedor/formulario_producto.html",
        {
            "formulario": formulario,
            "producto": producto,
            "es_nuevo": True,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def editar_producto_vendedor(request, producto_id):
    """Edita un producto propio y actualiza su estado de revisión."""

    productos_propios = Producto.objects.filter(
        tienda__propietario=request.user,
    )

    # Evita guardar sobre una revisión que cambie durante este guardado.
    if request.method == "POST":
        productos_propios = productos_propios.select_for_update()

    producto = get_object_or_404(
        productos_propios,
        pk=producto_id,
    )

    if request.method == "POST":
        formulario = FormularioProductoVendedor(
            request.POST,
            instance=producto,
        )

        if formulario.is_valid():
            if formulario.has_changed():
                producto = formulario.save(commit=False)

                # Los cambios generales requieren revisar la publicación.
                if (
                    producto.estado_revision
                    == Producto.EstadoRevision.APROBADO
                ):
                    producto.estado_revision = (
                        Producto.EstadoRevision.PENDIENTE
                    )

                    mensaje = (
                        "Los cambios se guardaron. "
                        "La publicación volvió a estar en revisión."
                    )

                elif (
                    producto.estado_revision
                    == Producto.EstadoRevision.RECHAZADO
                ):
                    # Corregir no reactiva una publicación rechazada.
                    producto.publicado = False

                    mensaje = (
                        "Las correcciones se guardaron. "
                        "La publicación continúa rechazada."
                    )

                else:
                    mensaje = "Los cambios se guardaron correctamente."

                producto.save()
                messages.success(request, mensaje)

            else:
                messages.info(
                    request,
                    "No realizaste cambios en el producto.",
                )

            return redirect(
                "vendedores:detalle_producto",
                producto_id=producto.pk,
            )
    else:
        formulario = FormularioProductoVendedor(
            instance=producto,
        )

    return render(
        request,
        "catalog/vendedor/formulario_producto.html",
        {
            "formulario": formulario,
            "producto": producto,
            "es_nuevo": False,
        },
    )

@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def gestionar_variantes_vendedor(request, producto_id):
    """Permite administrar las variantes de un producto propio."""

    productos_propios = Producto.objects.filter(
        tienda__propietario=request.user,
    )

    # Bloquea el producto mientras se procesan los cambios.
    if request.method == "POST":
        productos_propios = productos_propios.select_for_update()

    producto = get_object_or_404(
        productos_propios,
        pk=producto_id,
    )

    if request.method == "POST":
        conjunto = FormularioVariantesVendedor(
            request.POST,
            request.FILES,
            instance=producto,
            prefix="variantes",
        )

        if conjunto.is_valid():
            # Estos cambios requieren una nueva revisión del contenido.
            campos_revisables = {
                "color",
                "medidas",
                "material",
                "imagen",
            }

            hay_cambios = False
            requiere_revision = False

            for formulario in conjunto.forms:
                datos = formulario.cleaned_data

                # Descartar una fila nueva no modifica el producto.
                if datos.get("DELETE"):
                    if formulario.instance.pk:
                        hay_cambios = True
                        requiere_revision = True
                    continue

                if not formulario.has_changed():
                    continue

                hay_cambios = True

                # Una variante nueva también necesita revisión.
                if not formulario.instance.pk:
                    requiere_revision = True

                elif campos_revisables.intersection(
                    formulario.changed_data
                ):
                    requiere_revision = True

            if hay_cambios:
                try:
                    # Revierte todos los cambios de variantes si fallan.
                    with transaction.atomic():
                        conjunto.save()

                except IntegrityError as error:
                    es_combinacion_duplicada = (
                        error.args
                        and error.args[0] == 1062
                        and "variante_combinacion_unica" in str(error)
                    )

                    # Otros errores requieren su propio diagnóstico.
                    if not es_combinacion_duplicada:
                        raise

                    messages.error(
                        request,
                        "No se guardaron los cambios: una combinación "
                        "de color, medidas y material ya existe. "
                        "Abrí nuevamente Administrar variantes "
                        "y revisá los datos actuales.",
                    )

                    return redirect(
                        "vendedores:detalle_producto",
                        producto_id=producto.pk,
                    )

                if (
                    requiere_revision
                    and producto.estado_revision
                    == Producto.EstadoRevision.APROBADO
                ):
                    producto.estado_revision = (
                        Producto.EstadoRevision.PENDIENTE
                    )

                    mensaje = (
                        "Variantes guardadas. "
                        "El producto volvió a estar en revisión."
                    )

                elif (
                    producto.estado_revision
                    == Producto.EstadoRevision.RECHAZADO
                ):
                    # Corregir variantes no reactiva una publicación.
                    producto.publicado = False

                    mensaje = (
                        "Variantes guardadas. El producto sigue "
                        "rechazado hasta solicitar una nueva revisión."
                    )

                else:
                    mensaje = "Variantes guardadas correctamente."

                producto.save(
                    update_fields=[
                        "estado_revision",
                        "publicado",
                        "fecha_actualizacion",
                    ],
                )

                messages.success(request, mensaje)

            else:
                messages.info(
                    request,
                    "No realizaste cambios en las variantes.",
                )

            return redirect(
                "vendedores:detalle_producto",
                producto_id=producto.pk,
            )

    else:
        conjunto = FormularioVariantesVendedor(
            instance=producto,
            prefix="variantes",
        )

    return render(
        request,
        "catalog/vendedor/variantes.html",
        {
            "producto": producto,
            "conjunto": conjunto,
        },
    )

@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def gestionar_galeria_vendedor(request, producto_id):
    """Permite administrar las imágenes de un producto propio."""

    productos_propios = Producto.objects.filter(
        tienda__propietario=request.user,
    )

    # Bloquea el producto durante el guardado.
    if request.method == "POST":
        productos_propios = productos_propios.select_for_update()

    producto = get_object_or_404(
        productos_propios,
        pk=producto_id,
    )

    if request.method == "POST":
        conjunto = FormularioGaleriaVendedor(
            request.POST,
            request.FILES,
            instance=producto,
            prefix="galeria",
        )

        if conjunto.is_valid():
            hay_cambios = False

            for formulario in conjunto.forms:
                datos = formulario.cleaned_data

                # Descartar una fila nueva no cambia la galería.
                if datos.get("DELETE"):
                    if formulario.instance.pk:
                        hay_cambios = True
                    continue

                if formulario.has_changed():
                    hay_cambios = True

            if hay_cambios:
                conjunto.save()

                # Los cambios en la galería requieren revisión.
                if (
                    producto.estado_revision
                    == Producto.EstadoRevision.APROBADO
                ):
                    producto.estado_revision = (
                        Producto.EstadoRevision.PENDIENTE
                    )

                    mensaje = (
                        "Galería guardada. "
                        "El producto volvió a estar en revisión."
                    )

                elif (
                    producto.estado_revision
                    == Producto.EstadoRevision.RECHAZADO
                ):
                    # Editar la galería no reactiva el producto.
                    producto.publicado = False

                    mensaje = (
                        "Galería guardada. El producto continúa "
                        "rechazado hasta solicitar una nueva revisión."
                    )

                else:
                    mensaje = "Galería guardada correctamente."

                producto.save(
                    update_fields=[
                        "estado_revision",
                        "publicado",
                        "fecha_actualizacion",
                    ],
                )

                messages.success(request, mensaje)

            else:
                messages.info(
                    request,
                    "No realizaste cambios en la galería.",
                )

            return redirect(
                "vendedores:detalle_producto",
                producto_id=producto.pk,
            )

    else:
        conjunto = FormularioGaleriaVendedor(
            instance=producto,
            prefix="galeria",
        )

    return render(
        request,
        "catalog/vendedor/galeria.html",
        {
            "producto": producto,
            "conjunto": conjunto,
        },
    )

@login_required
@require_POST
@transaction.atomic
def cambiar_publicacion_vendedor(request, producto_id):
    """Publica, pausa o solicita revisar un producto propio."""

    # Busca y bloquea únicamente un producto del vendedor.
    productos_propios = Producto.objects.select_for_update().filter(
        tienda__propietario=request.user,
    )

    producto = get_object_or_404(
        productos_propios,
        pk=producto_id,
    )

    accion = request.POST.get("accion")

    acciones_permitidas = {
        "publicar",
        "pausar",
        "solicitar_revision",
    }

    if accion not in acciones_permitidas:
        messages.error(request, "La acción solicitada no es válida.")

        return redirect(
            "vendedores:detalle_producto",
            producto_id=producto.pk,
        )

    # Pausar siempre está permitido para el propietario.
    if accion == "pausar":
        if producto.publicado:
            producto.publicado = False

            producto.save(
                update_fields=["publicado", "fecha_actualizacion"],
            )

            messages.success(request, "La publicación quedó pausada.")
        else:
            messages.info(request, "El producto ya estaba sin publicar.")

        return redirect(
            "vendedores:detalle_producto",
            producto_id=producto.pk,
        )

    # Un rechazo requiere una solicitud explícita de revisión.
    if (
        accion == "publicar"
        and producto.estado_revision
        == Producto.EstadoRevision.RECHAZADO
    ):
        messages.error(
            request,
            "El producto está rechazado. Corregí las observaciones "
            "y utilizá «Solicitar nueva revisión».",
        )

        return redirect(
            "vendedores:detalle_producto",
            producto_id=producto.pk,
        )

    if (
        accion == "solicitar_revision"
        and producto.estado_revision
        != Producto.EstadoRevision.RECHAZADO
    ):
        messages.info(
            request,
            "Solo los productos rechazados necesitan "
            "solicitar una nueva revisión.",
        )

        return redirect(
            "vendedores:detalle_producto",
            producto_id=producto.pk,
        )

    # Comprueba los requisitos antes de habilitar la publicación.
    errores = []

    if producto.tienda.estado != Tienda.Estado.APROBADA:
        errores.append(
            "La tienda debe estar aprobada para publicar productos."
        )

    if not producto.categoria.activa:
        errores.append(
            "La categoría del producto debe estar habilitada."
        )

    if not producto.variantes.filter(activa=True).exists():
        errores.append(
            "El producto debe tener al menos una variante activa."
        )

    if not producto.imagenes.exclude(imagen="").exists():
        errores.append(
            "El producto debe tener al menos una imagen en la galería."
        )

    if errores:
        for error in errores:
            messages.error(request, error)

        return redirect(
            "vendedores:detalle_producto",
            producto_id=producto.pk,
        )

    if accion == "solicitar_revision":
        # La nueva solicitud reactiva provisionalmente el producto.
        producto.estado_revision = Producto.EstadoRevision.PENDIENTE
        producto.publicado = True

        producto.save(
            update_fields=[
                "estado_revision",
                "publicado",
                "fecha_actualizacion",
            ],
        )

        messages.success(
            request,
            "Solicitaste una nueva revisión. La publicación quedó "
            "activa provisionalmente y todavía no está verificada.",
        )

    elif producto.publicado:
        messages.info(request, "El producto ya estaba publicado.")

    else:
        # Publicar conserva el estado de revisión existente.
        producto.publicado = True

        producto.save(
            update_fields=["publicado", "fecha_actualizacion"],
        )

        if (
            producto.estado_revision
            == Producto.EstadoRevision.PENDIENTE
        ):
            messages.success(
                request,
                "Producto publicado. Está en revisión "
                "y todavía no está verificado.",
            )
        else:
            messages.success(request, "Producto publicado.")

    return redirect(
        "vendedores:detalle_producto",
        producto_id=producto.pk,
    )
@login_required
@require_GET
def pedidos_vendedor(request):
    """Lista los pedidos confirmados de la tienda del usuario."""

    tienda = get_object_or_404(
        Tienda,
        propietario=request.user,
    )

    pedidos = (
        Pedido.objects.filter(
            tienda=tienda,
            compra__estado=Compra.Estado.CONFIRMADA,
        )
        .select_related("compra")
        .prefetch_related("detalles")
        .order_by("-fecha_creacion", "-pk")
    )

    paginador = Paginator(pedidos, 10)
    pagina = paginador.get_page(request.GET.get("pagina"))

    return render(
        request,
        "catalog/vendedor/pedidos.html",
        {
            "tienda": tienda,
            "pagina": pagina,
        },
    )


@login_required
@require_GET
def detalle_pedido_vendedor(request, pedido_id):
    """Muestra los artículos y la entrega de un pedido propio."""

    pedidos_propios = (
        Pedido.objects.filter(
            tienda__propietario=request.user,
            compra__estado=Compra.Estado.CONFIRMADA,
        )
        .select_related("compra", "tienda")
        .prefetch_related("detalles")
    )

    pedido = get_object_or_404(
        pedidos_propios,
        pk=pedido_id,
    )

    return render(
        request,
        "catalog/vendedor/detalle_pedido.html",
        {"pedido": pedido},
    )

@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def registrar_despacho_vendedor(request, pedido_id):
    """Registra una sola vez el despacho de un pedido propio."""

    pedidos_propios = Pedido.objects.filter(
        tienda__propietario=request.user,
        compra__estado=Compra.Estado.CONFIRMADA,
    ).select_related("compra")

    # Bloquea los registros durante el cambio de estado.
    if request.method == "POST":
        pedidos_propios = pedidos_propios.select_for_update()

    pedido = get_object_or_404(
        pedidos_propios,
        pk=pedido_id,
    )
        # Los retiros no utilizan transporte ni código de seguimiento.
    if pedido.modalidad_entrega != Pedido.ModalidadEntrega.ENVIO:
        messages.error(
            request,
            "Este pedido es para retirar en tienda. "
            "No corresponde registrar un despacho.",
        )
        return redirect(
            "vendedores:detalle_pedido",
            pedido_id=pedido.pk,
        )


    # Impide despachar de nuevo o modificar estados posteriores.
    if pedido.estado != Pedido.Estado.PREPARACION:
        messages.info(
            request,
            "Solo podés despachar pedidos que estén en preparación. "
            "No se realizaron cambios.",
        )
        return redirect(
            "vendedores:detalle_pedido",
            pedido_id=pedido.pk,
        )

    if request.method == "POST":
        formulario = FormularioDespacho(request.POST)

        if formulario.is_valid():
            pedido.empresa_transporte = (
                formulario.cleaned_data["empresa_transporte"]
            )
            pedido.codigo_seguimiento = (
                formulario.cleaned_data["codigo_seguimiento"]
            )
            pedido.fecha_despacho = timezone.now()
            pedido.estado = Pedido.Estado.ENVIADO

            pedido.save(
                update_fields=[
                    "empresa_transporte",
                    "codigo_seguimiento",
                    "fecha_despacho",
                    "estado",
                    "fecha_actualizacion",
                ],
            )

            messages.success(
                request,
                "Despacho registrado. El pedido quedó marcado como enviado.",
            )
            return redirect(
                "vendedores:detalle_pedido",
                pedido_id=pedido.pk,
            )
    else:
        formulario = FormularioDespacho()

    return render(
        request,
        "catalog/vendedor/registrar_despacho.html",
        {
            "pedido": pedido,
            "formulario": formulario,
        },
    )

@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def responder_devolucion_vendedor(request, pedido_id):
    """Permite responder una sola vez una devolución de la tienda propia."""

    pedidos_propios = Pedido.objects.filter(
        tienda__propietario=request.user,
        compra__estado=Compra.Estado.CONFIRMADA,
    ).select_related("compra")

    # Evita que dos respuestas sobrescriban la misma solicitud.
    if request.method == "POST":
        pedidos_propios = pedidos_propios.select_for_update()

    pedido = get_object_or_404(
        pedidos_propios,
        pk=pedido_id,
    )

    if pedido.estado_devolucion != Pedido.EstadoDevolucion.SOLICITADA:
        messages.info(
            request,
            "Este pedido no tiene una solicitud pendiente de respuesta. "
            "No se realizaron cambios.",
        )
        return redirect(
            "vendedores:detalle_pedido",
            pedido_id=pedido.pk,
        )

    # Comprueba que el pedido siga siendo válido para una devolución.
    if (
        pedido.estado not in {
            Pedido.Estado.ENVIADO,
            Pedido.Estado.ENTREGADO,
        }
        or pedido.fecha_reembolso_simulado is not None
    ):
        messages.error(
            request,
            "El estado actual del pedido impide responder esta devolución. "
            "Se necesita una revisión administrativa.",
        )
        return redirect(
            "vendedores:detalle_pedido",
            pedido_id=pedido.pk,
        )

    if request.method == "POST":
        formulario = FormularioRespuestaDevolucion(request.POST)

        if formulario.is_valid():
            decision = formulario.cleaned_data["decision"]

            if decision == "aceptar":
                pedido.estado_devolucion = (
                    Pedido.EstadoDevolucion.ACEPTADA
                )
                mensaje = (
                    "Devolución aceptada. Queda pendiente recibir "
                    "los artículos; todavía no se registró un reembolso."
                )
            else:
                pedido.estado_devolucion = (
                    Pedido.EstadoDevolucion.RECHAZADA
                )
                mensaje = "Devolución rechazada. La respuesta quedó registrada."

            pedido.respuesta_devolucion = (
                formulario.cleaned_data["respuesta"]
            )
            pedido.fecha_respuesta_devolucion = timezone.now()

            pedido.save(
                update_fields=[
                    "estado_devolucion",
                    "respuesta_devolucion",
                    "fecha_respuesta_devolucion",
                    "fecha_actualizacion",
                ],
            )

            messages.success(request, mensaje)

            return redirect(
                "vendedores:detalle_pedido",
                pedido_id=pedido.pk,
            )
    else:
        formulario = FormularioRespuestaDevolucion()

    return render(
        request,
        "catalog/vendedor/responder_devolucion.html",
        {
            "pedido": pedido,
            "formulario": formulario,
        },
    )
@login_required
@require_http_methods(["GET", "POST"])
def recibir_devolucion_vendedor(request, pedido_id):
    """Permite registrar la recepción de una devolución propia."""

    pedido = get_object_or_404(
        Pedido,
        pk=pedido_id,
        tienda__propietario=request.user,
        compra__estado=Compra.Estado.CONFIRMADA,
    )

    if pedido.estado_devolucion != Pedido.EstadoDevolucion.ACEPTADA:
        messages.info(
            request,
            "La devolución no está pendiente de recepción. "
            "No se realizaron cambios.",
        )
        return redirect(
            "vendedores:detalle_pedido",
            pedido_id=pedido.pk,
        )

    if request.method == "POST":
        formulario = FormularioRecepcionDevolucion(request.POST)

        if formulario.is_valid():
            try:
                pedido, completada = completar_devolucion_pedido(
                    request.user,
                    pedido.pk,
                    formulario.cleaned_data["reposicion"] == "si",
                    formulario.cleaned_data["observaciones"],
                )
            except Pedido.DoesNotExist:
                raise Http404("No se encontró el pedido.")
            except ValidationError as error:
                formulario.add_error(None, error)
            else:
                if completada:
                    messages.success(
                        request,
                        "Devolución completada y reembolso simulado "
                        "registrado.",
                    )
                else:
                    messages.info(
                        request,
                        "Esta devolución ya estaba completada. "
                        "No se realizaron cambios.",
                    )

                return redirect(
                    "vendedores:detalle_pedido",
                    pedido_id=pedido.pk,
                )
    else:
        formulario = FormularioRecepcionDevolucion()

    return render(
        request,
        "catalog/vendedor/recibir_devolucion.html",
        {"pedido": pedido, "formulario": formulario},
    )
@login_required
@require_POST
@transaction.atomic
def marcar_listo_retiro_vendedor(request, pedido_id):
    """Marca una sola vez un pedido propio como listo para retirar."""

    pedido = get_object_or_404(
        Pedido.objects.select_for_update().select_related("compra"),
        pk=pedido_id,
        tienda__propietario=request.user,
        compra__estado=Compra.Estado.CONFIRMADA,
    )

    if pedido.modalidad_entrega != Pedido.ModalidadEntrega.RETIRO:
        messages.error(
            request,
            "Este pedido corresponde a un envío a domicilio.",
        )

    elif pedido.estado == Pedido.Estado.LISTO_RETIRO:
        messages.info(
            request,
            "El pedido ya estaba listo para retirar.",
        )

    elif pedido.estado != Pedido.Estado.PREPARACION:
        messages.error(
            request,
            "Solo podés preparar para retiro un pedido en preparación.",
        )

    elif (
        pedido.fecha_despacho is not None
        or pedido.fecha_entrega is not None
        or pedido.fecha_reembolso_simulado is not None
        or pedido.estado_devolucion
        != Pedido.EstadoDevolucion.SIN_SOLICITUD
        or not pedido.direccion_retiro.strip()
    ):
        messages.error(
            request,
            "El pedido tiene datos que requieren revisión. "
            "No se realizaron cambios.",
        )

    else:
        pedido.estado = Pedido.Estado.LISTO_RETIRO
        pedido.fecha_listo_retiro = timezone.now()

        pedido.save(
            update_fields=[
                "estado",
                "fecha_listo_retiro",
                "fecha_actualizacion",
            ],
        )

        messages.success(
            request,
            "El pedido quedó listo para retirar. "
            "El comprador puede consultar la dirección en su compra.",
        )

    return redirect(
        "vendedores:detalle_pedido",
        pedido_id=pedido.pk,
    )