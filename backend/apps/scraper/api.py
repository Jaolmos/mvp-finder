"""
API endpoints para scraper de Product Hunt y análisis IA.
"""
from typing import List, Optional
from ninja import Router, Schema
from django.http import HttpRequest

from config.auth import JWTAuth
from .tasks import sync_products, test_connection, analyze_products, check_ollama, pull_ollama_model
from .ai_analyzer import OllamaClient

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


class AnalyzeRequestSchema(Schema):
    """Schema para request de análisis IA."""
    product_ids: Optional[List[int]] = None
    limit: int = 10


class OllamaStatusSchema(Schema):
    """Schema para estado de Ollama."""
    host: str
    model: str
    ollama_available: bool
    model_available: bool
    ready: bool


# ============================================
# ENDPOINTS
# ============================================

@router.post(
    "/sync/",
    response={200: TaskResponseSchema},
    summary="Sincronizar productos de Product Hunt"
)
def sync_products_endpoint(request: HttpRequest, payload: SyncRequestSchema = None):
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
    task = sync_products.delay(
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


# ============================================
# ENDPOINTS OLLAMA / ANÁLISIS IA
# ============================================

@router.post(
    "/analyze/",
    response={200: TaskResponseSchema},
    summary="Analizar productos con IA"
)
def analyze_products_endpoint(request: HttpRequest, payload: AnalyzeRequestSchema = None):
    """
    Inicia análisis de productos con Ollama en background.

    - Si `product_ids` está vacío o None: analiza productos no analizados
    - Si `product_ids` tiene valores: analiza solo esos productos
    - `limit`: número máximo de productos a analizar (default: 10)

    Requiere que Ollama esté disponible y el modelo descargado.
    """
    if payload is None:
        payload = AnalyzeRequestSchema()

    task = analyze_products.delay(
        product_ids=payload.product_ids,
        limit=payload.limit,
    )

    return {
        "task_id": task.id,
        "message": "Análisis iniciado en background",
        "status": "processing"
    }


@router.get(
    "/ollama-status/",
    response={200: OllamaStatusSchema},
    summary="Verificar estado de Ollama"
)
def get_ollama_status(request: HttpRequest):
    """
    Obtiene el estado de Ollama y el modelo configurado.

    Retorna:
    - `ollama_available`: Si Ollama está corriendo
    - `model_available`: Si el modelo está descargado
    - `ready`: Si está listo para analizar (ambos true)
    """
    client = OllamaClient.get_client()
    return client.get_status()


@router.post(
    "/pull-model/",
    response={200: TaskResponseSchema},
    summary="Descargar modelo de Ollama"
)
def pull_model_endpoint(request: HttpRequest):
    """
    Inicia la descarga del modelo de Ollama en background.

    El modelo configurado es: OLLAMA_MODEL en .env (default: llama3.2:1b)
    """
    task = pull_ollama_model.delay()

    return {
        "task_id": task.id,
        "message": "Descarga de modelo iniciada en background",
        "status": "processing"
    }
