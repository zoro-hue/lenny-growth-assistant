import pytest
from app.services.chunking_service import ChunkingService, DialogueTurn


def test_parse_turns():
    sample_text = """
**Lenny Rachitsky** (00:00:10):
Welcome to the podcast. Today my guest is Casey Winters.

**Casey Winters** (00:00:25):
Thanks Lenny, excited to be here!

Lenny (00:00:30):
Let's talk about growth loops.
"""
    turns = ChunkingService.parse_turns(sample_text)
    assert len(turns) == 3
    assert turns[0].speaker == "Lenny Rachitsky"
    assert turns[0].timestamp == "00:00:10"
    assert "Casey Winters" in turns[0].text

    assert turns[1].speaker == "Casey Winters"
    assert turns[1].timestamp == "00:00:25"
    assert "excited to be here" in turns[1].text

    assert turns[2].speaker == "Lenny"
    assert turns[2].timestamp == "00:00:30"


def test_chunking_with_overlap():
    dialogue = """
**Lenny** (00:01):
Point one about retention.

**Casey** (00:05):
Product-market fit is revealed when a cohort retention curve stops dropping and runs flat.

**Lenny** (00:15):
What about linear funnels?

**Casey** (00:20):
Linear funnels suffer from diminishing returns. Growth loops compound.
"""
    chunks = ChunkingService.chunk_transcript(dialogue, chunk_size=150, chunk_overlap=50)
    assert len(chunks) >= 2

    # Check structure
    for i, c in enumerate(chunks):
        assert c.chunk_index == i
        assert len(c.content) > 0
        assert c.token_count > 0

    # Earliest timestamp preserved
    assert chunks[0].timestamp == "00:01"


def test_chunking_empty():
    assert ChunkingService.chunk_transcript("") == []
    assert ChunkingService.chunk_transcript("   \n\n  ") == []
