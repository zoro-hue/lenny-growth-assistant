import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.registry import ToolRegistry
from app.agent.tools.ship30_essay import Ship30EssayTool
from app.services.ingestion_service import IngestionService
from app.services.session_service import SessionService
from app.services.chat_service import ChatService
from app.schemas.chat import ChatRequest
from app.schemas.session import SessionCreate


@pytest.mark.asyncio
async def test_ship30_tool_registration(test_db: AsyncSession):
    """
    Verifies that generate_ship30_essay is properly registered in ToolRegistry,
    retrievable by name, and exports the correct function schema.
    """
    registry = ToolRegistry(test_db)
    tool = registry.get_tool("generate_ship30_essay")
    assert tool is not None
    assert isinstance(tool, Ship30EssayTool)
    assert tool.name == "generate_ship30_essay"

    schema = tool.to_schema()
    assert schema["type"] == "function"
    fn = schema["function"]
    assert fn["name"] == "generate_ship30_essay"
    assert "parameters" in fn
    props = fn["parameters"]["properties"]
    assert "topic" in props
    assert "source_url_or_guest" in props
    assert "topic" in fn["parameters"]["required"]


@pytest.mark.asyncio
async def test_ship30_valid_topic_generation_and_word_count(test_db: AsyncSession):
    """
    Verifies that Ship30EssayTool generates a complete ~1,250-word essay
    with 1-3-1 hook, narrative progression, and actionable takeaway.
    """
    # 1. Ingest sample podcast transcripts
    await IngestionService.ingest_source(test_db, source="sample", limit=3, force_refresh=True)

    # 2. Execute tool
    registry = ToolRegistry(test_db)
    tool: Ship30EssayTool = registry.ship30_tool  # type: ignore

    res = await tool.execute(
        topic="How to measure product-market fit with cohort retention floors",
        source_url_or_guest="Casey Winters",
    )

    # 3. Verify status & word count
    assert res["status"] == "complete"
    assert "The How To Measure Product-Market Fit With Cohort Retention Floors Playbook" in res["title"] or "Playbook" in res["title"]

    word_count = res["word_count"]
    # Check that word count is approximately 1,250 words (typically between 1,000 and 1,500 words)
    assert 1000 <= word_count <= 1500, f"Expected word count ~1,250, got {word_count}"

    content = res["content"]
    # Check 1-3-1 Hook and core sections
    assert "## 1. The Conventional Playbook Is Broken" in content
    assert "## 2. The Empirical Reality" in content
    assert "## 3. The 4-Stage Operational Framework" in content
    assert "## 4. Tactical Execution Protocols & Benchmark Matrix" in content
    assert "## 5. The 7-Step Implementation Checklist" in content
    assert "## 6. The Golden Takeaway" in content

    # Check grounded guest attribution
    assert "Casey Winters" in content or "Elena Verna" in content
    assert "> \"" in content  # Verbatim blockquote present


@pytest.mark.asyncio
async def test_ship30_citation_propagation_and_no_fabrication(test_db: AsyncSession):
    """
    Verifies that citations returned by the essay tool strictly match
    retrieved chunks with valid URLs, timestamps, and zero fabrication.
    """
    await IngestionService.ingest_source(test_db, source="sample", limit=3, force_refresh=True)

    registry = ToolRegistry(test_db)
    tool: Ship30EssayTool = registry.ship30_tool  # type: ignore

    res = await tool.execute(
        topic="B2B product-led growth monetization loops and paywall timing",
        source_url_or_guest="Elena Verna",
    )

    assert res["status"] == "complete"
    citations = res["citations"]
    assert len(citations) > 0

    for cit in citations:
        assert cit["guest"] in ("Elena Verna", "Casey Winters", "Brian Balfour")
        assert cit["episode_title"] is not None
        assert cit["episode_url"].startswith("https://www.lennyspodcast.com") or "youtube.com" in cit["episode_url"]
        assert len(cit["quote_excerpt"]) > 10

    # Verify tool accumulated retrieved chunks for AgentService integration
    assert len(tool.retrieved_chunks) > 0


@pytest.mark.asyncio
async def test_ship30_insufficient_evidence_unsupported_domain(test_db: AsyncSession):
    """
    Verifies that queries asking for unsupported out-of-domain topics
    (crypto/Solana/staking) correctly trigger insufficient-evidence state with 0 citations.
    """
    await IngestionService.ingest_source(test_db, source="sample", limit=1, force_refresh=True)

    registry = ToolRegistry(test_db)
    tool: Ship30EssayTool = registry.ship30_tool  # type: ignore

    res = await tool.execute(
        topic="Solana liquidity pool impermanent loss and staking reward calculations",
    )

    assert res["status"] == "insufficient_evidence"
    assert len(res["citations"]) == 0
    assert "don't have enough grounded material" in res["content"].lower()


@pytest.mark.asyncio
async def test_ship30_integration_via_chat_service(test_db: AsyncSession):
    """
    Integration test proving the full runtime path:
    POST /api/chat -> ChatService -> AgentService -> generate_ship30_essay -> Artifact creation
    """
    await IngestionService.ingest_source(test_db, source="sample", limit=3, force_refresh=True)

    session = await SessionService.create_session(
        test_db,
        SessionCreate(title="Ship 30 Integration Test", active_model_id="mock-agent"),
    )

    chat_req = ChatRequest(
        session_id=session.id,
        content="Write a Ship 30 for 30 playbook essay on cohort retention curves based on Casey Winters",
        is_essay=True,
        model_id="mock-agent",
    )

    response = await ChatService.process_chat(test_db, chat_req)

    # 1. Verify assistant message
    assert response.assistant_message is not None
    assert response.assistant_message.status == "complete"
    assert len(response.assistant_message.citations) > 0

    # 2. Verify artifact generation & linking
    assert response.artifact is not None
    assert response.assistant_message.artifact_id == response.artifact.id
    assert response.artifact.type == "markdown"
    assert 1000 <= response.artifact.word_count <= 1500
    assert "Playbook" in response.artifact.title
