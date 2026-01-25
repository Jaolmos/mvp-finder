"""
Tests para API endpoints del scraper de Product Hunt.
"""
import pytest
from unittest.mock import patch, Mock


@pytest.fixture
def scraper_client(api_client, access_token):
    """Cliente de test autenticado para endpoints del scraper."""
    api_client.headers = {"Authorization": f"Bearer {access_token}"}
    return api_client


@pytest.mark.django_db
class TestScraperAPI:
    """Tests para endpoints del scraper de Product Hunt."""

    @patch('apps.scraper.api.sync_products.delay')
    def test_sync_products_all_topics(self, mock_task, scraper_client):
        """Test: Endpoint para sincronizar todos los topics."""
        # Setup mock
        mock_task.return_value = Mock(id='task-123')

        # Execute
        response = scraper_client.post(
            "/scraper/sync/",
            json={}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['task_id'] == 'task-123'
        assert data['status'] == 'processing'
        assert 'Sincronización iniciada' in data['message']

        # Verificar que se llamó a la tarea con parámetros por defecto
        mock_task.assert_called_once_with(
            topic_ids=None,
            limit=50,
        )

    @patch('apps.scraper.api.sync_products.delay')
    def test_sync_products_specific_topics(self, mock_task, scraper_client, topic):
        """Test: Endpoint para sincronizar topics específicos."""
        # Setup mock
        mock_task.return_value = Mock(id='task-456')

        # Execute
        response = scraper_client.post(
            "/scraper/sync/",
            json={
                "topic_ids": [topic.id],
                "limit": 100
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['task_id'] == 'task-456'

        # Verificar parámetros personalizados
        mock_task.assert_called_once_with(
            topic_ids=[topic.id],
            limit=100,
        )

    def test_sync_products_requires_auth(self, api_client):
        """Test: Endpoint requiere autenticación."""
        # Execute
        response = api_client.post("/scraper/sync/", json={})

        # Assert
        assert response.status_code == 401

    @patch('apps.scraper.api.test_connection.delay')
    def test_test_connection(self, mock_task, scraper_client):
        """Test: Endpoint para probar conexión con Product Hunt."""
        # Setup mock
        mock_task.return_value = Mock(id='test-789')

        # Execute
        response = scraper_client.post("/scraper/test-connection/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['task_id'] == 'test-789'
        assert 'Probando conexión' in data['message']

        mock_task.assert_called_once()

    def test_test_connection_requires_auth(self, api_client):
        """Test: Test de conexión requiere autenticación."""
        # Execute
        response = api_client.post("/scraper/test-connection/")

        # Assert
        assert response.status_code == 401


# Instrucciones de ejecución:
#
# Ejecutar tests de API del scraper:
#   docker compose exec backend uv run pytest apps/scraper/tests/test_api.py -v
#
# Ejecutar todos los tests del scraper:
#   docker compose exec backend uv run pytest apps/scraper/tests/ -v
