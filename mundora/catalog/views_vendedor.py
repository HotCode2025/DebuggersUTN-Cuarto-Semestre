from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods
from django.contrib import messages
from django.db import transaction

from .forms_vendedor import FormularioProductoVendedor
from .models import Producto, Tienda


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