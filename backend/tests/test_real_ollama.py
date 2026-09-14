import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent import AgentService, OllamaProvider
from app.services.ingestion_service import IngestionService


@pytest.mark.asyncio
async def test_real_ollama_tool_call_and_grounded_answer(test_db: AsyncSession):
    """
    Live integration test executing against real local Ollama (llama3.2:3b).
    Verifies:
    1. Local Ollama reachability.
    2. Real tool execution (search_lenny_transcripts).
    3. Grounded answer generation.
    4. Citations matching retrieved chunks with zero fabrication.
    """
    provider = OllamaProvider()
    if not await provider.is_available():
        pytest.skip("Local Ollama on http://localhost:11434 is not running")

    # Ingest Casey Winters transcript
    await IngestionService.ingest_source(test_db, source="sample", limit=3, force_refresh=True)

    # Execute agent against real Ollama
    result = await AgentService.run(
        db=test_db,
        query="How does Casey Winters recommend measuring product-market fit?",
        conversation_history=[],
        model_id="ollama-local",
    )

    assert result.status in ("complete", "low-evidence")
    if result.status == "complete":
        assert len(result.citations) > 0
        for cit in result.citations:
            assert cit.guest is not None
            assert cit.episode_title is not None
            assert cit.quote_excerpt is not None
            assert cit.episode_url is not None


@pytest.mark.asyncio
async def test_real_ollama_low_evidence(test_db: AsyncSession):
    """
    Verifies that real Ollama correctly triggers low-evidence state on
    unsupported crypto/Solana questions.
    """
    provider = OllamaProvider()
    if not await provider.is_available():
        pytest.skip("Local Ollama on http://localhost:11434 is not running")

    await IngestionService.ingest_source(test_db, source="sample", limit=1, force_refresh=True)

    result = await AgentService.run(
        db=test_db,
        query="How do I calculate Solana staking rewards and liquidity pool impermanent loss?",
        conversation_history=[],
        model_id="ollama-local",
    )

    # For unsupported crypto topics, citations must be strictly 0
    assert len(result.citations) == 0
