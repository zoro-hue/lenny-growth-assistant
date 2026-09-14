import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.scripts.seed_demo import seed_demo_conversations, DEMO_CONVERSATIONS
from app.models.session import SessionModel
from app.models.message import MessageModel
from app.models.artifact import ArtifactModel
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_seed_demo_conversations_persistence(test_db: AsyncSession):
    # Seed conversations with reset
    result = await seed_demo_conversations(db=test_db, reset=True)
    assert result["status"] == "success"
    assert result["sessions_created"] == 6

    # Verify sessions in DB
    sessions = (await test_db.execute(select(SessionModel).order_by(SessionModel.updated_at.desc()))).scalars().all()
    assert len(sessions) == 6

    titles = [s.title for s in sessions]
    assert "Brian Balfour — Channel Model Fit" in titles
    assert "Retention Curves — What Actually Matters" in titles
    assert "Ship 30/30 — Pricing Strategy" in titles
    assert "B2B SaaS Retention Playbook" in titles
    assert "Elena Verna — Product-Led Growth" in titles
    assert "Rahul Vohra — PMF Framework" in titles

    # Verify messages and citations
    messages = (await test_db.execute(select(MessageModel))).scalars().all()
    assert len(messages) >= 12  # At least 2 per conversation

    # Verify artifacts exist for session 3 & 4
    artifacts = (await test_db.execute(select(ArtifactModel))).scalars().all()
    assert len(artifacts) >= 2


@pytest.mark.asyncio
async def test_seed_demo_api_endpoint(client: AsyncClient):
    resp = await client.post("/api/sessions/seed-demo?reset=true")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["sessions_created"] == 6
