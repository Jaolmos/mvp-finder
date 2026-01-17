FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

# Configurar uv para instalar en el sistema
ENV UV_SYSTEM_PYTHON=1

# Copiar archivos de dependencias
COPY backend/pyproject.toml backend/uv.lock ./

# Instalar dependencias
RUN uv sync --frozen --no-cache

# Copiar código de la aplicación
COPY backend/ .

# Crear usuario no-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
