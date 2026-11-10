from django import forms

from .models import Categoria, Variante


class FormularioFiltrosCatalogo(forms.Form):
    """Valida los filtros y el orden del catálogo público."""

    buscar = forms.CharField(
        label="Buscar productos",
        required=False,
        max_length=150,
        widget=forms.TextInput(
            attrs={"placeholder": "Producto, marca o tienda"},
        ),
    )

    categoria = forms.ModelChoiceField(
        label="Categoría",
        queryset=Categoria.objects.filter(activa=True).order_by("nombre"),
        required=False,
        empty_label="Todas las categorías",
    )

    provincia = forms.ChoiceField(
        label="Provincia de origen",
        required=False,
    )

    material = forms.ChoiceField(
        label="Material",
        required=False,
    )

    precio_minimo = forms.DecimalField(
        label="Precio mínimo en ARS",
        required=False,
        min_value=0,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.01"}),
    )

    precio_maximo = forms.DecimalField(
        label="Precio máximo en ARS",
        required=False,
        min_value=0,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.01"}),
    )

    orden = forms.ChoiceField(
        label="Ordenar por",
        required=False,
        choices=(
            ("", "Más recientes"),
            ("precio_asc", "Menor precio"),
            ("precio_desc", "Mayor precio"),
            ("nombre", "Nombre: A a Z"),
        ),
    )

    def __init__(self, *args, productos, **kwargs):
        """Ofrece provincias y materiales del catálogo visible."""

        super().__init__(*args, **kwargs)

        provincias = (
            productos.exclude(provincia_origen="")
            .order_by("provincia_origen")
            .values_list("provincia_origen", flat=True)
            .distinct()
        )

        materiales = (
            Variante.objects.filter(
                producto__in=productos.values("pk"),
                activa=True,
            )
            .exclude(material="")
            .order_by("material")
            .values_list("material", flat=True)
            .distinct()
        )

        self.fields["provincia"].choices = [
            ("", "Todas las provincias"),
            *((provincia, provincia) for provincia in provincias),
        ]

        self.fields["material"].choices = [
            ("", "Todos los materiales"),
            *((material, material) for material in materiales),
        ]

    def clean(self):
        """Comprueba que el rango de precios tenga sentido."""

        datos = super().clean()

        minimo = datos.get("precio_minimo")
        maximo = datos.get("precio_maximo")

        if minimo is not None and maximo is not None:
            if minimo > maximo:
                self.add_error(
                    "precio_maximo",
                    "El precio máximo debe ser mayor o igual al mínimo.",
                )

        return datos