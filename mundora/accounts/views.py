from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

from .forms import FormularioInicioSesion

from .forms import FormularioRegistro


def registro(request):
    """Muestra el formulario y crea una cuenta con datos válidos."""

    if request.method == "POST":
        formulario = FormularioRegistro(request.POST)

        if formulario.is_valid():
            formulario.save()

            messages.success(
                request,
                "Tu cuenta se creó correctamente.",
            )

            return redirect("accounts:iniciar_sesion")
    else:
        formulario = FormularioRegistro()

    return render(
        request,
        "accounts/registro.html",
        {"formulario": formulario},
    )

class VistaInicioSesion(LoginView):
    """Muestra el formulario y abre la sesión del usuario."""

    template_name = "accounts/iniciar_sesion.html"
    authentication_form = FormularioInicioSesion
    redirect_authenticated_user = True


@login_required
def mi_cuenta(request):
    """Muestra los datos de la persona que inició sesión."""

    return render(request, "accounts/mi_cuenta.html")