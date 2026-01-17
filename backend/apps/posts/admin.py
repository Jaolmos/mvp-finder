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

    list_display = ['title', 'subreddit', 'author', 'score', 'analyzed', 'created_at_reddit']
    list_filter = ['analyzed', 'subreddit', 'created_at_reddit']
    search_fields = ['title', 'content', 'author', 'reddit_id']
    readonly_fields = ['reddit_id', 'created_at', 'updated_at', 'analyzed_at']
    ordering = ['-created_at_reddit']
    date_hierarchy = 'created_at_reddit'

    fieldsets = (
        ('Datos de Reddit', {
            'fields': ('reddit_id', 'subreddit', 'title', 'content', 'author', 'score', 'url', 'created_at_reddit')
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
        """Optimiza consultas incluyendo el subreddit relacionado."""
        qs = super().get_queryset(request)
        return qs.select_related('subreddit')
