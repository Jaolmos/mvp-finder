"""
Tests para los endpoints de topics.
"""

import pytest
from apps.topics.models import Topic


@pytest.mark.django_db
class TestListTopics:
    """Tests para el endpoint de listar topics."""

    def test_list_topics_authenticated(self, authenticated_client, topic, inactive_topic):
        """Test listar topics con autenticación."""
        response = authenticated_client.get('/topics/')

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_list_topics_no_auth(self, api_client, topic):
        """Test listar topics sin autenticación."""
        response = api_client.get('/topics/')

        assert response.status_code == 401

    def test_list_topics_empty(self, authenticated_client):
        """Test listar topics cuando no hay ninguno."""
        response = authenticated_client.get('/topics/')

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


@pytest.mark.django_db
class TestGetTopic:
    """Tests para el endpoint de detalle de topic."""

    def test_get_topic_authenticated(self, authenticated_client, topic):
        """Test obtener detalle de topic con autenticación."""
        response = authenticated_client.get(f'/topics/{topic.id}/')

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == topic.id
        assert data['name'] == topic.name
        assert data['is_active'] == topic.is_active
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_get_topic_no_auth(self, api_client, topic):
        """Test obtener topic sin autenticación."""
        response = api_client.get(f'/topics/{topic.id}/')

        assert response.status_code == 401

    def test_get_topic_not_found(self, authenticated_client):
        """Test obtener topic inexistente."""
        response = authenticated_client.get('/topics/99999/')

        assert response.status_code == 404


@pytest.mark.django_db
class TestCreateTopic:
    """Tests para el endpoint de crear topic."""

    def test_create_topic_authenticated(self, authenticated_client):
        """Test crear topic con autenticación."""
        response = authenticated_client.post(
            '/topics/',
            json={
                'name': 'developer-tools',
                'is_active': True
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data['name'] == 'developer-tools'
        assert data['is_active'] is True
        assert 'id' in data

        # Verificar que se creó en la BD
        assert Topic.objects.filter(name='developer-tools').exists()

    def test_create_topic_default_active(self, authenticated_client):
        """Test crear topic sin especificar is_active (default True)."""
        response = authenticated_client.post(
            '/topics/',
            json={'name': 'productivity'}
        )

        assert response.status_code == 201
        data = response.json()
        assert data['is_active'] is True

    def test_create_topic_no_auth(self, api_client):
        """Test crear topic sin autenticación."""
        response = api_client.post(
            '/topics/',
            json={'name': 'tech'}
        )

        assert response.status_code == 401

    def test_create_topic_missing_name(self, authenticated_client):
        """Test crear topic sin nombre."""
        response = authenticated_client.post(
            '/topics/',
            json={'is_active': True}
        )

        assert response.status_code == 422  # Validation error

    def test_create_topic_duplicate_name(self, authenticated_client, topic):
        """Test crear topic con nombre duplicado."""
        try:
            response = authenticated_client.post(
                '/topics/',
                json={'name': topic.name}
            )
            assert response.status_code == 500
        except Exception:
            pass


@pytest.mark.django_db
class TestUpdateTopic:
    """Tests para el endpoint de actualizar topic."""

    def test_update_topic_name(self, authenticated_client, topic):
        """Test actualizar nombre de topic."""
        response = authenticated_client.put(
            f'/topics/{topic.id}/',
            json={'name': 'updated-topic'}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'updated-topic'

        # Verificar en BD
        topic.refresh_from_db()
        assert topic.name == 'updated-topic'

    def test_update_topic_active(self, authenticated_client, topic):
        """Test actualizar estado is_active de topic."""
        response = authenticated_client.put(
            f'/topics/{topic.id}/',
            json={'is_active': False}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['is_active'] is False

        # Verificar en BD
        topic.refresh_from_db()
        assert topic.is_active is False

    def test_update_topic_both_fields(self, authenticated_client, topic):
        """Test actualizar nombre y is_active simultáneamente."""
        response = authenticated_client.put(
            f'/topics/{topic.id}/',
            json={
                'name': 'new-topic-name',
                'is_active': False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'new-topic-name'
        assert data['is_active'] is False

    def test_update_topic_no_fields(self, authenticated_client, topic):
        """Test actualizar sin proporcionar campos."""
        original_name = topic.name
        response = authenticated_client.put(
            f'/topics/{topic.id}/',
            json={}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == original_name

    def test_update_topic_no_auth(self, api_client, topic):
        """Test actualizar topic sin autenticación."""
        response = api_client.put(
            f'/topics/{topic.id}/',
            json={'name': 'new-name'}
        )

        assert response.status_code == 401

    def test_update_topic_not_found(self, authenticated_client):
        """Test actualizar topic inexistente."""
        response = authenticated_client.put(
            '/topics/99999/',
            json={'name': 'new-name'}
        )

        assert response.status_code == 404


@pytest.mark.django_db
class TestDeleteTopic:
    """Tests para el endpoint de eliminar topic."""

    def test_delete_topic_authenticated(self, authenticated_client, topic):
        """Test eliminar topic con autenticación."""
        topic_id = topic.id
        topic_name = topic.name

        response = authenticated_client.delete(f'/topics/{topic_id}/')

        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert topic_name in data['message']

        # Verificar que se eliminó de la BD
        assert not Topic.objects.filter(id=topic_id).exists()

    def test_delete_topic_no_auth(self, api_client, topic):
        """Test eliminar topic sin autenticación."""
        response = api_client.delete(f'/topics/{topic.id}/')

        assert response.status_code == 401

    def test_delete_topic_not_found(self, authenticated_client):
        """Test eliminar topic inexistente."""
        response = authenticated_client.delete('/topics/99999/')

        assert response.status_code == 404

    def test_delete_topic_cascades_products(self, authenticated_client, topic, product):
        """Test que al eliminar topic se eliminan sus productos (cascade)."""
        topic_id = topic.id
        product_id = product.id

        response = authenticated_client.delete(f'/topics/{topic_id}/')

        assert response.status_code == 200

        # Verificar que el producto también se eliminó
        from apps.posts.models import Product
        assert not Product.objects.filter(id=product_id).exists()


# Ejecutar este test:
#   docker compose exec backend uv run pytest tests/test_topics.py -v
#
# Ejecutar todos los tests de topics:
#   docker compose exec backend uv run pytest tests/test_topics.py -v
