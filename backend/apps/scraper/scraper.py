"""
Scraper de posts de Reddit.
Obtiene posts de subreddits configurados y los guarda en la base de datos.
"""
from typing import List, Dict, Optional
from datetime import datetime, timezone
from django.db import transaction
from django.utils import timezone as django_timezone

from apps.subreddits.models import Subreddit
from apps.posts.models import Post
from .reddit_client import RedditClient


class RedditScraper:
    """Scraper para obtener posts de Reddit."""

    def __init__(self):
        self.reddit = RedditClient.get_client()

    def scrape_subreddit(
        self,
        subreddit_name: str,
        limit: int = 50,
        time_filter: str = "week"
    ) -> Dict[str, any]:
        """
        Scrapes posts from a specific subreddit.

        Args:
            subreddit_name: Nombre del subreddit (sin 'r/')
            limit: Número máximo de posts a obtener (default: 50)
            time_filter: Filtro temporal: hour, day, week, month, year, all (default: week)

        Returns:
            Dict con resultados: {
                'subreddit': str,
                'new_posts': int,
                'skipped_posts': int,
                'errors': List[str]
            }
        """
        results = {
            'subreddit': subreddit_name,
            'new_posts': 0,
            'skipped_posts': 0,
            'errors': []
        }

        try:
            # Obtener instancia del subreddit desde BD
            try:
                subreddit_obj = Subreddit.objects.get(name=subreddit_name)
            except Subreddit.DoesNotExist:
                results['errors'].append(f"Subreddit '{subreddit_name}' no existe en BD")
                return results

            # Obtener posts del subreddit usando PRAW
            subreddit = self.reddit.subreddit(subreddit_name)
            submissions = subreddit.top(time_filter=time_filter, limit=limit)

            # Procesar cada post
            for submission in submissions:
                # Verificar si el post ya existe (por reddit_id)
                if Post.objects.filter(reddit_id=submission.id).exists():
                    results['skipped_posts'] += 1
                    continue

                # Crear nuevo post
                try:
                    post = self._create_post_from_submission(submission, subreddit_obj)
                    if post:
                        results['new_posts'] += 1
                except Exception as e:
                    results['errors'].append(f"Error al crear post {submission.id}: {str(e)}")

            # Actualizar última sincronización del subreddit
            subreddit_obj.last_sync = django_timezone.now()
            subreddit_obj.save(update_fields=['last_sync', 'updated_at'])

        except Exception as e:
            results['errors'].append(f"Error al scrape subreddit: {str(e)}")

        return results

    def scrape_all_active_subreddits(
        self,
        limit: int = 50,
        time_filter: str = "week"
    ) -> List[Dict[str, any]]:
        """
        Scrapes posts from all active subreddits.

        Args:
            limit: Número máximo de posts por subreddit (default: 50)
            time_filter: Filtro temporal (default: week)

        Returns:
            List de resultados por cada subreddit
        """
        results = []

        # Obtener subreddits activos
        active_subreddits = Subreddit.objects.filter(active=True)

        for subreddit in active_subreddits:
            result = self.scrape_subreddit(
                subreddit_name=subreddit.name,
                limit=limit,
                time_filter=time_filter
            )
            results.append(result)

        return results

    def _create_post_from_submission(
        self,
        submission,
        subreddit_obj: Subreddit
    ) -> Optional[Post]:
        """
        Crea un Post desde un submission de PRAW.

        Args:
            submission: Objeto Submission de PRAW
            subreddit_obj: Instancia de Subreddit de Django

        Returns:
            Post creado o None si hay error
        """
        try:
            # Convertir timestamp Unix a datetime
            created_at = datetime.fromtimestamp(
                submission.created_utc,
                tz=timezone.utc
            )

            # Extraer contenido (selftext o URL)
            content = submission.selftext if submission.selftext else ""
            if not content and submission.url:
                content = f"Link: {submission.url}"

            # Crear post
            post = Post.objects.create(
                reddit_id=submission.id,
                subreddit=subreddit_obj,
                title=submission.title,
                content=content[:5000],  # Limitar a 5000 caracteres
                author=str(submission.author) if submission.author else "[deleted]",
                score=submission.score,
                url=submission.url,
                created_at_reddit=created_at
            )

            return post

        except Exception as e:
            print(f"Error al crear post desde submission: {e}")
            return None

    def get_scraping_summary(self, results: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Genera un resumen de los resultados del scraping.

        Args:
            results: Lista de resultados por subreddit

        Returns:
            Dict con resumen general
        """
        total_new = sum(r['new_posts'] for r in results)
        total_skipped = sum(r['skipped_posts'] for r in results)
        total_errors = sum(len(r['errors']) for r in results)
        subreddits_processed = len(results)

        return {
            'subreddits_processed': subreddits_processed,
            'total_new_posts': total_new,
            'total_skipped_posts': total_skipped,
            'total_errors': total_errors,
            'details': results
        }
