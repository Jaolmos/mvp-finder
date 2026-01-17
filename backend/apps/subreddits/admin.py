"""
Configuración del admin para la app subreddits.
"""

from django.contrib import admin
from .models import Subreddit


@admin.register(Subreddit)
class SubredditAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Subreddit.
    """

    list_display = ['name', 'active', 'last_sync', 'created_at']
    list_filter = ['active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']

    fieldsets = (
        ('Información del Subreddit', {
            'fields': ('name', 'active')
        }),
        ('Sincronización', {
            'fields': ('last_sync',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
