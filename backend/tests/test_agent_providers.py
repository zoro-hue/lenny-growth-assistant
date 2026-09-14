import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.agent.providers import (
    BaseLLMProvider,
    OpenAIProvider,
    OllamaProvider,
    MockAgentProvider,
    ProviderManager,
    ProviderError,
    MissingProviderKeyError,
    ProviderUnavailableError,
)
from app.config import settings


@pytest.mark.asyncio
async def test_openai_provider_missing_key():
    """Verify OpenAIProvider without an API key raises MissingProviderKeyError."""
    provider = OpenAIProvider(api_key="")
    assert await provider.is_available() is False

    with pytest.raises(MissingProviderKeyError) as exc_info:
        await provider.chat(messages=[{"role": "user", "content": "Hello"}])

    err = exc_info.value
    assert err.status_code == 400
    assert "API key is missing" in err.message
    assert err.details.get("canSwitchToLocal") is True


@pytest.mark.asyncio
async def test_openai_provider_mocked_chat():
    """Verify OpenAIProvider parses assistant message and tool calls correctly."""
    provider = OpenAIProvider(api_key="test-key", model="gpt-4o-mini")
    assert await provider.is_available() is True

    mock_response_data = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Searching transcripts...",
                    "tool_calls": [
                        {
                            "id": "call_123",
                            "type": "function",
                            "function": {
                                "name": "search_lenny_transcripts",
                                "arguments": json.dumps({"query": "retention curves", "top_k": 3}),
                            },
                        }
                    ],
                }
            }
        ]
    }

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response_data

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        content, tool_calls = await provider.chat(
            messages=[{"role": "user", "content": "What is cohort retention?"}],
            tools=[{"type": "function", "function": {"name": "search_lenny_transcripts"}}],
        )

        assert content == "Searching transcripts..."
        assert len(tool_calls) == 1
        assert tool_calls[0]["id"] == "call_123"
        assert tool_calls[0]["name"] == "search_lenny_transcripts"
        assert tool_calls[0]["arguments"] == {"query": "retention curves", "top_k": 3}


@pytest.mark.asyncio
async def test_ollama_provider_unavailable():
    """Verify OllamaProvider raises ProviderUnavailableError when port is unreachable."""
    # Port 59999 is closed
    provider = OllamaProvider(base_url="http://localhost:59999")
    assert await provider.is_available() is False

    with pytest.raises(ProviderUnavailableError) as exc_info:
        await provider.chat(messages=[{"role": "user", "content": "Hello"}])

    err = exc_info.value
    assert "Couldn't reach local Ollama" in err.message
    assert err.details.get("canSwitchToCloud") is True


@pytest.mark.asyncio
async def test_ollama_provider_mocked_chat():
    """Verify OllamaProvider parses /api/chat tool calls properly."""
    provider = OllamaProvider(base_url="http://localhost:11434", model="llama3.2:3b")

    mock_response_data = {
        "message": {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call_ollama_1",
                    "function": {
                        "name": "search_lenny_transcripts",
                        "arguments": {"query": "Casey Winters product market fit"},
                    },
                }
            ],
        }
    }

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response_data

    with patch.object(provider, "is_available", new_callable=AsyncMock, return_value=True):
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
            content, tool_calls = await provider.chat(
                messages=[{"role": "user", "content": "How does Casey Winters measure PMF?"}],
                tools=[{"type": "function", "function": {"name": "search_lenny_transcripts"}}],
            )
            assert len(tool_calls) == 1
            assert tool_calls[0]["name"] == "search_lenny_transcripts"
            assert tool_calls[0]["arguments"]["query"] == "Casey Winters product market fit"


@pytest.mark.asyncio
async def test_mock_agent_provider():
    """Verify MockAgentProvider deterministic behavior."""
    provider = MockAgentProvider()
    assert await provider.is_available() is True

    # Turn 1: returns tool call
    content, calls = await provider.chat(
        messages=[{"role": "user", "content": "What is retention?"}],
        tools=[{"type": "function", "function": {"name": "search_lenny_transcripts"}}],
    )
    assert len(calls) == 1
    assert calls[0]["name"] == "search_lenny_transcripts"

    # Turn 2: synthesizes final grounded answer with tool results
    tool_output = {
        "results": [
            {
                "chunk_id": "c1",
                "guest": "Casey Winters",
                "episode_title": "Casey Winters on Growth Loops",
                "content": "Cohort retention curves must flatten parallel to the x-axis.",
            }
        ]
    }
    content2, calls2 = await provider.chat(
        messages=[
            {"role": "user", "content": "What is retention?"},
            {"role": "tool", "content": json.dumps(tool_output)},
        ],
        tools=[],
    )
    assert len(calls2) == 0
    assert "Casey Winters" in content2
    assert "retention curve" in content2


@pytest.mark.asyncio
async def test_provider_manager_fallback_disabled():
    """Verify fallback=False immediately raises error if requested provider is unavailable."""
    with patch.object(OpenAIProvider, "is_available", new_callable=AsyncMock, return_value=False):
        # Force production mode for explicit error check
        orig_env = settings.app_env
        try:
            settings.app_env = "production"
            with pytest.raises(MissingProviderKeyError):
                await ProviderManager.resolve_provider_with_fallback(
                    model_id="openai-cloud",
                    fallback_enabled=False,
                )
        finally:
            settings.app_env = orig_env


@pytest.mark.asyncio
async def test_provider_manager_fallback_enabled():
    """Verify fallback=True transparently switches when primary is unavailable."""
    orig_env = settings.app_env
    try:
        settings.app_env = "production"
        with patch.object(OpenAIProvider, "is_available", new_callable=AsyncMock, return_value=False):
            with patch.object(OllamaProvider, "is_available", new_callable=AsyncMock, return_value=True):
                provider, actual, reason = await ProviderManager.resolve_provider_with_fallback(
                    model_id="openai-cloud",
                    fallback_enabled=True,
                )
                assert actual == "ollama"
                assert "falling back to Local Ollama" in reason
                assert isinstance(provider, OllamaProvider)
    finally:
        settings.app_env = orig_env
