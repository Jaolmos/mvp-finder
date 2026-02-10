"""
Tests para los endpoints de products.
"""

import pytest
from apps.posts.models import Product, Favorite


@pytest.mark.django_db
class TestListProducts:
    """Tests para el endpoint de listar products."""

    def test_list_products_authenticated(self, authenticated_client, product, analyzed_product):
        """Test listar products con autenticación."""
        response = authenticated_client.get('/products/')

        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert 'count' in data
        assert len(data['items']) == 2

    def test_list_products_no_auth(self, api_client, product):
        """Test listar products sin autenticación."""
        response = api_client.get('/products/')

        assert response.status_code == 401

    def test_list_products_filter_by_topic(self, authenticated_client, product, topic):
        """Test filtrar products por topic."""
        response = authenticated_client.get(f'/products/?topic={product.topic.id}')

        assert response.status_code == 200
        data = response.json()
        assert data['count'] >= 1
        for item in data['items']:
            assert item['topic']['id'] == product.topic.id

    def test_list_products_filter_analyzed_true(self, authenticated_client, analyzed_product):
        """Test filtrar products analizados."""
        response = authenticated_client.get('/products/?analyzed=true')

        assert response.status_code == 200
        data = response.json()
        for item in data['items']:
            assert item['analyzed'] is True

    def test_list_products_filter_analyzed_false(self, authenticated_client, product):
        """Test filtrar products no analizados."""
        response = authenticated_client.get('/products/?analyzed=false')

        assert response.status_code == 200
        data = response.json()
        for item in data['items']:
            assert item['analyzed'] is False

    def test_list_products_filter_min_score(self, authenticated_client, product):
        """Test filtrar products por score mínimo."""
        response = authenticated_client.get('/products/?min_score=50')

        assert response.status_code == 200
        data = response.json()
        for item in data['items']:
            assert item['score'] >= 50

        response = authenticated_client.get('/products/?min_score=40')

        assert response.status_code == 200
        data = response.json()
        assert data['count'] >= 1
        for item in data['items']:
            assert item['score'] >= 40

    def test_list_products_filter_search(self, authenticated_client, product):
        """Test buscar products por texto en título o contenido."""
        response = authenticated_client.get('/products/?search=Assistant')

        assert response.status_code == 200
        data = response.json()
        assert data['count'] >= 1
        found = False
        for item in data['items']:
            if 'assistant' in item['title'].lower():
                found = True
                break
        assert found, "No se encontró ningún producto con 'Assistant' en el título"

    def test_list_products_filter_by_tag(self, authenticated_client, analyzed_product):
        """Test filtrar products por tag."""
        response = authenticated_client.get('/products/?tag=productividad')

        assert response.status_code == 200
        data = response.json()
        assert data['count'] >= 1
        for item in data['items']:
            assert 'productividad' in item['tags']

    def test_list_products_filter_by_tag_no_partial_match(self, authenticated_client, analyzed_product):
        """Test que el filtro por tag no hace match parcial."""
        # analyzed_product tiene tags='productividad,focus,pomodoro'
        # 'prod' es subcadena de 'productividad' pero no un tag completo
        response = authenticated_client.get('/products/?tag=prod')

        assert response.status_code == 200
        data = response.json()
        assert data['count'] == 0

    def test_list_products_filter_by_tag_no_results(self, authenticated_client, product):
        """Test filtrar products por tag inexistente."""
        response = authenticated_client.get('/products/?tag=nonexistent-tag-xyz')

        assert response.status_code == 200
        data = response.json()
        assert data['count'] == 0

    def test_list_products_pagination(self, authenticated_client, topic):
        """Test paginación de products."""
        for i in range(25):
            Product.objects.create(
                external_id=f'ph_product{i}',
                topic=topic,
                title=f'Product {i}',
                tagline=f'Tagline {i}',
                content='Content',
                author='author',
                score=i,
                votes_count=i,
                comments_count=0,
                url=f'https://producthunt.com/posts/product{i}',
                created_at_source=topic.created_at
            )

        response = authenticated_client.get('/products/')
        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) == 20

        response = authenticated_client.get('/products/?page=2')
        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) >= 5


