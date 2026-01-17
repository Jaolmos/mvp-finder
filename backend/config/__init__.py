"""
Inicialización del proyecto Django con Celery.
"""

from .celery import app as celery_app

__all__ = ('celery_app',)
