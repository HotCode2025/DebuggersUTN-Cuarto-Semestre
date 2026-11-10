from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.deletion import ProtectedError, RestrictedError
from django.shortcuts import redirect, render
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods


@sensitive_post_parameters("clave")
@login_required
@require_http_methods(["GET", "POST"])
def eliminar_cuenta(request):
    """Elimina únicamente la cuenta autenticada, si no tiene vínculos protegidos."""
    plantilla = "accounts/eliminar_cuenta.html"
    if request.method == "GET":
        return render(request, plantilla)

    try:
        with transaction.atomic():
            usuario = get_user_model().objects.select_for_update().get(pk=request.user.pk)
            if not usuario.check_password(request.POST.get("clave", "")):
                return render(request, plantilla, {"error": "La contraseña no coincide."})

            if usuario.is_staff or usuario.is_superuser:
                messages.error(request, "Las cuentas administrativas no se eliminan desde el perfil.")
                return redirect("accounts:mi_cuenta")

            if usuario.compras.exists() or hasattr(usuario, "tienda"):
                messages.error(request, "Tu cuenta tiene compras o una tienda asociada y no se puede eliminar.")
                return redirect("accounts:mi_cuenta")

            usuario.delete()
    except (ProtectedError, RestrictedError):
        messages.error(request, "Hay registros asociados que impiden eliminar tu cuenta.")
        return redirect("accounts:mi_cuenta")

    logout(request)
    messages.success(request, "Tu cuenta se eliminó.")
    return redirect("accounts:iniciar_sesion")
