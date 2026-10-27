from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef, Prefetch, Subquery, Q
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import ImagenProducto, Producto, Tienda, Variante
from .forms_publicos import FormularioFiltrosCatalogo


def productos_visibles():
    """Obtiene los productos habilitados para el catálogo público."""

    variantes = Variante.objects.filter(
        producto_id=OuterRef("pk"),
        activa=True,
    )

    imagenes = ImagenProducto.objects.filter(
        producto_id=OuterRef("pk"),
    ).exclude(imagen="")

    return (
        Producto.objects.filter(
            Exists(variantes),
            Exists(imagenes),
            publicado=True,
            tienda__estado=Tienda.Estado.APROBADA,
            categoria__activa=True,
            estado_revision__in=[
                Producto.EstadoRevision.PENDIENTE,
                Producto.EstadoRevision.APROBADO,
            ],
        )
        .annotate(
            # Precio mínimo entre todas las variantes activas.
            precio_desde=Subquery(
                variantes.order_by("precio", "pk").values("precio")[:1]
            ),
            # Un producto agotado permanece visible.
            hay_stock=Exists(variantes.filter(stock__gt=0)),
        )
        .select_related("tienda", "categoria")
        .prefetch_related(
            Prefetch(
                "imagenes",
                queryset=ImagenProducto.objects.exclude(
                    imagen="",
                ).order_by("orden", "pk"),
                to_attr="fotos_catalogo",
            ),
        )
        .order_by("-fecha_creacion", "-pk")
    )


@require_GET
def listado_productos(request):
    """Busca, filtra, ordena y pagina los productos visibles."""

    catalogo = productos_visibles()

    formulario = FormularioFiltrosCatalogo(
        request.GET,
        productos=catalogo,
    )

    productos = catalogo

    if formulario.is_valid():
        datos = formulario.cleaned_data

        busqueda = datos.get("buscar")
        categoria = datos.get("categoria")
        provincia = datos.get("provincia")
        material = datos.get("material")
        minimo = datos.get("precio_minimo")
        maximo = datos.get("precio_maximo")

        if busqueda:
            productos = productos.filter(
                Q(nombre__icontains=busqueda)
                | Q(descripcion__icontains=busqueda)
                | Q(marca__icontains=busqueda)
                | Q(tienda__nombre__icontains=busqueda)
            )

        if categoria:
            productos = productos.filter(categoria=categoria)

        if provincia:
            productos = productos.filter(provincia_origen=provincia)

        # Una misma variante debe cumplir material y rango de precios.
        variantes_coincidentes = Variante.objects.filter(
            producto_id=OuterRef("pk"),
            activa=True,
        )

        if material:
            variantes_coincidentes = variantes_coincidentes.filter(
                material=material,
            )

        if minimo is not None:
            variantes_coincidentes = variantes_coincidentes.filter(
                precio__gte=minimo,
            )

        if maximo is not None:
            variantes_coincidentes = variantes_coincidentes.filter(
                precio__lte=maximo,
            )

        productos = productos.filter(
            Exists(variantes_coincidentes),
        ).annotate(
            # El precio mostrado corresponde a las variantes filtradas.
            precio_desde=Subquery(
                variantes_coincidentes.order_by(
                    "precio", "pk",
                ).values("precio")[:1]
            ),
            hay_stock=Exists(
                variantes_coincidentes.filter(stock__gt=0)
            ),
        )

        ordenamientos = {
            "precio_asc": ("precio_desde", "pk"),
            "precio_desc": ("-precio_desde", "pk"),
            "nombre": ("nombre", "pk"),
        }

        orden = ordenamientos.get(
            datos.get("orden"),
            ("-fecha_creacion", "-pk"),
        )

        productos = productos.order_by(*orden)

    else:
        # Evita presentar resultados que no respeten filtros inválidos.
        productos = catalogo.none()

    paginador = Paginator(productos, 3)
    pagina = paginador.get_page(request.GET.get("pagina"))

    # Conserva los filtros y reemplaza solo el número de página.
    parametros = request.GET.copy()
    parametros.pop("pagina", None)

    return render(
        request,
        "catalog/publico/listado.html",
        {
            "pagina": pagina,
            "formulario": formulario,
            "parametros": parametros.urlencode(),
        },
    )

@require_GET
def detalle_producto_publico(request, identificador_url):
    """Muestra un producto visible y sus variantes activas."""

    productos = productos_visibles().prefetch_related(
        Prefetch(
            "variantes",
            queryset=Variante.objects.filter(
                activa=True,
            ).order_by("precio", "pk"),
            to_attr="variantes_activas",
        ),
    )

    # Aplica las mismas restricciones que el listado.
    producto = get_object_or_404(
        productos,
        identificador_url=identificador_url,
    )

    return render(
        request,
        "catalog/publico/detalle.html",
        {"producto": producto},
    )