@pytest.mark.django_db
class TestGetProduct:
    """Tests para el endpoint de detalle de product."""

    def test_get_product_authenticated(self, authenticated_client, product):
        """Test obtener detalle de product con autenticación."""
        response = authenticated_client.get(f'/products/{product.id}/')

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == product.id
        assert data['external_id'] == product.external_id
        assert data['title'] == product.title
        assert data['content'] == product.content
        assert 'topic' in data
        assert data['topic']['name'] == product.topic.name

    def test_get_product_no_auth(self, api_client, product):
        """Test obtener product sin autenticación."""
        response = api_client.get(f'/products/{product.id}/')

        assert response.status_code == 401

    def test_get_product_not_found(self, authenticated_client):
        """Test obtener product inexistente."""
        response = authenticated_client.get('/products/99999/')

        assert response.status_code == 404


@pytest.mark.django_db
class TestToggleFavorite:
    """Tests para el endpoint de marcar/desmarcar favoritos."""

    def test_toggle_favorite_add(self, authenticated_client, product, user):
        """Test añadir product a favoritos."""
        response = authenticated_client.post(f'/products/{product.id}/favorite/')

        assert response.status_code == 200
        data = response.json()
        assert data['is_favorite'] is True
        assert 'añadido' in data['message'].lower()

        assert Favorite.objects.filter(user=user, product=product).exists()

    def test_toggle_favorite_remove(self, authenticated_client, product, user):
        """Test quitar product de favoritos."""
        Favorite.objects.create(user=user, product=product)

        response = authenticated_client.post(f'/products/{product.id}/favorite/')

        assert response.status_code == 200
        data = response.json()
        assert data['is_favorite'] is False
        assert 'eliminado' in data['message'].lower()

        assert not Favorite.objects.filter(user=user, product=product).exists()

    def test_toggle_favorite_no_auth(self, api_client, product):
        """Test toggle favorite sin autenticación."""
        response = api_client.post(f'/products/{product.id}/favorite/')

        assert response.status_code == 401

    def test_toggle_favorite_product_not_found(self, authenticated_client):
        """Test toggle favorite de product inexistente."""
        response = authenticated_client.post('/products/99999/favorite/')

        assert response.status_code == 404


@pytest.mark.django_db
class TestListFavorites:
    """Tests para el endpoint de listar favoritos."""

    def test_list_favorites_authenticated(self, authenticated_client, product, analyzed_product, user):
        """Test listar favoritos del usuario."""
        Favorite.objects.create(user=user, product=product)
        Favorite.objects.create(user=user, product=analyzed_product)

        response = authenticated_client.get('/products/favorites/')

        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert len(data['items']) == 2

    def test_list_favorites_empty(self, authenticated_client, user):
        """Test listar favoritos cuando no hay ninguno."""
        response = authenticated_client.get('/products/favorites/')

        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) == 0

    def test_list_favorites_no_auth(self, api_client):
        """Test listar favoritos sin autenticación."""
        response = api_client.get('/products/favorites/')

        assert response.status_code == 401

    def test_list_favorites_only_user_favorites(self, authenticated_client, product, user, admin_user):
        """Test que solo muestra favoritos del usuario actual."""
        Favorite.objects.create(user=user, product=product)
        Favorite.objects.create(user=admin_user, product=product)

        response = authenticated_client.get('/products/favorites/')

        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) == 1


