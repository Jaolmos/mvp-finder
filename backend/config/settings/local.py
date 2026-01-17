"""
Configuración de desarrollo local.
"""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# PostgreSQL (usar cuando Docker esté activo)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('POSTGRES_DB', 'reddit_mvp_finder'),
#         'USER': os.environ.get('POSTGRES_USER', 'postgres'),
#         'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
#         'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
#         'PORT': os.environ.get('POSTGRES_PORT', '5432'),
#     }
# }

# SQLite para desarrollo sin Docker
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS para desarrollo
CORS_ALLOW_ALL_ORIGINS = True

# Cache con Redis (descomentar cuando Docker esté activo)
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
#     }
# }
