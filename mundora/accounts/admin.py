from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class AdministradorUsuario(UserAdmin):
    """Administra cuentas conservando las funciones de autenticación."""

    # Columnas visibles en el listado de usuarios.
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "telefono",
        "is_staff",
        "is_active",
    )

    # Campos disponibles para buscar una cuenta.
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "telefono",
    )

    # Agrega el teléfono al formulario de edición.
    fieldsets = UserAdmin.fieldsets + (
        (
            "Contacto adicional",
            {
                "fields": ("telefono",),
            },
        ),
    )

    # Agrega los datos personales al formulario de creación.
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Datos personales",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "telefono",
                ),
            },
        ),
    )
