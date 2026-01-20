"""
Tests para el scraper de Reddit.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from apps.scraper.scraper import RedditScraper
from apps.scraper.reddit_client import RedditClient
from apps.subreddits.models import Subreddit
from apps.posts.models import Post


@pytest.fixture
def mock_reddit_client():
    """Mock del cliente de Reddit."""
    with patch('apps.scraper.scraper.RedditClient.get_client') as mock:
        yield mock.return_value


@pytest.fixture
def mock_submission():
    """Mock de un submission de PRAW."""
    submission = Mock()
    submission.id = "test123"
    submission.title = "Test Post Title"
    submission.selftext = "Test post content"
    submission.author = Mock()
    submission.author.__str__ = Mock(return_value="testuser")
    submission.score = 100
    submission.url = "https://reddit.com/r/test/comments/test123"
    submission.created_utc = 1704067200  # 2024-01-01 00:00:00 UTC
    return submission


@pytest.fixture
def mock_subreddit_praw(mock_submission):
    """Mock de un subreddit de PRAW."""
    subreddit = Mock()
    subreddit.top = Mock(return_value=[mock_submission])
    return subreddit


@pytest.mark.django_db
class TestRedditScraper:
    """Tests para la clase RedditScraper."""

    def test_scraper_initialization(self, mock_reddit_client):
        """Test: El scraper se inicializa correctamente."""
        scraper = RedditScraper()
        assert scraper.reddit is not None

    def test_scrape_subreddit_creates_new_posts(
        self,
        mock_reddit_client,
        mock_subreddit_praw,
        subreddit
    ):
        """Test: Scraping crea posts nuevos."""
        # Setup
        mock_reddit_client.subreddit.return_value = mock_subreddit_praw
        scraper = RedditScraper()

        # Execute
        result = scraper.scrape_subreddit(subreddit.name, limit=10)

        # Assert
        assert result['new_posts'] == 1
        assert result['skipped_posts'] == 0
        assert len(result['errors']) == 0
        assert Post.objects.count() == 1

        # Verificar el post creado
        post = Post.objects.first()
        assert post.reddit_id == "test123"
        assert post.title == "Test Post Title"
        assert post.subreddit == subreddit

    def test_scrape_subreddit_skips_duplicates(
        self,
        mock_reddit_client,
        mock_subreddit_praw,
        subreddit,
        post
    ):
        """Test: Scraping omite posts duplicados."""
        # Setup - el post ya existe
        mock_reddit_client.subreddit.return_value = mock_subreddit_praw
        scraper = RedditScraper()

        # Cambiar el mock para que retorne el mismo reddit_id que el post existente
        mock_submission = mock_subreddit_praw.top.return_value[0]
        mock_submission.id = post.reddit_id

        # Execute
        result = scraper.scrape_subreddit(subreddit.name, limit=10)

        # Assert
        assert result['new_posts'] == 0
        assert result['skipped_posts'] == 1
        assert Post.objects.count() == 1  # No se creó uno nuevo

    def test_scrape_subreddit_nonexistent(self, mock_reddit_client):
        """Test: Scraping de subreddit que no existe en BD."""
        scraper = RedditScraper()

        # Execute
        result = scraper.scrape_subreddit("NonExistent", limit=10)

        # Assert
        assert result['new_posts'] == 0
        assert result['skipped_posts'] == 0
        assert len(result['errors']) == 1
        assert "no existe en BD" in result['errors'][0]

    def test_scrape_subreddit_updates_last_sync(
        self,
        mock_reddit_client,
        mock_subreddit_praw,
        subreddit
    ):
        """Test: Scraping actualiza last_sync del subreddit."""
        # Setup
        mock_reddit_client.subreddit.return_value = mock_subreddit_praw
        scraper = RedditScraper()
        original_last_sync = subreddit.last_sync

        # Execute
        scraper.scrape_subreddit(subreddit.name, limit=10)

        # Assert
        subreddit.refresh_from_db()
        assert subreddit.last_sync != original_last_sync

    def test_scrape_all_active_subreddits(
        self,
        mock_reddit_client,
        subreddit
    ):
        """Test: Scraping de todos los subreddits activos."""
        # Setup - Crear segundo subreddit activo
        subreddit2 = Subreddit.objects.create(name="Python", active=True)

        # Crear mock submissions diferentes para cada subreddit
        def create_mock_subreddit(name):
            mock_sub = Mock()
            mock_submission = Mock()
            mock_submission.id = f"{name}_post123"
            mock_submission.title = f"Test Post from {name}"
            mock_submission.selftext = "Test content"
            mock_submission.author = Mock()
            mock_submission.author.__str__ = Mock(return_value="testuser")
            mock_submission.score = 100
            mock_submission.url = f"https://reddit.com/r/{name}/comments/test123"
            mock_submission.created_utc = 1704067200
            mock_sub.top = Mock(return_value=[mock_submission])
            return mock_sub

        # Configurar mock para retornar diferentes subreddits según el nombre
        def get_subreddit_side_effect(name):
            return create_mock_subreddit(name)

        mock_reddit_client.subreddit.side_effect = get_subreddit_side_effect
        scraper = RedditScraper()

        # Execute
        results = scraper.scrape_all_active_subreddits(limit=10)

        # Assert
        assert len(results) == 2
        assert Post.objects.count() == 2

    def test_scrape_all_skips_inactive_subreddits(
        self,
        mock_reddit_client,
        mock_subreddit_praw
    ):
        """Test: Scraping omite subreddits inactivos."""
        # Setup
        mock_reddit_client.subreddit.return_value = mock_subreddit_praw
        scraper = RedditScraper()

        # Crear subreddit inactivo
        Subreddit.objects.create(name="Inactive", active=False)

        # Execute
        results = scraper.scrape_all_active_subreddits(limit=10)

        # Assert
        assert len(results) == 0  # No debería procesar ninguno

    def test_create_post_from_submission(
        self,
        mock_reddit_client,
        mock_submission,
        subreddit
    ):
        """Test: Creación de post desde submission de PRAW."""
        scraper = RedditScraper()

        # Execute
        post = scraper._create_post_from_submission(mock_submission, subreddit)

        # Assert
        assert post is not None
        assert post.reddit_id == "test123"
        assert post.title == "Test Post Title"
        assert post.content == "Test post content"
        assert post.author == "testuser"
        assert post.score == 100
        assert post.subreddit == subreddit

    def test_create_post_from_submission_no_selftext(self, mock_reddit_client, subreddit):
        """Test: Creación de post sin selftext (solo link)."""
        scraper = RedditScraper()

        # Mock submission sin selftext
        submission = Mock()
        submission.id = "link123"
        submission.title = "Link Post"
        submission.selftext = ""
        submission.author = Mock()
        submission.author.__str__ = Mock(return_value="linkuser")
        submission.score = 50
        submission.url = "https://example.com"
        submission.created_utc = 1704067200

        # Execute
        post = scraper._create_post_from_submission(submission, subreddit)

        # Assert
        assert post is not None
        assert "Link: https://example.com" in post.content

    def test_create_post_from_submission_deleted_author(self, mock_reddit_client, subreddit):
        """Test: Creación de post con autor eliminado."""
        scraper = RedditScraper()

        # Mock submission con autor None
        submission = Mock()
        submission.id = "deleted123"
        submission.title = "Deleted Author Post"
        submission.selftext = "Content"
        submission.author = None
        submission.score = 10
        submission.url = "https://reddit.com/deleted"
        submission.created_utc = 1704067200

        # Execute
        post = scraper._create_post_from_submission(submission, subreddit)

        # Assert
        assert post is not None
        assert post.author == "[deleted]"

    def test_get_scraping_summary(self, mock_reddit_client):
        """Test: Generación de resumen de scraping."""
        scraper = RedditScraper()

        results = [
            {'subreddit': 'Python', 'new_posts': 5, 'skipped_posts': 2, 'errors': []},
            {'subreddit': 'Django', 'new_posts': 3, 'skipped_posts': 1, 'errors': ['error1']},
        ]

        # Execute
        summary = scraper.get_scraping_summary(results)

        # Assert
        assert summary['subreddits_processed'] == 2
        assert summary['total_new_posts'] == 8
        assert summary['total_skipped_posts'] == 3
        assert summary['total_errors'] == 1
        assert len(summary['details']) == 2


@pytest.mark.django_db
class TestRedditClient:
    """Tests para RedditClient."""

    def test_client_requires_credentials(self):
        """Test: Cliente requiere credenciales."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Faltan credenciales"):
                RedditClient.get_client()

    def test_client_singleton_pattern(self):
        """Test: Cliente usa patrón singleton."""
        with patch.dict('os.environ', {
            'REDDIT_CLIENT_ID': 'test_id',
            'REDDIT_CLIENT_SECRET': 'test_secret'
        }):
            # Reset singleton
            RedditClient._instance = None

            with patch('praw.Reddit') as mock_praw:
                client1 = RedditClient.get_client()
                client2 = RedditClient.get_client()

                assert client1 is client2
                # PRAW debe ser llamado solo una vez
                assert mock_praw.call_count == 1

    def test_client_is_read_only(self):
        """Test: Cliente se configura en modo read-only."""
        with patch.dict('os.environ', {
            'REDDIT_CLIENT_ID': 'test_id',
            'REDDIT_CLIENT_SECRET': 'test_secret'
        }):
            RedditClient._instance = None

            with patch('praw.Reddit') as mock_praw:
                mock_reddit = Mock()
                mock_reddit.read_only = False
                mock_praw.return_value = mock_reddit

                client = RedditClient.get_client()

                # Verificar que se puso en read_only
                assert mock_reddit.read_only is True


# Instrucciones de ejecución:
#
# Ejecutar todos los tests del scraper:
#   cd backend
#   uv run pytest apps/scraper/tests/ -v
#
# Ejecutar este archivo específico:
#   uv run pytest apps/scraper/tests/test_scraper.py -v
#
# Ejecutar con cobertura:
#   uv run pytest apps/scraper/tests/ -v --cov=apps.scraper
