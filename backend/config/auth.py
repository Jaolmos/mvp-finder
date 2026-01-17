"""
Autenticación JWT para Django Ninja.
"""

from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import User


class JWTAuth(HttpBearer):
    """
    Clase de autenticación JWT para Django Ninja.

    Valida el token JWT del header Authorization: Bearer <token>
    y retorna el usuario autenticado.
    """

    def authenticate(self, request, token):
        """
        Valida el token JWT y retorna el usuario.

        Args:
            request: HttpRequest de Django
            token: Token JWT extraído del header Authorization

        Returns:
            User: Usuario autenticado si el token es válido
            None: Si el token es inválido
        """
        try:
            # Validar y decodificar el token
            access_token = AccessToken(token)
            user_id = access_token['user_id']

            # Obtener el usuario
            user = User.objects.get(id=user_id)
            return user

        except (InvalidToken, TokenError, User.DoesNotExist):
            return None
