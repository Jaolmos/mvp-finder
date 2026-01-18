"""
Configuración de fixtures para pytest.

Este archivo contiene fixtures reutilizables para todos los tests del backend.
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.subreddits.models import Subreddit
from apps.posts.models import Post

User = get_user_model()


@pytest.fixture
def user(db):
    """
    Fixture que crea un usuario de prueba.
    """
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """
    Fixture que crea un usuario admin de prueba.
    """
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )


@pytest.fixture
def tokens(user):
    """
    Fixture que genera tokens JWT para un usuario.
    Retorna dict con 'access' y 'refresh'.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@pytest.fixture
def subreddit(db):
    """
    Fixture que crea un subreddit de prueba.
    """
    return Subreddit.objects.create(
        name='SomebodyMakeThis',
        active=True
    )


@pytest.fixture
def inactive_subreddit(db):
    """
    Fixture que crea un subreddit inactivo.
    """
    return Subreddit.objects.create(
        name='InactiveSubreddit',
        active=False
    )


@pytest.fixture
def post(subreddit):
    """
    Fixture que crea un post de prueba sin analizar.
    """
    return Post.objects.create(
        reddit_id='abc123',
        subreddit=subreddit,
        title='I need an app to track my expenses',
        content='I\'m looking for a simple app to track shared expenses with roommates.',
        author='testauthor',
        score=42,
        url='https://reddit.com/r/SomebodyMakeThis/comments/abc123',
        created_at_reddit=timezone.now(),
        analyzed=False
    )


@pytest.fixture
def analyzed_post(subreddit):
    """
    Fixture que crea un post analizado por IA.
    """
    return Post.objects.create(
        reddit_id='xyz789',
        subreddit=subreddit,
        title='Need a tool for team collaboration',
        content='Looking for a better way to manage team tasks and communication.',
        author='anotheruser',
        score=100,
        url='https://reddit.com/r/SomebodyMakeThis/comments/xyz789',
        created_at_reddit=timezone.now(),
        analyzed=True,
        analyzed_at=timezone.now(),
        summary='Team collaboration tool for task management',
        problem='Difficulty managing team tasks and communication',
        mvp_idea='Simple kanban board with built-in chat',
        target_audience='Small teams, startups',
        potential_score=8,
        tags='productivity,collaboration,team'
    )


_test_client_instance = None


@pytest.fixture
def api_client():
    """
    Fixture que retorna un cliente API de Django Ninja para tests.
    Usa una única instancia compartida para evitar problemas de registro.
    """
    global _test_client_instance

    if _test_client_instance is None:
        from ninja.testing import TestClient
        from config.api import api
        _test_client_instance = TestClient(api)

    # Limpiar headers para cada test
    _test_client_instance.headers = {}
    return _test_client_instance


@pytest.fixture
def authenticated_client(api_client, tokens):
    """
    Fixture que retorna un cliente API autenticado con JWT.
    """
    api_client.headers = {
        'Authorization': f'Bearer {tokens["access"]}'
    }
    return api_client


# Ejecutar estos tests:
#   uv run pytest -v
#
# Ejecutar con cobertura:
#   uv run pytest --cov=apps -v
