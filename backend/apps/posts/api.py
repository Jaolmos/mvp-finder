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
    created_at: datetime
    updated_at: datetime


class PostFilterSchema(FilterSchema):
    """Schema para filtros de posts."""
    subreddit: Optional[int] = None
    analyzed: Optional[bool] = None
    min_score: Optional[int] = None
    search: Optional[str] = None


class FavoriteToggleSchema(Schema):
    """Schema para respuesta de toggle favorite."""
    favorited: bool
    message: str


# Endpoints
@router.get("/", response=List[PostListSchema], auth=JWTAuth())
@paginate(PageNumberPagination, page_size=20)
def list_posts(request, filters: PostFilterSchema = PostFilterSchema()):
    """
    Listar posts con filtros y paginación.

    Requiere autenticación JWT.
    """
    posts = Post.objects.select_related('subreddit').all()

    # Aplicar filtros
    if filters.subreddit:
        posts = posts.filter(subreddit_id=filters.subreddit)

    if filters.analyzed is not None:
        posts = posts.filter(analyzed=filters.analyzed)

    if filters.min_score:
        posts = posts.filter(score__gte=filters.min_score)

    if filters.search:
        posts = posts.filter(title__icontains=filters.search) | posts.filter(content__icontains=filters.search)

    return posts


@router.get("/favorites/", response=List[PostListSchema], auth=JWTAuth())
@paginate(PageNumberPagination, page_size=20)
def list_favorites(request):
    """
    Listar posts favoritos del usuario actual.

    Requiere autenticación JWT.
    """
    user = request.auth
    favorites = Favorite.objects.filter(user=user).select_related('post__subreddit')
    posts = [fav.post for fav in favorites]
    return posts


@router.get("/{post_id}/", response=PostDetailSchema, auth=JWTAuth())
def get_post(request, post_id: int):
    """
    Obtener detalle de un post.

    Requiere autenticación JWT.
    """
    post = get_object_or_404(Post.objects.select_related('subreddit'), id=post_id)
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
            "favorited": False,
            "message": "Post eliminado de favoritos"
        }

    return {
        "favorited": True,
        "message": "Post añadido a favoritos"
    }
