import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseAgentTool
from .transcript_search import TranscriptSearchTool
from .source_lookup import SourceLookupTool
from .ship30_essay import Ship30EssayTool
from .artifact_generator import ArtifactGeneratorTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry of tools accessible to the Pi Coding Agent.
    Manages tool lifecycle, schema generation, and execution dispatch.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.search_tool = TranscriptSearchTool(db)
        self.lookup_tool = SourceLookupTool(db)
        self.ship30_tool = Ship30EssayTool(db)
        self.artifact_tool = ArtifactGeneratorTool(db)
        self._tools: Dict[str, BaseAgentTool] = {
            self.search_tool.name: self.search_tool,
            self.lookup_tool.name: self.lookup_tool,
            self.ship30_tool.name: self.ship30_tool,
            self.artifact_tool.name: self.artifact_tool,
        }

    def get_tool(self, name: str) -> Optional[BaseAgentTool]:
        """Look up a tool by its unique function name."""
        return self._tools.get(name)

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Return the list of tool definitions formatted as function schemas."""
        return [tool.to_schema() for tool in self._tools.values()]

    @property
    def tools(self) -> Dict[str, BaseAgentTool]:
        return self._tools
