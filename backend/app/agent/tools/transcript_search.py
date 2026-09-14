import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseAgentTool
from ...schemas.knowledge import SearchResultItem
from ...config import settings

logger = logging.getLogger(__name__)


class TranscriptSearchTool(BaseAgentTool):
    """
    Agent tool exposing the semantic RAG knowledge base.
    Allows Pi Coding Agent to search Lenny's Podcast transcripts.
    """

    name = "search_lenny_transcripts"
    description = (
        "Search Lenny's Podcast transcripts for relevant passages, frameworks, and guest insights. "
        "Use this tool whenever answering questions about product management, growth loops, retention, "
        "PLG, B2B SaaS benchmarks, and startup leadership."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The natural language search query or topic to look up in the transcripts.",
            },
            "top_k": {
                "type": "integer",
                "description": "Number of transcript passages to retrieve (default: 3).",
                "default": 3,
            },
        },
        "required": ["query"],
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        # Accumulates chunks across all tool invocations during this turn
        self.retrieved_chunks: List[SearchResultItem] = []

    async def execute(self, query: str, top_k: int = 3, **kwargs: Any) -> Dict[str, Any]:
        """Performs semantic similarity search via RetrievalService."""
        logger.info(f"[PiAgentTool:search_lenny_transcripts] query='{query}', top_k={top_k}")
        try:
            from ...services.retrieval_service import RetrievalService

            chunks = await RetrievalService.retrieve(
                db=self.db,
                query=query.strip(),
                top_k=top_k or settings.retrieval_top_k,
                similarity_threshold=settings.similarity_threshold,
            )
            # Store chunks for citation extraction
            self.retrieved_chunks.extend(chunks)

            results = []
            for c in chunks:
                results.append({
                    "chunk_id": c.chunk_id,
                    "episode_number": c.episode_number,
                    "episode_title": c.episode_title,
                    "guest": c.guest,
                    "guest_role": c.guest_role or "",
                    "timestamp": c.timestamp or "",
                    "content": c.content,
                    "source_url": c.source_url,
                    "similarity": round(c.similarity_score, 4),
                })

            return {"results": results, "count": len(results)}
        except Exception as e:
            logger.error(f"Error executing search_lenny_transcripts tool: {e}", exc_info=True)
            return {"results": [], "count": 0, "error": str(e)}
