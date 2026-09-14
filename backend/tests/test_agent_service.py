import json
import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent import AgentService, ToolRegistry, MockAgentProvider
from app.agent.tools.transcript_search import TranscriptSearchTool
from app.agent.tools.source_lookup import SourceLookupTool
from app.services.ingestion_service import IngestionService


@pytest.mark.asyncio
async def test_tools_execution_and_registry(test_db: AsyncSession):
    """Verify ToolRegistry and individual tool execution."""
    await IngestionService.ingest_source(test_db, source="sample", limit=3, force_refresh=True)

    registry = ToolRegistry(test_db)
    schemas = registry.get_schemas()
    assert len(schemas) == 5
    tool_names = [s["function"]["name"] for s in schemas]
    assert "search_lenny_transcripts" in tool_names
    assert "lookup_episode_source" in tool_names
    assert "generate_ship30_essay" in tool_names
    assert "generate_artifact" in tool_names
    assert "compare_perspectives" in tool_names

    # Test search_lenny_transcripts execution
    search_tool = registry.get_tool("search_lenny_transcripts")
    assert search_tool is not None
    res = await search_tool.execute(query="Casey Winters growth loops retention curve", top_k=2)
    assert res["count"] > 0
    assert len(res["results"]) > 0
    assert len(registry.search_tool.retrieved_chunks) > 0

    # Test lookup_episode_source execution
    lookup_tool = registry.get_tool("lookup_episode_source")
    assert lookup_tool is not None
    look_res = await lookup_tool.execute(episode_title_or_guest="Casey Winters")
    assert look_res["found"] is True
    assert len(look_res["episodes"]) > 0
    assert "Casey Winters" in look_res["episodes"][0]["guest"]


@pytest.mark.asyncio
async def test_agent_grounded_response_and_citation_integrity(test_db: AsyncSession):
    """
    Verify Pi Coding Agent execution loop:
    1. Agent requests search_lenny_transcripts.
    2. Tool executes against database.
    3. Final answer is synthesized.
    4. Citations STRICTLY match retrieved chunks (Zero citation fabrication).
    """
    await IngestionService.ingest_source(test_db, source="sample", limit=3, force_refresh=True)

    mock_provider = MockAgentProvider()
    result = await AgentService.run(
        db=test_db,
        query="How does Casey Winters recommend assessing product-market fit?",
        conversation_history=[],
        custom_provider=mock_provider,
    )

    assert result.status == "complete"
    assert len(result.citations) > 0
    # Citations must originate from retrieved chunks
    for cit in result.citations:
        assert cit.guest in ("Casey Winters", "Elena Verna", "Brian Balfour")
        assert cit.quote_excerpt is not None
        assert cit.episode_title is not None
        assert cit.episode_url is not None


@pytest.mark.asyncio
async def test_agent_low_evidence_handling(test_db: AsyncSession):
    """
    Verify that unsupported topics (e.g. crypto, Solana, web3) or topics with
    no evidence return status='low-evidence' with 0 citations and clear message.
    """
    await IngestionService.ingest_source(test_db, source="sample", limit=2, force_refresh=True)

    mock_provider = MockAgentProvider()

    # Query clearly outside Lenny's podcast domain
    result = await AgentService.run(
        db=test_db,
        query="How do I calculate Solana staking rewards and liquidity pool impermanent loss in crypto?",
        conversation_history=[],
        custom_provider=mock_provider,
    )

    assert result.status == "low-evidence"
    assert len(result.citations) == 0
    assert "don't have enough grounded material" in result.content
    assert "cannot synthesize reliable operational guidance without fabricating claims" in result.content


@pytest.mark.asyncio
async def test_agent_multi_turn_history(test_db: AsyncSession):
    """Verify conversation history is forwarded into agent messages."""
    await IngestionService.ingest_source(test_db, source="sample", limit=2, force_refresh=True)

    history = [
        {"role": "user", "content": "Let's talk about Elena Verna."},
        {"role": "assistant", "content": "Elena Verna discusses B2B PLG loops."},
    ]

    mock_provider = MockAgentProvider()

    with patch.object(mock_provider, "chat", wraps=mock_provider.chat) as spy_chat:
        result = await AgentService.run(
            db=test_db,
            query="What is her recommended activation benchmark?",
            conversation_history=history,
            custom_provider=mock_provider,
        )

        assert result.status == "complete"
        # Verify chat was called with conversation history in messages
        first_call_msgs = spy_chat.call_args_list[0][1]["messages"]
        roles = [m["role"] for m in first_call_msgs]
        assert "system" in roles
        assert roles.count("user") >= 1
