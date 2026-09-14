import math
import logging
from typing import List, Optional
from sqlalchemy import select, func, asc
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..models.transcript import TranscriptChunkModel, TranscriptMetadataModel
from ..schemas.knowledge import SearchResultItem
from ..schemas.message import CitationSchema
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


def compute_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes cosine similarity between two float vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a, b in zip(v1, v2)))
    norm2 = math.sqrt(sum(b * b for a, b in zip(v1, v2)))
    if norm1 > 0 and norm2 > 0:
        return dot / (norm1 * norm2)
    return 0.0


class RetrievalService:
    """
    Dedicated semantic search & RAG retrieval service over Lenny's Podcast transcripts.
    """

    @classmethod
    async def retrieve(
        cls,
        db: AsyncSession,
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
    ) -> List[SearchResultItem]:
        """
        Performs semantic similarity search against transcript chunks.
        Returns top_k matching chunks with complete source metadata and citations.
        """
        k = top_k or settings.retrieval_top_k
        threshold = similarity_threshold if similarity_threshold is not None else settings.similarity_threshold

        clean_query = query.strip()
        if not clean_query:
            return []

        # 1. Check if knowledge base is empty
        chunk_count = await db.scalar(select(func.count()).select_from(TranscriptChunkModel))
        if not chunk_count or chunk_count == 0:
            logger.info("Knowledge base is empty. Returning 0 retrieval results.")
            return []

        # 2. Generate embedding for query
        try:
            query_embedding = await EmbeddingService.embed_query(clean_query)
        except Exception as e:
            logger.error(f"Failed to generate embedding for query '{clean_query}': {e}", exc_info=True)
            return []

        # 3. Perform vector retrieval
        results: List[SearchResultItem] = []
        try:
            bind = db.bind or getattr(db, "_bind", None)
            is_postgres = (bind.dialect.name == "postgresql") if bind else False

            if is_postgres:
                results = await cls._search_postgres(db, query_embedding, k, threshold)
            else:
                results = await cls._search_sqlite(db, query_embedding, k, threshold)

        except Exception as ex:
            logger.error(f"Database query error during vector retrieval: {ex}", exc_info=True)
            return []

        logger.info(
            f"Retrieved {len(results)} chunks for query '{clean_query[:50]}' "
            f"(top_k={k}, threshold={threshold})"
        )
        return results

    @classmethod
    async def _search_postgres(
        cls,
        db: AsyncSession,
        query_embedding: List[float],
        top_k: int,
        threshold: float,
    ) -> List[SearchResultItem]:
        """Native PostgreSQL pgvector cosine distance search."""
        distance_col = TranscriptChunkModel.embedding.cosine_distance(query_embedding).label("distance")
        stmt = (
            select(TranscriptChunkModel, distance_col)
            .where(TranscriptChunkModel.embedding.isnot(None))
            .order_by(asc("distance"))
            .limit(top_k * 2)  # fetch buffer to apply similarity threshold
        )
        rows = (await db.execute(stmt)).all()

        results: List[SearchResultItem] = []
        for chunk, dist in rows:
            # Cosine distance = 1.0 - cosine_similarity (for unit vectors)
            similarity = round(1.0 - float(dist), 4)
            if similarity < threshold:
                continue

            item = cls._to_search_result(chunk, similarity)
            results.append(item)
            if len(results) >= top_k:
                break

        return results

    @classmethod
    async def _search_sqlite(
        cls,
        db: AsyncSession,
        query_embedding: List[float],
        top_k: int,
        threshold: float,
    ) -> List[SearchResultItem]:
        """In-memory cosine similarity search for SQLite local/test fallback."""
        stmt = select(TranscriptChunkModel).where(TranscriptChunkModel.embedding.isnot(None))
        chunks = (await db.execute(stmt)).scalars().all()

        scored_chunks = []
        for chunk in chunks:
            if chunk.embedding is not None:
                sim = compute_cosine_similarity(query_embedding, list(chunk.embedding))
                if sim >= threshold:
                    scored_chunks.append((chunk, round(sim, 4)))

        # Sort descending by similarity
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        top_scored = scored_chunks[:top_k]

        return [cls._to_search_result(chunk, sim) for chunk, sim in top_scored]

    @classmethod
    def _to_search_result(cls, chunk: TranscriptChunkModel, similarity: float) -> SearchResultItem:
        """Constructs SearchResultItem and CitationSchema from chunk model."""
        # Extract quote excerpt (first ~220 chars or up to sentence end)
        text = chunk.content.strip()
        lines = [line.strip() for line in text.split("\n") if line.strip() and not line.startswith("#")]
        content_sample = " ".join(lines)
        if len(content_sample) > 220:
            excerpt = content_sample[:217] + "..."
        else:
            excerpt = content_sample

        citation = CitationSchema(
            id=chunk.id,
            episodeNumber=chunk.episode_number,
            episodeTitle=chunk.episode_title,
            guest=chunk.guest,
            guestRole=chunk.guest_role,
            timestamp=chunk.timestamp or "00:00",
            quoteExcerpt=excerpt,
            episodeUrl=chunk.source_url or "https://www.lennyspodcast.com",
            relevanceScore=similarity,
        )

        return SearchResultItem(
            chunkId=chunk.id,
            transcriptId=chunk.transcript_id,
            episodeNumber=chunk.episode_number,
            episodeTitle=chunk.episode_title,
            guest=chunk.guest,
            guestRole=chunk.guest_role,
            sourceUrl=chunk.source_url,
            chunkIndex=chunk.chunk_index,
            timestamp=chunk.timestamp,
            content=chunk.content,
            similarityScore=similarity,
            citation=citation,
        )
