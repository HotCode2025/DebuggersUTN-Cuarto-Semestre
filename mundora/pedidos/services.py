import hashlib
import json

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.models import DomicilioEntrega, User
from carrito.models import Carrito, ItemCarrito
from carrito.views import motivo_no_disponible
from catalog.models import Variante
from catalog.views_publicas import productos_visibles

from .models import Compra, DetallePedido, Pedido


# Campos que se copian del domicilio habitual a la compra.
CAMPOS_DOMICILIO = (
    "destinatario",
    "telefono_contacto",
    "provincia",
    "localidad",
    "codigo_postal",
    "calle",
    "numero",
    "detalle_direccion",
)


def huella_revision(items, domicilio):
    """Identifica los datos mostrados para detectar cambios posteriores."""

    datos = {
        "domicilio": {
            campo: getattr(domicilio, campo)
            for campo in CAMPOS_DOMICILIO
        },
        "items": [
            {
                "variante": item.variante_id,
                "cantidad": item.cantidad,
                "precio": str(item.variante.precio),
                "producto": item.variante.producto.nombre,
                "marca": item.variante.producto.marca,
                "color": item.variante.color,
                "medidas": item.variante.medidas,
                "material": item.variante.material,
                "tienda": item.variante.producto.tienda_id,
                "nombre_tienda": item.variante.producto.tienda.nombre,
            }
            for item in sorted(items, key=lambda item: item.variante_id)
        ],
    }

    contenido = json.dumps(
        datos,
        ensure_ascii=False,
        sort_keys=True,
    )

    return hashlib.sha256(contenido.encode("utf-8")).hexdigest()

def _cancelar_pendientes_anteriores(usuario, conservar_id=None):
    """Cancela otras compras pendientes dentro de la transacción de creación."""

    pendientes = Compra.objects.select_for_update().filter(
        comprador=usuario,
        estado=Compra.Estado.PENDIENTE,
    )

    if conservar_id is not None:
        pendientes = pendientes.exclude(pk=conservar_id)

    ids_pendientes = list(
        pendientes.values_list("pk", flat=True)
    )

    if not ids_pendientes:
        return

    ahora = timezone.now()

    # Conserva las compras y sus detalles como historial.
    Compra.objects.filter(
        pk__in=ids_pendientes,
        comprador=usuario,
        estado=Compra.Estado.PENDIENTE,
    ).update(
        estado=Compra.Estado.CANCELADA,
        fecha_actualizacion=ahora,
    )

    # Cancela también los pedidos que esperaban esa confirmación.
    Pedido.objects.filter(
        compra_id__in=ids_pendientes,
        estado=Pedido.Estado.PENDIENTE,
    ).update(
        estado=Pedido.Estado.CANCELADO,
        fecha_actualizacion=ahora,
    )

