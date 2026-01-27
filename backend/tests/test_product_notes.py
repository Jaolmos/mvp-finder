"""
Tests para el sistema de notas de productos.

Ejecutar: docker compose exec backend uv run pytest tests/test_product_notes.py -v
"""
import pytest
from apps.posts.models import ProductNote


@pytest.mark.django_db
class TestGetProductNote:
    """Tests para obtener nota de un producto."""

    def test_get_note_success(self, authenticated_client, user, product):
        """Debe retornar la nota si existe."""
        note = ProductNote.objects.create(
            user=user,
            product=product,
            content="Esta es mi nota de prueba"
        )

        response = authenticated_client.get(f'/products/{product.id}/note/')
        assert response.status_code == 200

        data = response.json()
        assert data['id'] == note.id
        assert data['content'] == "Esta es mi nota de prueba"
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_get_note_not_found(self, authenticated_client, product):
        """Debe retornar 404 si no existe nota."""
        response = authenticated_client.get(f'/products/{product.id}/note/')
        assert response.status_code == 404
        assert 'message' in response.json()

    def test_get_note_requires_auth(self, api_client, product):
        """Debe requerir autenticación."""
        response = api_client.get(f'/products/{product.id}/note/')
        assert response.status_code == 401

    def test_get_note_product_not_found(self, authenticated_client):
        """Debe retornar 404 si el producto no existe."""
        response = authenticated_client.get('/products/99999/note/')
        assert response.status_code == 404


@pytest.mark.django_db
class TestCreateProductNote:
    """Tests para crear nota de un producto."""

    def test_create_note_success(self, authenticated_client, user, product):
        """Debe crear nota correctamente."""
        payload = {"content": "Mi primera nota sobre este producto"}

        response = authenticated_client.post(
            f'/products/{product.id}/note/',
            json=payload
        )
        assert response.status_code == 201

        data = response.json()
        assert data['success'] is True
        assert data['message'] == "Nota creada correctamente"
        assert data['note']['content'] == payload['content']

        # Verificar en BD
        assert ProductNote.objects.filter(product=product, user=user).count() == 1

    def test_create_note_duplicate(self, authenticated_client, user, product):
        """Debe rechazar crear nota duplicada."""
        ProductNote.objects.create(
            user=user,
            product=product,
            content="Nota existente"
        )

        payload = {"content": "Nueva nota"}
        response = authenticated_client.post(
            f'/products/{product.id}/note/',
            json=payload
        )
        assert response.status_code == 400
        assert 'Ya existe una nota' in response.json()['message']

    def test_create_note_empty_content(self, authenticated_client, product):
        """Debe rechazar contenido vacío."""
        payload = {"content": ""}
        response = authenticated_client.post(
            f'/products/{product.id}/note/',
            json=payload
        )
        # Django Ninja valida required fields
        assert response.status_code in [400, 422]

    def test_create_note_product_not_found(self, authenticated_client):
        """Debe retornar 404 si producto no existe."""
        payload = {"content": "Nota para producto inexistente"}
        response = authenticated_client.post('/products/99999/note/', json=payload)
        assert response.status_code == 404

    def test_create_note_requires_auth(self, api_client, product):
        """Debe requerir autenticación."""
        payload = {"content": "Nota sin autenticación"}
        response = api_client.post(f'/products/{product.id}/note/', json=payload)
        assert response.status_code == 401

    def test_create_note_long_content(self, authenticated_client, product):
        """Debe aceptar contenido largo."""
        long_content = "Este es un texto muy largo. " * 100
        payload = {"content": long_content}

        response = authenticated_client.post(
            f'/products/{product.id}/note/',
            json=payload
        )
        assert response.status_code == 201
        assert response.json()['note']['content'] == long_content


@pytest.mark.django_db
class TestUpdateProductNote:
    """Tests para actualizar nota de un producto."""

    def test_update_note_success(self, authenticated_client, user, product):
        """Debe actualizar nota correctamente."""
        note = ProductNote.objects.create(
            user=user,
            product=product,
            content="Contenido original"
        )

        payload = {"content": "Contenido actualizado"}
        response = authenticated_client.put(
            f'/products/{product.id}/note/',
            json=payload
        )
        assert response.status_code == 200

        data = response.json()
        assert data['success'] is True
        assert data['note']['content'] == "Contenido actualizado"

        # Verificar en BD
        note.refresh_from_db()
        assert note.content == "Contenido actualizado"

    def test_update_note_not_found(self, authenticated_client, product):
        """Debe retornar 404 si no existe nota."""
        payload = {"content": "Intentar actualizar nota inexistente"}
        response = authenticated_client.put(
            f'/products/{product.id}/note/',
            json=payload
        )
        assert response.status_code == 404
        assert 'No existe nota' in response.json()['message']

    def test_update_note_product_not_found(self, authenticated_client):
        """Debe retornar 404 si producto no existe."""
        payload = {"content": "Actualizar nota de producto inexistente"}
        response = authenticated_client.put('/products/99999/note/', json=payload)
        assert response.status_code == 404

    def test_update_note_requires_auth(self, api_client, product):
        """Debe requerir autenticación."""
        payload = {"content": "Actualización sin autenticación"}
        response = api_client.put(f'/products/{product.id}/note/', json=payload)
        assert response.status_code == 401

    def test_update_note_empty_content(self, authenticated_client, user, product):
        """Debe rechazar contenido vacío."""
        ProductNote.objects.create(
            user=user,
            product=product,
            content="Contenido original"
        )

        payload = {"content": ""}
        response = authenticated_client.put(
            f'/products/{product.id}/note/',
            json=payload
        )
        assert response.status_code in [400, 422]


