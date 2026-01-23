"""
Tareas Celery para scraping de Product Hunt y análisis IA.
Ejecutan operaciones en background sin bloquear la API.
"""
from celery import shared_task
from typing import List, Optional
import logging

from .scraper import ProductHuntScraper
from .ai_analyzer import OllamaClient, PostAnalyzer

logger = logging.getLogger(__name__)


@shared_task(name='scraper.sync_posts')
def sync_posts(
    topic_ids: Optional[List[int]] = None,
    limit: int = 50,
) -> dict:
    """
    Tarea Celery para sincronizar productos de Product Hunt.

    Args:
        topic_ids: Lista de IDs de topics a sincronizar.
                   Si es None, sincroniza todos los activos.
        limit: Número máximo de productos por topic (default: 50)

    Returns:
        Dict con resumen de la sincronización
    """
    logger.info(f"Iniciando sincronización de posts. Topics: {topic_ids or 'todos'}")

    try:
        scraper = ProductHuntScraper()

        # Si se especifican topics concretos
        if topic_ids:
            from apps.topics.models import Topic
            results = []

            for topic_id in topic_ids:
                try:
                    topic = Topic.objects.get(id=topic_id, is_active=True)
                    result = scraper.scrape_topic(
                        topic_name=topic.name,
                        limit=limit,
                    )
                    results.append(result)
                except Topic.DoesNotExist:
                    logger.warning(f"Topic con ID {topic_id} no existe o no está activo")
                    results.append({
                        'topic': f'ID:{topic_id}',
                        'new_posts': 0,
                        'skipped_posts': 0,
                        'errors': ['Topic no encontrado o inactivo']
                    })
        else:
            # Sincronizar todos los topics activos
            results = scraper.scrape_all_active_topics(limit=limit)

        # Generar resumen
        summary = scraper.get_scraping_summary(results)

        logger.info(
            f"Sincronización completada. "
            f"Nuevos posts: {summary['total_new_posts']}, "
            f"Omitidos: {summary['total_skipped_posts']}, "
            f"Errores: {summary['total_errors']}"
        )

        return {
            'status': 'success',
            'summary': summary
        }

    except Exception as e:
        logger.error(f"Error en sincronización de posts: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task(name='scraper.test_connection')
def test_connection() -> dict:
    """
    Tarea de prueba para verificar conexión con Product Hunt.

    Returns:
        Dict indicando si la conexión fue exitosa
    """
    try:
        from .producthunt_client import ProductHuntClient

        success = ProductHuntClient.test_connection()

        if success:
            logger.info("Conexión con Product Hunt exitosa")
            return {'status': 'success', 'message': 'Conexión con Product Hunt exitosa'}
        else:
            logger.error("Fallo al conectar con Product Hunt")
            return {'status': 'error', 'message': 'Fallo al conectar con Product Hunt'}

    except Exception as e:
        logger.error(f"Error al probar conexión: {str(e)}", exc_info=True)
        return {'status': 'error', 'error': str(e)}


@shared_task(name='scraper.analyze_posts')
def analyze_posts(post_ids: Optional[List[int]] = None, limit: int = 10) -> dict:
    """
    Tarea Celery para analizar posts con Ollama.

    Args:
        post_ids: Lista de IDs específicos a analizar.
                  Si es None, analiza posts no analizados.
        limit: Número máximo de posts a analizar (default: 10)

    Returns:
        Dict con resumen del análisis
    """
    from apps.posts.models import Post

    logger.info(f"Iniciando análisis de posts. IDs: {post_ids or 'no analizados'}, limit: {limit}")

    try:
        client = OllamaClient.get_client()

        # Verificar que Ollama esté disponible
        if not client.is_available():
            return {
                'status': 'error',
                'error': 'Ollama no está disponible'
            }

        if not client.is_model_available():
            return {
                'status': 'error',
                'error': f'Modelo {client.model} no está descargado. Usa /api/scraper/pull-model/ primero.'
            }

        analyzer = PostAnalyzer(client)

        # Seleccionar posts a analizar
        if post_ids:
            posts = Post.objects.filter(id__in=post_ids)
        else:
            posts = Post.objects.filter(analyzed=False)[:limit]

        analyzed = 0
        failed = 0
        errors = []

        for post in posts:
            try:
                result = analyzer.analyze_post(post)
                if result:
                    analyzer.update_post_with_analysis(post, result)
                    analyzed += 1
                    logger.info(f"Post {post.id} analizado correctamente")
                else:
                    failed += 1
                    errors.append(f"Post {post.id}: Sin respuesta de Ollama")
            except Exception as e:
                failed += 1
                errors.append(f"Post {post.id}: {str(e)}")
                logger.error(f"Error al analizar post {post.id}: {e}")

        logger.info(f"Análisis completado. Analizados: {analyzed}, Fallidos: {failed}")

        return {
            'status': 'success',
            'analyzed': analyzed,
            'failed': failed,
            'errors': errors[:10] if errors else []
        }

    except Exception as e:
        logger.error(f"Error en análisis de posts: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task(name='scraper.check_ollama')
def check_ollama() -> dict:
    """
    Tarea para verificar estado de Ollama y modelo.

    Returns:
        Dict con estado de Ollama
    """
    try:
        client = OllamaClient.get_client()
        status = client.get_status()

        logger.info(f"Estado de Ollama: {status}")
        return {
            'status': 'success',
            **status
        }

    except Exception as e:
        logger.error(f"Error al verificar Ollama: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task(name='scraper.pull_ollama_model')
def pull_ollama_model() -> dict:
    """
    Tarea para descargar el modelo de Ollama configurado.

    Returns:
        Dict con resultado de la descarga
    """
    try:
        client = OllamaClient.get_client()

        if not client.is_available():
            return {
                'status': 'error',
                'error': 'Ollama no está disponible'
            }

        logger.info(f"Iniciando descarga del modelo {client.model}")
        result = client.pull_model()

        if result['status'] == 'success':
            logger.info(f"Modelo {client.model} descargado correctamente")
        else:
            logger.error(f"Error al descargar modelo: {result.get('message')}")

        return result

    except Exception as e:
        logger.error(f"Error al descargar modelo: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e)
        }
