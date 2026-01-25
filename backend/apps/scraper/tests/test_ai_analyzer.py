"""
Tests para el analizador IA con Ollama.
"""
import pytest
from unittest.mock import patch, Mock, MagicMock

from apps.scraper.ai_analyzer import OllamaClient, ProductAnalyzer, AnalysisResult


class TestOllamaClient:
    """Tests para OllamaClient."""

    def setup_method(self):
        """Reset singleton antes de cada test."""
        OllamaClient.reset_client()

    def teardown_method(self):
        """Reset singleton después de cada test."""
        OllamaClient.reset_client()

    def test_singleton_pattern(self):
        """Test: get_client retorna la misma instancia."""
        with patch.dict('os.environ', {
            'OLLAMA_HOST': 'http://test:11434',
            'OLLAMA_MODEL': 'test-model'
        }):
            client1 = OllamaClient.get_client()
            client2 = OllamaClient.get_client()
            assert client1 is client2

    def test_reset_client(self):
        """Test: reset_client crea nueva instancia."""
        with patch.dict('os.environ', {
            'OLLAMA_HOST': 'http://test:11434',
            'OLLAMA_MODEL': 'test-model'
        }):
            client1 = OllamaClient.get_client()
            OllamaClient.reset_client()
            client2 = OllamaClient.get_client()
            assert client1 is not client2

    @patch('apps.scraper.ai_analyzer.httpx.Client')
    def test_is_available_success(self, mock_httpx):
        """Test: is_available retorna True cuando Ollama responde."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_httpx.return_value.__enter__.return_value.get.return_value = mock_response

        client = OllamaClient('http://test:11434', 'llama3.2:1b')
        assert client.is_available() is True

    @patch('apps.scraper.ai_analyzer.httpx.Client')
    def test_is_available_failure(self, mock_httpx):
        """Test: is_available retorna False cuando Ollama no responde."""
        mock_httpx.return_value.__enter__.return_value.get.side_effect = Exception("Connection refused")

        client = OllamaClient('http://test:11434', 'llama3.2:1b')
        assert client.is_available() is False

    @patch('apps.scraper.ai_analyzer.httpx.Client')
    def test_is_model_available_true(self, mock_httpx):
        """Test: is_model_available retorna True cuando el modelo está descargado."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "llama3.2:1b"}]
        }
        mock_httpx.return_value.__enter__.return_value.get.return_value = mock_response

        client = OllamaClient('http://test:11434', 'llama3.2:1b')
        assert client.is_model_available() is True

    @patch('apps.scraper.ai_analyzer.httpx.Client')
    def test_is_model_available_false(self, mock_httpx):
        """Test: is_model_available retorna False cuando el modelo no está."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "other-model:latest"}]
        }
        mock_httpx.return_value.__enter__.return_value.get.return_value = mock_response

        client = OllamaClient('http://test:11434', 'llama3.2:1b')
        assert client.is_model_available() is False

    @patch('apps.scraper.ai_analyzer.httpx.Client')
    def test_generate_success(self, mock_httpx):
        """Test: generate retorna respuesta del modelo."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test response"}
        mock_httpx.return_value.__enter__.return_value.post.return_value = mock_response

        client = OllamaClient('http://test:11434', 'llama3.2:1b')
        result = client.generate("Test prompt")

        assert result == "Test response"

    @patch('apps.scraper.ai_analyzer.httpx.Client')
    def test_generate_error(self, mock_httpx):
        """Test: generate retorna None en caso de error."""
        mock_httpx.return_value.__enter__.return_value.post.side_effect = Exception("Error")

        client = OllamaClient('http://test:11434', 'llama3.2:1b')
        result = client.generate("Test prompt")

        assert result is None

    @patch('apps.scraper.ai_analyzer.httpx.Client')
    def test_get_status(self, mock_httpx):
        """Test: get_status retorna estado completo."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "llama3.2:1b"}]}
        mock_httpx.return_value.__enter__.return_value.get.return_value = mock_response

        client = OllamaClient('http://test:11434', 'llama3.2:1b')
        status = client.get_status()

        assert status['host'] == 'http://test:11434'
        assert status['model'] == 'llama3.2:1b'
        assert 'ollama_available' in status
        assert 'model_available' in status
        assert 'ready' in status


class TestProductAnalyzer:
    """Tests para ProductAnalyzer."""

    def setup_method(self):
        """Reset singleton antes de cada test."""
        OllamaClient.reset_client()

    def teardown_method(self):
        """Reset singleton después de cada test."""
        OllamaClient.reset_client()

    def test_parse_response_valid_json(self):
        """Test: _parse_response parsea JSON válido correctamente."""
        mock_client = Mock()
        analyzer = ProductAnalyzer(mock_client)

        json_response = '''{
            "summary": "AI coding assistant",
            "problem": "Developers need help writing code",
            "mvp_idea": "Build a simpler version",
            "target_audience": "Software developers",
            "potential_score": 8,
            "tags": ["ai", "coding", "productivity"]
        }'''

        result = analyzer._parse_response(json_response)

        assert isinstance(result, AnalysisResult)
        assert result.summary == "AI coding assistant"
        assert result.problem == "Developers need help writing code"
        assert result.mvp_idea == "Build a simpler version"
        assert result.target_audience == "Software developers"
        assert result.potential_score == 8
        assert result.tags == ["ai", "coding", "productivity"]

    def test_parse_response_with_markdown(self):
        """Test: _parse_response extrae JSON de respuesta con markdown."""
        mock_client = Mock()
        analyzer = ProductAnalyzer(mock_client)

        response = '''Here is the analysis:
        {"summary": "Test", "problem": "Problem", "mvp_idea": "Idea", "target_audience": "Users", "potential_score": 5, "tags": ["test"]}
        Some extra text'''

        result = analyzer._parse_response(response)

        assert result is not None
        assert result.summary == "Test"

    def test_parse_response_clamps_score(self):
        """Test: _parse_response limita potential_score entre 1 y 10."""
        mock_client = Mock()
        analyzer = ProductAnalyzer(mock_client)

        # Score demasiado alto
        high_score_json = '{"summary": "Test", "problem": "P", "mvp_idea": "I", "target_audience": "T", "potential_score": 15, "tags": []}'
        result = analyzer._parse_response(high_score_json)
        assert result.potential_score == 10

        # Score demasiado bajo
        low_score_json = '{"summary": "Test", "problem": "P", "mvp_idea": "I", "target_audience": "T", "potential_score": 0, "tags": []}'
        result = analyzer._parse_response(low_score_json)
        assert result.potential_score == 1

    def test_parse_response_handles_string_tags(self):
        """Test: _parse_response convierte tags string a lista."""
        mock_client = Mock()
        analyzer = ProductAnalyzer(mock_client)

        json_response = '{"summary": "Test", "problem": "P", "mvp_idea": "I", "target_audience": "T", "potential_score": 5, "tags": "ai, coding, test"}'

        result = analyzer._parse_response(json_response)

        assert isinstance(result.tags, list)
        assert len(result.tags) == 3

    def test_parse_response_normalizes_tags(self):
        """Test: _parse_response normaliza tags a lowercase sin espacios."""
        mock_client = Mock()
        analyzer = ProductAnalyzer(mock_client)

        json_response = '{"summary": "Test", "problem": "P", "mvp_idea": "I", "target_audience": "T", "potential_score": 5, "tags": ["AI Tools", "Machine Learning"]}'

        result = analyzer._parse_response(json_response)

        assert result.tags == ["ai-tools", "machine-learning"]

    def test_parse_response_invalid_json(self):
        """Test: _parse_response retorna None con JSON inválido."""
        mock_client = Mock()
        analyzer = ProductAnalyzer(mock_client)

        result = analyzer._parse_response("This is not JSON at all")

        assert result is None

    @pytest.mark.django_db
    def test_analyze_product(self, product):
        """Test: analyze_product genera prompt y parsea respuesta."""
        mock_client = Mock()
        mock_client.generate.return_value = '{"summary": "Test", "problem": "P", "mvp_idea": "I", "target_audience": "T", "potential_score": 7, "tags": ["test"]}'

        analyzer = ProductAnalyzer(mock_client)
        result = analyzer.analyze_product(product)

        assert result is not None
        assert result.summary == "Test"
        assert result.potential_score == 7

        # Verificar que se llamó a generate con prompt que incluye datos del producto
        call_args = mock_client.generate.call_args[0][0]
        assert product.title in call_args
        assert product.tagline in call_args

    @pytest.mark.django_db
    def test_analyze_product_no_response(self, product):
        """Test: analyze_product retorna None si Ollama no responde."""
        mock_client = Mock()
        mock_client.generate.return_value = None

        analyzer = ProductAnalyzer(mock_client)
        result = analyzer.analyze_product(product)

        assert result is None

    @pytest.mark.django_db
    def test_update_product_with_analysis(self, product):
        """Test: update_product_with_analysis actualiza campos del producto."""
        mock_client = Mock()
        analyzer = ProductAnalyzer(mock_client)

        result = AnalysisResult(
            summary="Test summary",
            problem="Test problem",
            mvp_idea="Test MVP idea",
            target_audience="Test audience",
            potential_score=8,
            tags=["tag1", "tag2"]
        )

        analyzer.update_product_with_analysis(product, result)

        # Recargar desde DB
        product.refresh_from_db()

        assert product.summary == "Test summary"
        assert product.problem == "Test problem"
        assert product.mvp_idea == "Test MVP idea"
        assert product.target_audience == "Test audience"
        assert product.potential_score == 8
        assert product.tags == "tag1,tag2"
        assert product.analyzed is True
        assert product.analyzed_at is not None


@pytest.mark.django_db
class TestAnalyzeProductsAPI:
    """Tests para endpoints de análisis IA."""

    @pytest.fixture
    def scraper_client(self, api_client, access_token):
        """Cliente de test autenticado."""
        api_client.headers = {"Authorization": f"Bearer {access_token}"}
        return api_client

    @patch('apps.scraper.api.analyze_products.delay')
    def test_analyze_endpoint(self, mock_task, scraper_client):
        """Test: Endpoint para iniciar análisis."""
        mock_task.return_value = Mock(id='analyze-123')

        response = scraper_client.post("/scraper/analyze/", json={"limit": 5})

        assert response.status_code == 200
        data = response.json()
        assert data['task_id'] == 'analyze-123'
        assert data['status'] == 'processing'

        mock_task.assert_called_once_with(product_ids=None, limit=5)

    @patch('apps.scraper.api.analyze_products.delay')
    def test_analyze_specific_products(self, mock_task, scraper_client, product):
        """Test: Endpoint para analizar productos específicos."""
        mock_task.return_value = Mock(id='analyze-456')

        response = scraper_client.post(
            "/scraper/analyze/",
            json={"product_ids": [product.id], "limit": 10}
        )

        assert response.status_code == 200
        mock_task.assert_called_once_with(product_ids=[product.id], limit=10)

    @patch('apps.scraper.api.OllamaClient')
    def test_ollama_status_endpoint(self, mock_client_class, scraper_client):
        """Test: Endpoint para verificar estado de Ollama."""
        mock_client = Mock()
        mock_client.get_status.return_value = {
            "host": "http://ollama:11434",
            "model": "llama3.2:1b",
            "ollama_available": True,
            "model_available": True,
            "ready": True
        }
        mock_client_class.get_client.return_value = mock_client

        response = scraper_client.get("/scraper/ollama-status/")

        assert response.status_code == 200
        data = response.json()
        assert data['ready'] is True
        assert data['model'] == 'llama3.2:1b'

    @patch('apps.scraper.api.pull_ollama_model.delay')
    def test_pull_model_endpoint(self, mock_task, scraper_client):
        """Test: Endpoint para descargar modelo."""
        mock_task.return_value = Mock(id='pull-789')

        response = scraper_client.post("/scraper/pull-model/")

        assert response.status_code == 200
        data = response.json()
        assert data['task_id'] == 'pull-789'
        assert 'Descarga de modelo iniciada' in data['message']

    def test_analyze_requires_auth(self, api_client):
        """Test: Endpoint de análisis requiere autenticación."""
        response = api_client.post("/scraper/analyze/", json={})
        assert response.status_code == 401

    def test_ollama_status_requires_auth(self, api_client):
        """Test: Endpoint de estado requiere autenticación."""
        response = api_client.get("/scraper/ollama-status/")
        assert response.status_code == 401


# Ejecutar: docker compose exec backend uv run pytest apps/scraper/tests/test_ai_analyzer.py -v
