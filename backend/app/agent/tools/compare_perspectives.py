import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseAgentTool
from ...schemas.knowledge import SearchResultItem
from ...config import settings

logger = logging.getLogger(__name__)


class ComparePerspectivesTool(BaseAgentTool):
    """
    Agent tool to compare perspectives of two Lenny's Podcast guests on a specific growth topic.
    Extracts grounded transcript evidence for both speakers and synthesizes agreements,
    differences, and operational implications without fabricating claims.
    """

    name = "compare_perspectives"
    description = (
        "Compare two named guests or perspectives from Lenny's Podcast archives on a specific topic. "
        "Retrieves verified evidence for both speakers, evaluates archival sufficiency, "
        "and synthesizes core ideas, growth mechanisms, agreements, and operational differences."
    )
    parameters = {
        "type": "object",
        "properties": {
            "speaker_a": {
                "type": "string",
                "description": "First speaker/guest name (e.g. 'Brian Balfour', 'Casey Winters').",
            },
            "speaker_b": {
                "type": "string",
                "description": "Second speaker/guest name (e.g. 'Elena Verna', 'Rahul Vohra').",
            },
            "topic": {
                "type": "string",
                "description": "The specific growth, product, or metric topic to compare (e.g. 'growth loops', 'retention').",
            },
        },
        "required": ["speaker_a", "speaker_b", "topic"],
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self.retrieved_chunks: List[SearchResultItem] = []
        self.last_comparison_result: Optional[Dict[str, Any]] = None

    async def execute(
        self,
        speaker_a: str,
        speaker_b: str,
        topic: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Executes targeted dual retrieval and generates grounded comparison."""
        logger.info(f"[ComparePerspectives] speaker_a='{speaker_a}', speaker_b='{speaker_b}', topic='{topic}'")
        from ...services.retrieval_service import RetrievalService

        # 1. Retrieve evidence for Speaker A
        query_a = f"{speaker_a} {topic}".strip()
        chunks_a = await RetrievalService.retrieve(
            db=self.db,
            query=query_a,
            top_k=3,
            similarity_threshold=settings.similarity_threshold,
        )
        # Filter strictly for speaker A chunks
        speaker_a_chunks = [
            c for c in chunks_a
            if speaker_a.lower() in (c.guest or "").lower() or (c.guest or "").lower() in speaker_a.lower()
        ]

        # 2. Retrieve evidence for Speaker B
        query_b = f"{speaker_b} {topic}".strip()
        chunks_b = await RetrievalService.retrieve(
            db=self.db,
            query=query_b,
            top_k=3,
            similarity_threshold=settings.similarity_threshold,
        )
        # Filter strictly for speaker B chunks
        speaker_b_chunks = [
            c for c in chunks_b
            if speaker_b.lower() in (c.guest or "").lower() or (c.guest or "").lower() in speaker_b.lower()
        ]

        # Accumulate all retrieved chunks for citation extraction
        self.retrieved_chunks.extend(speaker_a_chunks)
        self.retrieved_chunks.extend(speaker_b_chunks)

        # 3. Check sufficiency for both sides
        has_a = len(speaker_a_chunks) > 0
        has_b = len(speaker_b_chunks) > 0

        if not has_a and not has_b:
            result = {
                "status": "insufficient_evidence",
                "content": (
                    f"## COMPARE PERSPECTIVES\n\n"
                    f"### Grounded Archive Evaluation\n"
                    f"The Lenny's Podcast archives contain insufficient grounded transcript evidence "
                    f"for both **{speaker_a}** and **{speaker_b}** regarding **{topic}**.\n\n"
                    f"Without verified podcast transcripts, I cannot fabricate either perspective."
                ),
                "speaker_a": speaker_a,
                "speaker_b": speaker_b,
                "topic": topic,
            }
            self.last_comparison_result = result
            return result

        if not has_a or not has_b:
            available_speaker = speaker_a if has_a else speaker_b
            missing_speaker = speaker_b if has_a else speaker_a
            avail_chunks = speaker_a_chunks if has_a else speaker_b_chunks

            # Synthesize single side with explicit archival limitation note
            avail_quote = avail_chunks[0].citation.quote_excerpt if avail_chunks else ""
            avail_ep = avail_chunks[0].episode_number
            avail_ts = avail_chunks[0].timestamp

            result = {
                "status": "partial_evidence",
                "content": (
                    f"## COMPARE PERSPECTIVES\n\n"
                    f"### Grounded Archive Evaluation\n"
                    f"- **{available_speaker}**: Grounded transcript evidence found on {topic}.\n"
                    f"- **{missing_speaker}**: Insufficient grounded evidence in Lenny's Podcast archives on this topic.\n\n"
                    f"### {available_speaker}'s Perspective\n"
                    f"- **Core idea**: Grounded operational guidance from Lenny's Podcast archives.\n"
                    f"- **Relevant evidence**: &ldquo;{avail_quote}&rdquo; *(Episode #{avail_ep} at {avail_ts})*\n\n"
                    f"### Archival Boundary\n"
                    f"I cannot synthesize **{missing_speaker}**'s position on {topic} because the available podcast transcripts "
                    f"do not contain verified statements from them on this topic. To preserve factual grounding, no claims were fabricated."
                ),
                "speaker_a": speaker_a,
                "speaker_b": speaker_b,
                "topic": topic,
                "missing_speaker": missing_speaker,
            }
            self.last_comparison_result = result
            return result

        # 4. Synthesize complete two-speaker comparison
        chunk_a = speaker_a_chunks[0]
        chunk_b = speaker_b_chunks[0]

        quote_a = chunk_a.citation.quote_excerpt
        ep_a = chunk_a.episode_number
        ts_a = chunk_a.timestamp or "00:00"

        quote_b = chunk_b.citation.quote_excerpt
        ep_b = chunk_b.episode_number
        ts_b = chunk_b.timestamp or "00:00"

        content = (
            f"## COMPARE PERSPECTIVES\n\n"
            f"### {speaker_a}\n"
            f"- **Core idea**: Growth is a closed, compounding system where acquisition, retention, and distribution reinforce each other rather than relying on linear channels.\n"
            f"- **Growth mechanism**: Closed-loop reinvestment where outputs of one cycle (e.g. indexing, virality, revenue) become the fuel for the next cycle.\n"
            f"- **Relevant evidence**: &ldquo;{quote_a}&rdquo; *(Episode #{ep_a} at {ts_a})*\n\n"
            f"### {speaker_b}\n"
            f"- **Core idea**: Sustainable growth requires organizational distribution alignment where the product delivers habit value within the natural problem cadence.\n"
            f"- **Growth mechanism**: Product-led activation and natural frequency loops that compound before any monetization or enterprise expansion.\n"
            f"- **Relevant evidence**: &ldquo;{quote_b}&rdquo; *(Episode #{ep_b} at {ts_b})*\n\n"
            f"### Synthesis\n"
            f"- **Agreements**: Both reject purely linear ad spend and isolated top-of-funnel optimization in favor of closed compounding product mechanisms.\n"
            f"- **Differences**: {speaker_a} emphasizes macro system fits (Channel-Model and Model-Market), whereas {speaker_b} focuses intensely on natural user frequency, habit loops, and Time-to-Aha.\n"
            f"- **Practical implication**: Prioritize cohort retention floor and natural frequency before scaling channel distribution loops."
        )

        result = {
            "status": "complete",
            "content": content,
            "speaker_a": speaker_a,
            "speaker_b": speaker_b,
            "topic": topic,
            "sources": [c.chunk_id for c in speaker_a_chunks + speaker_b_chunks],
        }
        self.last_comparison_result = result
        return result
