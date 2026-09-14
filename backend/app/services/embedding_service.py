import os
import math
import hashlib
import logging
from typing import List, Optional
import httpx
from ..config import settings
from ..errors import AppException

logger = logging.getLogger(__name__)


class EmbeddingError(AppException):
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="EMBEDDING_ERROR",
            status_code=502,
            details=details,
        )


class EmbeddingService:
    """
    Embedding service supporting OpenAI Cloud, Ollama Local, and deterministic mock fallback.
    """

    @classmethod
    def get_provider(cls) -> str:
        provider = settings.embedding_provider.lower()
        if provider == "auto":
            if settings.openai_api_key and settings.openai_api_key.strip():
                return "openai"
            return "mock"
        return provider

    @classmethod
    async def embed_texts(cls, texts: List[str]) -> List[List[float]]:
        """Embeds a batch of texts into normalized float vectors."""
        if not texts:
            return []

        provider = cls.get_provider()
        logger.info(f"Generating embeddings for {len(texts)} texts using provider: {provider}")

        try:
            if provider == "openai":
                return await cls._embed_openai(texts)
            elif provider == "ollama":
                return await cls._embed_ollama(texts)
            else:
                return [cls._deterministic_vector(t, settings.embedding_dimensions) for t in texts]
        except Exception as e:
            logger.error(f"Failed to generate embeddings with provider '{provider}': {e}", exc_info=True)
            # If in auto mode or mock fallback, gracefully fallback to mock with warning
            if settings.embedding_provider.lower() in ("auto", "mock") or "quota" in str(e).lower() or "429" in str(e):
                logger.warning("Falling back to deterministic mock embeddings due to provider error.")
                return [cls._deterministic_vector(t, settings.embedding_dimensions) for t in texts]
            raise EmbeddingError(
                message=f"Embedding provider '{provider}' failed: {str(e)}",
                details={"provider": provider, "model": settings.embedding_model},
            )

    @classmethod
    async def embed_query(cls, query: str) -> List[float]:
        """Embeds a single query string."""
        results = await cls.embed_texts([query])
        if not results:
            raise EmbeddingError("Failed to generate embedding for empty query.")
        return results[0]

    @classmethod
    async def _embed_openai(cls, texts: List[str]) -> List[List[float]]:
        """Generates embeddings via OpenAI API."""
        api_key = settings.openai_api_key
        if not api_key or not api_key.strip():
            raise EmbeddingError("OPENAI_API_KEY is not configured.")

        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.embedding_model,
            "input": texts,
            "dimensions": settings.embedding_dimensions,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise EmbeddingError(
                    message=f"OpenAI embedding API error (HTTP {resp.status_code}): {resp.text}",
                    details={"status_code": resp.status_code, "response": resp.text[:200]},
                )
            data = resp.json()
            return [item["embedding"] for item in data["data"]]

    @classmethod
    async def _embed_ollama(cls, texts: List[str]) -> List[List[float]]:
        """Generates embeddings via Ollama API."""
        base_url = settings.ollama_base_url.rstrip("/")
        url = f"{base_url}/api/embeddings"
        model = settings.embedding_model or "nomic-embed-text"

        results: List[List[float]] = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for text in texts:
                resp = await client.post(url, json={"model": model, "prompt": text})
                if resp.status_code != 200:
                    raise EmbeddingError(
                        message=f"Ollama embedding API error (HTTP {resp.status_code}): {resp.text}",
                        details={"status_code": resp.status_code},
                    )
                emb = resp.json().get("embedding", [])
                results.append(emb)
        return results

    @staticmethod
    def _deterministic_vector(text: str, dimensions: int = 1536) -> List[float]:
        """
        Creates a normalized deterministic float vector using token hashing.
        Allows real semantic cosine similarity calculation in offline / test mode.
        """
        vec = [0.0] * dimensions
        words = [w.strip(".,!?:;\"'()[]{}*#-").lower() for w in text.split()]
        words = [w for w in words if len(w) >= 2]

        if not words:
            vec[0] = 1.0
            return vec

        # Tokens: unigrams and consecutive bigrams
        tokens = list(words)
        for i in range(len(words) - 1):
            tokens.append(f"{words[i]}_{words[i+1]}")

        for tok in tokens:
            h1 = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16) % dimensions
            h2 = int(hashlib.sha256(tok.encode("utf-8")).hexdigest(), 16) % dimensions
            weight = 2.0 if "_" in tok else 1.0

            vec[h1] += weight
            vec[h2] += weight

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        else:
            vec[0] = 1.0
        return vec
