import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ingestion_service import IngestionService


@pytest.mark.asyncio
async def test_chat_grounding_with_transcript_citations(client: AsyncClient, test_db: AsyncSession):
    # Ingest sample data
    await IngestionService.ingest_source(test_db, source="sample", limit=3, force_refresh=True)

    # 1. Create session
    s_resp = await client.post("/api/sessions", json={"title": "New conversation"})
    session_id = s_resp.json()["id"]

    # 2. Ask product question supported by Lenny's podcast
    chat_resp = await client.post(
        "/api/chat",
        json={
            "sessionId": session_id,
            "content": "What does Casey Winters say about cohort retention and growth loops?",
            "modelId": "openai-cloud",
        },
    )
    assert chat_resp.status_code == 200
    data = chat_resp.json()

    assistant_msg = data["assistantMessage"]
    assert assistant_msg["status"] == "complete"
    assert len(assistant_msg["citations"]) > 0

    # Verify citation attributes
    first_cit = assistant_msg["citations"][0]
    assert first_cit["guest"] in ("Casey Winters", "Elena Verna", "Brian Balfour")
    assert first_cit["episodeTitle"] is not None
    assert first_cit["quoteExcerpt"] is not None
    assert first_cit["episodeUrl"] is not None


@pytest.mark.asyncio
async def test_chat_unsupported_questions_low_evidence(client: AsyncClient, test_db: AsyncSession):
    # Ingest sample data
    await IngestionService.ingest_source(test_db, source="sample", limit=2, force_refresh=True)

    s_resp = await client.post("/api/sessions", json={"title": "New conversation"})
    session_id = s_resp.json()["id"]

    # Ask unsupported question (crypto/web3/astrophysics)
    chat_resp = await client.post(
        "/api/chat",
        json={
            "sessionId": session_id,
            "content": "How do I calculate Solana staking rewards and liquidity pool impermanent loss in crypto?",
            "modelId": "openai-cloud",
        },
    )
    assert chat_resp.status_code == 200
    data = chat_resp.json()

    assistant_msg = data["assistantMessage"]
    assert assistant_msg["status"] == "low-evidence"
    assert len(assistant_msg["citations"]) == 0
    assert "don't have enough grounded material" in assistant_msg["content"]


@pytest.mark.asyncio
async def test_chat_follow_up_context(client: AsyncClient, test_db: AsyncSession):
    await IngestionService.ingest_source(test_db, source="sample", limit=3, force_refresh=True)

    s_resp = await client.post("/api/sessions", json={"title": "New conversation"})
    session_id = s_resp.json()["id"]

    # First turn
    await client.post(
        "/api/chat",
        json={
            "sessionId": session_id,
            "content": "Tell me about Elena Verna's views on B2B product-led growth.",
            "modelId": "openai-cloud",
        },
    )

    # Follow-up turn with relative reference
    followup_resp = await client.post(
        "/api/chat",
        json={
            "sessionId": session_id,
            "content": "What is her recommended activation benchmark?",
            "modelId": "openai-cloud",
        },
    )
    assert followup_resp.status_code == 200
    data = followup_resp.json()
    assistant_msg = data["assistantMessage"]
    assert assistant_msg["status"] == "complete"
    assert len(assistant_msg["citations"]) > 0
    assert any(c["guest"] == "Elena Verna" for c in assistant_msg["citations"])


@pytest.mark.asyncio
async def test_chat_session_isolation(client: AsyncClient, test_db: AsyncSession):
    await IngestionService.ingest_source(test_db, source="sample", limit=2, force_refresh=True)

    # Session A
    sA = (await client.post("/api/sessions", json={"title": "Session A"})).json()["id"]
    await client.post("/api/chat", json={"sessionId": sA, "content": "Tell me about growth loops"})

    # Session B
    sB = (await client.post("/api/sessions", json={"title": "Session B"})).json()["id"]

    # Verify session B messages do not contain session A messages
    detailB = (await client.get(f"/api/sessions/{sB}")).json()
    assert len(detailB["messages"]) == 0

    detailA = (await client.get(f"/api/sessions/{sA}")).json()
    assert len(detailA["messages"]) == 2
