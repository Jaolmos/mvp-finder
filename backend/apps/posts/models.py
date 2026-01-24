"""
Modelos para la app posts.
"""

from django.db import models
from django.contrib.auth.models import User
from apps.topics.models import Topic


class Post(models.Model):
    """
    Modelo para almacenar productos de Product Hunt.

    Cada post representa un producto de Product Hunt que contiene
    una idea, problema o necesidad expresada por sus creadores.
    """

    # Datos del producto de Product Hunt
    external_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="ID único del producto en Product Hunt"
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text="Topic de origen"
    )
    title = models.CharField(
        max_length=300,
        help_text="Nombre del producto"
    )
    tagline = models.CharField(
        max_length=300,
        blank=True,
        help_text="Tagline del producto"
    )
    content = models.TextField(
        blank=True,
        help_text="Descripción completa del producto"
    )
    author = models.CharField(
        max_length=100,
        help_text="Maker principal del producto"
    )
    score = models.IntegerField(
        default=0,
        help_text="Puntuación (votos) en Product Hunt"
    )
    votes_count = models.IntegerField(
        default=0,
        help_text="Número de votos"
    )
    comments_count = models.IntegerField(
        default=0,
        help_text="Número de comentarios"
    )
    url = models.URLField(
        max_length=500,
        help_text="URL del producto en Product Hunt"
    )
    website = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL del sitio web del producto"
    )
    created_at_source = models.DateTimeField(
        help_text="Fecha de creación en Product Hunt"
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
        ordering = ['-created_at_source']
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        indexes = [
            models.Index(fields=['external_id']),
            models.Index(fields=['analyzed']),
            models.Index(fields=['-created_at_source']),
        ]

    def __str__(self):
        return f"{self.title[:50]}... ({self.topic.name})"


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
        db_table = 'users_favorite'  # Mantener tabla existente
        unique_together = ['user', 'post']
        ordering = ['-created_at']
        verbose_name = "Favorito"
        verbose_name_plural = "Favoritos"

    def __str__(self):
        return f"{self.user.username} - {self.post.title[:30]}..."
