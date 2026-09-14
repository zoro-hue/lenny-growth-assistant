import pytest
import math
from app.services.embedding_service import EmbeddingService, EmbeddingError
from app.services.retrieval_service import compute_cosine_similarity
from app.config import settings


@pytest.mark.asyncio
async def test_deterministic_mock_vector():
    # Verify dimensions
    vec = EmbeddingService._deterministic_vector("product growth loops retention", dimensions=settings.embedding_dimensions)
    assert len(vec) == settings.embedding_dimensions

    # Verify unit norm
    norm = math.sqrt(sum(x * x for x in vec))
    assert abs(norm - 1.0) < 1e-4

    # Verify semantic similarity:
    # "growth loops retention" should be closer to "growth loops" than "astrophysics black hole"
    vec_related = EmbeddingService._deterministic_vector("growth loops in SaaS", dimensions=settings.embedding_dimensions)
    vec_unrelated = EmbeddingService._deterministic_vector("astrophysics quantum particles galaxy", dimensions=settings.embedding_dimensions)

    sim_related = compute_cosine_similarity(vec, vec_related)
    sim_unrelated = compute_cosine_similarity(vec, vec_unrelated)

    assert sim_related > sim_unrelated
    assert sim_related > 0.25


@pytest.mark.asyncio
async def test_embed_texts_mock_fallback():
    texts = ["Casey Winters on growth loops", "Elena Verna on PLG activation"]
    embeddings = await EmbeddingService.embed_texts(texts)
    assert len(embeddings) == 2
    assert len(embeddings[0]) == settings.embedding_dimensions
    assert len(embeddings[1]) == settings.embedding_dimensions


@pytest.mark.asyncio
async def test_openai_embedding_missing_key_raises():
    orig_key = settings.openai_api_key
    try:
        settings.openai_api_key = ""
        with pytest.raises(EmbeddingError) as exc_info:
            await EmbeddingService._embed_openai(["test text"])
        assert "OPENAI_API_KEY is not configured" in str(exc_info.value)
    finally:
        settings.openai_api_key = orig_key
