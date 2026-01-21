"""
Configuración del admin para la app topics.
"""

from django.contrib import admin
from .models import Topic


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Topic.
    """

    list_display = ['name', 'is_active', 'last_sync', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']

    fieldsets = (
        ('Información del Topic', {
            'fields': ('name', 'is_active')
        }),
        ('Sincronización', {
            'fields': ('last_sync',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
