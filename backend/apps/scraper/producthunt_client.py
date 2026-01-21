"""
Cliente de Product Hunt usando GraphQL API.
Maneja la conexión y autenticación con la API de Product Hunt.
"""
import os
import httpx
from typing import Optional, List, Dict, Any


class ProductHuntClient:
    """Cliente singleton para conexión con Product Hunt API."""

    _instance: Optional["ProductHuntClient"] = None
    API_URL = "https://api.producthunt.com/v2/api/graphql"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
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
            ValueError: Si falta la API key en variables de entorno
        """
        if cls._instance is None:
            cls._instance = cls._create_client()
        return cls._instance

    @classmethod
    def _create_client(cls) -> "ProductHuntClient":
        """Crea nueva instancia del cliente Product Hunt."""
        api_key = os.getenv('PRODUCT_HUNT_API_KEY')

        if not api_key:
            raise ValueError(
                "Falta API key de Product Hunt. "
                "Asegúrate de definir PRODUCT_HUNT_API_KEY en .env"
            )

        return cls(api_key)

    @classmethod
    def reset_client(cls) -> None:
        """Resetea la instancia singleton (útil para tests)."""
        cls._instance = None

    def _execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Ejecuta una query GraphQL.

        Args:
            query: Query GraphQL
            variables: Variables para la query

        Returns:
            Dict con la respuesta de la API

        Raises:
            httpx.HTTPError: Si hay error en la petición
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        with httpx.Client() as client:
            response = client.post(
                self.API_URL,
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

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
