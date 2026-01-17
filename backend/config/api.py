"""
API principal con Django Ninja.
"""

from ninja import NinjaAPI, Schema
from ninja.responses import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .auth import JWTAuth

# Crear instancia de la API
api = NinjaAPI(
    title="Reddit MVP Finder API",
    version="1.0.0",
    description="API para gestionar posts de Reddit y encontrar ideas de MVPs"
)

# Registrar routers de las apps
from apps.posts.api import router as posts_router
from apps.subreddits.api import router as subreddits_router

api.add_router("/posts", posts_router)
api.add_router("/subreddits", subreddits_router)


# Schemas para autenticación
class LoginSchema(Schema):
    """Schema para login."""
    username: str
    password: str


class TokenSchema(Schema):
    """Schema para respuesta de tokens."""
    access: str
    refresh: str


class RefreshSchema(Schema):
    """Schema para refresh token."""
    refresh: str


class UserInfoSchema(Schema):
    """Schema para información del usuario."""
    id: int
    username: str
    email: str
    first_name: str
    last_name: str


class MessageSchema(Schema):
    """Schema para mensajes generales."""
    message: str


# Endpoints de autenticación
@api.post("/auth/login/", response={200: TokenSchema, 401: MessageSchema}, auth=None)
def login(request, payload: LoginSchema):
    """
    Login con username y password.

    Retorna access_token y refresh_token si las credenciales son correctas.
    """
    user = authenticate(username=payload.username, password=payload.password)

    if user is None:
        return 401, {"message": "Credenciales inválidas"}

    # Generar tokens JWT
    refresh = RefreshToken.for_user(user)

    return 200, {
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    }


@api.post("/auth/refresh/", response={200: TokenSchema, 401: MessageSchema}, auth=None)
def refresh_token(request, payload: RefreshSchema):
    """
    Renovar access_token usando refresh_token.

    Retorna un nuevo access_token.
    """
    try:
        refresh = RefreshToken(payload.refresh)
        return 200, {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
    except Exception:
        return 401, {"message": "Refresh token inválido"}


@api.get("/auth/me/", response=UserInfoSchema, auth=JWTAuth())
def get_current_user(request):
    """
    Obtener información del usuario actual autenticado.

    Requiere token JWT válido en el header Authorization.
    """
    user = request.auth
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    }