@transaction.atomic
def crear_compra_pendiente(usuario, codigo, huella_esperada):
    """Crea o reutiliza una compra completa sin descontar stock."""

    # Serializa la creación para este usuario y sus cambios de domicilio.
    User.objects.select_for_update().get(pk=usuario.pk)

    # Reconoce el reenvío de una solicitud ya procesada.
    existente = Compra.objects.filter(
        codigo=codigo,
        comprador=usuario,
    ).first()

    if existente:
        # Evita reutilizar una compra pendiente vacía de las pruebas anteriores.
        if (
            existente.estado == Compra.Estado.PENDIENTE
            and not existente.pedidos.filter(
                detalles__isnull=False,
            ).exists()
        ):
            raise ValidationError(
                "Esta compra quedó incompleta. "
                "Revisá nuevamente el carrito y volvé a crearla."
            )

        return existente, False

    carrito = Carrito.objects.select_for_update().filter(
        usuario=usuario,
    ).first()

    if carrito is None:
        raise ValidationError("Tu carrito está vacío.")

    domicilio = DomicilioEntrega.objects.filter(
        usuario=usuario,
    ).first()

    if domicilio is None:
        raise ValidationError(
            "Completá tu domicilio de entrega antes de continuar."
        )

    items = list(
        ItemCarrito.objects.filter(
            carrito=carrito,
        ).select_related("variante__producto__tienda")
    )

    if not items:
        raise ValidationError("Tu carrito está vacío.")

    # Consulta y bloquea las variantes durante la comprobación y la copia.
    variantes = {
        variante.pk: variante
        for variante in Variante.objects.select_for_update()
        .filter(pk__in=[item.variante_id for item in items])
        .order_by("pk")
    }

    for item in items:
        variante = variantes.get(item.variante_id)

        if variante is None:
            raise ValidationError(
                "Una variante ya no existe. Revisá tu carrito."
            )

        item.variante = variante

    ids_visibles = set(
        productos_visibles()
        .filter(
            pk__in=[
                item.variante.producto_id
                for item in items
            ],
        )
        .values_list("pk", flat=True)
    )

    # Primero valida TODOS los artículos, sin crear compras dentro del bucle.
    for item in items:
        motivo = motivo_no_disponible(
            item.variante,
            item.variante.producto_id in ids_visibles,
            item.cantidad,
        )

        if motivo:
            raise ValidationError(
                f"{item.variante}: {motivo}"
            )

    # A partir de aquí, el código está fuera del bucle de validación.
    huella_actual = huella_revision(items, domicilio)

    if huella_actual != huella_esperada:
        raise ValidationError(
            "Cambió el carrito, el domicilio o la información de un producto. "
            "Revisá los datos actualizados antes de continuar."
        )

    # Busca una compra coincidente que tenga pedidos con detalles.
    # Excluye las compras vacías producidas por el error anterior.
    coincidente = (
        Compra.objects.filter(
            comprador=usuario,
            estado=Compra.Estado.PENDIENTE,
            huella_revision=huella_actual,
            pedidos__detalles__isnull=False,
        )
        .distinct()
        .first()
    )

    # Cancela las otras pendientes, incluidas las antiguas compras vacías.
    _cancelar_pendientes_anteriores(
        usuario,
        conservar_id=coincidente.pk if coincidente else None,
    )

    if coincidente:
        return coincidente, False

    # Crea una sola compra después de superar todas las validaciones.
    compra = Compra.objects.create(
        codigo=codigo,
        comprador=usuario,
        huella_revision=huella_actual,
        **{
            campo: getattr(domicilio, campo)
            for campo in CAMPOS_DOMICILIO
        },
    )

    pedidos_por_tienda = {}

    # Genera los pedidos y copia todos los artículos.
    for item in items:
        variante = item.variante
        producto = variante.producto
        tienda = producto.tienda

        if tienda.pk not in pedidos_por_tienda:
            pedidos_por_tienda[tienda.pk] = Pedido.objects.create(
                compra=compra,
                tienda=tienda,
                nombre_tienda=tienda.nombre,
            )

        DetallePedido.objects.create(
            pedido=pedidos_por_tienda[tienda.pk],
            variante=variante,
            nombre_producto=producto.nombre,
            marca=producto.marca,
            color=variante.color,
            medidas=variante.medidas,
            material=variante.material,
            cantidad=item.cantidad,
            precio_unitario=variante.precio,
        )

    # Devuelve la compra recién cuando todos sus detalles están guardados.
    return compra, True
def _rechazar_compra(compra, motivo):
    """Registra el rechazo y cancela sus pedidos sin modificar stock."""

    compra.estado = Compra.Estado.RECHAZADA
    compra.motivo_rechazo = motivo[:250]
    compra.save(
        update_fields=[
            "estado",
            "motivo_rechazo",
            "fecha_actualizacion",
        ],
    )

    compra.pedidos.filter(
        estado=Pedido.Estado.PENDIENTE,
    ).update(
        estado=Pedido.Estado.CANCELADO,
        fecha_actualizacion=timezone.now(),
    )


