import pytest
import os
import json
import httpx
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.agent_service import AgentService, AgentExecutionResult
from app.agent.pi_rpc_client import PiRpcClient, PiExecutionOutput
from app.agent.tool_bridge import ToolBridge
from app.agent.tools.registry import ToolRegistry
from app.schemas.knowledge import SearchResultItem
from app.schemas.message import CitationSchema


@pytest.mark.asyncio
async def test_agent_service_routes_through_pi_rpc(test_db: AsyncSession):
    """
    Verification test: Proves that AgentService routes through the official
    Pi Coding Agent (PiRpcClient) rather than the old custom ReAct loop.
    """
    citation = CitationSchema(
        id="101",
        episodeNumber=88,
        episodeTitle="Elena Verna on PLG",
        guest="Elena Verna",
        guestRole="Head of Growth",
        timestamp="14:20",
        quoteExcerpt="Product-led growth is a distribution model where user acquisition relies on product.",
        episodeUrl="https://lennyspodcast.com/elena-verna",
        relevanceScore=0.92,
    )
    mock_chunks = [
        SearchResultItem(
            chunkId="101",
            transcriptId="t1",
            episodeNumber=88,
            episodeTitle="Elena Verna on PLG",
            guest="Elena Verna",
            guestRole="Head of Growth",
            sourceUrl="https://lennyspodcast.com/elena-verna",
            chunkIndex=0,
            timestamp="14:20",
            content="Product-led growth is a distribution model where user acquisition relies on product.",
            similarityScore=0.92,
            citation=citation,
        )
    ]

    # Mock the tool execution so chunks are populated on the search tool
    async def fake_pi_execute(*args, **kwargs):
        bridge_port = kwargs.get("tool_bridge_port")
        assert bridge_port is not None, "Tool bridge port must be passed to Pi Coding Agent"
        # Simulate Pi calling the tool over the bridge
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"http://127.0.0.1:{bridge_port}/tool",
                json={"name": "search_lenny_transcripts", "params": {"query": "PLG retention"}},
            )
            assert resp.status_code == 200
            print("BRIDGE RESP:", resp.json())

        return PiExecutionOutput(
            content="Elena Verna highlights that PLG relies directly on user self-serve activation.",
            provider=kwargs.get("provider", "ollama"),
            model=kwargs.get("model_id", "llama3.2:3b"),
            success=True,
        )

    with patch.object(PiRpcClient, "execute", side_effect=fake_pi_execute) as mock_execute:
        with patch("app.services.retrieval_service.RetrievalService.retrieve", new_callable=AsyncMock, return_value=mock_chunks):
            result: AgentExecutionResult = await AgentService.run(
                db=test_db,
                query="How does Elena Verna define PLG?",
                conversation_history=[],
                model_id="ollama-local",
            )
            print("RESULT IS:", result)

            # Assert PiRpcClient was called, proving primary path is Pi
            assert mock_execute.called, "AgentService must execute through PiRpcClient"
            call_kwargs = mock_execute.call_args.kwargs
            assert call_kwargs["provider"] == "ollama"
            assert call_kwargs["model_id"] == "llama3.2:3b"
            assert "Elena Verna define PLG" in call_kwargs["prompt"]

            # Assert response outcome
            assert result.status == "complete"
            assert "Elena Verna" in result.content
            assert len(result.citations) == 1
            assert result.citations[0].guest == "Elena Verna"
            assert result.citations[0].episode_number == 88


@pytest.mark.asyncio
async def test_tool_bridge_execution_and_chunk_accumulation(test_db: AsyncSession):
    """
    Tests the in-process ToolBridge HTTP server invoked by Pi's TypeScript extension.
    """
    registry = ToolRegistry(test_db)
    bridge = ToolBridge(registry)
    port = await bridge.start()
    assert port > 0

    try:
        async with httpx.AsyncClient() as client:
            # 1. Test lookup_episode_source tool
            resp = await client.post(
                f"http://127.0.0.1:{port}/tool",
                json={"name": "lookup_episode_source", "params": {"episode_title_or_guest": "Elena Verna"}},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "found" in data

            # 2. Test unknown tool
            err_resp = await client.post(
                f"http://127.0.0.1:{port}/tool",
                json={"name": "non_existent_tool", "params": {}},
            )
            assert err_resp.status_code == 200
            err_data = err_resp.json()
            assert "error" in err_data
    finally:
        await bridge.stop()


@pytest.mark.asyncio
async def test_pi_agent_out_of_domain_returns_low_evidence(test_db: AsyncSession):
    """
    Verifies that safe low-evidence handling protects against unsupported queries
    without invoking the model.
    """
    result = await AgentService.run(
        db=test_db,
        query="Tell me about Solana staking rewards and Web3 tokenomics",
        conversation_history=[],
        model_id="ollama-local",
    )

    assert result.status == "low-evidence"
    assert "Lenny's Podcast" in result.content
    assert result.citations == []


@pytest.mark.asyncio
async def test_pi_agent_mock_boundary_for_safe_testing(test_db: AsyncSession):
    """
    Verifies that PiRpcClient.mock_runner serves as a clean mock boundary
    for deterministic tests that do not need live model execution.
    """
    def mock_runner(prompt, provider, model_id, bridge_port):
        return PiExecutionOutput(
            content=f"Mock Pi response for {prompt[:10]}",
            provider=provider,
            model=model_id,
            success=True,
        )

    PiRpcClient.mock_runner = mock_runner
    try:
        client = PiRpcClient()
        output = await client.execute(prompt="Hello Lenny", provider="ollama", model_id="llama3.2:3b")
        assert output.success is True
        assert "Mock Pi response" in output.content
    finally:
        PiRpcClient.mock_runner = None
