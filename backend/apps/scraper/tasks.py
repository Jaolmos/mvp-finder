"""
Tareas Celery para scraping de Product Hunt.
Ejecutan operaciones en background sin bloquear la API.
"""
from celery import shared_task
from typing import List, Optional
import logging

from .scraper import ProductHuntScraper

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
