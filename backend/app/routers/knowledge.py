import logging
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..models.transcript import TranscriptMetadataModel, TranscriptChunkModel
from ..schemas.knowledge import (
    IngestRequest,
    IngestResponse,
    KnowledgeStatsResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from ..services.ingestion_service import IngestionService
from ..services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_200_OK)
async def ingest_transcripts(
    request: IngestRequest = IngestRequest(),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers transcript ingestion from local files or curated archives.
    Idempotent: skips duplicate episodes unless forceRefresh=True.
    """
    return await IngestionService.ingest_source(
        db=db,
        source=request.source or "sample",
        limit=request.limit,
        force_refresh=request.force_refresh or False,
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
    )


@router.get("/stats", response_model=KnowledgeStatsResponse, status_code=status.HTTP_200_OK)
async def get_knowledge_stats(
    db: AsyncSession = Depends(get_db),
):
    """
    Returns knowledge base statistics, counts of episodes and chunks, and top guests.
    """
    total_episodes = await db.scalar(select(func.count()).select_from(TranscriptMetadataModel)) or 0
    total_chunks = await db.scalar(select(func.count()).select_from(TranscriptChunkModel)) or 0

    # Top guests by chunk count
    guest_stmt = (
        select(
            TranscriptChunkModel.guest,
            func.count(TranscriptChunkModel.id).label("chunk_count"),
            func.count(func.distinct(TranscriptChunkModel.transcript_id)).label("episode_count"),
        )
        .group_by(TranscriptChunkModel.guest)
        .order_by(desc("chunk_count"))
        .limit(10)
    )
    guest_rows = (await db.execute(guest_stmt)).all()
    top_guests = [
        {"guest": row.guest, "chunkCount": row.chunk_count, "episodeCount": row.episode_count}
        for row in guest_rows
    ]

    # Last ingested timestamp
    last_ingested = await db.scalar(select(func.max(TranscriptMetadataModel.created_at)))
    last_ingested_str = last_ingested.isoformat() if last_ingested else None

    bind = db.bind or getattr(db, "_bind", None)
    dialect_name = bind.dialect.name if bind else "unknown"

    return KnowledgeStatsResponse(
        totalEpisodes=total_episodes,
        totalChunks=total_chunks,
        embeddingModel=settings.embedding_model,
        embeddingDimensions=settings.embedding_dimensions,
        databaseEngine=dialect_name,
        lastIngestedAt=last_ingested_str,
        topGuests=top_guests,
    )


@router.post("/search", response_model=KnowledgeSearchResponse, status_code=status.HTTP_200_OK)
async def search_knowledge(
    request: KnowledgeSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Performs semantic vector similarity search against ingested transcript passages.
    Returns matched chunks with source metadata and citations.
    """
    results = await RetrievalService.retrieve(
        db=db,
        query=request.query,
        top_k=request.top_k,
        similarity_threshold=request.similarity_threshold,
    )
    return KnowledgeSearchResponse(
        query=request.query,
        totalResults=len(results),
        results=results,
    )
