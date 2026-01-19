"""
API de posts con Django Ninja.
"""

from ninja import Router, Schema, FilterSchema, Field
from ninja.pagination import paginate, PageNumberPagination
from typing import List, Optional
from datetime import datetime
from django.shortcuts import get_object_or_404
from config.auth import JWTAuth
from .models import Post
from apps.users.models import Favorite

router = Router(tags=["Posts"])


# Schemas
class SubredditSchema(Schema):
    """Schema para subreddit en la respuesta de posts."""
    id: int
    name: str


class PostListSchema(Schema):
    """Schema para listar posts (sin contenido completo)."""
    id: int
    reddit_id: str
    subreddit: SubredditSchema
    title: str
    author: str
    score: int
    url: str
    created_at_reddit: datetime
    analyzed: bool
    potential_score: Optional[int] = None
    tags: str
    summary: str
    is_favorite: bool = False


class PostDetailSchema(Schema):
    """Schema para detalle de post (con contenido completo)."""
    id: int
    reddit_id: str
    subreddit: SubredditSchema
    title: str
    content: str
    author: str
    score: int
    url: str
    created_at_reddit: datetime
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


class PostFilterSchema(FilterSchema):
    """Schema para filtros de posts."""
    subreddit: Optional[int] = None
    analyzed: Optional[bool] = None
    min_score: Optional[int] = None
    search: Optional[str] = None
    is_favorite: Optional[bool] = None


class FavoriteToggleSchema(Schema):
    """Schema para respuesta de toggle favorite."""
    is_favorite: bool
    message: str


# Endpoints
@router.get("/", response=List[PostListSchema], auth=JWTAuth())
@paginate(PageNumberPagination, page_size=20)
def list_posts(request, filters: PostFilterSchema = PostFilterSchema()):
    """
    Listar posts con filtros y paginación.

    Requiere autenticación JWT.
    """
    from django.db.models import Exists, OuterRef

    user = request.auth
    posts = Post.objects.select_related('subreddit').annotate(
        is_favorite=Exists(Favorite.objects.filter(user=user, post=OuterRef('pk')))
    ).all()

    # Aplicar filtros
    if filters.subreddit:
        posts = posts.filter(subreddit_id=filters.subreddit)

    if filters.analyzed is not None:
        posts = posts.filter(analyzed=filters.analyzed)

    if filters.min_score:
        posts = posts.filter(score__gte=filters.min_score)

    if filters.search:
        posts = posts.filter(title__icontains=filters.search) | posts.filter(content__icontains=filters.search)

    if filters.is_favorite:
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
    # Obtener los IDs de posts favoritos
    favorite_ids = Favorite.objects.filter(user=user).values_list('post_id', flat=True)
    posts = Post.objects.filter(id__in=favorite_ids).select_related('subreddit').annotate(
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
        Post.objects.select_related('subreddit').annotate(
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
        # Ya existía, lo eliminamos
        favorite.delete()
        return {
            "is_favorite": False,
            "message": "Post eliminado de favoritos"
        }

    return {
        "is_favorite": True,
        "message": "Post añadido a favoritos"
    }
