import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.retrieval_service import RetrievalService
from app.services.ingestion_service import IngestionService
from app.services.message_service import MessageService
from app.models.message import MessageModel
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_speaker_detection_and_prioritization(test_db: AsyncSession):
    # Ensure sample transcripts are ingested
    await IngestionService.ingest_source(db=test_db, source="sample", force_refresh=False)

    # 1. Test speaker target extraction
    targets_balfour = RetrievalService.extract_query_targets(
        "Why does Brian Balfour argue that traditional acquisition funnels are dead?"
    )
    assert "Brian Balfour" in targets_balfour["speakers"]

    targets_verna = RetrievalService.extract_query_targets(
        "What is Elena Verna's definition of Time-to-Aha in PLG?"
    )
    assert "Elena Verna" in targets_verna["speakers"]

    targets_ep = RetrievalService.extract_query_targets("In Episode 112, what framework is discussed?")
    assert targets_ep["episode_number"] == 112

    # 2. Test speaker-prioritized retrieval
    balfour_query = "Why does Brian Balfour argue that traditional acquisition funnels are dead?"
    results = await RetrievalService.retrieve(db=test_db, query=balfour_query, top_k=3, similarity_threshold=0.10)
    assert len(results) > 0

    # Top result MUST be from Brian Balfour because he was explicitly named
    top_chunk = results[0]
    assert top_chunk.guest == "Brian Balfour"
    assert top_chunk.citation.why_this_source is not None
    assert "Brian Balfour" in top_chunk.citation.why_this_source

    # 3. Test non-exclusion of another relevant speaker
    # Both Balfour and Casey discuss growth loops / funnels; Casey should not be erased if space permits
    all_guests = [r.guest for r in results]
    assert "Brian Balfour" in all_guests


@pytest.mark.asyncio
async def test_evidence_strength_computation():
    # 1. High evidence: >= 2 citations, 2 speakers
    msg_high = MessageModel(
        id="msg-1",
        session_id="test-session",
        role="assistant",
        content="Grounded answer.",
        status="complete",
        created_at=datetime.now(timezone.utc),
        citations=[
            {
                "id": "c1",
                "episodeTitle": "Ep 1",
                "guest": "Brian Balfour",
                "timestamp": "00:01",
                "quoteExcerpt": "Quote 1",
                "episodeUrl": "https://youtube.com/1",
            },
            {
                "id": "c2",
                "episodeTitle": "Ep 2",
                "guest": "Casey Winters",
                "timestamp": "00:02",
                "quoteExcerpt": "Quote 2",
                "episodeUrl": "https://youtube.com/2",
            },
        ],
    )
    resp_high = MessageService.to_response(msg_high)
    assert resp_high.evidence_strength == "high"
    assert "2 transcript sources · 2 speakers" in (resp_high.evidence_label or "")

    # 2. Limited evidence: exactly 1 citation
    msg_limited = MessageModel(
        id="msg-2",
        session_id="test-session",
        role="assistant",
        content="Single source answer.",
        status="complete",
        created_at=datetime.now(timezone.utc),
        citations=[
            {
                "id": "c1",
                "episodeTitle": "Ep 1",
                "guest": "Brian Balfour",
                "timestamp": "00:01",
                "quoteExcerpt": "Quote 1",
                "episodeUrl": "https://youtube.com/1",
            }
        ],
    )
    resp_limited = MessageService.to_response(msg_limited)
    assert resp_limited.evidence_strength == "limited"
    assert "1 relevant transcript source" in (resp_limited.evidence_label or "")

    # 3. Not grounded: low-evidence status
    msg_not_grounded = MessageModel(
        id="msg-3",
        session_id="test-session",
        role="assistant",
        content="Low evidence answer.",
        status="low-evidence",
        created_at=datetime.now(timezone.utc),
        citations=[],
    )
    resp_not_grounded = MessageService.to_response(msg_not_grounded)
    assert resp_not_grounded.evidence_strength == "not-grounded"
    assert "No supporting Lenny Podcast evidence found" in (resp_not_grounded.evidence_label or "")
