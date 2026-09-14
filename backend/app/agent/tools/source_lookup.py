import logging
from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseAgentTool
from ...models.transcript import TranscriptMetadataModel

logger = logging.getLogger(__name__)


class SourceLookupTool(BaseAgentTool):
    """
    Agent tool to look up verified source metadata for a specific Lenny's Podcast episode.
    """

    name = "lookup_episode_source"
    description = (
        "Lookup verified source metadata for an episode (episode number, guest title, source URL, "
        "audio URL, publication date) from the database."
    )
    parameters = {
        "type": "object",
        "properties": {
            "episode_title_or_guest": {
                "type": "string",
                "description": "The title of the episode or guest name to inspect.",
            },
        },
        "required": ["episode_title_or_guest"],
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, episode_title_or_guest: str, **kwargs: Any) -> Dict[str, Any]:
        """Looks up episode record matching guest or title."""
        logger.info(f"[PiAgentTool:lookup_episode_source] query='{episode_title_or_guest}'")
        try:
            term = f"%{episode_title_or_guest.strip()}%"
            stmt = select(TranscriptMetadataModel).where(
                (TranscriptMetadataModel.episode_title.ilike(term)) |
                (TranscriptMetadataModel.guest.ilike(term))
            ).limit(3)
            result = await self.db.execute(stmt)
            episodes = result.scalars().all()

            if not episodes:
                return {"found": False, "message": f"No episode found matching '{episode_title_or_guest}'."}

            data = []
            for ep in episodes:
                data.append({
                    "episode_number": ep.episode_number,
                    "episode_title": ep.episode_title,
                    "guest": ep.guest,
                    "guest_role": ep.guest_role,
                    "source_url": ep.transcript_url,
                    "transcript_url": ep.transcript_url,
                    "audio_url": ep.audio_url,
                    "publication_date": ep.published_date.isoformat() if ep.published_date else None,
                })

            return {"found": True, "episodes": data}
        except Exception as e:
            logger.error(f"Error in lookup_episode_source: {e}", exc_info=True)
            return {"found": False, "error": str(e)}
