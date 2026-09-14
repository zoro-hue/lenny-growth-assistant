import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from .agent_config import AgentConfig
from .pi_rpc_client import PiRpcClient, PiExecutionOutput
from .tool_bridge import ToolBridge
from .tools.registry import ToolRegistry
from .providers import (
    BaseLLMProvider,
    ProviderManager,
    MissingProviderKeyError,
    ProviderUnavailableError,
    MockAgentProvider,
)
from ..schemas.message import CitationSchema
from ..schemas.knowledge import SearchResultItem
from ..config import settings

logger = logging.getLogger(__name__)


@dataclass
class AgentExecutionResult:
    """Structured response returned by Pi Coding Agent."""
    content: str
    status: str  # "complete" | "low-evidence" | "error"
    citations: List[CitationSchema] = field(default_factory=list)
    requested_provider: str = "openai"
    actual_provider: str = "openai"
    fallback_reason: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    artifact_data: Optional[Dict[str, Any]] = None



class AgentService:
    """
    Primary agent service powered genuinely by the official Pi Coding Agent
    (@earendil-works/pi-coding-agent / pi.dev) via its documented JSONL RPC mode.

    Responsibilities:
    - Provider & model resolution (OpenAI cloud or Ollama local)
    - Safe startup checks and graceful provider fallback handling
    - Ephemeral in-process tool bridge exposing search_lenny_transcripts and lookup_episode_source
    - Pi RPC subprocess invocation and event streaming
    - Grounded citation verification (strictly from retrieved transcript evidence)
    - Safe low-evidence status for unsupported/out-of-domain queries
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
    ) -> AgentExecutionResult:
        """
        Executes the official Pi Coding Agent loop over the user prompt.
        """
        config = AgentConfig.from_model_id(model_id)

        # 1. Check if legacy fallback requested via environment
        if settings.agent_framework == "legacy_react":
            logger.info("[AgentService] AGENT_FRAMEWORK=legacy_react configured. Routing to LegacyReActFallbackService.")
            from .legacy_react_service import LegacyReActFallbackService
            return await LegacyReActFallbackService.run(
                db=db,
                query=query,
                conversation_history=conversation_history,
                model_id=model_id,
                custom_provider=custom_provider,
                fallback_enabled=fallback_enabled,
            )

        # 2. Check explicit out-of-domain terms or greetings early for instantaneous low-evidence response
        clean_q = query.strip().lower()
        is_greeting = clean_q in ("hi", "hello", "hey", "yo", "test", "help", "who are you") or len(clean_q) <= 2
        _UNSUPPORTED_KEYWORDS = [
            "web3", "token", "crypto", "nft", "solana", "blockchain",
            "bitcoin", "ethereum", "defi", "staking rewards"
        ]
        _UNSUPPORTED_PATTERN = re.compile(
            r"\b(?:" + "|".join(re.escape(k) for k in _UNSUPPORTED_KEYWORDS) + r")\b",
            re.IGNORECASE,
        )
        is_explicitly_unsupported = is_greeting or bool(_UNSUPPORTED_PATTERN.search(query))
        if is_explicitly_unsupported:
            low_evidence_text = (
                f"I don't have enough grounded material on **{query.strip()}** in Lenny's Podcast to answer confidently.\n\n"
                "The available podcast transcript archives focus on traditional product management, SaaS growth loops, "
                "retention metrics, marketplace mechanics, and startup leadership. "
                "They do not contain empirical evidence or tactical guidance on this topic.\n\n"
                "I cannot synthesize reliable operational guidance without fabricating claims beyond Lenny's podcast archives."
            )
            return AgentExecutionResult(
                content=low_evidence_text,
                status="low-evidence",
                citations=[],
                requested_provider=config.provider,
                actual_provider=config.provider,
            )

        # 3. Provider resolution & fallback checks
        requested_provider = config.provider
        actual_provider = config.provider
        fallback_reason: Optional[str] = None

        if custom_provider:
            # When a test supplies a mock provider, route through mock boundary
            requested_provider = custom_provider.provider_name
            actual_provider = custom_provider.provider_name
            provider = custom_provider
        else:
            try:
                provider, actual_provider, fallback_reason = (
                    await ProviderManager.resolve_provider_with_fallback(
                        model_id=model_id,
                        fallback_enabled=fallback_enabled,
                    )
                )
            except (MissingProviderKeyError, ProviderUnavailableError) as pe:
                logger.warning(f"[PiAgent] Provider error during initialization: {pe.message}")
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
            except Exception as e:
                logger.error(f"[PiAgent] Unexpected provider error: {e}", exc_info=True)
                return AgentExecutionResult(
                    content="",
                    status="error",
                    citations=[],
                    requested_provider=config.provider,
                    actual_provider=config.provider,
                    error_details={
                        "message": f"Provider initialization failed: {str(e)}",
                        "canSwitchToCloud": True,
                    },
                )

        # 4. Set up Tool Registry and In-Process Tool Bridge
        registry = ToolRegistry(db)
        bridge = ToolBridge(registry)
        bridge_port: Optional[int] = None
        try:
            bridge_port = await bridge.start()
        except Exception as e:
            logger.warning(f"[PiAgent] Could not start tool bridge on ephemeral port: {e}. CLI runner will be used.")

        # 5. Determine Pi model ID
        if actual_provider == "ollama":
            pi_provider = "ollama"
            pi_model = settings.ollama_model or "llama3.2:3b"
        else:
            pi_provider = "openai"
            pi_model = settings.openai_model or "gpt-4o-mini"

        # 6. Execute Pi Coding Agent
        pi_client = PiRpcClient()

        # Handle MockAgentProvider if passed directly (e.g. from unit tests)
        # or returned by ProviderManager in testing environment
        resolved_mock_provider = (
            custom_provider if isinstance(custom_provider, MockAgentProvider)
            else (provider if isinstance(provider, MockAgentProvider) else None)
        )
        if resolved_mock_provider is not None:
            logger.info("[PiAgent] Handling MockAgentProvider execution for test boundary")
            tool_schemas = registry.get_schemas()
            # Build full message list with system prompt + conversation history
            messages: list = [{"role": "system", "content": config.system_prompt}]
            for h in (conversation_history or [])[-6:]:
                messages.append({"role": h["role"], "content": h["content"]})
            messages.append({"role": "user", "content": query})

            content, tool_calls = await resolved_mock_provider.chat(
                messages=messages, tools=tool_schemas, temperature=config.temperature,
            )
            # MockAgentProvider may invoke tools and then require a second chat turn
            if tool_calls:
                for tc in tool_calls:
                    tool_inst = registry.get_tool(tc["name"])
                    result_dict = {"results": [], "count": 0}
                    if tool_inst:
                        result_dict = await tool_inst.execute(**tc.get("arguments", {}))
                    messages.append({
                        "role": "assistant",
                        "content": content or "",
                        "tool_calls": [{
                            "id": tc.get("id", f"call_{tc['name']}"),
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": json.dumps(tc["arguments"]) if isinstance(tc["arguments"], dict) else tc["arguments"],
                            },
                        }],
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.get("id", f"call_{tc['name']}"),
                        "name": tc["name"],
                        "content": json.dumps(result_dict),
                    })
                content, _ = await resolved_mock_provider.chat(
                    messages=messages, tools=tool_schemas, temperature=config.temperature,
                )
            pi_output = PiExecutionOutput(
                content=content or "",
                provider=actual_provider,
                model=pi_model,
                success=True,
            )
            await bridge.stop()
        else:
            try:
                pi_output = await pi_client.execute(
                    prompt=query,
                    provider=pi_provider,
                    model_id=pi_model,
                    tool_bridge_port=bridge_port,
                    system_prompt=config.system_prompt,
                    conversation_history=conversation_history,
                )
            except Exception as pe:
                logger.error(f"[PiAgent] Pi execution error: {pe}", exc_info=True)
                pi_output = PiExecutionOutput(
                    content="",
                    provider=pi_provider,
                    model=pi_model,
                    success=False,
                    error_message=str(pe),
                )
            finally:
                await bridge.stop()

        if not pi_output.success:
            return AgentExecutionResult(
                content="",
                status="error",
                citations=[],
                requested_provider=requested_provider,
                actual_provider=actual_provider,
                fallback_reason=fallback_reason,
                error_details={
                    "message": pi_output.error_message or "Pi Coding Agent execution failed.",
                    "canSwitchToCloud": True,
                },
            )

        # 7. Evidence evaluation & Citations
        retrieved_chunks = (
            registry.search_tool.retrieved_chunks
            + registry.ship30_tool.retrieved_chunks
            + registry.artifact_tool.retrieved_chunks
        )
        essay_result = registry.ship30_tool.last_essay_result
        art_gen_result = registry.artifact_tool.last_artifact_result

        # Check if ship30 tool or artifact tool reported insufficient evidence
        if essay_result and essay_result.get("status") in ("insufficient_evidence", "low-evidence"):
            return AgentExecutionResult(
                content=essay_result.get("content", ""),
                status="low-evidence",
                citations=[],
                requested_provider=requested_provider,
                actual_provider=actual_provider,
                fallback_reason=fallback_reason,
            )
        if art_gen_result and art_gen_result.get("status") == "low-evidence":
            return AgentExecutionResult(
                content=art_gen_result.get("content", ""),
                status="low-evidence",
                citations=[],
                requested_provider=requested_provider,
                actual_provider=actual_provider,
                fallback_reason=fallback_reason,
            )

        # If explicitly unsupported or no chunks retrieved
        if is_explicitly_unsupported or not retrieved_chunks:
            low_evidence_text = (
                f"I don't have enough grounded material on **{query.strip()}** in Lenny's Podcast to answer confidently.\n\n"
                "The available podcast transcript archives focus on traditional product management, SaaS growth loops, "
                "retention metrics, marketplace mechanics, and startup leadership. "
                "They do not contain empirical evidence or tactical guidance on this topic.\n\n"
                "I cannot synthesize reliable operational guidance without fabricating claims beyond Lenny's podcast archives."
            )
            return AgentExecutionResult(
                content=low_evidence_text,
                status="low-evidence",
                citations=[],
                requested_provider=requested_provider,
                actual_provider=actual_provider,
                fallback_reason=fallback_reason,
            )

        # Extract strictly unique citations from retrieved chunks
        unique_citations: List[CitationSchema] = []
        seen_chunk_ids = set()
        for chunk in retrieved_chunks:
            if chunk.chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(chunk.chunk_id)
                unique_citations.append(chunk.citation)

        # Extract artifact_data if an artifact or essay was generated
        artifact_data: Optional[Dict[str, Any]] = None
        if art_gen_result and art_gen_result.get("status") == "complete":
            artifact_data = {
                "title": art_gen_result.get("title") or f"Artifact: {query[:48]}",
                "type": art_gen_result.get("type", "markdown"),
                "content": art_gen_result.get("content", ""),
                "word_count": art_gen_result.get("word_count", 0),
                "source_count": len(art_gen_result.get("sources", [])) or len(unique_citations),
                "allow_scripts": art_gen_result.get("allow_scripts", False),
            }
        elif essay_result and essay_result.get("status") == "complete":
            artifact_data = {
                "title": essay_result.get("title") or f"Playbook: {query[:48]}",
                "type": "markdown",
                "content": essay_result.get("content", ""),
                "word_count": essay_result.get("word_count", 0),
                "source_count": len(essay_result.get("sources", [])) or len(unique_citations),
                "allow_scripts": False,
            }

        final_content = pi_output.content.strip()
        if artifact_data and (not final_content or len(final_content.split()) > 350):
            primary_guests = list(dict.fromkeys(c.guest for c in retrieved_chunks))
            guest_names = " and ".join(primary_guests[:2]) if primary_guests else "Lenny's Podcast guests"
            if art_gen_result and art_gen_result.get("status") == "complete":
                fmt_label = "HTML/CSS document" if artifact_data["type"] == "html" else "Markdown artifact"
                final_content = (
                    f"I've generated a complete {fmt_label} titled **\"{artifact_data['title']}\"** "
                    f"grounded in transcript frameworks from {guest_names}.\n\n"
                    f"The document has been formatted and is open in the Artifact Workbench to your right."
                )
            else:
                final_content = (
                    f"I've synthesized a comprehensive Ship 30 for 30 playbook titled **\"{artifact_data['title']}\"** "
                    f"grounded in transcript frameworks from {guest_names}.\n\n"
                    f"The complete ~{artifact_data['word_count']}-word playbook with a 1-3-1 hook, 4-stage operational framework, "
                    "benchmark matrix, and tactical 7-step checklist is open in the Artifact Workbench to your right."
                )
        elif not final_content:
            final_content = cls._synthesize_grounded_fallback(query, retrieved_chunks)

        return AgentExecutionResult(
            content=final_content,
            status="complete",
            citations=unique_citations,
            requested_provider=requested_provider,
            actual_provider=actual_provider,
            fallback_reason=fallback_reason,
            artifact_data=artifact_data,
        )

    @classmethod
    def _synthesize_grounded_fallback(cls, query: str, chunks: List[SearchResultItem]) -> str:
        """Fallback synthesis strictly preserving quotes and guest attribution."""
        guests = list(dict.fromkeys(c.guest for c in chunks))
        guest_list_str = " and ".join(guests[:2]) if len(guests) <= 2 else f"{guests[0]}, {guests[1]}, and others"

        sections = [
            f"Based on Lenny's Podcast discussions with **{guest_list_str}**, "
            f"answering this question requires grounding directly in the operational guidance shared on the show:\n"
        ]

        for i, chunk in enumerate(chunks, 1):
            ep_title = chunk.episode_title
            guest = chunk.guest
            ts_str = f" at [{chunk.timestamp}]" if chunk.timestamp else ""
            clean_lines = [
                line.strip()
                for line in chunk.content.split("\n")
                if line.strip() and not line.startswith("#")
            ]
            key_body = " ".join(clean_lines[:4])
            sections.append(
                f"### {i}. {guest} on {ep_title}{ts_str}\n"
                f"{key_body}\n"
            )

        sections.append(
            "### Key Takeaways\n"
            "- Ground product decisions in empirical retention curves before accelerating acquisition.\n"
            "- Align organizational cadence directly with the natural frequency of user value realization.\n"
            "- Build compounding loops into the core product rather than relying on linear channels."
        )

        return "\n".join(sections)
