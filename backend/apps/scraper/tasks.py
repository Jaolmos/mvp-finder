"""
Tareas Celery para scraping de Reddit.
Ejecutan operaciones en background sin bloquear la API.
"""
from celery import shared_task
from typing import List, Optional
import logging

from .scraper import RedditScraper

logger = logging.getLogger(__name__)


@shared_task(name='scraper.sync_reddit_posts')
def sync_reddit_posts(
    subreddit_ids: Optional[List[int]] = None,
    limit: int = 50,
    time_filter: str = "week"
) -> dict:
    """
    Tarea Celery para sincronizar posts de Reddit.

    Args:
        subreddit_ids: Lista de IDs de subreddits a sincronizar.
                       Si es None, sincroniza todos los activos.
        limit: Número máximo de posts por subreddit (default: 50)
        time_filter: Filtro temporal: hour, day, week, month, year, all (default: week)

    Returns:
        Dict con resumen de la sincronización
    """
    logger.info(f"Iniciando sincronización de posts. Subreddits: {subreddit_ids or 'todos'}")

    try:
        scraper = RedditScraper()

        # Si se especifican subreddits concretos
        if subreddit_ids:
            from apps.subreddits.models import Subreddit
            results = []

            for subreddit_id in subreddit_ids:
                try:
                    subreddit = Subreddit.objects.get(id=subreddit_id, active=True)
                    result = scraper.scrape_subreddit(
                        subreddit_name=subreddit.name,
                        limit=limit,
                        time_filter=time_filter
                    )
                    results.append(result)
                except Subreddit.DoesNotExist:
                    logger.warning(f"Subreddit con ID {subreddit_id} no existe o no está activo")
                    results.append({
                        'subreddit': f'ID:{subreddit_id}',
                        'new_posts': 0,
                        'skipped_posts': 0,
                        'errors': ['Subreddit no encontrado o inactivo']
                    })
        else:
            # Sincronizar todos los subreddits activos
            results = scraper.scrape_all_active_subreddits(
                limit=limit,
                time_filter=time_filter
            )

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


@shared_task(name='scraper.test_reddit_connection')
def test_reddit_connection() -> dict:
    """
    Tarea de prueba para verificar conexión con Reddit.

    Returns:
        Dict indicando si la conexión fue exitosa
    """
    try:
        from .reddit_client import RedditClient

        success = RedditClient.test_connection()

        if success:
            logger.info("Conexión con Reddit exitosa")
            return {'status': 'success', 'message': 'Conexión con Reddit exitosa'}
        else:
            logger.error("Fallo al conectar con Reddit")
            return {'status': 'error', 'message': 'Fallo al conectar con Reddit'}

    except Exception as e:
        logger.error(f"Error al probar conexión: {str(e)}", exc_info=True)
        return {'status': 'error', 'error': str(e)}
