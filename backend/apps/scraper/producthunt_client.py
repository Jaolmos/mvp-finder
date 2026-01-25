"""
Cliente de Product Hunt usando GraphQL API.
Maneja la conexión y autenticación con la API de Product Hunt.
Usa OAuth 2.0 Client Credentials flow.
"""
import os
import time
import logging
import httpx
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class ProductHuntClient:
    """Cliente singleton para conexión con Product Hunt API."""

    _instance: Optional["ProductHuntClient"] = None
    API_URL = "https://api.producthunt.com/v2/api/graphql"
    OAUTH_URL = "https://api.producthunt.com/v2/oauth/token"

    # Rate limiting config
    REQUEST_DELAY = 1.5  # Segundos entre peticiones
    MAX_RETRIES = 3  # Máximo reintentos en caso de 429
    INITIAL_BACKOFF = 5  # Segundos de espera inicial en 429

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token: Optional[str] = None
        self._last_request_time: float = 0
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @classmethod
    def get_client(cls) -> "ProductHuntClient":
        """
        Obtiene instancia del cliente Product Hunt (singleton).

        Returns:
            ProductHuntClient: Cliente autenticado

        Raises:
            ValueError: Si faltan credenciales en variables de entorno
        """
        if cls._instance is None:
            cls._instance = cls._create_client()
        return cls._instance

    @classmethod
    def _create_client(cls) -> "ProductHuntClient":
        """Crea nueva instancia del cliente Product Hunt."""
        api_key = os.getenv('PRODUCT_HUNT_API_KEY')
        api_secret = os.getenv('PRODUCT_HUNT_API_SECRET')

        if not api_key or not api_secret:
            raise ValueError(
                "Faltan credenciales de Product Hunt. "
                "Asegúrate de definir PRODUCT_HUNT_API_KEY y PRODUCT_HUNT_API_SECRET en .env"
            )

        return cls(api_key, api_secret)

    @classmethod
    def reset_client(cls) -> None:
        """Resetea la instancia singleton (útil para tests)."""
        cls._instance = None

    def _get_access_token(self) -> str:
        """
        Obtiene un access token usando OAuth 2.0 Client Credentials.

        Returns:
            str: Access token válido

        Raises:
            httpx.HTTPError: Si hay error al obtener el token
        """
        if self.access_token:
            return self.access_token

        payload = {
            "client_id": self.api_key,
            "client_secret": self.api_secret,
            "grant_type": "client_credentials"
        }

        with httpx.Client() as client:
            response = client.post(
                self.OAUTH_URL,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("access_token")

            if not self.access_token:
                raise ValueError("No se pudo obtener access_token de Product Hunt")

            return self.access_token

    def _wait_for_rate_limit(self) -> None:
        """Espera el tiempo necesario entre peticiones."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.REQUEST_DELAY:
            sleep_time = self.REQUEST_DELAY - elapsed
            logger.debug(f"Rate limit: esperando {sleep_time:.2f}s")
            time.sleep(sleep_time)

    def _execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Ejecuta una query GraphQL con retry y rate limiting.

        Args:
            query: Query GraphQL
            variables: Variables para la query

        Returns:
            Dict con la respuesta de la API

        Raises:
            httpx.HTTPError: Si hay error en la petición después de reintentos
        """
        # Obtener access token (se cachea después de la primera llamada)
        access_token = self._get_access_token()

        # Actualizar headers con el token
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}"
        }

        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        # Retry con exponential backoff
        for attempt in range(self.MAX_RETRIES + 1):
            # Respetar rate limit entre peticiones
            self._wait_for_rate_limit()

            with httpx.Client() as client:
                response = client.post(
                    self.API_URL,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                self._last_request_time = time.time()

                # Si es 429, hacer backoff y reintentar
                if response.status_code == 429:
                    if attempt < self.MAX_RETRIES:
                        backoff = self.INITIAL_BACKOFF * (2 ** attempt)
                        logger.warning(f"Rate limit (429). Reintento {attempt + 1}/{self.MAX_RETRIES} en {backoff}s")
                        time.sleep(backoff)
                        continue
                    else:
                        logger.error("Rate limit: máximo de reintentos alcanzado")
                        response.raise_for_status()

                response.raise_for_status()
                return response.json()

        # No debería llegar aquí, pero por seguridad
        raise httpx.HTTPError("Error inesperado en _execute_query")

    def fetch_posts(
        self,
        topic_slug: Optional[str] = None,
        limit: int = 20,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene posts de Product Hunt.

        Args:
            topic_slug: Slug del topic (ej: "artificial-intelligence"). Si es None, obtiene todos.
            limit: Número máximo de posts (default: 20, max: 20 por página)
            cursor: Cursor para paginación

        Returns:
            Dict con posts y metadata de paginación
        """
        query = """
        query GetPosts($first: Int!, $after: String, $topic: String) {
            posts(first: $first, after: $after, topic: $topic) {
                edges {
                    cursor
                    node {
                        id
                        name
                        tagline
                        description
                        url
                        website
                        votesCount
                        commentsCount
                        createdAt
                        makers {
                            username
                            name
                        }
                        topics {
                            edges {
                                node {
                                    slug
                                    name
                                }
                            }
                        }
                    }
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
        """

        variables = {
            "first": min(limit, 20),
            "after": cursor,
            "topic": topic_slug,
        }

        result = self._execute_query(query, variables)
        return result.get("data", {}).get("posts", {})

    def fetch_topics(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Obtiene lista de topics disponibles.

        Args:
            limit: Número máximo de topics

        Returns:
            Lista de topics
        """
        query = """
        query GetTopics($first: Int!) {
            topics(first: $first) {
                edges {
                    node {
                        id
                        slug
                        name
                        description
                        postsCount
                    }
                }
            }
        }
        """

        variables = {"first": min(limit, 50)}
        result = self._execute_query(query, variables)

        topics_data = result.get("data", {}).get("topics", {}).get("edges", [])
        return [edge["node"] for edge in topics_data]

    @classmethod
    def test_connection(cls) -> bool:
        """
        Prueba la conexión con Product Hunt.

        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            client = cls.get_client()
            # Intenta obtener un topic como test
            topics = client.fetch_topics(limit=1)
            return len(topics) > 0
        except Exception as e:
            print(f"Error al conectar con Product Hunt: {e}")
            return False
