"""
Modelos para la app posts.
"""

from django.db import models
from apps.subreddits.models import Subreddit


class Post(models.Model):
    """
    Modelo para almacenar posts de Reddit.

    Cada post representa una publicación de Reddit que contiene
    una idea, problema o necesidad expresada por un usuario.
    """

    # Datos del post de Reddit
    reddit_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="ID único del post en Reddit"
    )
    subreddit = models.ForeignKey(
        Subreddit,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text="Subreddit de origen"
    )
    title = models.CharField(
        max_length=300,
        help_text="Título del post"
    )
    content = models.TextField(
        blank=True,
        help_text="Contenido completo del post"
    )
    author = models.CharField(
        max_length=100,
        help_text="Autor del post en Reddit"
    )
    score = models.IntegerField(
        default=0,
        help_text="Puntuación (upvotes) en Reddit"
    )
    url = models.URLField(
        max_length=500,
        help_text="URL del post en Reddit"
    )
    created_at_reddit = models.DateTimeField(
        help_text="Fecha de creación en Reddit"
    )

    # Campos de análisis IA (opcionales hasta que se analice)
    summary = models.TextField(
        blank=True,
        help_text="Resumen de 1 línea del problema/idea"
    )
    problem = models.TextField(
        blank=True,
        help_text="Problema identificado por la IA"
    )
    mvp_idea = models.TextField(
        blank=True,
        help_text="Idea de MVP sugerida por la IA"
    )
    target_audience = models.CharField(
        max_length=200,
        blank=True,
        help_text="Público objetivo identificado"
    )
    potential_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Puntuación de potencial 1-10"
    )
    tags = models.TextField(
        blank=True,
        help_text="Tags separados por comas"
    )
    analyzed = models.BooleanField(
        default=False,
        help_text="Si ya fue analizado por la IA"
    )
    analyzed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Cuándo fue analizado por la IA"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de importación a nuestra BD"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Última actualización del registro"
    )

    class Meta:
        ordering = ['-created_at_reddit']
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        indexes = [
            models.Index(fields=['reddit_id']),
            models.Index(fields=['analyzed']),
            models.Index(fields=['-created_at_reddit']),
        ]

    def __str__(self):
        return f"{self.title[:50]}... (r/{self.subreddit.name})"
