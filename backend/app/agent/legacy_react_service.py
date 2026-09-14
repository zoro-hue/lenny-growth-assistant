"""
DEPRECATED: Legacy custom ReAct loop.
This is kept ONLY as an emergency fallback if the official Pi Coding Agent
process is unavailable or disabled. It is NOT the primary agent implementation
and must not be described as Pi.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .agent_config import AgentConfig
from .providers import (
    BaseLLMProvider,
    ProviderManager,
    MissingProviderKeyError,
    ProviderUnavailableError,
)
from .tools.registry import ToolRegistry
from ..schemas.message import CitationSchema
from ..schemas.knowledge import SearchResultItem
from ..config import settings

logger = logging.getLogger(__name__)


class LegacyReActFallbackService:
    """
    Deprecated fallback using a manual while loop over provider.chat.
    NOT the primary agent path. Primary path is AgentService using official Pi Coding Agent.
    """

    @classmethod
    async def run(
        cls,
        db: AsyncSession,
        query: str,
        conversation_history: List[Dict[str, str]],
        model_id: str = "openai-cloud",
        custom_provider: Optional[BaseLLMProvider] = None,
        fallback_enabled: Optional[bool] = None,
    ) -> Any:
        from .agent_service import AgentExecutionResult

        logger.warning("[LegacyReActFallback] Using deprecated custom ReAct loop fallback.")
        config = AgentConfig.from_model_id(model_id)

        try:
            if custom_provider:
                provider = custom_provider
                requested_provider = custom_provider.provider_name
                actual_provider = custom_provider.provider_name
                fallback_reason = None
            else:
                provider, actual_provider, fallback_reason = (
                    await ProviderManager.resolve_provider_with_fallback(
                        model_id=model_id,
                        fallback_enabled=fallback_enabled,
                    )
                )
                requested_provider = config.provider
        except (MissingProviderKeyError, ProviderUnavailableError) as pe:
            return AgentExecutionResult(
                content="",
                status="error",
                citations=[],
                requested_provider=config.provider,
                actual_provider=config.provider,
                error_details={
                    "message": pe.message,
                    "errorCode": pe.error_code,
                    "canSwitchToCloud": pe.details.get("canSwitchToCloud", True) if pe.details else True,
                },
            )

        registry = ToolRegistry(db)
        tool_schemas = registry.get_schemas()
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": config.system_prompt}
        ]
        for h in conversation_history[-6:]:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": query})

        final_content = ""
        iterations = 0
        max_iters = config.max_iterations

        while iterations < max_iters:
            iterations += 1
            content, tool_calls = await provider.chat(
                messages=messages,
                tools=tool_schemas,
                temperature=config.temperature,
            )
            if not tool_calls:
                final_content = content.strip()
                break

            messages.append({
                "role": "assistant",
                "content": content or "",
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"])
                            if isinstance(tc["arguments"], dict)
                            else tc["arguments"],
                        },
                    }
                    for tc in tool_calls
                ],
            })

            for tc in tool_calls:
                tool_name = tc.get("name")
                call_id = tc.get("id") or f"call_{tool_name}"
                args = tc.get("arguments") or {}
                tool_inst = registry.get_tool(tool_name)
                res_dict = await tool_inst.execute(**args) if tool_inst else {"error": "unknown tool"}
                messages.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": tool_name,
                    "content": json.dumps(res_dict),
                })

        retrieved_chunks = registry.search_tool.retrieved_chunks
        if not retrieved_chunks:
            return AgentExecutionResult(
                content=f"I don't have enough grounded material on **{query.strip()}** in Lenny's Podcast to answer confidently.",
                status="low-evidence",
                citations=[],
                requested_provider=requested_provider,
                actual_provider=actual_provider,
                fallback_reason=fallback_reason,
            )

        unique_citations: List[CitationSchema] = []
        seen_chunk_ids = set()
        for chunk in retrieved_chunks:
            if chunk.chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(chunk.chunk_id)
                unique_citations.append(chunk.citation)

        return AgentExecutionResult(
            content=final_content,
            status="complete",
            citations=unique_citations,
            requested_provider=requested_provider,
            actual_provider=actual_provider,
            fallback_reason=fallback_reason,
        )
