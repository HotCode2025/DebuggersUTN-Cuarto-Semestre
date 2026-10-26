from django import forms

from .models import Categoria, Producto


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