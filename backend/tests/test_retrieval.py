import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ingestion_service import IngestionService
from app.services.retrieval_service import RetrievalService


@pytest.mark.asyncio
async def test_retrieval_empty_knowledge_base(test_db: AsyncSession):
    # Knowledge base has 0 chunks
    results = await RetrievalService.retrieve(test_db, query="growth loops and cohort retention")
    assert results == []


@pytest.mark.asyncio
async def test_retrieval_with_ingested_chunks(test_db: AsyncSession):
    # Ingest sample transcripts
    await IngestionService.ingest_source(test_db, source="sample", limit=3, force_refresh=True)

    # 1. Search for Casey Winters topic: growth loops and retention
    results = await RetrievalService.retrieve(
        test_db,
        query="Casey Winters growth loops retention curve",
        top_k=2,
    )
    assert len(results) > 0
    top_res = results[0]
    assert top_res.guest in ("Casey Winters", "Elena Verna", "Brian Balfour")
    assert top_res.similarity_score > 0.20
    assert top_res.citation is not None
    assert top_res.citation.episode_title is not None
    assert top_res.citation.guest is not None
    assert top_res.citation.quote_excerpt is not None

    # 2. Out-of-domain query should return 0 results due to threshold
    unrelated_results = await RetrievalService.retrieve(
        test_db,
        query="solana tokenomics liquidity staking yield farming smart contract",
        top_k=3,
        similarity_threshold=0.60,
    )
    assert len(unrelated_results) == 0
