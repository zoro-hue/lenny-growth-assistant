import pytest
from datetime import datetime, timezone
from app.models.message import MessageModel
from app.services.message_service import MessageService


def test_follow_up_suggestions_balfour():
    msg = MessageModel(
        id="msg-f1",
        session_id="test-s",
        role="assistant",
        content="Brian Balfour explained Channel-Model Fit on Lenny's Podcast.",
        status="complete",
        created_at=datetime.now(timezone.utc),
        citations=[
            {
                "id": "c1",
                "episodeTitle": "Ep 112",
                "guest": "Brian Balfour",
                "timestamp": "00:01:28",
                "quoteExcerpt": "Distribution channels do not care about your product...",
                "episodeUrl": "https://youtube.com/1",
            }
        ],
    )
    resp = MessageService.to_response(msg)
    suggestions = resp.follow_up_suggestions or []
    assert len(suggestions) >= 3
    assert any("Compare Brian Balfour" in s for s in suggestions)
    assert any("Channel-Model" in s or "metric" in s.lower() for s in suggestions)
    assert any("playbook" in s.lower() for s in suggestions)
    assert any("Ship 30" in s for s in suggestions)


def test_follow_up_suggestions_verna():
    msg = MessageModel(
        id="msg-f2",
        session_id="test-s",
        role="assistant",
        content="Elena Verna breaks down PLG and Time-to-Aha.",
        status="complete",
        created_at=datetime.now(timezone.utc),
        citations=[
            {
                "id": "c2",
                "episodeTitle": "Ep 88",
                "guest": "Elena Verna",
                "timestamp": "00:00:45",
                "quoteExcerpt": "PLG is an organizational distribution model...",
                "episodeUrl": "https://youtube.com/2",
            }
        ],
    )
    resp = MessageService.to_response(msg)
    suggestions = resp.follow_up_suggestions or []
    assert len(suggestions) >= 3
    assert any("Compare Elena Verna" in s for s in suggestions)
    assert any("Time-to-Aha" in s or "activation" in s.lower() for s in suggestions)


def test_no_follow_up_suggestions_on_low_evidence():
    msg = MessageModel(
        id="msg-f3",
        session_id="test-s",
        role="assistant",
        content="I do not have enough evidence on web3 tokenomics.",
        status="low-evidence",
        created_at=datetime.now(timezone.utc),
        citations=[],
    )
    resp = MessageService.to_response(msg)
    assert len(resp.follow_up_suggestions or []) == 0
