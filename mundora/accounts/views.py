from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.views.decorators.http import require_http_methods

from .forms import FormularioInicioSesion,FormularioDomicilioEntrega, FormularioRegistro
from .models import DomicilioEntrega, User


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
@login_required
@require_http_methods(["GET", "POST"])
def mi_domicilio(request):
    """Permite crear o editar el domicilio del usuario autenticado."""

    if request.method == "POST":
        with transaction.atomic():
            # Evita crear dos domicilios con envíos simultáneos.
            User.objects.select_for_update().get(
                pk=request.user.pk,
            )

            domicilio = DomicilioEntrega.objects.filter(
                usuario=request.user,
            ).first()

            formulario = FormularioDomicilioEntrega(
                request.POST,
                instance=domicilio,
            )

            if formulario.is_valid():
                domicilio = formulario.save(commit=False)

                # El propietario siempre se toma de la sesión.
                domicilio.usuario = request.user
                domicilio.save()

                messages.success(
                    request,
                    "Tu domicilio de entrega se guardó correctamente.",
                )

                return redirect("accounts:mi_domicilio")

    else:
        domicilio = DomicilioEntrega.objects.filter(
            usuario=request.user,
        ).first()

        # Propone los datos de contacto solo al cargar el primer domicilio.
        datos_iniciales = {}

        if domicilio is None:
            datos_iniciales = {
                "destinatario": request.user.get_full_name(),
                "telefono_contacto": request.user.telefono,
            }

        formulario = FormularioDomicilioEntrega(
            instance=domicilio,
            initial=datos_iniciales,
        )

    return render(
        request,
        "accounts/mi_domicilio.html",
        {"formulario": formulario},
    )