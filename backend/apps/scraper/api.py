"""
API endpoints para scraper de Reddit.
"""
from typing import List, Optional
from ninja import Router, Schema
from django.http import HttpRequest

from config.auth import JWTAuth
from .tasks import sync_reddit_posts, test_reddit_connection

router = Router(tags=["Scraper"], auth=JWTAuth())


# ============================================
# SCHEMAS
# ============================================

class SyncRequestSchema(Schema):
    """Schema para request de sincronización."""
    subreddit_ids: Optional[List[int]] = None
    limit: int = 50
    time_filter: str = "week"


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
    summary="Sincronizar posts de Reddit"
)
def sync_posts(request: HttpRequest, payload: SyncRequestSchema = None):
    """
    Inicia sincronización de posts de Reddit en background.

    - Si `subreddit_ids` está vacío o None: sincroniza todos los subreddits activos
    - Si `subreddit_ids` tiene valores: sincroniza solo esos subreddits
    - `limit`: número máximo de posts por subreddit (default: 50)
    - `time_filter`: hour, day, week, month, year, all (default: week)

    La tarea se ejecuta en background con Celery.
    """
    # Si no hay payload, usar valores por defecto
    if payload is None:
        payload = SyncRequestSchema()

    # Lanzar tarea Celery
    task = sync_reddit_posts.delay(
        subreddit_ids=payload.subreddit_ids,
        limit=payload.limit,
        time_filter=payload.time_filter
    )

    return {
        "task_id": task.id,
        "message": "Sincronización iniciada en background",
        "status": "processing"
    }


@router.post(
    "/test-connection/",
    response={200: TestConnectionResponseSchema},
    summary="Probar conexión con Reddit"
)
def test_connection(request: HttpRequest):
    """
    Prueba la conexión con la API de Reddit.

    Útil para verificar que las credenciales están configuradas correctamente.
    """
    task = test_reddit_connection.delay()

    return {
        "task_id": task.id,
        "message": "Probando conexión con Reddit..."
    }
