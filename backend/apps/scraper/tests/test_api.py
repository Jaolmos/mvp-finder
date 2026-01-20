"""
Tests para API endpoints del scraper.
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
    """Tests para endpoints del scraper."""

    @patch('apps.scraper.api.sync_reddit_posts.delay')
    def test_sync_posts_all_subreddits(self, mock_task, scraper_client):
        """Test: Endpoint para sincronizar todos los subreddits."""
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
            subreddit_ids=None,
            limit=50,
            time_filter='week'
        )

    @patch('apps.scraper.api.sync_reddit_posts.delay')
    def test_sync_posts_specific_subreddits(self, mock_task, scraper_client, subreddit):
        """Test: Endpoint para sincronizar subreddits específicos."""
        # Setup mock
        mock_task.return_value = Mock(id='task-456')

        # Execute
        response = scraper_client.post(
            "/scraper/sync/",
            json={
                "subreddit_ids": [subreddit.id],
                "limit": 100,
                "time_filter": "month"
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['task_id'] == 'task-456'

        # Verificar parámetros personalizados
        mock_task.assert_called_once_with(
            subreddit_ids=[subreddit.id],
            limit=100,
            time_filter='month'
        )

    def test_sync_posts_requires_auth(self, api_client):
        """Test: Endpoint requiere autenticación."""
        # Execute
        response = api_client.post("/scraper/sync/", json={})

        # Assert
        assert response.status_code == 401

    @patch('apps.scraper.api.test_reddit_connection.delay')
    def test_test_connection(self, mock_task, scraper_client):
        """Test: Endpoint para probar conexión con Reddit."""
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
#   cd backend
#   uv run pytest apps/scraper/tests/test_api.py -v
#
# Ejecutar todos los tests del scraper:
#   uv run pytest apps/scraper/tests/ -v
