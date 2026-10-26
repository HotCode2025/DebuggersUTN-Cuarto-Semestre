from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import Producto, Tienda

class FormularioProducto(forms.ModelForm):
    """Valida la publicación y la revisión administrativa."""

    class Meta:
        """Define los campos administrativos del producto."""

        model = Producto
        fields = "__all__"

    def clean(self):
        """Exige requisitos para aprobar y un motivo para rechazar."""

        datos = super().clean()

        estado = datos.get("estado_revision")
        observaciones = (
            datos.get("observaciones_revision") or ""
        ).strip()

        datos["observaciones_revision"] = observaciones

        if estado == Producto.EstadoRevision.RECHAZADO:
            if not observaciones:
                self.add_error(
                    "observaciones_revision",
                    "Explicá el motivo del rechazo para que "
                    "el vendedor pueda corregirlo.",
                )

            # Rechazar retira automáticamente la publicación.
            datos["publicado"] = False

            return datos

        requiere_requisitos = (
            datos.get("publicado")
            or estado == Producto.EstadoRevision.APROBADO
        )

        if requiere_requisitos:
            tienda = datos.get("tienda")
            categoria = datos.get("categoria")

            if tienda and tienda.estado != Tienda.Estado.APROBADA:
                self.add_error(
                    "tienda",
                    "La tienda debe estar aprobada para "
                    "publicar o verificar el producto.",
                )

            if categoria and not categoria.activa:
                self.add_error(
                    "categoria",
                    "La categoría debe estar habilitada para "
                    "publicar o verificar el producto.",
                )

        return datos
    
class ConjuntoVariantesProducto(BaseInlineFormSet):
    """Valida combinaciones y disponibilidad de las variantes."""

    @staticmethod
    def normalizar_texto(valor):
        """Ignora mayúsculas y espacios repetidos al comparar."""

        return " ".join((valor or "").split()).casefold()

    def clean(self):
        """Impide duplicados y exige variantes activas al publicar."""

        # Conserva las validaciones propias de Django.
        super().clean()

        formularios_validos = []

        for formulario in self.forms:
            datos = getattr(formulario, "cleaned_data", {})

            # No valida las variantes que se van a eliminar.
            if datos.get("DELETE"):
                continue

            # Primero deben corregirse los errores de los campos.
            if formulario.errors:
                return

            # Ignora la fila adicional cuando permanece intacta.
            if (
                not formulario.instance.pk
                and not formulario.has_changed()
            ):
                continue

            formularios_validos.append(formulario)

        combinaciones = set()
        hay_duplicados = False
        hay_variante_activa = False

        for formulario in formularios_validos:
            datos = formulario.cleaned_data

            # Compara características sin modificar el texto guardado.
            combinacion = tuple(
                self.normalizar_texto(datos.get(campo))
                for campo in ("color", "medidas", "material")
            )

            if combinacion in combinaciones:
                formulario.add_error(
                    None,
                    "Esta combinación de color, medidas y material "
                    "ya existe en el producto.",
                )
                hay_duplicados = True
            else:
                combinaciones.add(combinacion)

            if datos.get("activa"):
                hay_variante_activa = True

        if hay_duplicados:
            raise ValidationError(
                "Corregí las variantes duplicadas. Las mayúsculas "
                "y los espacios repetidos no crean una variante distinta."
            )
        requiere_variante = (
            self.instance.publicado
            or self.instance.estado_revision
            == Producto.EstadoRevision.APROBADO
        )

        if requiere_variante and not hay_variante_activa:
            raise ValidationError(
                "Para publicar o verificar el producto, "
                "debe conservar al menos una variante activa."
            )
        


class ConjuntoImagenesProducto(BaseInlineFormSet):
    """Valida las fotografías que conservará la galería al guardar."""

    def clean(self):
        """Exige al menos una imagen de galería para publicar."""

        super().clean()

        requiere_imagen = (
            self.instance.publicado
            or self.instance.estado_revision
            == Producto.EstadoRevision.APROBADO
        )

        if not requiere_imagen:
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
                "Para publicar o verificar el producto, "
                "agregá o conservá al menos una imagen en la galería."
            )

class FormularioTienda(forms.ModelForm):
    """Valida la revisión administrativa de una tienda."""

    class Meta:
        """Define los campos administrativos de la tienda."""

        model = Tienda
        fields = "__all__"

    def clean(self):
        """Exige explicar el motivo cuando se rechaza una tienda."""

        datos = super().clean()

        observaciones = (
            datos.get("observaciones_revision") or ""
        ).strip()

        datos["observaciones_revision"] = observaciones

        if (
            datos.get("estado") == Tienda.Estado.RECHAZADA
            and not observaciones
        ):
            self.add_error(
                "observaciones_revision",
                "Explicá el motivo del rechazo de la tienda.",
            )

        return datos