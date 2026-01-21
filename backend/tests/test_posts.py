"""
Tests para los endpoints de posts.
"""

import pytest
from apps.posts.models import Post
from apps.users.models import Favorite


@pytest.mark.django_db
class TestListPosts:
    """Tests para el endpoint de listar posts."""

    def test_list_posts_authenticated(self, authenticated_client, post, analyzed_post):
        """Test listar posts con autenticación."""
        response = authenticated_client.get('/posts/')

        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert 'count' in data
        assert len(data['items']) == 2

    def test_list_posts_no_auth(self, api_client, post):
        """Test listar posts sin autenticación."""
        response = api_client.get('/posts/')

        assert response.status_code == 401

    def test_list_posts_filter_by_topic(self, authenticated_client, post, topic):
        """Test filtrar posts por topic."""
        # Filtrar por el topic del fixture (artificial-intelligence)
        response = authenticated_client.get(f'/posts/?topic={post.topic.id}')

        assert response.status_code == 200
        data = response.json()
        # Debe mostrar posts del topic
        assert data['count'] >= 1
        for item in data['items']:
            assert item['topic']['id'] == post.topic.id

    def test_list_posts_filter_analyzed_true(self, authenticated_client, analyzed_post):
        """Test filtrar posts analizados."""
        response = authenticated_client.get('/posts/?analyzed=true')

        assert response.status_code == 200
        data = response.json()
        # Todos los posts retornados deben estar analizados
        for item in data['items']:
            assert item['analyzed'] is True

    def test_list_posts_filter_analyzed_false(self, authenticated_client, post):
        """Test filtrar posts no analizados."""
        response = authenticated_client.get('/posts/?analyzed=false')

        assert response.status_code == 200
        data = response.json()
        # Todos los posts retornados deben estar sin analizar
        for item in data['items']:
            assert item['analyzed'] is False

    def test_list_posts_filter_min_score(self, authenticated_client, post):
        """Test filtrar posts por score mínimo."""
        # El post del fixture tiene score=42
        # Filtrar con min_score=50 no debe devolver el post del fixture
        response = authenticated_client.get('/posts/?min_score=50')

        assert response.status_code == 200
        data = response.json()
        for item in data['items']:
            assert item['score'] >= 50

        # Filtrar con min_score=40 debe incluir el post del fixture
        response = authenticated_client.get('/posts/?min_score=40')

        assert response.status_code == 200
        data = response.json()
        assert data['count'] >= 1
        for item in data['items']:
            assert item['score'] >= 40

    def test_list_posts_filter_search(self, authenticated_client, post):
        """Test buscar posts por texto en título o contenido."""
        # Buscar por texto que existe en el post del fixture
        # El post del fixture tiene title='AI Code Assistant'
        response = authenticated_client.get('/posts/?search=Assistant')

        assert response.status_code == 200
        data = response.json()
        assert data['count'] >= 1
        # Verificar que al menos un resultado contiene el término buscado
        found = False
        for item in data['items']:
            if 'assistant' in item['title'].lower():
                found = True
                break
        assert found, "No se encontró ningún post con 'Assistant' en el título"

    def test_list_posts_pagination(self, authenticated_client, topic):
        """Test paginación de posts."""
        # Crear 25 posts (más que el page_size de 20)
        for i in range(25):
            Post.objects.create(
                external_id=f'ph_post{i}',
                topic=topic,
                title=f'Post {i}',
                tagline=f'Tagline {i}',
                content='Content',
                author='author',
                score=i,
                votes_count=i,
                comments_count=0,
                url=f'https://producthunt.com/posts/post{i}',
                created_at_source=topic.created_at
            )

        # Primera página
        response = authenticated_client.get('/posts/')
        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) == 20

        # Segunda página
        response = authenticated_client.get('/posts/?page=2')
        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) >= 5  # Al menos 5 posts en segunda página


