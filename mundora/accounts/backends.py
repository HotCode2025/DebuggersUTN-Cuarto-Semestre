from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class AutenticacionCorreoUsuario(ModelBackend):
    """Permite ingresar con correo o nombre de usuario."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """Comprueba las credenciales y que la cuenta esté activa."""

        if username is None or password is None:
            return None

        Usuario = get_user_model()
        identificador = username.strip()

        if "@" in identificador:
            filtro = {"email__iexact": identificador}
        else:
            filtro = {"username__iexact": identificador}

        try:
            usuario = Usuario.objects.get(**filtro)
        except (Usuario.DoesNotExist, Usuario.MultipleObjectsReturned):
            # Ejecuta el cálculo de contraseña aunque no encuentre la cuenta.
            Usuario().set_password(password)
            return None

        if usuario.check_password(password) and self.user_can_authenticate(usuario):
            return usuario

        return None