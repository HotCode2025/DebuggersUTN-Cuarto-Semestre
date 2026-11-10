from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from catalog.models import ImagenProducto, Variante
from catalog.views_publicas import productos_visibles

from .forms import FormularioAgregarCarrito
from .models import Carrito, ItemCarrito


@require_POST
def agregar_variante(request, variante_id):
    """Agrega unidades de una variante al carrito del usuario."""

    # Solo admite variantes activas de publicaciones visibles.
    variante = get_object_or_404(
        Variante.objects.select_related("producto").filter(
            activa=True,
            producto__in=productos_visibles().values("pk"),
        ),
        pk=variante_id,
    )

    destino = reverse(
        "catalogo:detalle",
        kwargs={
            "identificador_url": variante.producto.identificador_url,
        },
    )

    # Después de iniciar sesión, vuelve a la ficha del producto.
    if not request.user.is_authenticated:
        return redirect_to_login(
            destino,
            login_url=reverse("accounts:iniciar_sesion"),
        )

    formulario = FormularioAgregarCarrito(request.POST)

    if not formulario.is_valid():
        for errores in formulario.errors.values():
            for error in errores:
                messages.error(request, error)

        return redirect(destino)

    cantidad_agregada = formulario.cleaned_data["cantidad"]

    with transaction.atomic():
        carrito, _ = Carrito.objects.get_or_create(
            usuario=request.user,
        )

        # Serializa las modificaciones simultáneas del mismo carrito.
        carrito = Carrito.objects.select_for_update().get(
            pk=carrito.pk,
        )

        # Vuelve a consultar la variante y su stock dentro de la operación.
        variante = get_object_or_404(
            Variante.objects.select_for_update(),
            pk=variante_id,
            activa=True,
        )

        # Revisa nuevamente la publicación antes de modificar el carrito.
        if not productos_visibles().filter(
            pk=variante.producto_id,
        ).exists():
            messages.error(
                request,
                "Esta publicación ya no está disponible.",
            )
            return redirect("catalogo:listado")

        item = ItemCarrito.objects.filter(
            carrito=carrito,
            variante=variante,
        ).first()

        cantidad_actual = item.cantidad if item else 0
        cantidad_total = cantidad_actual + cantidad_agregada

        # Compara el stock contra la cantidad total, no solo la nueva.
        if cantidad_total > variante.stock:
            messages.error(
                request,
                (
                    "No se pudo agregar esa cantidad. "
                    f"Stock disponible: {variante.stock}. "
                    f"Unidades que ya tenés en el carrito: {cantidad_actual}."
                ),
            )
            return redirect(destino)

        if item:
            item.cantidad = cantidad_total
            item.save(
                update_fields=["cantidad", "fecha_actualizacion"],
            )
        else:
            ItemCarrito.objects.create(
                carrito=carrito,
                variante=variante,
                cantidad=cantidad_total,
            )

    messages.success(
        request,
        (
            "Variante agregada al carrito. "
            f"Cantidad acumulada de esta variante: {cantidad_total}."
        ),
    )

    return redirect(destino)

def motivo_no_disponible(variante, producto_visible, cantidad):
    """Explica por qué una selección no puede comprarse actualmente."""

    if not producto_visible:
        return "La publicación ya no está disponible para la venta."

    if not variante.activa:
        return "Esta variante está desactivada."

    if variante.stock == 0:
        return "Esta variante está sin stock."

    if cantidad > variante.stock:
        return (
            f"Tenés {cantidad} unidades seleccionadas, "
            f"pero quedan {variante.stock}. Ajustá la cantidad."
        )

    return ""