@pytest.mark.django_db
class TestProductOrdering:
    """Tests para el ordenamiento de productos."""

    def test_ordering_by_date_desc_default(self, authenticated_client, topic):
        """Test ordenamiento por fecha descendente (por defecto)."""
        from django.utils import timezone
        from datetime import timedelta

        # Crear productos con fechas diferentes
        old = Product.objects.create(
            external_id='ph_old',
            topic=topic,
            title='Old Product',
            tagline='Old',
            content='Old',
            author='author',
            score=100,
            votes_count=100,
            comments_count=10,
            url='https://ph.com/old',
            created_at_source=timezone.now() - timedelta(days=10)
        )
        new = Product.objects.create(
            external_id='ph_new',
            topic=topic,
            title='New Product',
            tagline='New',
            content='New',
            author='author',
            score=50,
            votes_count=50,
            comments_count=5,
            url='https://ph.com/new',
            created_at_source=timezone.now()
        )

        response = authenticated_client.get('/products/')
        assert response.status_code == 200
        data = response.json()

        # El más reciente debe estar primero
        assert data['items'][0]['external_id'] == 'ph_new'

    def test_ordering_by_date_asc(self, authenticated_client, topic):
        """Test ordenamiento por fecha ascendente."""
        from django.utils import timezone
        from datetime import timedelta

        old = Product.objects.create(
            external_id='ph_oldest',
            topic=topic,
            title='Oldest Product',
            tagline='Old',
            content='Old',
            author='author',
            score=100,
            votes_count=100,
            comments_count=10,
            url='https://ph.com/oldest',
            created_at_source=timezone.now() - timedelta(days=30)
        )
        new = Product.objects.create(
            external_id='ph_newest',
            topic=topic,
            title='Newest Product',
            tagline='New',
            content='New',
            author='author',
            score=50,
            votes_count=50,
            comments_count=5,
            url='https://ph.com/newest',
            created_at_source=timezone.now()
        )

        response = authenticated_client.get('/products/?ordering=created_at_source')
        assert response.status_code == 200
        data = response.json()

        # El más antiguo debe estar primero
        assert data['items'][0]['external_id'] == 'ph_oldest'

    def test_ordering_by_votes_desc(self, authenticated_client, topic):
        """Test ordenamiento por votos descendente."""
        low_votes = Product.objects.create(
            external_id='ph_lowvotes',
            topic=topic,
            title='Low Votes',
            tagline='Low',
            content='Low',
            author='author',
            score=10,
            votes_count=10,
            comments_count=1,
            url='https://ph.com/lowvotes',
            created_at_source=topic.created_at
        )
        high_votes = Product.objects.create(
            external_id='ph_highvotes',
            topic=topic,
            title='High Votes',
            tagline='High',
            content='High',
            author='author',
            score=1000,
            votes_count=1000,
            comments_count=100,
            url='https://ph.com/highvotes',
            created_at_source=topic.created_at
        )

        response = authenticated_client.get('/products/?ordering=-votes_count')
        assert response.status_code == 200
        data = response.json()

        # El de más votos debe estar primero
        assert data['items'][0]['external_id'] == 'ph_highvotes'

    def test_ordering_by_potential_filters_analyzed(self, authenticated_client, topic):
        """Test que ordenar por potencial filtra solo productos analizados."""
        from django.utils import timezone

        # Producto sin analizar
        not_analyzed = Product.objects.create(
            external_id='ph_notanalyzed',
            topic=topic,
            title='Not Analyzed',
            tagline='Not',
            content='Not',
            author='author',
            score=100,
            votes_count=100,
            comments_count=10,
            url='https://ph.com/notanalyzed',
            created_at_source=timezone.now(),
            analyzed=False,
            potential_score=None
        )
        # Producto analizado con bajo potencial
        low_potential = Product.objects.create(
            external_id='ph_lowpotential',
            topic=topic,
            title='Low Potential',
            tagline='Low',
            content='Low',
            author='author',
            score=100,
            votes_count=100,
            comments_count=10,
            url='https://ph.com/lowpotential',
            created_at_source=timezone.now(),
            analyzed=True,
            potential_score=3
        )
        # Producto analizado con alto potencial
        high_potential = Product.objects.create(
            external_id='ph_highpotential',
            topic=topic,
            title='High Potential',
            tagline='High',
            content='High',
            author='author',
            score=100,
            votes_count=100,
            comments_count=10,
            url='https://ph.com/highpotential',
            created_at_source=timezone.now(),
            analyzed=True,
            potential_score=9
        )

        response = authenticated_client.get('/products/?ordering=-potential_score')
        assert response.status_code == 200
        data = response.json()

        # Solo deben aparecer los analizados
        external_ids = [item['external_id'] for item in data['items']]
        assert 'ph_notanalyzed' not in external_ids
        assert 'ph_highpotential' in external_ids
        assert 'ph_lowpotential' in external_ids

        # El de mayor potencial debe estar primero
        assert data['items'][0]['external_id'] == 'ph_highpotential'

    def test_ordering_invalid_ignored(self, authenticated_client, product):
        """Test que un ordenamiento inválido usa el por defecto."""
        response = authenticated_client.get('/products/?ordering=invalid_field')
        assert response.status_code == 200
        # No debe dar error, usa ordenamiento por defecto


# Ejecutar: docker compose exec backend uv run pytest tests/test_products.py -v
