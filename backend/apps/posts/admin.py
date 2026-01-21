"""
Configuración del admin para la app posts.
"""

from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Post.
    """

    list_display = ['title', 'topic', 'author', 'score', 'votes_count', 'comments_count', 'analyzed', 'created_at_source']
    list_filter = ['analyzed', 'topic', 'created_at_source']
    search_fields = ['title', 'content', 'tagline', 'author', 'external_id']
    readonly_fields = ['external_id', 'created_at', 'updated_at', 'analyzed_at']
    ordering = ['-created_at_source']
    date_hierarchy = 'created_at_source'

    fieldsets = (
        ('Datos de Product Hunt', {
            'fields': ('external_id', 'topic', 'title', 'tagline', 'content', 'author', 'score', 'votes_count', 'comments_count', 'url', 'website', 'created_at_source')
        }),
        ('Análisis IA', {
            'fields': ('analyzed', 'analyzed_at', 'summary', 'problem', 'mvp_idea', 'target_audience', 'potential_score', 'tags'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimiza consultas incluyendo el topic relacionado."""
        qs = super().get_queryset(request)
        return qs.select_related('topic')
