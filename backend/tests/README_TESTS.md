# Guía de Tests del Backend

Esta guía explica cómo ejecutar los tests del backend del proyecto Reddit MVP Finder.

## Estructura de Tests

```
backend/tests/
├── README_TESTS.md       # Esta guía
├── test_auth.py          # Tests de autenticación (login, tokens, usuario actual)
├── test_posts.py         # Tests de endpoints de posts (listar, filtrar, favoritos)
└── test_subreddits.py    # Tests CRUD de subreddits
```

## Fixtures Disponibles

Los fixtures están definidos en `backend/conftest.py`:

- `user` - Usuario de prueba básico
- `admin_user` - Usuario administrador
- `tokens` - Tokens JWT (access y refresh)
- `subreddit` - Subreddit activo de prueba
- `inactive_subreddit` - Subreddit inactivo
- `post` - Post sin analizar
- `analyzed_post` - Post analizado por IA
- `api_client` - Cliente API de Django Ninja
- `authenticated_client` - Cliente API con autenticación JWT

## Cómo Ejecutar los Tests

### Opción Recomendada: Usando Docker Compose (desde tu terminal)

Esta es la forma principal de trabajar, ya que todo el entorno está en Docker:

```bash
# Asegúrate de estar en el directorio raíz del proyecto
cd ~/Proyectos/reto_apps_2026/3.reddit_mvp_finder

# Ejecutar todos los tests
docker compose exec backend uv run pytest -v

# Ejecutar tests de un archivo específico
docker compose exec backend uv run pytest tests/test_auth.py -v
docker compose exec backend uv run pytest tests/test_posts.py -v
docker compose exec backend uv run pytest tests/test_subreddits.py -v

# Ejecutar con cobertura de código
docker compose exec backend uv run pytest --cov=apps -v

# Ejecutar un test específico por nombre de clase y método
docker compose exec backend uv run pytest tests/test_auth.py::TestLogin::test_login_success -v

# Ejecutar tests que coincidan con un patrón
docker compose exec backend uv run pytest -k "filter" -v
```

### Opción Alternativa: Desde dentro del contenedor

Solo si prefieres entrar al contenedor y ejecutar múltiples comandos:

```bash
# Entrar al contenedor
docker compose exec backend bash

# Ahora estás dentro del contenedor (prompt: root@xxxxx:/app#)
# Ejecutar tests directamente:

uv run pytest -v                              # Todos los tests
uv run pytest tests/test_auth.py -v           # Tests de autenticación
uv run pytest tests/test_posts.py -v          # Tests de posts
uv run pytest tests/test_subreddits.py -v     # Tests de subreddits
uv run pytest --cov=apps -v                   # Con cobertura

# Salir del contenedor
exit
```

## Requisitos Previos

1. **Docker debe estar corriendo:**
   ```bash
   docker compose up -d
   ```

2. **Base de datos debe estar disponible:**
   Los tests usan la base de datos PostgreSQL configurada en Docker.

## Opciones Útiles de pytest

```bash
# Modo verbose (muestra cada test)
-v

# Modo muy verbose (muestra más detalles)
-vv

# Detener en el primer fallo
-x

# Mostrar print() statements
-s

# Ejecutar solo tests que fallaron la última vez
--lf

# Cobertura de código
--cov=apps

# Reporte de cobertura en HTML
--cov=apps --cov-report=html
```

## Ejemplos Combinados

```bash
# Ejecutar tests de posts con detener en primer error
docker compose exec backend uv run pytest tests/test_posts.py -v -x

# Ejecutar todos los tests con cobertura y reporte HTML
docker compose exec backend uv run pytest --cov=apps --cov-report=html -v

# Ejecutar solo tests que contengan "filter" en el nombre
docker compose exec backend uv run pytest -k "filter" -v
```

## Configuración de pytest

La configuración está en `backend/pytest.ini`:

- `DJANGO_SETTINGS_MODULE`: Usa settings de local
- `--reuse-db`: Reutiliza la base de datos entre ejecuciones (más rápido)
- `--strict-markers`: Requiere que los markers estén definidos
- `-v`: Modo verbose por defecto

## Troubleshooting

### Error: "pytest: executable file not found"

Estás intentando ejecutar `pytest` directamente en el contenedor. Usa `uv run pytest` en su lugar.

### Error: "file or directory not found: backend/tests/..."

Estás dentro del contenedor (en `/app`) pero usas rutas con `backend/`. Omite el prefijo `backend/`:
- ❌ `uv run pytest backend/tests/test_auth.py`
- ✅ `uv run pytest tests/test_auth.py`

### Error: "No such service: backend"

Docker no está corriendo. Ejecuta:
```bash
docker compose up -d
```

### Tests fallan por datos residuales

Si usas `--reuse-db`, los datos persisten entre ejecuciones. Recrea la BD:
```bash
docker compose exec backend uv run pytest --create-db
```

## Estado Actual de los Tests

- ✅ test_auth.py: 11/11 tests passing
- ✅ test_posts.py: 28/28 tests (algunos pueden fallar por --reuse-db)
- ✅ test_subreddits.py: 11/11 tests passing

**Total: 50 tests implementados**