@transaction.atomic
def procesar_pago_simulado(usuario, codigo, resultado):
    """Confirma o rechaza una compra propia de manera indivisible."""

    if resultado not in {"aprobado", "rechazado"}:
        raise ValidationError("El resultado del pago no es válido.")

    # Mantiene el mismo orden de bloqueo que la creación de compras.
    User.objects.select_for_update().get(pk=usuario.pk)

    carrito = Carrito.objects.select_for_update().filter(
        usuario=usuario,
    ).first()

    compra = Compra.objects.select_for_update().get(
        codigo=codigo,
        comprador=usuario,
    )

    # Una compra ya procesada no vuelve a modificar stock ni carrito.
    if compra.estado != Compra.Estado.PENDIENTE:
        return compra, False

    pedidos = list(compra.pedidos.all())
    detalles = list(
        DetallePedido.objects.filter(
            pedido__compra=compra,
        ).order_by("pk")
    )

    # Impide confirmar compras vacías o con pedidos incompletos.
    ids_con_detalles = {detalle.pedido_id for detalle in detalles}

    if (
        not pedidos
        or any(pedido.pk not in ids_con_detalles for pedido in pedidos)
        or any(
            pedido.estado != Pedido.Estado.PENDIENTE
            for pedido in pedidos
        )
    ):
        _rechazar_compra(
            compra,
            "La compra está incompleta. Revisá el carrito y creá otra compra.",
        )
        return compra, True

    if resultado == "rechazado":
        _rechazar_compra(
            compra,
            "El pago simulado fue rechazado. No se realizó ningún cargo.",
        )
        return compra, True

    # Suma las unidades requeridas por cada variante.
    cantidades = {}

    for detalle in detalles:
        if detalle.variante_id is None:
            _rechazar_compra(
                compra,
                "Un artículo ya no existe. Revisá el carrito.",
            )
            return compra, True

        cantidades[detalle.variante_id] = (
            cantidades.get(detalle.variante_id, 0)
            + detalle.cantidad
        )

    # Bloquea las variantes en un orden estable hasta terminar.
    variantes = {
        variante.pk: variante
        for variante in Variante.objects.select_for_update()
        .filter(pk__in=cantidades)
        .order_by("pk")
    }

    ids_visibles = set(
        productos_visibles()
        .filter(
            pk__in=[
                variante.producto_id
                for variante in variantes.values()
            ],
        )
        .values_list("pk", flat=True)
    )

    # Comprueba todos los artículos antes de descontar una sola unidad.
    for variante_id, cantidad in cantidades.items():
        variante = variantes.get(variante_id)

        if variante is None:
            _rechazar_compra(
                compra,
                "Un artículo ya no está disponible. Revisá el carrito.",
            )
            return compra, True

        motivo = motivo_no_disponible(
            variante,
            variante.producto_id in ids_visibles,
            cantidad,
        )

        if motivo:
            _rechazar_compra(
                compra,
                f"No se pudo confirmar la compra: {variante}. {motivo}",
            )
            return compra, True

    # Descuenta stock únicamente cuando toda la compra es válida.
    for variante_id, cantidad in cantidades.items():
        variante = variantes[variante_id]
        variante.stock -= cantidad
        variante.save(update_fields=["stock"])

    compra.estado = Compra.Estado.CONFIRMADA
    compra.motivo_rechazo = ""
    compra.fecha_confirmacion = timezone.now()
    compra.save(
        update_fields=[
            "estado",
            "motivo_rechazo",
            "fecha_confirmacion",
            "fecha_actualizacion",
        ],
    )

    compra.pedidos.update(
        estado=Pedido.Estado.PREPARACION,
        fecha_actualizacion=timezone.now(),
    )

    # Retira del carrito las cantidades compradas.
    # Conserva otros artículos y las unidades adicionales.
    if carrito is not None:
        items = ItemCarrito.objects.filter(
            carrito=carrito,
            variante_id__in=cantidades,
        )

        for item in items:
            cantidad_restante = (
                item.cantidad - cantidades[item.variante_id]
            )

            if cantidad_restante <= 0:
                item.delete()
            else:
                item.cantidad = cantidad_restante
                item.save(
                    update_fields=[
                        "cantidad",
                        "fecha_actualizacion",
                    ],
                )

    return compra, True