"""
API de subreddits con Django Ninja.
"""

from ninja import Router, Schema
from typing import List, Optional
from datetime import datetime
from django.shortcuts import get_object_or_404
from config.auth import JWTAuth
from .models import Subreddit

router = Router(tags=["Subreddits"])


# Schemas
class SubredditSchema(Schema):
    """Schema para subreddit."""
    id: int
    name: str
    active: bool
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class SubredditCreateSchema(Schema):
    """Schema para crear subreddit."""
    name: str
    active: bool = True


class SubredditUpdateSchema(Schema):
    """Schema para actualizar subreddit."""
    name: Optional[str] = None
    active: Optional[bool] = None


class MessageSchema(Schema):
    """Schema para mensajes."""
    message: str


# Endpoints
@router.get("/", response=List[SubredditSchema], auth=JWTAuth())
def list_subreddits(request):
    """
    Listar todos los subreddits.

    Requiere autenticación JWT.
    """
    return Subreddit.objects.all()


@router.get("/{subreddit_id}/", response=SubredditSchema, auth=JWTAuth())
def get_subreddit(request, subreddit_id: int):
    """
    Obtener detalle de un subreddit.

    Requiere autenticación JWT.
    """
    return get_object_or_404(Subreddit, id=subreddit_id)


@router.post("/", response={201: SubredditSchema}, auth=JWTAuth())
def create_subreddit(request, payload: SubredditCreateSchema):
    """
    Crear un nuevo subreddit.

    Requiere autenticación JWT.
    """
    subreddit = Subreddit.objects.create(**payload.dict())
    return 201, subreddit


@router.put("/{subreddit_id}/", response=SubredditSchema, auth=JWTAuth())
def update_subreddit(request, subreddit_id: int, payload: SubredditUpdateSchema):
    """
    Actualizar un subreddit.

    Requiere autenticación JWT.
    """
    subreddit = get_object_or_404(Subreddit, id=subreddit_id)

    # Actualizar solo los campos proporcionados
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(subreddit, attr, value)

    subreddit.save()
    return subreddit


@router.delete("/{subreddit_id}/", response={200: MessageSchema}, auth=JWTAuth())
def delete_subreddit(request, subreddit_id: int):
    """
    Eliminar un subreddit.

    Requiere autenticación JWT.
    """
    subreddit = get_object_or_404(Subreddit, id=subreddit_id)
    subreddit_name = subreddit.name
    subreddit.delete()

    return 200, {"message": f"Subreddit r/{subreddit_name} eliminado correctamente"}