@pytest.mark.django_db
class TestGetPost:
    """Tests para el endpoint de detalle de post."""

    def test_get_post_authenticated(self, authenticated_client, post):
        """Test obtener detalle de post con autenticación."""
        response = authenticated_client.get(f'/posts/{post.id}/')

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == post.id
        assert data['external_id'] == post.external_id
        assert data['title'] == post.title
        assert data['content'] == post.content
        assert 'topic' in data
        assert data['topic']['name'] == post.topic.name

    def test_get_post_no_auth(self, api_client, post):
        """Test obtener post sin autenticación."""
        response = api_client.get(f'/posts/{post.id}/')

        assert response.status_code == 401

    def test_get_post_not_found(self, authenticated_client):
        """Test obtener post inexistente."""
        response = authenticated_client.get('/posts/99999/')

        assert response.status_code == 404


@pytest.mark.django_db
class TestToggleFavorite:
    """Tests para el endpoint de marcar/desmarcar favoritos."""

    def test_toggle_favorite_add(self, authenticated_client, post, user):
        """Test añadir post a favoritos."""
        response = authenticated_client.post(f'/posts/{post.id}/favorite/')

        assert response.status_code == 200
        data = response.json()
        assert data['is_favorite'] is True
        assert 'añadido' in data['message'].lower()

        # Verificar que se creó el favorito
        assert Favorite.objects.filter(user=user, post=post).exists()

    def test_toggle_favorite_remove(self, authenticated_client, post, user):
        """Test quitar post de favoritos."""
        # Primero añadirlo
        Favorite.objects.create(user=user, post=post)

        response = authenticated_client.post(f'/posts/{post.id}/favorite/')

        assert response.status_code == 200
        data = response.json()
        assert data['is_favorite'] is False
        assert 'eliminado' in data['message'].lower()

        # Verificar que se eliminó el favorito
        assert not Favorite.objects.filter(user=user, post=post).exists()

    def test_toggle_favorite_no_auth(self, api_client, post):
        """Test toggle favorite sin autenticación."""
        response = api_client.post(f'/posts/{post.id}/favorite/')

        assert response.status_code == 401

    def test_toggle_favorite_post_not_found(self, authenticated_client):
        """Test toggle favorite de post inexistente."""
        response = authenticated_client.post('/posts/99999/favorite/')

        assert response.status_code == 404


@pytest.mark.django_db
class TestListFavorites:
    """Tests para el endpoint de listar favoritos."""

    def test_list_favorites_authenticated(self, authenticated_client, post, analyzed_post, user):
        """Test listar favoritos del usuario."""
        # Añadir ambos posts a favoritos
        Favorite.objects.create(user=user, post=post)
        Favorite.objects.create(user=user, post=analyzed_post)

        response = authenticated_client.get('/posts/favorites/')

        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert len(data['items']) == 2

    def test_list_favorites_empty(self, authenticated_client, user):
        """Test listar favoritos cuando no hay ninguno."""
        response = authenticated_client.get('/posts/favorites/')

        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) == 0

    def test_list_favorites_no_auth(self, api_client):
        """Test listar favoritos sin autenticación."""
        response = api_client.get('/posts/favorites/')

        assert response.status_code == 401

    def test_list_favorites_only_user_favorites(self, authenticated_client, post, user, admin_user):
        """Test que solo muestra favoritos del usuario actual."""
        # Usuario actual añade un favorito
        Favorite.objects.create(user=user, post=post)

        # Admin añade su propio favorito
        Favorite.objects.create(user=admin_user, post=post)

        response = authenticated_client.get('/posts/favorites/')

        assert response.status_code == 200
        data = response.json()
        # Solo debe ver su propio favorito, no el del admin
        assert len(data['items']) == 1


# Ejecutar este test:
#   docker compose exec backend uv run pytest tests/test_posts.py -v
#
# Ejecutar todos los tests de posts:
#   docker compose exec backend uv run pytest tests/test_posts.py -v
