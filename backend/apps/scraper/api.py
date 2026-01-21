"""
API endpoints para scraper de Product Hunt.
"""
from typing import List, Optional
from ninja import Router, Schema
from django.http import HttpRequest

from config.auth import JWTAuth
from .tasks import sync_posts, test_connection

router = Router(tags=["Scraper"], auth=JWTAuth())


# ============================================
# SCHEMAS
# ============================================

class SyncRequestSchema(Schema):
    """Schema para request de sincronización."""
    topic_ids: Optional[List[int]] = None
    limit: int = 50


class TaskResponseSchema(Schema):
    """Schema para respuesta de tarea iniciada."""
    task_id: str
    message: str
    status: str


class TestConnectionResponseSchema(Schema):
    """Schema para respuesta de test de conexión."""
    task_id: str
    message: str


# ============================================
# ENDPOINTS
# ============================================

@router.post(
    "/sync/",
    response={200: TaskResponseSchema},
    summary="Sincronizar productos de Product Hunt"
)
def sync_products(request: HttpRequest, payload: SyncRequestSchema = None):
    """
    Inicia sincronización de productos de Product Hunt en background.

    - Si `topic_ids` está vacío o None: sincroniza todos los topics activos
    - Si `topic_ids` tiene valores: sincroniza solo esos topics
    - `limit`: número máximo de productos por topic (default: 50)

    La tarea se ejecuta en background con Celery.
    """
    # Si no hay payload, usar valores por defecto
    if payload is None:
        payload = SyncRequestSchema()

    # Lanzar tarea Celery
    task = sync_posts.delay(
        topic_ids=payload.topic_ids,
        limit=payload.limit,
    )

    return {
        "task_id": task.id,
        "message": "Sincronización iniciada en background",
        "status": "processing"
    }


@router.post(
    "/test-connection/",
    response={200: TestConnectionResponseSchema},
    summary="Probar conexión con Product Hunt"
)
def test_producthunt_connection(request: HttpRequest):
    """
    Prueba la conexión con la API de Product Hunt.

    Útil para verificar que la API key está configurada correctamente.
    """
    task = test_connection.delay()

    return {
        "task_id": task.id,
        "message": "Probando conexión con Product Hunt..."
    }
