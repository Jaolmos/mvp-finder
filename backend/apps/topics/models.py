"""
Modelos para la app topics.
"""

from django.db import models


class Topic(models.Model):
    """
    Modelo para gestionar topics a monitorear.

    Cada topic representa una categoría de Product Hunt que queremos
    monitorear para encontrar productos con ideas/problemas/necesidades.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre del topic (ej: artificial-intelligence)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Si está activo para scraping"
    )
    last_sync = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Última vez que se sincronizó con Product Hunt"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación del registro"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Última actualización del registro"
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Topic"
        verbose_name_plural = "Topics"
        db_table = 'subreddits_subreddit'

    def __str__(self):
        return self.name