@login_required
@require_GET
def ver_carrito(request):
    """Muestra la selección del usuario con precios y stock actuales."""

    # Consultar un carrito vacío no crea registros nuevos.
    items = list(
        ItemCarrito.objects.filter(
            carrito__usuario=request.user,
        )
        .select_related(
            "variante__producto__tienda",
        )
        .prefetch_related(
            Prefetch(
                "variante__producto__imagenes",
                queryset=ImagenProducto.objects.exclude(
                    imagen="",
                ).order_by("orden", "pk"),
                to_attr="fotos_carrito",
            ),
        )
    )

    # Consulta la visibilidad de los productos en conjunto.
    ids_productos = {
        item.variante.producto_id
        for item in items
    }

    ids_visibles = set(
        productos_visibles()
        .filter(pk__in=ids_productos)
        .values_list("pk", flat=True)
    )

    filas = []
    total_disponible = Decimal("0.00")
    hay_problemas = False

    for item in items:
        variante = item.variante
        producto = variante.producto
        producto_visible = producto.pk in ids_visibles

        motivo = motivo_no_disponible(
            variante,
            producto_visible,
            item.cantidad,
        )

        # Prefiere la imagen de la variante y utiliza la galería como respaldo.
        imagen_url = ""
        texto_imagen = producto.nombre

        if variante.imagen:
            imagen_url = variante.imagen.url
            texto_imagen = (
                f"{producto.nombre} — "
                f"{variante.color or 'variante estándar'}"
            )
        elif producto.fotos_carrito:
            foto = producto.fotos_carrito[0]
            imagen_url = foto.imagen.url
            texto_imagen = foto.texto_alternativo

        subtotal = item.subtotal

        if motivo:
            hay_problemas = True
        else:
            total_disponible += subtotal

        filas.append({
            "item": item,
            "producto": producto,
            "variante": variante,
            "producto_visible": producto_visible,
            "motivo": motivo,
            "subtotal": subtotal,
            "imagen_url": imagen_url,
            "texto_imagen": texto_imagen,
            # Permite corregir una cantidad que supera el stock.
            "puede_actualizar": (
                producto_visible
                and variante.activa
                and variante.stock > 0
            ),
        })

    return render(
        request,
        "carrito/detalle.html",
        {
            "filas": filas,
            "total_disponible": total_disponible,
            "hay_problemas": hay_problemas,
        },
    )


@require_POST
def actualizar_cantidad(request, item_id):
    """Reemplaza la cantidad de un ítem del usuario autenticado."""

    if not request.user.is_authenticated:
        return redirect_to_login(
            reverse("carrito:detalle"),
            login_url=reverse("accounts:iniciar_sesion"),
        )

    with transaction.atomic():
        # Mantiene el mismo orden de bloqueo que al agregar productos.
        carrito = get_object_or_404(
            Carrito.objects.select_for_update(),
            usuario=request.user,
        )

        # Un identificador de otro carrito devuelve 404.
        item = get_object_or_404(
            ItemCarrito,
            pk=item_id,
            carrito=carrito,
        )

        formulario = FormularioAgregarCarrito(request.POST)

        if not formulario.is_valid():
            for errores in formulario.errors.values():
                for error in errores:
                    messages.error(request, error)

            return redirect("carrito:detalle")

        cantidad = formulario.cleaned_data["cantidad"]

        variante = get_object_or_404(
            Variante.objects.select_for_update(),
            pk=item.variante_id,
        )

        producto_visible = productos_visibles().filter(
            pk=variante.producto_id,
        ).exists()

        motivo = motivo_no_disponible(
            variante,
            producto_visible,
            cantidad,
        )

        if motivo:
            messages.error(request, motivo)
            return redirect("carrito:detalle")

        # Actualizar reemplaza la cantidad; no suma unidades.
        item.cantidad = cantidad
        item.save(
            update_fields=["cantidad", "fecha_actualizacion"],
        )

    messages.success(request, "Cantidad actualizada.")
    return redirect("carrito:detalle")


@require_POST
def quitar_item(request, item_id):
    """Quita un ítem propio, incluso si ya no está disponible."""

    if not request.user.is_authenticated:
        return redirect_to_login(
            reverse("carrito:detalle"),
            login_url=reverse("accounts:iniciar_sesion"),
        )

    with transaction.atomic():
        carrito = get_object_or_404(
            Carrito.objects.select_for_update(),
            usuario=request.user,
        )

        item = get_object_or_404(
            ItemCarrito,
            pk=item_id,
            carrito=carrito,
        )

        item.delete()

    messages.success(request, "Producto quitado del carrito.")
    return redirect("carrito:detalle")