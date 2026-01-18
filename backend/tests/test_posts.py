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

    def test_list_posts_filter_by_subreddit(self, authenticated_client, subreddit, inactive_subreddit):
        """Test filtrar posts por subreddit."""
        from django.utils import timezone

        # Crear post en el subreddit principal
        Post.objects.create(
            reddit_id='main123',
            subreddit=subreddit,
            title='Main post',
            content='Content',
            author='author',
            score=50,
            url='https://reddit.com/main',
            created_at_reddit=timezone.now()
        )

        # Crear post de otro subreddit
        Post.objects.create(
            reddit_id='other123',
            subreddit=inactive_subreddit,
            title='Other post',
            content='Content',
            author='author',
            score=10,
            url='https://reddit.com/test',
            created_at_reddit=timezone.now()
        )

        response = authenticated_client.get(f'/posts/?subreddit={subreddit.id}')

        assert response.status_code == 200
        data = response.json()
        assert data['count'] == 1
        assert data['items'][0]['subreddit']['id'] == subreddit.id

    def test_list_posts_filter_analyzed(self, authenticated_client, subreddit):
        """Test filtrar posts por estado de análisis."""
        from django.utils import timezone

        # Crear post NO analizado
        Post.objects.create(
            reddit_id='not_analyzed',
            subreddit=subreddit,
            title='Not analyzed post',
            content='Content',
            author='author',
            score=42,
            url='https://reddit.com/not_analyzed',
            created_at_reddit=timezone.now(),
            analyzed=False
        )

        # Crear post analizado
        Post.objects.create(
            reddit_id='analyzed',
            subreddit=subreddit,
            title='Analyzed post',
            content='Content',
            author='author',
            score=100,
            url='https://reddit.com/analyzed',
            created_at_reddit=timezone.now(),
            analyzed=True
        )

        # Filtrar solo analizados
        response = authenticated_client.get('/posts/?analyzed=true')

        assert response.status_code == 200
        data = response.json()
        assert data['count'] == 1
        assert data['items'][0]['analyzed'] is True

        # Filtrar solo no analizados
        response = authenticated_client.get('/posts/?analyzed=false')

        assert response.status_code == 200
        data = response.json()
        assert data['count'] == 1
        assert data['items'][0]['analyzed'] is False

    def test_list_posts_filter_min_score(self, authenticated_client, subreddit):
        """Test filtrar posts por score mínimo."""
        from django.utils import timezone

        # Crear post con score bajo
        Post.objects.create(
            reddit_id='low_score',
            subreddit=subreddit,
            title='Low score post',
            content='Content',
            author='author',
            score=42,
            url='https://reddit.com/low',
            created_at_reddit=timezone.now()
        )

        # Crear post con score alto
        Post.objects.create(
            reddit_id='high_score',
            subreddit=subreddit,
            title='High score post',
            content='Content',
            author='author',
            score=100,
            url='https://reddit.com/high',
            created_at_reddit=timezone.now()
        )

        response = authenticated_client.get('/posts/?min_score=50')

        assert response.status_code == 200
        data = response.json()
        assert data['count'] == 1
        assert data['items'][0]['score'] >= 50

    def test_list_posts_filter_search(self, authenticated_client, subreddit):
        """Test buscar posts por texto en título o contenido."""
        from django.utils import timezone

        # Crear post que coincide con búsqueda
        Post.objects.create(
            reddit_id='with_expenses',
            subreddit=subreddit,
            title='I need an app to track my expenses',
            content='Content about expenses',
            author='author',
            score=42,
            url='https://reddit.com/expenses',
            created_at_reddit=timezone.now()
        )

        # Crear post que no coincide
        Post.objects.create(
            reddit_id='no_match',
            subreddit=subreddit,
            title='Another post',
            content='Different content',
            author='author',
            score=50,
            url='https://reddit.com/nomatch',
            created_at_reddit=timezone.now()
        )

        response = authenticated_client.get('/posts/?search=expenses')

        assert response.status_code == 200
        data = response.json()
        assert data['count'] == 1
        assert 'expenses' in data['items'][0]['title'].lower()

    def test_list_posts_pagination(self, authenticated_client, subreddit):
        """Test paginación de posts."""
        # Crear 25 posts (más que el page_size de 20)
        for i in range(25):
            Post.objects.create(
                reddit_id=f'post{i}',
                subreddit=subreddit,
                title=f'Post {i}',
                content='Content',
                author='author',
                score=i,
                url=f'https://reddit.com/post{i}',
                created_at_reddit=subreddit.created_at
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
        assert len(data['items']) == 5


@pytest.mark.django_db
class TestGetPost:
    """Tests para el endpoint de detalle de post."""

    def test_get_post_authenticated(self, authenticated_client, post):
        """Test obtener detalle de post con autenticación."""
        response = authenticated_client.get(f'/posts/{post.id}/')

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == post.id
        assert data['reddit_id'] == post.reddit_id
        assert data['title'] == post.title
        assert data['content'] == post.content
        assert 'subreddit' in data
        assert data['subreddit']['name'] == post.subreddit.name

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
        assert data['favorited'] is True
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
        assert data['favorited'] is False
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
#   uv run pytest backend/tests/test_posts.py -v
#
# Ejecutar todos los tests de posts:
#   uv run pytest backend/tests/test_posts.py -v
