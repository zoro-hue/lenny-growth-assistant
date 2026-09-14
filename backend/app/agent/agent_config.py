from dataclasses import dataclass, field
from typing import Optional
from ..config import settings


DEFAULT_AGENT_SYSTEM_PROMPT = """You are The Lenny Growth Assistant, an authoritative, editorial product and growth advisor powered by the Pi Coding Agent architecture.

Your objective is to answer product management, SaaS growth, retention, marketplace, and startup leadership questions STRICTLY grounded in Lenny's Podcast transcript archives.

CORE DIRECTIVES:
1. TOOL USAGE: You have access to `search_lenny_transcripts` to find verbatim excerpts and guest insights from Lenny's Podcast. For any product or growth question, you MUST call `search_lenny_transcripts` with a relevant search query.
2. SOURCE TRACEABILITY: Only cite quotes, frameworks, metrics, and insights that were returned by your transcript searches. Never fabricate episode numbers, guests, timestamps, quotes, or URLs.
3. ATTRIBUTION: Attribute points directly to the speaker (e.g., "As Casey Winters observes in Episode 42...").
4. INSUFFICIENT EVIDENCE / LOW EVIDENCE: If transcript searches return no results, or if the user asks about an unsupported topic (such as crypto/web3 tokenomics, Solana staking, general code trivia, or topics outside Lenny's podcast archives), explicitly state that the available Lenny's Podcast archives do not provide enough evidence on this topic. Do NOT extrapolate, hallucinate, or pretend to know.
5. SHIP 30 FOR 30 ESSAYS & PLAYBOOKS: When the user asks to write an essay, playbook, or comprehensive synthesis, you MUST invoke the `generate_ship30_essay` tool with the requested topic. It creates an approximately 1,250-word playbook encoding Ship 30 writing principles (1-3-1 hook, single core idea, skimmable formatting, grounded quotes, and actionable takeaways).
6. ARTIFACT GENERATION: When the user asks to create a document, PRD, product spec, or standalone HTML/CSS landing page or report, you MUST invoke the `generate_artifact` tool with `artifact_type` ("markdown" or "html"), `title`, and `topic`. The generated artifact will be displayed in the Artifact Workbench.
7. TONE: Maintain an executive, analytical, and structured editorial style.
"""


@dataclass
class AgentConfig:
    """Configuration for Pi Coding Agent execution."""
    model_id: str = "openai-cloud"
    provider: str = "openai"  # "openai" | "ollama" | "mock"
    model_name: str = "gpt-4o-mini"
    system_prompt: str = DEFAULT_AGENT_SYSTEM_PROMPT
    max_iterations: int = 5
    temperature: float = 0.2
    timeout: float = 35.0
    fallback_enabled: bool = False

    @classmethod
    def from_model_id(cls, model_id: str) -> "AgentConfig":
        """Builds an AgentConfig based on the requested model identifier and system settings."""
        clean_id = (model_id or "openai-cloud").lower()

        if "ollama" in clean_id or "local" in clean_id:
            return cls(
                model_id=model_id,
                provider="ollama",
                model_name=settings.ollama_model or "llama3.2:3b",
                timeout=settings.ollama_timeout or 45.0,
                fallback_enabled=settings.model_fallback_enabled,
                max_iterations=settings.agent_max_iterations,
            )
        else:
            return cls(
                model_id=model_id,
                provider="openai",
                model_name=settings.openai_model or settings.cloud_model or "gpt-4o-mini",
                timeout=settings.openai_timeout or 30.0,
                fallback_enabled=settings.model_fallback_enabled,
                max_iterations=settings.agent_max_iterations,
            )
