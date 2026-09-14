import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.agent.tools.compare_perspectives import ComparePerspectivesTool
from app.agent.tools.registry import ToolRegistry
from app.services.ingestion_service import IngestionService
from app.services.chat_service import ChatService
from app.schemas.chat import ChatRequest
from app.agent.providers import MockAgentProvider


@pytest.mark.asyncio
async def test_compare_perspectives_two_speakers(test_db: AsyncSession):
    await IngestionService.ingest_source(db=test_db, source="sample", force_refresh=False)

    tool = ComparePerspectivesTool(test_db)
    result = await tool.execute(
        speaker_a="Brian Balfour",
        speaker_b="Elena Verna",
        topic="growth loops",
    )

    assert result["status"] == "complete"
    assert "COMPARE PERSPECTIVES" in result["content"]
    assert "Brian Balfour" in result["content"]
    assert "Elena Verna" in result["content"]
    assert "Synthesis" in result["content"]
    assert "Agreements" in result["content"]
    assert "Differences" in result["content"]
    assert "Practical implication" in result["content"]
    # Citations collected from both speakers
    assert len(tool.retrieved_chunks) >= 2
    guests = [c.guest for c in tool.retrieved_chunks]
    assert "Brian Balfour" in guests
    assert "Elena Verna" in guests


@pytest.mark.asyncio
async def test_compare_perspectives_insufficient_evidence_speaker(test_db: AsyncSession):
    await IngestionService.ingest_source(db=test_db, source="sample", force_refresh=False)

    tool = ComparePerspectivesTool(test_db)
    # Speaker B is not in the archive
    result = await tool.execute(
        speaker_a="Brian Balfour",
        speaker_b="Unknown Nonexistent Guest",
        topic="growth loops",
    )

    # Must explicitly state insufficient evidence for Speaker B without fabricating
    assert result["status"] == "partial_evidence"
    assert "Brian Balfour" in result["content"]
    assert "Unknown Nonexistent Guest" in result["content"]
    assert "Insufficient grounded evidence" in result["content"]
    assert "no claims were fabricated" in result["content"].lower()


@pytest.mark.asyncio
async def test_compare_perspectives_chat_service_integration(test_db: AsyncSession):
    await IngestionService.ingest_source(db=test_db, source="sample", force_refresh=False)

    mock_provider = MockAgentProvider()
    chat_resp = await ChatService.process_chat(
        db=test_db,
        request=ChatRequest(
            session_id="test-compare-session",
            content="Compare Brian Balfour and Elena Verna on growth loops.",
            model_id="openai-cloud",
        ),
        custom_provider=mock_provider,
    )

    assert chat_resp.assistant_message.status == "complete"
    assert "COMPARE PERSPECTIVES" in chat_resp.assistant_message.content
    assert len(chat_resp.assistant_message.citations) >= 2
    # Ensure citations are propagated from both speakers
    guests = [c.guest for c in chat_resp.assistant_message.citations]
    assert "Brian Balfour" in guests
    assert "Elena Verna" in guests
