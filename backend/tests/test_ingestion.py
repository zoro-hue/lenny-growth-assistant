import pytest
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ingestion_service import IngestionService
from app.models.transcript import TranscriptMetadataModel, TranscriptChunkModel


@pytest.mark.asyncio
async def test_ingestion_and_idempotency(test_db: AsyncSession):
    # 1. First run: Ingest sample episodes
    res1 = await IngestionService.ingest_source(
        db=test_db,
        source="sample",
        limit=2,
        force_refresh=False,
    )
    assert res1.status == "success"
    assert res1.episodes_ingested == 2
    assert res1.episodes_skipped == 0
    assert res1.chunks_created > 0

    # Verify rows in DB
    ep_count = await test_db.scalar(select(func.count()).select_from(TranscriptMetadataModel))
    chk_count = await test_db.scalar(select(func.count()).select_from(TranscriptChunkModel))
    assert ep_count == 2
    assert chk_count == res1.chunks_created

    # 2. Second run: Should be completely idempotent (0 ingested, 2 skipped, 0 chunks added)
    res2 = await IngestionService.ingest_source(
        db=test_db,
        source="sample",
        limit=2,
        force_refresh=False,
    )
    assert res2.episodes_ingested == 0
    assert res2.episodes_skipped == 2
    assert res2.chunks_created == 0

    ep_count_after = await test_db.scalar(select(func.count()).select_from(TranscriptMetadataModel))
    chk_count_after = await test_db.scalar(select(func.count()).select_from(TranscriptChunkModel))
    assert ep_count_after == 2
    assert chk_count_after == chk_count

    # 3. Third run: With force_refresh=True, it re-indexes without creating duplicate episodes
    res3 = await IngestionService.ingest_source(
        db=test_db,
        source="sample",
        limit=2,
        force_refresh=True,
    )
    assert res3.episodes_ingested == 2
    assert res3.episodes_skipped == 0

    ep_count_final = await test_db.scalar(select(func.count()).select_from(TranscriptMetadataModel))
    chk_count_final = await test_db.scalar(select(func.count()).select_from(TranscriptChunkModel))
    assert ep_count_final == 2
    assert chk_count_final == chk_count
