"""
Tests para el scraper de Product Hunt.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from apps.scraper.scraper import ProductHuntScraper
from apps.scraper.producthunt_client import ProductHuntClient
from apps.topics.models import Topic
from apps.posts.models import Product


@pytest.fixture
def mock_ph_client():
    """Mock del cliente de Product Hunt."""
    with patch('apps.scraper.scraper.ProductHuntClient.get_client') as mock:
        yield mock.return_value


@pytest.fixture
def mock_ph_response():
    """Mock de respuesta de la API de Product Hunt."""
    return {
        'edges': [
            {
                'cursor': 'cursor123',
                'node': {
                    'id': 'ph_test123',
                    'name': 'Test Product',
                    'tagline': 'A great product',
                    'description': 'This is a test product description.',
                    'url': 'https://producthunt.com/posts/test-product',
                    'website': 'https://testproduct.com',
                    'votesCount': 500,
                    'commentsCount': 45,
                    'createdAt': '2026-01-15T10:00:00Z',
                    'makers': [
                        {'username': 'testmaker'}
                    ]
                }
            }
        ],
        'pageInfo': {
            'hasNextPage': False,
            'endCursor': 'cursor123'
        }
    }


@pytest.mark.django_db
class TestProductHuntScraper:
    """Tests para la clase ProductHuntScraper."""

    def test_scraper_initialization(self, mock_ph_client):
        """Test: El scraper se inicializa correctamente."""
        scraper = ProductHuntScraper()
        assert scraper.client is not None

    def test_scrape_topic_creates_new_products(
        self,
        mock_ph_client,
        mock_ph_response,
        topic
    ):
        """Test: Scraping crea productos nuevos."""
        # Setup
        mock_ph_client.fetch_posts.return_value = mock_ph_response
        scraper = ProductHuntScraper()

        # Execute
        result = scraper.scrape_topic(topic.name, limit=10)

        # Assert
        assert result['new_products'] == 1
        assert result['skipped_products'] == 0
        assert len(result['errors']) == 0
        assert Product.objects.count() == 1

        # Verificar el producto creado
        product = Product.objects.first()
        assert product.external_id == "ph_test123"
        assert product.title == "Test Product"
        assert product.topic == topic

    def test_scrape_topic_skips_duplicates(
        self,
        mock_ph_client,
        mock_ph_response,
        topic,
        product
    ):
        """Test: Scraping omite productos duplicados."""
        # Setup - modificar mock para usar el mismo external_id
        mock_ph_response['edges'][0]['node']['id'] = product.external_id
        mock_ph_client.fetch_posts.return_value = mock_ph_response
        scraper = ProductHuntScraper()

        # Execute
        result = scraper.scrape_topic(topic.name, limit=10)

        # Assert
        assert result['new_products'] == 0
        assert result['skipped_products'] == 1
        assert Product.objects.count() == 1  # No se creó uno nuevo

    def test_scrape_topic_nonexistent(self, mock_ph_client):
        """Test: Scraping de topic que no existe en BD."""
        scraper = ProductHuntScraper()

        # Execute
        result = scraper.scrape_topic("nonexistent-topic", limit=10)

        # Assert
        assert result['new_products'] == 0
        assert result['skipped_products'] == 0
        assert len(result['errors']) == 1
        assert "no existe en BD" in result['errors'][0]

    def test_scrape_topic_updates_last_sync(
        self,
        mock_ph_client,
        mock_ph_response,
        topic
    ):
        """Test: Scraping actualiza last_sync del topic."""
        # Setup
        mock_ph_client.fetch_posts.return_value = mock_ph_response
        scraper = ProductHuntScraper()
        original_last_sync = topic.last_sync

        # Execute
        scraper.scrape_topic(topic.name, limit=10)

        # Assert
        topic.refresh_from_db()
        assert topic.last_sync != original_last_sync

    def test_scrape_all_active_topics(
        self,
        mock_ph_client,
        topic
    ):
        """Test: Scraping de todos los topics activos."""
        # Setup - Crear segundo topic activo
        topic2 = Topic.objects.create(name="productivity", is_active=True)

        # Crear mock responses diferentes para cada topic
        def create_mock_response(topic_name):
            return {
                'edges': [{
                    'cursor': 'cursor123',
                    'node': {
                        'id': f'ph_{topic_name}_product123',
                        'name': f'Test Product from {topic_name}',
                        'tagline': 'A great product',
                        'description': 'Test content',
                        'url': f'https://producthunt.com/posts/{topic_name}-test',
                        'website': f'https://{topic_name}.com',
                        'votesCount': 100,
                        'commentsCount': 10,
                        'createdAt': '2026-01-15T10:00:00Z',
                        'makers': [{'username': 'testmaker'}]
                    }
                }],
                'pageInfo': {'hasNextPage': False, 'endCursor': 'cursor123'}
            }

        mock_ph_client.fetch_posts.side_effect = [
            create_mock_response(topic.name),
            create_mock_response(topic2.name)
        ]
        scraper = ProductHuntScraper()

        # Execute
        results = scraper.scrape_all_active_topics(limit=10)

        # Assert
        assert len(results) == 2
        assert Product.objects.count() == 2

    def test_scrape_all_skips_inactive_topics(
        self,
        mock_ph_client,
        mock_ph_response
    ):
        """Test: Scraping omite topics inactivos."""
        # Setup
        mock_ph_client.fetch_posts.return_value = mock_ph_response
        scraper = ProductHuntScraper()

        # Crear topic inactivo
        Topic.objects.create(name="inactive-topic", is_active=False)

        # Execute
        results = scraper.scrape_all_active_topics(limit=10)

        # Assert
        assert len(results) == 0  # No debería procesar ninguno

    def test_create_product_from_node(
        self,
        mock_ph_client,
        topic
    ):
        """Test: Creación de producto desde nodo de Product Hunt."""
        scraper = ProductHuntScraper()

        node = {
            'id': 'ph_node123',
            'name': 'Test Node Product',
            'tagline': 'Test tagline',
            'description': 'Test description',
            'url': 'https://producthunt.com/posts/test-node',
            'website': 'https://testnode.com',
            'votesCount': 200,
            'commentsCount': 25,
            'createdAt': '2026-01-15T10:00:00Z',
            'makers': [{'username': 'nodemaker'}]
        }

        # Execute
        product = scraper._create_product_from_node(node, topic)

        # Assert
        assert product is not None
        assert product.external_id == "ph_node123"
        assert product.title == "Test Node Product"
        assert product.tagline == "Test tagline"
        assert product.author == "nodemaker"
        assert product.score == 200
        assert product.topic == topic

    def test_create_product_from_node_no_makers(self, mock_ph_client, topic):
        """Test: Creación de producto sin makers."""
        scraper = ProductHuntScraper()

        node = {
            'id': 'ph_nomaker123',
            'name': 'No Maker Product',
            'tagline': 'Test tagline',
            'description': 'Content',
            'url': 'https://producthunt.com/posts/nomaker',
            'website': None,
            'votesCount': 50,
            'commentsCount': 5,
            'createdAt': '2026-01-15T10:00:00Z',
            'makers': []
        }

        # Execute
        product = scraper._create_product_from_node(node, topic)

        # Assert
        assert product is not None
        assert product.author == "unknown"

    def test_create_product_from_node_no_description(self, mock_ph_client, topic):
        """Test: Creación de producto sin description (usa tagline)."""
        scraper = ProductHuntScraper()

        node = {
            'id': 'ph_nodesc123',
            'name': 'No Description Product',
            'tagline': 'Just a tagline',
            'description': '',
            'url': 'https://producthunt.com/posts/nodesc',
            'website': None,
            'votesCount': 30,
            'commentsCount': 2,
            'createdAt': '2026-01-15T10:00:00Z',
            'makers': [{'username': 'maker'}]
        }

        # Execute
        product = scraper._create_product_from_node(node, topic)

        # Assert
        assert product is not None
        assert product.content == "Just a tagline"

    def test_get_scraping_summary(self, mock_ph_client):
        """Test: Generación de resumen de scraping."""
        scraper = ProductHuntScraper()

        results = [
            {'topic': 'artificial-intelligence', 'new_products': 5, 'skipped_products': 2, 'errors': []},
            {'topic': 'productivity', 'new_products': 3, 'skipped_products': 1, 'errors': ['error1']},
        ]

        # Execute
        summary = scraper.get_scraping_summary(results)

        # Assert
        assert summary['topics_processed'] == 2
        assert summary['total_new_products'] == 8
        assert summary['total_skipped_products'] == 3
        assert summary['total_errors'] == 1
        assert len(summary['details']) == 2


@pytest.mark.django_db
class TestProductHuntClient:
    """Tests para ProductHuntClient."""

    def test_client_requires_api_key(self):
        """Test: Cliente requiere API key."""
        ProductHuntClient.reset_client()
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Falta API key"):
                ProductHuntClient.get_client()

    def test_client_singleton_pattern(self):
        """Test: Cliente usa patrón singleton."""
        with patch.dict('os.environ', {
            'PRODUCT_HUNT_API_KEY': 'test_key'
        }):
            # Reset singleton
            ProductHuntClient.reset_client()

            client1 = ProductHuntClient.get_client()
            client2 = ProductHuntClient.get_client()

            assert client1 is client2

    def test_client_headers(self):
        """Test: Cliente configura headers correctamente."""
        with patch.dict('os.environ', {
            'PRODUCT_HUNT_API_KEY': 'test_key_123'
        }):
            ProductHuntClient.reset_client()

            client = ProductHuntClient.get_client()

            assert client.headers['Authorization'] == 'Bearer test_key_123'
            assert client.headers['Content-Type'] == 'application/json'


# Instrucciones de ejecución:
#
# Ejecutar todos los tests del scraper:
#   docker compose exec backend uv run pytest apps/scraper/tests/ -v
#
# Ejecutar este archivo específico:
#   docker compose exec backend uv run pytest apps/scraper/tests/test_scraper.py -v
#
# Ejecutar con cobertura:
#   docker compose exec backend uv run pytest apps/scraper/tests/ -v --cov=apps.scraper
