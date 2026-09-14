import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_models_endpoint(client: AsyncClient):
    """Verify GET /api/models returns cloud and local providers with correct metadata."""
    response = await client.get("/api/models")
    assert response.status_code == 200
    data = response.json()

    assert "providers" in data
    assert "fallbackEnabled" in data
    assert isinstance(data["providers"], list)
    assert len(data["providers"]) >= 2

    provider_ids = [p["id"] for p in data["providers"]]
    assert "openai-cloud" in provider_ids
    assert "ollama-local" in provider_ids

    # Verify OpenAI provider details
    openai_prov = next(p for p in data["providers"] if p["id"] == "openai-cloud")
    assert openai_prov["name"] == "OpenAI"
    assert openai_prov["provider"] == "Cloud"
    assert "gpt-4o-mini" in openai_prov["model"]
    assert isinstance(openai_prov["available"], bool)
    assert isinstance(openai_prov["note"], str)

    # Verify Ollama provider details
    ollama_prov = next(p for p in data["providers"] if p["id"] == "ollama-local")
    assert ollama_prov["name"] == "Ollama"
    assert ollama_prov["provider"] == "Local"
    assert "llama3.2:3b" in ollama_prov["model"]
    assert isinstance(ollama_prov["available"], bool)
    assert isinstance(ollama_prov["note"], str)


@pytest.mark.asyncio
async def test_session_model_persistence(client: AsyncClient):
    """Verify switching model via PATCH /api/sessions/{id} persists."""
    # 1. Create session with openai-cloud
    res = await client.post("/api/sessions", json={"title": "Model Switch Test", "activeModelId": "openai-cloud"})
    assert res.status_code == 201
    session_id = res.json()["id"]
    assert res.json()["activeModelId"] == "openai-cloud"

    # 2. Switch to ollama-local via PATCH
    patch_res = await client.patch(f"/api/sessions/{session_id}", json={"activeModelId": "ollama-local"})
    assert patch_res.status_code == 200
    assert patch_res.json()["activeModelId"] == "ollama-local"

    # 3. Verify retrieved session has ollama-local
    get_res = await client.get(f"/api/sessions/{session_id}")
    assert get_res.status_code == 200
    assert get_res.json()["activeModelId"] == "ollama-local"


@pytest.mark.asyncio
async def test_chat_updates_session_model_if_provided(client: AsyncClient):
    """Verify sending a chat message with a different modelId updates the session."""
    res = await client.post("/api/sessions", json={"title": "Chat Model Test", "activeModelId": "ollama-local"})
    session_id = res.json()["id"]

    chat_res = await client.post(
        "/api/chat",
        json={
            "sessionId": session_id,
            "content": "What does Casey Winters say about growth?",
            "modelId": "openai-cloud",
        },
    )
    assert chat_res.status_code == 200

    # Verify session active model was updated
    get_res = await client.get(f"/api/sessions/{session_id}")
    assert get_res.json()["activeModelId"] == "openai-cloud"
