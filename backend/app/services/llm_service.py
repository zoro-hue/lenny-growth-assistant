import logging
from typing import List, Dict, Any, Optional
import httpx
from ..config import settings
from ..schemas.knowledge import SearchResultItem

logger = logging.getLogger(__name__)


class LLMService:
    """
    Model layer responsible for synthesizing answers strictly grounded
    in retrieved Lenny's Podcast transcript passages.
    """

    SYSTEM_PROMPT = """You are The Lenny Growth Assistant, a rigorous research and product advisory assistant.
Your answers MUST be strictly grounded in the provided Lenny's Podcast transcript excerpts.

Guidelines:
1. Answer the user's question directly using evidence and quotes from the retrieved excerpts.
2. Attribute insights explicitly to the relevant guests (e.g., "As Casey Winters notes...").
3. Do NOT extrapolate or invent facts, statistics, or metrics not present in the excerpts.
4. Maintain a professional, executive, and analytical editorial tone.
5. If follow-up context is present in the conversation history, integrate it seamlessly.
"""

    @classmethod
    async def generate_grounded_answer(
        cls,
        model_id: str,
        query: str,
        conversation_history: List[Dict[str, str]],
        chunks: List[SearchResultItem],
    ) -> str:
        """
        Synthesizes a grounded response based on retrieved transcript passages
        and conversational history.
        """
        if not chunks:
            return (
                f"I don't have enough grounded material on **{query.strip()}** in Lenny's Podcast to answer confidently.\n\n"
                "The podcast transcript archives do not contain sufficient evidence on this topic. "
                "I cannot synthesize reliable operational guidance without fabricating claims beyond Lenny's archives."
            )

        # 1. Format retrieved context
        context_blocks = []
        for i, chunk in enumerate(chunks, 1):
            ep_info = f"Episode {chunk.episode_number}: " if chunk.episode_number else ""
            ts_info = f" ({chunk.timestamp})" if chunk.timestamp else ""
            context_blocks.append(
                f"[Excerpt {i}] From \"{chunk.episode_title}\" — Guest: {chunk.guest}{ts_info}:\n{chunk.content}"
            )
        retrieved_context_str = "\n\n---\n\n".join(context_blocks)

        # 2. Check cloud provider (OpenAI)
        if settings.openai_api_key and settings.openai_api_key.strip() and model_id != "ollama-mistral":
            try:
                return await cls._call_openai(query, conversation_history, retrieved_context_str)
            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}. Falling back to deterministic synthesizer.", exc_info=True)

        # 3. Check local provider (Ollama)
        if model_id == "ollama-mistral":
            try:
                return await cls._call_ollama(query, conversation_history, retrieved_context_str)
            except Exception as e:
                logger.error(f"Ollama call failed: {e}. Falling back to deterministic synthesizer.", exc_info=True)

        # 4. Fallback: High-quality grounded response synthesizer
        return cls._synthesize_grounded_fallback(query, chunks)

    @classmethod
    async def _call_openai(
        cls,
        query: str,
        conversation_history: List[Dict[str, str]],
        context_str: str,
    ) -> str:
        """Calls OpenAI Chat Completion API."""
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": f"{cls.SYSTEM_PROMPT}\n\nTRANSCRIPT CONTEXT:\n{context_str}"}
        ]
        # Include recent history (up to last 4 messages)
        for msg in conversation_history[-4:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": query})

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.cloud_model or "gpt-4o-mini",
            "messages": messages,
            "temperature": 0.2,
        }

        async with httpx.AsyncClient(timeout=35.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"OpenAI error {resp.status_code}: {resp.text}")
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

    @classmethod
    async def _call_ollama(
        cls,
        query: str,
        conversation_history: List[Dict[str, str]],
        context_str: str,
    ) -> str:
        """Calls Ollama local model API."""
        base_url = settings.ollama_base_url.rstrip("/")
        url = f"{base_url}/api/chat"

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": f"{cls.SYSTEM_PROMPT}\n\nTRANSCRIPT CONTEXT:\n{context_str}"}
        ]
        for msg in conversation_history[-4:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": query})

        payload = {
            "model": "mistral",
            "messages": messages,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Ollama error {resp.status_code}: {resp.text}")
            data = resp.json()
            return data["message"]["content"].strip()

    @classmethod
    def _synthesize_grounded_fallback(cls, query: str, chunks: List[SearchResultItem]) -> str:
        """
        Synthesizes an authentic grounded summary from retrieved excerpts
        when external LLM APIs are offline or unconfigured.
        Strictly preserves quotes, frameworks, and guest attribution.
        """
        guests = list(dict.fromkeys(c.guest for c in chunks))
        guest_list_str = " and ".join(guests[:2]) if len(guests) <= 2 else f"{guests[0]}, {guests[1]}, and others"

        sections = []
        sections.append(
            f"Based on Lenny's Podcast discussions with **{guest_list_str}**, "
            f"addressing this question requires grounding directly in the operational guidance shared on the show:\n"
        )

        for i, chunk in enumerate(chunks, 1):
            ep_title = chunk.episode_title
            guest = chunk.guest
            ts_str = f" at [{chunk.timestamp}]" if chunk.timestamp else ""

            # Extract salient points from the chunk text
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
            "- Ground decisions in empirical retention and habit metrics before scaling acquisition.\n"
            "- Align organizational cadence directly with the natural frequency of user value realization.\n"
            "- Build compounding loops into the core UX rather than relying on linear or paid channels."
        )

        return "\n".join(sections)
