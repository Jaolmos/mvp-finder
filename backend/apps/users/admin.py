"""
Configuración del admin para la app users.
"""

from django.contrib import admin
from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Favorite.
    """

    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'post__title']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Información del Favorito', {
            'fields': ('user', 'post')
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimiza consultas incluyendo user y post relacionados."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'post', 'post__subreddit')
