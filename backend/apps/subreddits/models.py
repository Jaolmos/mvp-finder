"""
Modelos para la app subreddits.
"""

from django.db import models


class Subreddit(models.Model):
    """
    Modelo para gestionar subreddits a monitorear.

    Cada subreddit representa una comunidad de Reddit que queremos
    monitorear para encontrar posts con ideas/problemas/necesidades.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre del subreddit (ej: SomebodyMakeThis)"
    )
    active = models.BooleanField(
        default=True,
        help_text="Si está activo para scraping"
    )
    last_sync = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Última vez que se sincronizó con Reddit"
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
        verbose_name = "Subreddit"
        verbose_name_plural = "Subreddits"

    def __str__(self):
        return f"r/{self.name}"
