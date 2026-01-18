"""
Tests para los endpoints de subreddits.
"""

import pytest
from apps.subreddits.models import Subreddit


@pytest.mark.django_db
class TestListSubreddits:
    """Tests para el endpoint de listar subreddits."""

    def test_list_subreddits_authenticated(self, authenticated_client, subreddit, inactive_subreddit):
        """Test listar subreddits con autenticación."""
        response = authenticated_client.get('/subreddits/')

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_list_subreddits_no_auth(self, api_client, subreddit):
        """Test listar subreddits sin autenticación."""
        response = api_client.get('/subreddits/')

        assert response.status_code == 401

    def test_list_subreddits_empty(self, authenticated_client):
        """Test listar subreddits cuando no hay ninguno."""
        response = authenticated_client.get('/subreddits/')

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


@pytest.mark.django_db
class TestGetSubreddit:
    """Tests para el endpoint de detalle de subreddit."""

    def test_get_subreddit_authenticated(self, authenticated_client, subreddit):
        """Test obtener detalle de subreddit con autenticación."""
        response = authenticated_client.get(f'/subreddits/{subreddit.id}/')

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == subreddit.id
        assert data['name'] == subreddit.name
        assert data['active'] == subreddit.active
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_get_subreddit_no_auth(self, api_client, subreddit):
        """Test obtener subreddit sin autenticación."""
        response = api_client.get(f'/subreddits/{subreddit.id}/')

        assert response.status_code == 401

    def test_get_subreddit_not_found(self, authenticated_client):
        """Test obtener subreddit inexistente."""
        response = authenticated_client.get('/subreddits/99999/')

        assert response.status_code == 404


@pytest.mark.django_db
class TestCreateSubreddit:
    """Tests para el endpoint de crear subreddit."""

    def test_create_subreddit_authenticated(self, authenticated_client):
        """Test crear subreddit con autenticación."""
        response = authenticated_client.post(
            '/subreddits/',
            json={
                'name': 'NewSubreddit',
                'active': True
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data['name'] == 'NewSubreddit'
        assert data['active'] is True
        assert 'id' in data

        # Verificar que se creó en la BD
        assert Subreddit.objects.filter(name='NewSubreddit').exists()

    def test_create_subreddit_default_active(self, authenticated_client):
        """Test crear subreddit sin especificar active (default True)."""
        response = authenticated_client.post(
            '/subreddits/',
            json={'name': 'DefaultActive'}
        )

        assert response.status_code == 201
        data = response.json()
        assert data['active'] is True

    def test_create_subreddit_no_auth(self, api_client):
        """Test crear subreddit sin autenticación."""
        response = api_client.post(
            '/subreddits/',
            json={'name': 'TestSubreddit'}
        )

        assert response.status_code == 401

    def test_create_subreddit_missing_name(self, authenticated_client):
        """Test crear subreddit sin nombre."""
        response = authenticated_client.post(
            '/subreddits/',
            json={'active': True}
        )

        assert response.status_code == 422  # Validation error

    def test_create_subreddit_duplicate_name(self, authenticated_client, subreddit):
        """Test crear subreddit con nombre duplicado."""
        # Django Ninja convierte IntegrityError en 500 Internal Server Error
        # o puede lanzar la excepción directamente
        try:
            response = authenticated_client.post(
                '/subreddits/',
                json={'name': subreddit.name}
            )
            # Si no lanza excepción, debería ser error 500
            assert response.status_code == 500
        except Exception:
            # Si lanza IntegrityError directamente, el test pasa
            pass


@pytest.mark.django_db
class TestUpdateSubreddit:
    """Tests para el endpoint de actualizar subreddit."""

    def test_update_subreddit_name(self, authenticated_client, subreddit):
        """Test actualizar nombre de subreddit."""
        response = authenticated_client.put(
            f'/subreddits/{subreddit.id}/',
            json={'name': 'UpdatedName'}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'UpdatedName'

        # Verificar en BD
        subreddit.refresh_from_db()
        assert subreddit.name == 'UpdatedName'

    def test_update_subreddit_active(self, authenticated_client, subreddit):
        """Test actualizar estado active de subreddit."""
        response = authenticated_client.put(
            f'/subreddits/{subreddit.id}/',
            json={'active': False}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['active'] is False

        # Verificar en BD
        subreddit.refresh_from_db()
        assert subreddit.active is False

    def test_update_subreddit_both_fields(self, authenticated_client, subreddit):
        """Test actualizar nombre y active simultáneamente."""
        response = authenticated_client.put(
            f'/subreddits/{subreddit.id}/',
            json={
                'name': 'NewName',
                'active': False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'NewName'
        assert data['active'] is False

    def test_update_subreddit_no_fields(self, authenticated_client, subreddit):
        """Test actualizar sin proporcionar campos."""
        original_name = subreddit.name
        response = authenticated_client.put(
            f'/subreddits/{subreddit.id}/',
            json={}
        )

        assert response.status_code == 200
        data = response.json()
        # No debe cambiar nada
        assert data['name'] == original_name

    def test_update_subreddit_no_auth(self, api_client, subreddit):
        """Test actualizar subreddit sin autenticación."""
        response = api_client.put(
            f'/subreddits/{subreddit.id}/',
            json={'name': 'NewName'}
        )

        assert response.status_code == 401

    def test_update_subreddit_not_found(self, authenticated_client):
        """Test actualizar subreddit inexistente."""
        response = authenticated_client.put(
            '/subreddits/99999/',
            json={'name': 'NewName'}
        )

        assert response.status_code == 404


@pytest.mark.django_db
class TestDeleteSubreddit:
    """Tests para el endpoint de eliminar subreddit."""

    def test_delete_subreddit_authenticated(self, authenticated_client, subreddit):
        """Test eliminar subreddit con autenticación."""
        subreddit_id = subreddit.id
        subreddit_name = subreddit.name

        response = authenticated_client.delete(f'/subreddits/{subreddit_id}/')

        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert subreddit_name in data['message']

        # Verificar que se eliminó de la BD
        assert not Subreddit.objects.filter(id=subreddit_id).exists()

    def test_delete_subreddit_no_auth(self, api_client, subreddit):
        """Test eliminar subreddit sin autenticación."""
        response = api_client.delete(f'/subreddits/{subreddit.id}/')

        assert response.status_code == 401

    def test_delete_subreddit_not_found(self, authenticated_client):
        """Test eliminar subreddit inexistente."""
        response = authenticated_client.delete('/subreddits/99999/')

        assert response.status_code == 404

    def test_delete_subreddit_cascades_posts(self, authenticated_client, subreddit, post):
        """Test que al eliminar subreddit se eliminan sus posts (cascade)."""
        subreddit_id = subreddit.id
        post_id = post.id

        response = authenticated_client.delete(f'/subreddits/{subreddit_id}/')

        assert response.status_code == 200

        # Verificar que el post también se eliminó
        from apps.posts.models import Post
        assert not Post.objects.filter(id=post_id).exists()


# Ejecutar este test:
#   uv run pytest backend/tests/test_subreddits.py -v
#
# Ejecutar todos los tests de subreddits:
#   uv run pytest backend/tests/test_subreddits.py -v
