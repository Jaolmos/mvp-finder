# MVP Finder

Aplicación web para descubrir oportunidades de negocio analizando productos de Product Hunt con IA local.

## Stack Tecnológico

- **Backend**: Django 5.2 + Django Ninja
- **Frontend**: Vue.js 3 + TypeScript + Tailwind CSS v4
- **Base de datos**: PostgreSQL 16
- **IA**: Ollama (qwen2.5:3b) para análisis de productos
- **Cache**: Redis 7
- **Tasks**: Celery
- **Containerización**: Docker Compose

## Características

- Sincronización automática de productos desde Product Hunt
- Análisis IA de productos (resumen, problema, idea MVP, potencial)
- Sistema de favoritos y notas personales
- Filtrado avanzado (topic, potencial, analizados)
- Ordenamiento por fecha, votos o potencial
- Autenticación JWT
- API REST documentada (Swagger)

## Estado del Proyecto

- **Backend**: 121 tests passing
- **Frontend**: 118 tests passing
- **Productos sincronizados**: 814
- **Topics activos**: artificial-intelligence, developer-tools, productivity

## Configuración Local

### Prerequisitos

- Docker y Docker Compose
- Python 3.14+ con `uv` (para desarrollo sin Docker)
- Node.js 18+ (para desarrollo frontend sin Docker)

### Levantar servicios

```bash
# Clonar repositorio
git clone <repo-url>
cd mvp_finder

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Product Hunt

# Levantar servicios
docker compose up -d

# Aplicar migraciones
docker compose exec backend uv run manage.py migrate

# Crear superusuario
docker compose exec backend uv run manage.py createsuperuser

# Descargar modelo de Ollama
docker compose exec ollama ollama pull qwen2.5:3b
```

Acceder a:
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/api/docs
- Admin: http://localhost:8000/admin

## Testing

```bash
# Tests backend
docker compose exec backend uv run pytest -v

# Tests frontend
docker compose exec frontend npm run test:unit -- --run
```

## Desarrollo

Ver `CLAUDE.md` para convenciones de código, estructura del proyecto y guías de desarrollo.

## Licencia

Privado - Todos los derechos reservados
