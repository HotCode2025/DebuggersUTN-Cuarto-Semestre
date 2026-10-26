from django import forms
from django.forms import inlineformset_factory
from .forms import ConjuntoVariantesProducto, ConjuntoImagenesProducto

from .models import Categoria, Producto, Variante, ImagenProducto


class FormularioProductoVendedor(forms.ModelForm):
    """Permite editar los datos generales de un producto propio."""

    class Meta:
        """Define los campos disponibles para el vendedor."""

        model = Producto

        fields = (
            "categoria",
            "nombre",
            "identificador_url",
            "descripcion",
            "marca",
            "cuidados",
            "provincia_origen",
        )

        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 5}),
            "cuidados": forms.Textarea(attrs={"rows": 3}),
        }

        help_texts = {
            "identificador_url": (
                "Usá un identificador único, sin espacios. "
                "Ejemplo: lampara-alerce-negra."
            ),
        }

    def __init__(self, *args, **kwargs):
        """Ofrece las categorías habilitadas para el catálogo."""

        super().__init__(*args, **kwargs)

        self.fields["categoria"].queryset = Categoria.objects.filter(
            activa=True,
        ).order_by("nombre")

# Permite administrar las variantes de un producto desde el panel.
FormularioVariantesVendedor = inlineformset_factory(
    parent_model=Producto,
    model=Variante,
    formset=ConjuntoVariantesProducto,
    fields=(
        "color",
        "medidas",
        "material",
        "precio",
        "stock",
        "imagen",
        "activa",
    ),
    extra=1,
    can_delete=True,
    can_delete_extra=True,
)
# Administra las fotografías generales de un producto.
FormularioGaleriaVendedor = inlineformset_factory(
    parent_model=Producto,
    model=ImagenProducto,
    formset=ConjuntoImagenesProducto,
    fields=(
        "imagen",
        "texto_alternativo",
        "orden",
    ),
    extra=1,
    can_delete=True,
    can_delete_extra=True,
)