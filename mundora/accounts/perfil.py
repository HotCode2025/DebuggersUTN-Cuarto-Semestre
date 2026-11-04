from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UsernameField
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods

Usuario = get_user_model()


class FormularioPerfil(forms.ModelForm):
    """Edita los datos personales de la cuenta autenticada."""
    clave_actual = forms.CharField(label="Contraseña actual", required=False, strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
        help_text="Solo si cambiás tu correo o nombre de usuario.")

    class Meta:
        model = Usuario
        fields = ("first_name", "last_name", "username", "email", "telefono")
        field_classes = {"username": UsernameField}
        labels = {"first_name": "Nombre", "last_name": "Apellido", "username": "Nombre de usuario",
                  "email": "Correo electrónico", "telefono": "Teléfono"}
        help_texts = {"username": "Podés usar letras, números y los símbolos . + - _"}
        widgets = {"telefono": forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.Meta.fields:
            self.fields[campo].required = True

    def clean_username(self):
        valor = self.cleaned_data["username"]
        if "@" in valor:
            raise forms.ValidationError("El nombre de usuario no puede contener @.")
        if Usuario.objects.exclude(pk=self.instance.pk).filter(username__iexact=valor).exists():
            raise forms.ValidationError("Ese nombre de usuario ya está en uso.")
        return valor

    def clean_email(self):
        valor = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.exclude(pk=self.instance.pk).filter(email__iexact=valor).exists():
            raise forms.ValidationError("Ese correo ya está en uso.")
        return valor

    def clean(self):
        datos = super().clean()
        if any(k in datos and datos[k] != getattr(self.instance, k) for k in ("username", "email")):
            if not self.instance.check_password(datos.get("clave_actual", "")):
                self.add_error("clave_actual", "Ingresá tu contraseña actual para confirmar el cambio.")
        return datos


@sensitive_post_parameters("clave_actual")
@login_required
@require_http_methods(["GET", "POST"])
def editar_perfil(request):
    # No se recibe un ID desde el navegador.
    usuario = Usuario.objects.get(pk=request.user.pk)
    formulario = FormularioPerfil(request.POST if request.method == "POST" else None, instance=usuario)
    if request.method == "POST" and formulario.is_valid():
        try:
            with transaction.atomic():
                cambios = [c for c in formulario.Meta.fields if getattr(usuario, c) != formulario.initial[c]]
                if cambios:
                    usuario.save(update_fields=cambios)
        except IntegrityError:
            formulario.add_error(None, "No pudimos guardar los datos. Revisá el nombre de usuario y el correo.")
        else:
            messages.success(request, "Tus datos se guardaron.")
            return redirect("accounts:mi_cuenta")
    return render(request, "accounts/editar_perfil.html", {"formulario": formulario})
