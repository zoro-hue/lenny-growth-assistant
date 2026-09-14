from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgentTool(ABC):
    """Base class for tools executable by Pi Coding Agent."""

    name: str
    description: str
    parameters: Dict[str, Any]

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute the tool action and return a structured dictionary."""
        pass

    def to_schema(self) -> Dict[str, Any]:
        """Returns the function calling JSON schema compatible with OpenAI and Ollama."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
