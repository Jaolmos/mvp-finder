"""
API de topics con Django Ninja.
"""

from ninja import Router, Schema
from typing import List, Optional
from datetime import datetime
from django.shortcuts import get_object_or_404
from config.auth import JWTAuth
from .models import Topic

router = Router(tags=["Topics"])


# Schemas
class TopicSchema(Schema):
    """Schema para topic."""
    id: int
    name: str
    is_active: bool
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TopicCreateSchema(Schema):
    """Schema para crear topic."""
    name: str
    is_active: bool = True


class TopicUpdateSchema(Schema):
    """Schema para actualizar topic."""
    name: Optional[str] = None
    is_active: Optional[bool] = None


class MessageSchema(Schema):
    """Schema para mensajes."""
    message: str


# Endpoints
@router.get("/", response=List[TopicSchema], auth=JWTAuth())
def list_topics(request):
    """
    Listar todos los topics.

    Requiere autenticación JWT.
    """
    return Topic.objects.all()


@router.get("/{topic_id}/", response=TopicSchema, auth=JWTAuth())
def get_topic(request, topic_id: int):
    """
    Obtener detalle de un topic.

    Requiere autenticación JWT.
    """
    return get_object_or_404(Topic, id=topic_id)


@router.post("/", response={201: TopicSchema}, auth=JWTAuth())
def create_topic(request, payload: TopicCreateSchema):
    """
    Crear un nuevo topic.

    Requiere autenticación JWT.
    """
    topic = Topic.objects.create(**payload.dict())
    return 201, topic


@router.put("/{topic_id}/", response=TopicSchema, auth=JWTAuth())
def update_topic(request, topic_id: int, payload: TopicUpdateSchema):
    """
    Actualizar un topic.

    Requiere autenticación JWT.
    """
    topic = get_object_or_404(Topic, id=topic_id)

    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(topic, attr, value)

    topic.save()
    return topic


@router.delete("/{topic_id}/", response={200: MessageSchema}, auth=JWTAuth())
def delete_topic(request, topic_id: int):
    """
    Eliminar un topic.

    Requiere autenticación JWT.
    """
    topic = get_object_or_404(Topic, id=topic_id)
    topic_name = topic.name
    topic.delete()

    return 200, {"message": f"Topic {topic_name} eliminado correctamente"}
