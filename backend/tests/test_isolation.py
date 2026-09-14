import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_session_isolation(client: AsyncClient):
    """
    Validates that messages and conversation histories are completely isolated
    between sessions. Messages added to Session A must never appear in Session B.
    """
    # 1. Create Session A and Session B
    res_a = await client.post("/api/sessions", json={"title": "Session A (Growth)"})
    res_b = await client.post("/api/sessions", json={"title": "Session B (Pricing)"})
    id_a = res_a.json()["id"]
    id_b = res_b.json()["id"]

    # 2. Add messages to Session A
    msg_a1 = {
        "role": "user",
        "content": "What is cohort flattening?",
    }
    msg_a2 = {
        "role": "assistant",
        "content": "Cohort flattening occurs when retention asymptote runs parallel to x-axis.",
        "citations": [
            {
                "id": "cit-casey",
                "episodeTitle": "Casey Winters on Growth Loops",
                "guest": "Casey Winters",
                "timestamp": "12:30",
                "quoteExcerpt": "If you don't have that horizontal floor, nothing else matters.",
                "episodeUrl": "https://lennyspodcast.com/casey",
            }
        ],
    }
    await client.post(f"/api/sessions/{id_a}/messages", json=msg_a1)
    await client.post(f"/api/sessions/{id_a}/messages", json=msg_a2)

    # 3. Add one message to Session B
    msg_b1 = {
        "role": "user",
        "content": "How do you price B2B SaaS?",
    }
    await client.post(f"/api/sessions/{id_b}/messages", json=msg_b1)

    # 4. Verify Session A has 2 messages
    detail_a = (await client.get(f"/api/sessions/{id_a}")).json()
    assert len(detail_a["messages"]) == 2
    assert detail_a["messages"][0]["content"] == "What is cohort flattening?"
    assert detail_a["messages"][1]["citations"][0]["guest"] == "Casey Winters"

    # 5. Verify Session B has strictly 1 message and none from Session A
    detail_b = (await client.get(f"/api/sessions/{id_b}")).json()
    assert len(detail_b["messages"]) == 1
    assert detail_b["messages"][0]["content"] == "How do you price B2B SaaS?"

    # 6. Verify messages endpoint isolation
    msgs_b = (await client.get(f"/api/sessions/{id_b}/messages")).json()
    assert len(msgs_b) == 1
    assert msgs_b[0]["content"] == "How do you price B2B SaaS?"
