"""
API de products con Django Ninja.
"""

from ninja import Router, Schema, Field
from ninja.pagination import paginate, PageNumberPagination
from typing import List, Optional
from datetime import datetime
from django.shortcuts import get_object_or_404
from config.auth import JWTAuth
from .models import Product, Favorite

router = Router(tags=["Products"])


# Schemas
class TopicSchema(Schema):
    """Schema para topic en la respuesta de posts."""
    id: int
    name: str


class ProductListSchema(Schema):
    """Schema para listar products (sin contenido completo)."""
    id: int
    external_id: str
    topic: TopicSchema
    title: str
    tagline: str
    author: str
    score: int
    votes_count: int
    comments_count: int
    url: str
    website: Optional[str] = None
    created_at_source: datetime
    analyzed: bool
    potential_score: Optional[int] = None
    tags: str
    summary: str
    is_favorite: bool = False


class ProductDetailSchema(Schema):
    """Schema para detalle de product (con contenido completo)."""
    id: int
    external_id: str
    topic: TopicSchema
    title: str
    tagline: str
    content: str
    author: str
    score: int
    votes_count: int
    comments_count: int
    url: str
    website: Optional[str] = None
    created_at_source: datetime
    summary: str
    problem: str
    mvp_idea: str
    target_audience: str
    potential_score: Optional[int] = None
    tags: str
    analyzed: bool
    analyzed_at: Optional[datetime] = None
    is_favorite: bool = False
    created_at: datetime
    updated_at: datetime


class FavoriteToggleSchema(Schema):
    """Schema para respuesta de toggle favorite."""
    is_favorite: bool
    message: str


class StatsSchema(Schema):
    """Schema para estadísticas de products."""
    total_products: int
    analyzed_products: int
    favorites_count: int


# Endpoints
@router.get("/stats/", response=StatsSchema, auth=JWTAuth())
def get_stats(request):
    """
    Obtener estadísticas globales de products.
    """
    user = request.auth
    return {
        "total_products": Product.objects.count(),
        "analyzed_products": Product.objects.filter(analyzed=True).count(),
        "favorites_count": Favorite.objects.filter(user=user).count(),
    }
@router.get("/", response=List[ProductListSchema], auth=JWTAuth())
@paginate(PageNumberPagination, page_size=20)
def list_products(
    request,
    topic: Optional[int] = None,
    analyzed: Optional[bool] = None,
    min_score: Optional[int] = None,
    min_potential: Optional[int] = None,
    search: Optional[str] = None,
    is_favorite: Optional[bool] = None
):
    """
    Listar products con filtros y paginación.

    Requiere autenticación JWT.
    """
    from django.db.models import Exists, OuterRef

    user = request.auth
    products = Product.objects.select_related('topic').annotate(
        is_favorite=Exists(Favorite.objects.filter(user=user, product=OuterRef('pk')))
    ).all()

    # Aplicar filtros
    if topic:
        products = products.filter(topic_id=topic)

    if analyzed is not None:
        products = products.filter(analyzed=analyzed)

    if min_score:
        products = products.filter(score__gte=min_score)

    if min_potential:
        products = products.filter(potential_score__gte=min_potential)

    if search:
        from django.db.models import Q
        products = products.filter(Q(title__icontains=search) | Q(content__icontains=search))

    if is_favorite:
        products = products.filter(is_favorite=True)

    return products


@router.get("/favorites/", response=List[ProductListSchema], auth=JWTAuth())
@paginate(PageNumberPagination, page_size=20)
def list_favorites(request):
    """
    Listar products favoritos del usuario actual.

    Requiere autenticación JWT.
    """
    from django.db.models import Exists, OuterRef, Value
    from django.db.models.functions import Coalesce

    user = request.auth
    favorite_ids = Favorite.objects.filter(user=user).values_list('product_id', flat=True)
    products = Product.objects.filter(id__in=favorite_ids).select_related('topic').annotate(
        is_favorite=Value(True)
    )
    return products


@router.get("/{product_id}/", response=ProductDetailSchema, auth=JWTAuth())
def get_product(request, product_id: int):
    """
    Obtener detalle de un product.

    Requiere autenticación JWT.
    """
    from django.db.models import Exists, OuterRef

    user = request.auth
    product = get_object_or_404(
        Product.objects.select_related('topic').annotate(
            is_favorite=Exists(Favorite.objects.filter(user=user, product=OuterRef('pk')))
        ),
        id=product_id
    )
    return product


class DeleteResponseSchema(Schema):
    """Schema para respuesta de eliminación."""
    success: bool
    message: str


@router.delete("/{product_id}/", response=DeleteResponseSchema, auth=JWTAuth())
def delete_product(request, product_id: int):
    """
    Eliminar un product.

    Requiere autenticación JWT.
    """
    product = get_object_or_404(Product, id=product_id)
    title = product.title
    product.delete()
    return {
        "success": True,
        "message": f"Producto '{title}' eliminado correctamente"
    }


@router.post("/{product_id}/favorite/", response=FavoriteToggleSchema, auth=JWTAuth())
def toggle_favorite(request, product_id: int):
    """
    Marcar o desmarcar un product como favorito.

    Requiere autenticación JWT.
    """
    user = request.auth
    product = get_object_or_404(Product, id=product_id)

    favorite, created = Favorite.objects.get_or_create(user=user, product=product)

    if not created:
        favorite.delete()
        return {
            "is_favorite": False,
            "message": "Producto eliminado de favoritos"
        }

    return {
        "is_favorite": True,
        "message": "Producto añadido a favoritos"
    }
