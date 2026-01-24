"""
API de posts con Django Ninja.
"""

from ninja import Router, Schema, Field
from ninja.pagination import paginate, PageNumberPagination
from typing import List, Optional
from datetime import datetime
from django.shortcuts import get_object_or_404
from config.auth import JWTAuth
from .models import Post, Favorite

router = Router(tags=["Posts"])


# Schemas
class TopicSchema(Schema):
    """Schema para topic en la respuesta de posts."""
    id: int
    name: str


class PostListSchema(Schema):
    """Schema para listar posts (sin contenido completo)."""
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


class PostDetailSchema(Schema):
    """Schema para detalle de post (con contenido completo)."""
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
    """Schema para estadísticas de posts."""
    total_posts: int
    analyzed_posts: int
    favorites_count: int


# Endpoints
@router.get("/stats/", response=StatsSchema, auth=JWTAuth())
def get_stats(request):
    """
    Obtener estadísticas globales de posts.
    """
    user = request.auth
    return {
        "total_posts": Post.objects.count(),
        "analyzed_posts": Post.objects.filter(analyzed=True).count(),
        "favorites_count": Favorite.objects.filter(user=user).count(),
    }
@router.get("/", response=List[PostListSchema], auth=JWTAuth())
@paginate(PageNumberPagination, page_size=20)
def list_posts(
    request,
    topic: Optional[int] = None,
    analyzed: Optional[bool] = None,
    min_score: Optional[int] = None,
    min_potential: Optional[int] = None,
    search: Optional[str] = None,
    is_favorite: Optional[bool] = None
):
    """
    Listar posts con filtros y paginación.

    Requiere autenticación JWT.
    """
    from django.db.models import Exists, OuterRef

    user = request.auth
    posts = Post.objects.select_related('topic').annotate(
        is_favorite=Exists(Favorite.objects.filter(user=user, post=OuterRef('pk')))
    ).all()

    # Aplicar filtros
    if topic:
        posts = posts.filter(topic_id=topic)

    if analyzed is not None:
        posts = posts.filter(analyzed=analyzed)

    if min_score:
        posts = posts.filter(score__gte=min_score)

    if min_potential:
        posts = posts.filter(potential_score__gte=min_potential)

    if search:
        from django.db.models import Q
        posts = posts.filter(Q(title__icontains=search) | Q(content__icontains=search))

    if is_favorite:
        posts = posts.filter(is_favorite=True)

    return posts


@router.get("/favorites/", response=List[PostListSchema], auth=JWTAuth())
@paginate(PageNumberPagination, page_size=20)
def list_favorites(request):
    """
    Listar posts favoritos del usuario actual.

    Requiere autenticación JWT.
    """
    from django.db.models import Exists, OuterRef, Value
    from django.db.models.functions import Coalesce

    user = request.auth
    favorite_ids = Favorite.objects.filter(user=user).values_list('post_id', flat=True)
    posts = Post.objects.filter(id__in=favorite_ids).select_related('topic').annotate(
        is_favorite=Value(True)
    )
    return posts


@router.get("/{post_id}/", response=PostDetailSchema, auth=JWTAuth())
def get_post(request, post_id: int):
    """
    Obtener detalle de un post.

    Requiere autenticación JWT.
    """
    from django.db.models import Exists, OuterRef

    user = request.auth
    post = get_object_or_404(
        Post.objects.select_related('topic').annotate(
            is_favorite=Exists(Favorite.objects.filter(user=user, post=OuterRef('pk')))
        ),
        id=post_id
    )
    return post


@router.post("/{post_id}/favorite/", response=FavoriteToggleSchema, auth=JWTAuth())
def toggle_favorite(request, post_id: int):
    """
    Marcar o desmarcar un post como favorito.

    Requiere autenticación JWT.
    """
    user = request.auth
    post = get_object_or_404(Post, id=post_id)

    favorite, created = Favorite.objects.get_or_create(user=user, post=post)

    if not created:
        favorite.delete()
        return {
            "is_favorite": False,
            "message": "Post eliminado de favoritos"
        }

    return {
        "is_favorite": True,
        "message": "Post añadido a favoritos"
    }