@pytest.mark.django_db
class TestDeleteProductNote:
    """Tests para eliminar nota de un producto."""

    def test_delete_note_success(self, authenticated_client, user, product):
        """Debe eliminar nota correctamente."""
        note = ProductNote.objects.create(
            user=user,
            product=product,
            content="Nota a eliminar"
        )

        response = authenticated_client.delete(f'/products/{product.id}/note/')
        assert response.status_code == 200
        assert 'eliminada correctamente' in response.json()['message']

        # Verificar que se eliminó de BD
        assert not ProductNote.objects.filter(id=note.id).exists()

    def test_delete_note_not_found(self, authenticated_client, product):
        """Debe retornar 404 si no existe nota."""
        response = authenticated_client.delete(f'/products/{product.id}/note/')
        assert response.status_code == 404
        assert 'No existe nota' in response.json()['message']

    def test_delete_note_product_not_found(self, authenticated_client):
        """Debe retornar 404 si producto no existe."""
        response = authenticated_client.delete('/products/99999/note/')
        assert response.status_code == 404

    def test_delete_note_requires_auth(self, api_client, product):
        """Debe requerir autenticación."""
        response = api_client.delete(f'/products/{product.id}/note/')
        assert response.status_code == 401


@pytest.mark.django_db
class TestProductNoteIsolation:
    """Tests para verificar aislamiento entre usuarios."""

    def test_users_cannot_see_each_other_notes(
        self, authenticated_client, user, admin_user, product
    ):
        """Cada usuario solo ve sus propias notas."""
        # Admin crea nota
        ProductNote.objects.create(
            user=admin_user,
            product=product,
            content="Nota del admin"
        )

        # Usuario normal intenta obtenerla
        response = authenticated_client.get(f'/products/{product.id}/note/')
        assert response.status_code == 404  # No debe verla

    def test_multiple_users_same_product(self, user, admin_user, product):
        """Múltiples usuarios pueden tener notas en el mismo producto."""
        note1 = ProductNote.objects.create(
            user=user,
            product=product,
            content="Nota del usuario"
        )
        note2 = ProductNote.objects.create(
            user=admin_user,
            product=product,
            content="Nota del admin"
        )

        assert ProductNote.objects.filter(product=product).count() == 2
        assert note1.content != note2.content

    def test_user_can_only_update_own_note(self, authenticated_client, user, admin_user, product):
        """Usuario solo puede actualizar su propia nota."""
        # Admin crea nota
        ProductNote.objects.create(
            user=admin_user,
            product=product,
            content="Nota del admin"
        )

        # Usuario normal intenta actualizarla
        payload = {"content": "Intento de modificación"}
        response = authenticated_client.put(f'/products/{product.id}/note/', json=payload)
        assert response.status_code == 404  # No encuentra la nota del admin

    def test_user_can_only_delete_own_note(self, authenticated_client, user, admin_user, product):
        """Usuario solo puede eliminar su propia nota."""
        # Admin crea nota
        admin_note = ProductNote.objects.create(
            user=admin_user,
            product=product,
            content="Nota del admin"
        )

        # Usuario normal intenta eliminarla
        response = authenticated_client.delete(f'/products/{product.id}/note/')
        assert response.status_code == 404  # No encuentra la nota del admin

        # Verificar que la nota del admin sigue existiendo
        assert ProductNote.objects.filter(id=admin_note.id).exists()


@pytest.mark.django_db
class TestProductNoteCascade:
    """Tests para verificar eliminación en cascada."""

    def test_delete_product_deletes_notes(self, user, product):
        """Al eliminar producto, se eliminan sus notas."""
        note = ProductNote.objects.create(
            user=user,
            product=product,
            content="Nota que se eliminará"
        )

        product.delete()

        # Verificar que la nota también se eliminó
        assert not ProductNote.objects.filter(id=note.id).exists()

    def test_delete_user_deletes_notes(self, user, product):
        """Al eliminar usuario, se eliminan sus notas."""
        note = ProductNote.objects.create(
            user=user,
            product=product,
            content="Nota que se eliminará"
        )

        user.delete()

        # Verificar que la nota también se eliminó
        assert not ProductNote.objects.filter(id=note.id).exists()
