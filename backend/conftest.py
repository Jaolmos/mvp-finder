"""
Configuración de fixtures para pytest.

Este archivo contiene fixtures reutilizables para todos los tests del backend.
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.topics.models import Topic
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
def access_token(tokens):
    """
    Fixture que retorna solo el access token.
    """
    return tokens['access']


@pytest.fixture
def topic(db):
    """
    Fixture que crea un topic de prueba.
    """
    return Topic.objects.create(
        name='artificial-intelligence',
        is_active=True
    )


@pytest.fixture
def inactive_topic(db):
    """
    Fixture que crea un topic inactivo.
    """
    return Topic.objects.create(
        name='marketing',
        is_active=False
    )


@pytest.fixture
def post(topic):
    """
    Fixture que crea un post de prueba sin analizar.
    """
    return Post.objects.create(
        external_id='ph_test001',
        topic=topic,
        title='AI Code Assistant',
        tagline='Your intelligent pair programmer',
        content='AI-powered code assistant that helps developers write better code.',
        author='testmaker',
        score=500,
        votes_count=500,
        comments_count=45,
        url='https://producthunt.com/posts/ai-code-assistant',
        website='https://aicodeassistant.com',
        created_at_source=timezone.now(),
        analyzed=False
    )


@pytest.fixture
def analyzed_post(topic):
    """
    Fixture que crea un post analizado por IA.
    """
    return Post.objects.create(
        external_id='ph_test002',
        topic=topic,
        title='FocusFlow - Productivity Timer',
        tagline='Smart pomodoro with distraction blocking',
        content='Combine pomodoro technique with AI-powered website blocking.',
        author='productivityguru',
        score=800,
        votes_count=800,
        comments_count=67,
        url='https://producthunt.com/posts/focusflow',
        website='https://focusflow.app',
        created_at_source=timezone.now(),
        analyzed=True,
        analyzed_at=timezone.now(),
        summary='Timer pomodoro con bloqueo inteligente de distracciones',
        problem='Las distracciones digitales reducen la productividad',
        mvp_idea='App de pomodoro que bloquea sitios automáticamente',
        target_audience='Trabajadores remotos, estudiantes',
        potential_score=8,
        tags='productividad,focus,pomodoro'
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
#   docker compose exec backend uv run pytest -v
#
# Ejecutar con cobertura:
#   docker compose exec backend uv run pytest --cov=apps -v
