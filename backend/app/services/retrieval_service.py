import math
import logging
from typing import List, Optional
from sqlalchemy import select, func, asc
from sqlalchemy.orm import selectinload
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

        # 2. Extract targeted entities (speakers, episode number) from query
        targets = cls.extract_query_targets(clean_query)

        # 3. Generate embedding for query
        try:
            query_embedding = await EmbeddingService.embed_query(clean_query)
        except Exception as e:
            logger.error(f"Failed to generate embedding for query '{clean_query}': {e}", exc_info=True)
            return []

        # 4. Perform vector retrieval with speaker/relevance-aware ranking
        results: List[SearchResultItem] = []
        try:
            bind = db.bind or getattr(db, "_bind", None)
            is_postgres = (bind.dialect.name == "postgresql") if bind else False

            if is_postgres:
                results = await cls._search_postgres(db, query_embedding, k, threshold, targets)
            else:
                results = await cls._search_sqlite(db, query_embedding, k, threshold, targets)

        except Exception as ex:
            logger.error(f"Database query error during vector retrieval: {ex}", exc_info=True)
            return []

        logger.info(
            f"Retrieved {len(results)} chunks for query '{clean_query[:50]}' "
            f"(targets={targets}, top_k={k}, threshold={threshold})"
        )
        return results

    @classmethod
    def extract_query_targets(cls, query: str) -> Dict[str, Any]:
        """Detects explicitly mentioned speakers and episode numbers in the query."""
        import re

        # Episode number matching: "episode 112", "#112", "ep. 42"
        ep_num: Optional[int] = None
        ep_match = re.search(r'(?:episode|ep\.?)\s*#?\s*(\d+)|#(\d+)', query, re.IGNORECASE)
        if ep_match:
            ep_num = int(ep_match.group(1) or ep_match.group(2))

        # Known guests in Lenny's Podcast archives
        known_guests = [
            "Brian Balfour",
            "Casey Winters",
            "Elena Verna",
            "Shreyas Doshi",
            "Rahul Vohra",
        ]
        detected_speakers = []
        q_lower = query.lower()
        for guest in known_guests:
            parts = guest.lower().split()
            # Match full name or surname (if >= 4 letters)
            if guest.lower() in q_lower or (len(parts) > 1 and parts[-1] in q_lower):
                detected_speakers.append(guest)

        return {
            "episode_number": ep_num,
            "speakers": detected_speakers,
        }

    @classmethod
    async def _search_postgres(
        cls,
        db: AsyncSession,
        query_embedding: List[float],
        top_k: int,
        threshold: float,
        targets: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResultItem]:
        """Native PostgreSQL pgvector cosine distance search with speaker-aware reranking."""
        distance_col = TranscriptChunkModel.embedding.cosine_distance(query_embedding).label("distance")
        stmt = (
            select(TranscriptChunkModel, distance_col)
            .options(selectinload(TranscriptChunkModel.transcript))
            .where(TranscriptChunkModel.embedding.isnot(None))
            .order_by(asc("distance"))
            .limit(top_k * 3)  # fetch broader candidate buffer for reranking
        )
        rows = (await db.execute(stmt)).all()

        target_speakers = [s.lower() for s in (targets.get("speakers") if targets else [])]
        target_ep = targets.get("episode_number") if targets else None

        candidates = []
        for chunk, dist in rows:
            similarity = round(1.0 - float(dist), 4)
            if similarity < threshold:
                continue

            guest_lower = (chunk.guest or "").lower()
            speaker_match = any(ts in guest_lower or guest_lower in ts for ts in target_speakers)
            ep_match = (target_ep is not None and chunk.episode_number == target_ep)

            candidates.append((chunk, similarity, speaker_match, ep_match))

        # Sort: priority to speaker_match, then episode_match, then similarity descending
        candidates.sort(key=lambda x: (1 if x[2] else 0, 1 if x[3] else 0, x[1]), reverse=True)
        top_scored = candidates[:top_k]

        return [cls._to_search_result(c, sim, targets) for c, sim, _, _ in top_scored]

    @classmethod
    async def _search_sqlite(
        cls,
        db: AsyncSession,
        query_embedding: List[float],
        top_k: int,
        threshold: float,
        targets: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResultItem]:
        """In-memory cosine similarity search with speaker-aware reranking for SQLite."""
        stmt = (
            select(TranscriptChunkModel)
            .options(selectinload(TranscriptChunkModel.transcript))
            .where(TranscriptChunkModel.embedding.isnot(None))
        )
        chunks = (await db.execute(stmt)).scalars().all()

        target_speakers = [s.lower() for s in (targets.get("speakers") if targets else [])]
        target_ep = targets.get("episode_number") if targets else None

        candidates = []
        for chunk in chunks:
            if chunk.embedding is not None:
                sim = compute_cosine_similarity(query_embedding, list(chunk.embedding))
                if sim >= threshold:
                    guest_lower = (chunk.guest or "").lower()
                    speaker_match = any(ts in guest_lower or guest_lower in ts for ts in target_speakers)
                    ep_match = (target_ep is not None and chunk.episode_number == target_ep)
                    candidates.append((chunk, round(sim, 4), speaker_match, ep_match))

        # Priority to speaker_match, then episode_match, then similarity descending
        candidates.sort(key=lambda x: (1 if x[2] else 0, 1 if x[3] else 0, x[1]), reverse=True)
        top_scored = candidates[:top_k]

        return [cls._to_search_result(chunk, sim, targets) for chunk, sim, _, _ in top_scored]

    @classmethod
    def _to_search_result(
        cls,
        chunk: TranscriptChunkModel,
        similarity: float,
        targets: Optional[Dict[str, Any]] = None,
    ) -> SearchResultItem:
        """Constructs SearchResultItem and CitationSchema with why_this_source from chunk model."""
        # Extract quote excerpt (first ~220 chars or up to sentence end)
        text = chunk.content.strip()
        lines = [line.strip() for line in text.split("\n") if line.strip() and not line.startswith("#")]
        content_sample = " ".join(lines)
        if len(content_sample) > 220:
            excerpt = content_sample[:217] + "..."
        else:
            excerpt = content_sample

        # Prefer audio_url (YouTube) over transcript_url
        episode_url = chunk.source_url or ""
        if hasattr(chunk, 'transcript') and chunk.transcript and chunk.transcript.audio_url:
            episode_url = chunk.transcript.audio_url
        if not episode_url:
            episode_url = "https://www.lennyspodcast.com"

        # Generate contextual "Why this source?" explanation
        target_speakers = targets.get("speakers", []) if targets else []
        target_ep = targets.get("episode_number") if targets else None

        guest_lower = (chunk.guest or "").lower()
        is_speaker_target = any(ts.lower() in guest_lower or guest_lower in ts.lower() for ts in target_speakers)
        is_ep_target = (target_ep is not None and chunk.episode_number == target_ep)

        if is_speaker_target:
            why_source = f"Direct evidence from {chunk.guest} supporting the core argument."
        elif is_ep_target:
            why_source = f"Relevant transcript evidence from Episode #{chunk.episode_number}."
        else:
            topic = chunk.episode_title.split("on ")[-1] if "on " in chunk.episode_title else chunk.episode_title
            why_source = f"Relevant archive framework on {topic}."

        citation = CitationSchema(
            id=chunk.id,
            episodeNumber=chunk.episode_number,
            episodeTitle=chunk.episode_title,
            guest=chunk.guest,
            guestRole=chunk.guest_role,
            timestamp=chunk.timestamp or "00:00",
            quoteExcerpt=excerpt,
            episodeUrl=episode_url,
            relevanceScore=similarity,
            whyThisSource=why_source,
        )

        return SearchResultItem(
            chunkId=chunk.id,
            transcriptId=chunk.transcript_id,
            episodeNumber=chunk.episode_number,
            episodeTitle=chunk.episode_title,
            guest=chunk.guest,
            guestRole=chunk.guest_role,
            sourceUrl=episode_url,
            chunkIndex=chunk.chunk_index,
            timestamp=chunk.timestamp,
            content=chunk.content,
            similarityScore=similarity,
            citation=citation,
        )
