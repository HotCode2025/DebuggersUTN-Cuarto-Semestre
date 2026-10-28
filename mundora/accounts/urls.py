from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views


# Identifica las rutas de la aplicación de cuentas.
app_name = "accounts"

urlpatterns = [
    # Permite crear una cuenta.
    path("registro/", views.registro, name="registro"),
    #permite iniciar sesion
    path(
        "iniciar-sesion/",
        views.VistaInicioSesion.as_view(),
        name="iniciar_sesion",
    ),
    #muestra los datos de la cuenta autenticada.
    path("mi-cuenta/", views.mi_cuenta, name="mi_cuenta"),

    #cierra la sesion mediante una solicitud POST.
    path(
        "cerrar-sesion/",
        LogoutView.as_view(),
        name="cerrar_sesion",
        ),
    
    # Permite completar y modificar el domicilio habitual de entrega.
    path(
        "mi-domicilio/",
        views.mi_domicilio,
        name="mi_domicilio",
    ),
]