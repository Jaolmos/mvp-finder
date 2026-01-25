"""
Scraper de productos de Product Hunt.
Obtiene productos de topics configurados y los guarda en la base de datos.
"""
from typing import List, Dict, Optional, Any
from django.utils import timezone as django_timezone
from dateutil import parser as date_parser

from apps.topics.models import Topic
from apps.posts.models import Product
from .producthunt_client import ProductHuntClient


class ProductHuntScraper:
    """Scraper para obtener productos de Product Hunt."""

    def __init__(self):
        self.client = ProductHuntClient.get_client()

    def scrape_topic(
        self,
        topic_name: str,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Scrapes productos de un topic específico.

        Args:
            topic_name: Nombre del topic
            limit: Número máximo de productos a obtener (default: 50)

        Returns:
            Dict con resultados: {
                'topic': str,
                'new_posts': int,
                'skipped_posts': int,
                'errors': List[str]
            }
        """
        results = {
            'topic': topic_name,
            'new_products': 0,
            'skipped_products': 0,
            'errors': []
        }

        try:
            # Obtener instancia del topic desde BD
            try:
                topic_obj = Topic.objects.get(name=topic_name)
            except Topic.DoesNotExist:
                results['errors'].append(f"Topic '{topic_name}' no existe en BD")
                return results

            # Obtener products del topic usando la API
            fetched = 0
            cursor = None

            while fetched < limit:
                batch_limit = min(20, limit - fetched)
                products_data = self.client.fetch_posts(
                    topic_slug=topic_name,
                    limit=batch_limit,
                    cursor=cursor
                )

                edges = products_data.get('edges', [])
                if not edges:
                    break

                # Procesar cada product
                for edge in edges:
                    node = edge.get('node', {})
                    external_id = node.get('id')

                    # Verificar si el product ya existe
                    if Product.objects.filter(external_id=external_id).exists():
                        results['skipped_products'] += 1
                        continue

                    # Crear nuevo product
                    try:
                        product = self._create_product_from_node(node, topic_obj)
                        if product:
                            results['new_products'] += 1
                    except Exception as e:
                        results['errors'].append(f"Error al crear product {external_id}: {str(e)}")

                    fetched += 1

                # Verificar si hay más páginas
                page_info = products_data.get('pageInfo', {})
                if not page_info.get('hasNextPage'):
                    break
                cursor = page_info.get('endCursor')

            # Actualizar última sincronización del topic
            topic_obj.last_sync = django_timezone.now()
            topic_obj.save(update_fields=['last_sync', 'updated_at'])

        except Exception as e:
            results['errors'].append(f"Error al scrape topic: {str(e)}")

        return results

    def scrape_all_active_topics(
        self,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Scrapes productos de todos los topics activos.

        Args:
            limit: Número máximo de productos por topic (default: 50)

        Returns:
            List de resultados por cada topic
        """
        results = []

        # Obtener topics activos
        active_topics = Topic.objects.filter(is_active=True)

        for topic in active_topics:
            result = self.scrape_topic(
                topic_name=topic.name,
                limit=limit,
            )
            results.append(result)

        return results

    def _create_product_from_node(
        self,
        node: Dict[str, Any],
        topic_obj: Topic
    ) -> Optional[Product]:
        """
        Crea un Product desde un nodo de la API de Product Hunt.

        Args:
            node: Nodo del producto de Product Hunt
            topic_obj: Instancia de Topic de Django

        Returns:
            Product creado o None si hay error
        """
        try:
            # Parsear fecha de creación
            created_at_str = node.get('createdAt')
            created_at = date_parser.parse(created_at_str) if created_at_str else django_timezone.now()

            # Extraer maker principal (usar name si username es [REDACTED])
            makers = node.get('makers', [])
            if makers:
                username = makers[0].get('username', '')
                name = makers[0].get('name', '')
                author = name if username == '[REDACTED]' or not username else username
            else:
                author = "Anónimo"

            # Obtener votos y comentarios
            votes_count = node.get('votesCount', 0)
            comments_count = node.get('commentsCount', 0)

            # Crear contenido combinando tagline y description
            tagline = node.get('tagline', '')
            description = node.get('description', '')
            content = description if description else tagline

            # Crear product
            product = Product.objects.create(
                external_id=node.get('id'),
                topic=topic_obj,
                title=node.get('name', ''),
                tagline=tagline,
                content=content[:5000],  # Limitar a 5000 caracteres
                author=author,
                score=votes_count,
                votes_count=votes_count,
                comments_count=comments_count,
                url=node.get('url', ''),
                website=node.get('website') or None,
                created_at_source=created_at
            )

            return product

        except Exception as e:
            print(f"Error al crear product desde node: {e}")
            return None

    def get_scraping_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Genera un resumen de los resultados del scraping.

        Args:
            results: Lista de resultados por topic

        Returns:
            Dict con resumen general
        """
        total_new = sum(r['new_products'] for r in results)
        total_skipped = sum(r['skipped_products'] for r in results)
        total_errors = sum(len(r['errors']) for r in results)
        topics_processed = len(results)

        return {
            'topics_processed': topics_processed,
            'total_new_products': total_new,
            'total_skipped_products': total_skipped,
            'total_errors': total_errors,
            'details': results
        }
