"""
Cliente de Reddit usando PRAW.
Maneja la conexión y autenticación con la API de Reddit.
"""
import os
import praw
from typing import Optional


class RedditClient:
    """Cliente singleton para conexión con Reddit API."""

    _instance: Optional[praw.Reddit] = None

    @classmethod
    def get_client(cls) -> praw.Reddit:
        """
        Obtiene instancia del cliente Reddit (singleton).

        Returns:
            praw.Reddit: Cliente autenticado de PRAW

        Raises:
            ValueError: Si faltan credenciales en variables de entorno
        """
        if cls._instance is None:
            cls._instance = cls._create_client()
        return cls._instance

    @classmethod
    def _create_client(cls) -> praw.Reddit:
        """Crea nueva instancia del cliente Reddit."""
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT', 'RedditMVPFinder/1.0')

        # Validar que existan las credenciales
        if not client_id or not client_secret:
            raise ValueError(
                "Faltan credenciales de Reddit. "
                "Asegúrate de definir REDDIT_CLIENT_ID y REDDIT_CLIENT_SECRET en .env"
            )

        # Crear cliente en modo read-only (sin username/password)
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

        # Verificar que el cliente esté en modo read-only
        if not reddit.read_only:
            reddit.read_only = True

        return reddit

    @classmethod
    def test_connection(cls) -> bool:
        """
        Prueba la conexión con Reddit.

        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            reddit = cls.get_client()
            # Intenta obtener un subreddit público como test
            subreddit = reddit.subreddit('Python')
            # Si podemos obtener el display_name, la conexión funciona
            _ = subreddit.display_name
            return True
        except Exception as e:
            print(f"Error al conectar con Reddit: {e}")
            return False
