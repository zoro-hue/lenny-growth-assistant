import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_message_persistence_and_ordering(client: AsyncClient):
    session_res = await client.post("/api/sessions", json={"title": "Test Chat"})
    session_id = session_res.json()["id"]

    # 1. Post user message
    user_payload = {
        "role": "user",
        "content": "First question from user",
    }
    msg1_res = await client.post(f"/api/sessions/{session_id}/messages", json=user_payload)
    assert msg1_res.status_code == 201
    msg1 = msg1_res.json()
    assert msg1["role"] == "user"
    assert msg1["content"] == "First question from user"
    assert "timestamp" in msg1

    # 2. Post assistant message with citation
    assistant_payload = {
        "role": "assistant",
        "content": "Grounded answer from Lenny transcripts",
        "citations": [
            {
                "id": "cit-elena",
                "episodeNumber": 88,
                "episodeTitle": "Elena Verna on PLG",
                "guest": "Elena Verna",
                "guestRole": "Head of Growth",
                "timestamp": "28:44",
                "quoteExcerpt": "Trying to create daily habits for quarterly problems always creates churn.",
                "episodeUrl": "https://lennyspodcast.com/elena",
            }
        ],
    }
    msg2_res = await client.post(f"/api/sessions/{session_id}/messages", json=assistant_payload)
    assert msg2_res.status_code == 201
    msg2 = msg2_res.json()
    assert msg2["role"] == "assistant"
    assert len(msg2["citations"]) == 1
    assert msg2["citations"][0]["guest"] == "Elena Verna"
    assert msg2["citations"][0]["episodeNumber"] == 88

    # 3. List messages and verify ordering
    list_res = await client.get(f"/api/sessions/{session_id}/messages")
    assert list_res.status_code == 200
    messages = list_res.json()
    assert len(messages) == 2
    assert messages[0]["id"] == msg1["id"]
    assert messages[1]["id"] == msg2["id"]


@pytest.mark.asyncio
async def test_chat_endpoint_interaction(client: AsyncClient):
    # Ingest sample transcripts so retrieval can ground and cite
    await client.post("/api/knowledge/ingest", json={"source": "sample", "limit": 2})

    # Test POST /api/chat
    session_res = await client.post("/api/sessions", json={"title": "New conversation"})
    session_id = session_res.json()["id"]

    chat_payload = {
        "sessionId": session_id,
        "content": "How do you achieve Product-Market Fit?",
        "modelId": "openai-cloud",
    }
    chat_res = await client.post("/api/chat", json=chat_payload)
    assert chat_res.status_code == 200
    data = chat_res.json()
    assert data["sessionId"] == session_id
    assert data["userMessage"]["content"] == "How do you achieve Product-Market Fit?"
    assert data["assistantMessage"]["role"] == "assistant"
    assert len(data["assistantMessage"]["citations"]) > 0

    # Verify auto-titling happened
    session_detail = (await client.get(f"/api/sessions/{session_id}")).json()
    assert session_detail["title"] != "New conversation"
    assert "Product-Market Fit" in session_detail["title"]
    # Both messages must be persisted in database
    assert len(session_detail["messages"]) == 2
