"""
Modelos para la app users.
"""

from django.db import models
from django.contrib.auth.models import User
from apps.posts.models import Post


class Favorite(models.Model):
    """
    Modelo para gestionar posts favoritos de usuarios.

    Permite a los usuarios marcar posts como favoritos para
    consultarlos más tarde o darles seguimiento.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        help_text="Usuario que marcó el favorito"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        help_text="Post marcado como favorito"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Cuándo se marcó como favorito"
    )

    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-created_at']
        verbose_name = "Favorito"
        verbose_name_plural = "Favoritos"

    def __str__(self):
        return f"{self.user.username} - {self.post.title[:30]}..."
