from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import Producto, Tienda

class FormularioProducto(forms.ModelForm):
    """Valida los datos generales antes de publicar un producto."""

    class Meta:
        """Vincula el formulario administrativo con el producto."""

        model = Producto
        fields = "__all__"

    def clean(self):
        """Exige una tienda aprobada para publicar."""

        datos = super().clean()

        # Los borradores no necesitan una tienda aprobada.
        if not datos.get("publicado"):
            return datos

        tienda = datos.get("tienda")

        if tienda and tienda.estado != Tienda.Estado.APROBADA:
            self.add_error(
                "tienda",
                "La tienda debe estar aprobada para publicar productos.",
            )

        # Una publicación rechazada no puede permanecer publicada.
        if (
            datos.get("estado_revision")
            == Producto.EstadoRevision.RECHAZADO
        ):
            self.add_error(
                "publicado",
                "Un producto rechazado no puede estar publicado.",
            )

        return datos


class ConjuntoVariantesProducto(BaseInlineFormSet):
    """Valida las variantes que conservará el producto al guardar."""

    def clean(self):
        """Exige al menos una variante activa para publicar."""

        # Conserva las validaciones existentes, incluidos los duplicados.
        super().clean()

        if not self.instance.publicado:
            return

        hay_variante_activa = False

        for formulario in self.forms:
            datos = getattr(formulario, "cleaned_data", {})

            # Omite las filas marcadas para eliminar.
            if datos.get("DELETE"):
                continue

            # Primero deben corregirse los errores de cada variante.
            if formulario.errors:
                return

            # Omite formularios nuevos que no fueron completados.
            if not formulario.instance.pk and not formulario.has_changed():
                continue

            if datos.get("activa"):
                hay_variante_activa = True

        if not hay_variante_activa:
            raise ValidationError(
                "Para publicar, agregá o conservá al menos "
                "una variante activa."
            )


class ConjuntoImagenesProducto(BaseInlineFormSet):
    """Valida las fotografías que conservará la galería al guardar."""

    def clean(self):
        """Exige al menos una imagen de galería para publicar."""

        super().clean()

        if not self.instance.publicado:
            return

        hay_imagen = False

        for formulario in self.forms:
            datos = getattr(formulario, "cleaned_data", {})

            # No cuenta fotografías que se van a eliminar.
            if datos.get("DELETE"):
                continue

            # Primero deben corregirse los archivos o campos inválidos.
            if formulario.errors:
                return

            # Omite las filas nuevas sin completar.
            if not formulario.instance.pk and not formulario.has_changed():
                continue

            if datos.get("imagen"):
                hay_imagen = True

        if not hay_imagen:
            raise ValidationError(
                "Para publicar, agregá o conservá al menos "
                "una imagen en la galería."
            )