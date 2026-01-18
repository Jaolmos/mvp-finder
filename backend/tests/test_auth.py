"""
Tests para los endpoints de autenticación.
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestLogin:
    """Tests para el endpoint de login."""

    def test_login_successful(self, api_client, user):
        """Test login con credenciales correctas."""
        response = api_client.post(
            '/auth/login/',
            json={
                'username': 'testuser',
                'password': 'testpass123'
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert 'access' in data
        assert 'refresh' in data
        assert isinstance(data['access'], str)
        assert isinstance(data['refresh'], str)

    def test_login_wrong_password(self, api_client, user):
        """Test login con contraseña incorrecta."""
        response = api_client.post(
            '/auth/login/',
            json={
                'username': 'testuser',
                'password': 'wrongpassword'
            }
        )

        assert response.status_code == 401
        data = response.json()
        assert 'message' in data
        assert data['message'] == 'Credenciales inválidas'

    def test_login_user_not_exists(self, api_client):
        """Test login con usuario inexistente."""
        response = api_client.post(
            '/auth/login/',
            json={
                'username': 'nonexistent',
                'password': 'password123'
            }
        )

        assert response.status_code == 401
        data = response.json()
        assert data['message'] == 'Credenciales inválidas'

    def test_login_missing_username(self, api_client):
        """Test login sin username."""
        response = api_client.post(
            '/auth/login/',
            json={'password': 'testpass123'}
        )

        assert response.status_code == 422  # Validation error

    def test_login_missing_password(self, api_client):
        """Test login sin password."""
        response = api_client.post(
            '/auth/login/',
            json={'username': 'testuser'}
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.django_db
class TestRefreshToken:
    """Tests para el endpoint de refresh token."""

    def test_refresh_token_successful(self, api_client, tokens):
        """Test refresh token con token válido."""
        response = api_client.post(
            '/auth/refresh/',
            json={'refresh': tokens['refresh']}
        )

        assert response.status_code == 200
        data = response.json()
        assert 'access' in data
        assert 'refresh' in data
        assert isinstance(data['access'], str)

    def test_refresh_token_invalid(self, api_client):
        """Test refresh token con token inválido."""
        response = api_client.post(
            '/auth/refresh/',
            json={'refresh': 'invalid_token_here'}
        )

        assert response.status_code == 401
        data = response.json()
        assert 'message' in data
        assert data['message'] == 'Refresh token inválido'

    def test_refresh_token_missing(self, api_client):
        """Test refresh token sin token."""
        response = api_client.post(
            '/auth/refresh/',
            json={}
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.django_db
class TestGetCurrentUser:
    """Tests para el endpoint de obtener usuario actual."""

    def test_get_current_user_authenticated(self, authenticated_client, user):
        """Test obtener info de usuario autenticado."""
        response = authenticated_client.get('/auth/me/')

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == user.id
        assert data['username'] == user.username
        assert data['email'] == user.email
        assert 'first_name' in data
        assert 'last_name' in data

    def test_get_current_user_no_token(self, api_client):
        """Test obtener info sin token de autenticación."""
        response = api_client.get('/auth/me/')

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, api_client):
        """Test obtener info con token inválido."""
        api_client.headers = {'Authorization': 'Bearer invalid_token'}
        response = api_client.get('/auth/me/')

        assert response.status_code == 401


# Ejecutar este test:
#   uv run pytest backend/tests/test_auth.py -v
#
# Ejecutar todos los tests de autenticación:
#   uv run pytest backend/tests/test_auth.py -v
