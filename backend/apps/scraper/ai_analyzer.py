"""
Cliente Ollama para análisis IA de posts de Product Hunt.
Extrae información estructurada usando LLM local.
"""
import os
import json
import re
import logging
from dataclasses import dataclass
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Resultado del análisis IA de un post."""
    summary: str
    problem: str
    mvp_idea: str
    target_audience: str
    potential_score: int
    tags: list[str]


class OllamaClient:
    """Cliente singleton para conexión con Ollama API."""

    _instance: Optional["OllamaClient"] = None
    DEFAULT_HOST = "http://ollama:11434"
    DEFAULT_MODEL = "llama3.2:1b"

    def __init__(self, host: str, model: str):
        self.host = host.rstrip('/')
        self.model = model

    @classmethod
    def get_client(cls) -> "OllamaClient":
        """
        Obtiene instancia del cliente Ollama (singleton).

        Returns:
            OllamaClient: Cliente configurado
        """
        if cls._instance is None:
            cls._instance = cls._create_client()
        return cls._instance

    @classmethod
    def _create_client(cls) -> "OllamaClient":
        """Crea nueva instancia del cliente Ollama."""
        host = os.getenv('OLLAMA_HOST', cls.DEFAULT_HOST)
        model = os.getenv('OLLAMA_MODEL', cls.DEFAULT_MODEL)
        return cls(host, model)

    @classmethod
    def reset_client(cls) -> None:
        """Resetea la instancia singleton (útil para tests)."""
        cls._instance = None

    def is_available(self) -> bool:
        """
        Verifica si Ollama está disponible.

        Returns:
            bool: True si Ollama responde
        """
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.host}/api/version")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama no disponible: {e}")
            return False

    def is_model_available(self) -> bool:
        """
        Verifica si el modelo configurado está descargado.

        Returns:
            bool: True si el modelo está disponible
        """
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.host}/api/tags")
                if response.status_code != 200:
                    return False

                data = response.json()
                models = data.get("models", [])
                model_names = [m.get("name", "") for m in models]

                # Verificar si el modelo está (con o sin :latest)
                return (
                    self.model in model_names or
                    f"{self.model}:latest" in model_names or
                    self.model.replace(":latest", "") in model_names
                )
        except Exception as e:
            logger.warning(f"Error al verificar modelo: {e}")
            return False

    def pull_model(self) -> dict:
        """
        Descarga el modelo configurado.

        Returns:
            dict: Resultado de la operación
        """
        try:
            with httpx.Client(timeout=600.0) as client:
                response = client.post(
                    f"{self.host}/api/pull",
                    json={"name": self.model, "stream": False}
                )
                if response.status_code == 200:
                    return {"status": "success", "message": f"Modelo {self.model} descargado"}
                else:
                    return {"status": "error", "message": response.text}
        except Exception as e:
            logger.error(f"Error al descargar modelo: {e}")
            return {"status": "error", "message": str(e)}

    def generate(self, prompt: str, timeout: float = 120.0) -> Optional[str]:
        """
        Genera respuesta usando el modelo LLM.

        Args:
            prompt: Prompt para el modelo
            timeout: Timeout en segundos

        Returns:
            str: Respuesta generada o None si hay error
        """
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(
                    f"{self.host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 2000,
                        }
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "")
                else:
                    logger.error(f"Error en generate: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error al generar respuesta: {e}")
            return None

    def get_status(self) -> dict:
        """
        Obtiene estado completo de Ollama.

        Returns:
            dict: Estado de Ollama y modelo
        """
        available = self.is_available()
        model_available = self.is_model_available() if available else False

        return {
            "host": self.host,
            "model": self.model,
            "ollama_available": available,
            "model_available": model_available,
            "ready": available and model_available
        }


class PostAnalyzer:
    """Analizador de posts usando Ollama."""

    ANALYSIS_PROMPT = """Analiza este producto de Product Hunt. Responde EN ESPAÑOL con JSON válido.

PRODUCTO: {title}
TAGLINE: {tagline}
DESCRIPCIÓN: {content}

INSTRUCCIONES:
- summary: 2-3 frases explicando qué hace el producto
- problem: 3-4 frases sobre el problema que resuelve y por qué importa
- mvp_idea: 3-4 frases con una idea de MVP que podrías construir inspirándote en este producto
- target_audience: 2-3 frases describiendo el público objetivo (profesión, contexto, necesidades)
- potential_score: número del 1 al 10 según potencial de mercado
- tags: 4-5 palabras clave relevantes en minúsculas

Responde SOLO con JSON válido:
{{"summary":"...","problem":"...","mvp_idea":"...","target_audience":"...","potential_score":7,"tags":["tag1","tag2","tag3","tag4"]}}

JSON:"""

    def __init__(self, client: Optional[OllamaClient] = None):
        self.client = client or OllamaClient.get_client()

    def analyze_post(self, post) -> Optional[AnalysisResult]:
        """
        Analiza un post y retorna resultado estructurado.

        Args:
            post: Instancia de Post model

        Returns:
            AnalysisResult o None si hay error
        """
        prompt = self.ANALYSIS_PROMPT.format(
            title=post.title,
            tagline=post.tagline or "",
            content=post.content or "",
            votes_count=post.votes_count,
            comments_count=post.comments_count,
        )

        response = self.client.generate(prompt)
        if not response:
            logger.warning(f"Sin respuesta de Ollama para post {post.id}")
            return None

        return self._parse_response(response)

    def _parse_response(self, response: str) -> Optional[AnalysisResult]:
        """
        Parsea la respuesta JSON del LLM.

        Args:
            response: Respuesta del modelo

        Returns:
            AnalysisResult o None si el parseo falla
        """
        try:
            # Limpiar respuesta (puede venir con markdown o texto extra)
            cleaned = response.strip()

            # Buscar JSON en la respuesta
            json_match = re.search(r'\{[^{}]*\}', cleaned, re.DOTALL)
            if json_match:
                cleaned = json_match.group()

            data = json.loads(cleaned)

            # Validar y sanitizar campos
            potential_score = data.get("potential_score", 5)
            if not isinstance(potential_score, int):
                potential_score = int(potential_score) if str(potential_score).isdigit() else 5
            potential_score = max(1, min(10, potential_score))

            tags = data.get("tags", [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",")]
            tags = [str(t).lower().replace(" ", "-") for t in tags[:5]]

            return AnalysisResult(
                summary=str(data.get("summary", ""))[:200],
                problem=str(data.get("problem", ""))[:500],
                mvp_idea=str(data.get("mvp_idea", ""))[:500],
                target_audience=str(data.get("target_audience", ""))[:200],
                potential_score=potential_score,
                tags=tags,
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Error al parsear respuesta: {e}. Respuesta: {response[:200]}")
            return None

    def update_post_with_analysis(self, post, result: AnalysisResult) -> None:
        """
        Actualiza un post con el resultado del análisis.

        Args:
            post: Instancia de Post model
            result: Resultado del análisis
        """
        from django.utils import timezone

        post.summary = result.summary
        post.problem = result.problem
        post.mvp_idea = result.mvp_idea
        post.target_audience = result.target_audience
        post.potential_score = result.potential_score
        post.tags = ",".join(result.tags)
        post.analyzed = True
        post.analyzed_at = timezone.now()
        post.save()
