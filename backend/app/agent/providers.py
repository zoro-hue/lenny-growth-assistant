import os
import json
import logging
import socket
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import httpx

from ..config import settings
from ..errors import AppError

logger = logging.getLogger(__name__)


class ProviderError(AppError):
    """Base error for LLM provider failures."""
    def __init__(self, message: str, provider: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=f"PROVIDER_{provider.upper()}_ERROR",
            status_code=503,
            details={"provider": provider, **(details or {})},
        )
        self.provider = provider
        self.error_code = f"PROVIDER_{provider.upper()}_ERROR"


class MissingProviderKeyError(ProviderError):
    def __init__(self, provider: str = "openai"):
        super().__init__(
            message=f"{provider.upper()} API key is missing. Please set {provider.upper()}_API_KEY in backend/.env or switch to Local Ollama.",
            provider=provider,
            details={"canSwitchToLocal": True},
        )
        self.status_code = 400


class ProviderUnavailableError(ProviderError):
    def __init__(self, provider: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Could not reach {provider} provider: {reason}",
            provider=provider,
            details=details,
        )


class BaseLLMProvider(ABC):
    """Abstract base provider for Pi Coding Agent."""

    provider_name: str

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is available and ready for inference."""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Sends messages and tools to the provider.
        Returns: (text_content, tool_calls_list)
        tool_call format: [{"id": str, "name": str, "arguments": dict}]
        """
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Cloud Provider implementation."""

    provider_name = "openai"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, timeout: Optional[float] = None):
        raw_key = api_key if api_key is not None else (settings.openai_api_key or "")
        self.api_key = raw_key.strip().replace("\r", "").replace("\n", "") if isinstance(raw_key, str) else ""
        self.model = model or settings.openai_model or settings.cloud_model or "gpt-4o-mini"
        self.timeout = timeout or settings.openai_timeout or 30.0

    async def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        if not await self.is_available():
            raise MissingProviderKeyError(provider="openai")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code != 200:
                    raise ProviderError(
                        message=f"OpenAI error {resp.status_code}: {resp.text}",
                        provider="openai",
                        details={"status_code": resp.status_code, "response": resp.text},
                    )
                data = resp.json()
                choice = data["choices"][0]["message"]
                content = choice.get("content") or ""
                raw_calls = choice.get("tool_calls") or []

                parsed_calls = []
                for call in raw_calls:
                    fn = call.get("function", {})
                    args_raw = fn.get("arguments", {})
                    args_dict = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
                    parsed_calls.append({
                        "id": call.get("id") or f"call_{fn.get('name')}",
                        "name": fn.get("name"),
                        "arguments": args_dict,
                    })

                return content, parsed_calls
        except (MissingProviderKeyError, ProviderError):
            raise
        except Exception as e:
            logger.error(f"OpenAI chat request failed: {e}", exc_info=True)
            raise ProviderUnavailableError(
                provider="openai",
                reason=str(e),
                details={"model": self.model},
            )


class OllamaProvider(BaseLLMProvider):
    """Local Ollama Provider implementation."""

    provider_name = "ollama"

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None, timeout: Optional[float] = None):
        self.base_url = (base_url or settings.ollama_base_url or "http://localhost:11434").rstrip("/")
        self.model = model or settings.ollama_model or "llama3.2:3b"
        self.timeout = timeout or settings.ollama_timeout or 45.0

    async def is_available(self) -> bool:
        """Fast TCP check to verify Ollama server is listening."""
        try:
            # Parse host and port from base_url
            import urllib.parse
            parsed = urllib.parse.urlparse(self.base_url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 11434
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except Exception:
            return False

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        if not await self.is_available():
            raise ProviderUnavailableError(
                provider="ollama",
                reason=f"Couldn't reach local Ollama on {self.base_url}. Please make sure Ollama is running.",
                details={"canSwitchToCloud": True, "baseUrl": self.base_url},
            )

        # Ollama expects function arguments in assistant tool_calls to be dicts, not JSON strings
        formatted_messages = []
        for m in messages:
            if m.get("role") == "assistant" and m.get("tool_calls"):
                norm_tool_calls = []
                for tc in m["tool_calls"]:
                    fn = tc.get("function", {})
                    raw_args = fn.get("arguments", {})
                    parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    norm_tool_calls.append({
                        "id": tc.get("id"),
                        "type": tc.get("type", "function"),
                        "function": {
                            "name": fn.get("name"),
                            "arguments": parsed_args if isinstance(parsed_args, dict) else {},
                        },
                    })
                formatted_messages.append({
                    "role": "assistant",
                    "content": m.get("content", ""),
                    "tool_calls": norm_tool_calls,
                })
            else:
                formatted_messages.append(m)

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }
        if tools:
            payload["tools"] = tools

        url = f"{self.base_url}/api/chat"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code != 200:
                    raise ProviderError(
                        message=f"Ollama error {resp.status_code}: {resp.text}",
                        provider="ollama",
                        details={"status_code": resp.status_code, "response": resp.text},
                    )
                data = resp.json()
                msg = data.get("message", {})
                content = msg.get("content") or ""
                raw_calls = msg.get("tool_calls") or []

                parsed_calls = []
                for call in raw_calls:
                    fn = call.get("function", {})
                    args_raw = fn.get("arguments", {})
                    args_dict = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
                    call_id = call.get("id") or f"call_{fn.get('name')}"
                    parsed_calls.append({
                        "id": call_id,
                        "name": fn.get("name"),
                        "arguments": args_dict,
                    })

                return content, parsed_calls
        except (ProviderError, ProviderUnavailableError):
            raise
        except Exception as e:
            logger.error(f"Ollama chat request failed: {e}", exc_info=True)
            raise ProviderUnavailableError(
                provider="ollama",
                reason=str(e),
                details={"baseUrl": self.base_url, "model": self.model},
            )


class MockAgentProvider(BaseLLMProvider):
    """
    Deterministic Mock Provider for unit testing and offline development.
    Simulates tool calling and final response synthesis without external network calls.
    """

    provider_name = "mock"

    def __init__(self, should_call_tool: bool = True, custom_reply: Optional[str] = None):
        self.should_call_tool = should_call_tool
        self.custom_reply = custom_reply
        self._turn_count = 0

    async def is_available(self) -> bool:
        return True

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        self._turn_count += 1
        # Turn 1: If tools provided and not called yet, invoke appropriate tool
        has_tool_results = any(m.get("role") == "tool" for m in messages)
        if self.should_call_tool and not has_tool_results and tools:
            # Extract last user query
            last_user = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "user"), "")
            tool_names = [t.get("function", {}).get("name") for t in tools]
            lower_user = last_user.lower()
            if ("artifact" in lower_user or "prd" in lower_user or "landing page" in lower_user or "html" in lower_user or "spec" in lower_user or "document" in lower_user) and "generate_artifact" in tool_names:
                art_type = "html" if ("html" in lower_user or "landing page" in lower_user) else "markdown"
                return "", [{
                    "id": "mock_call_artifact",
                    "name": "generate_artifact",
                    "arguments": {
                        "title": f"Artifact: {last_user[:36]}",
                        "topic": last_user,
                        "artifact_type": art_type,
                    },
                }]
            elif ("essay" in lower_user or "playbook" in lower_user or "ship 30" in lower_user) and "generate_ship30_essay" in tool_names:
                return "", [{
                    "id": "mock_call_ship30",
                    "name": "generate_ship30_essay",
                    "arguments": {"topic": last_user},
                }]
            elif "compare" in lower_user and "compare_perspectives" in tool_names:
                known = ["Brian Balfour", "Elena Verna", "Casey Winters", "Shreyas Doshi", "Rahul Vohra"]
                found_speakers = [g for g in known if g.lower() in lower_user or g.split()[-1].lower() in lower_user]
                spk_a = found_speakers[0] if len(found_speakers) > 0 else "Brian Balfour"
                spk_b = found_speakers[1] if len(found_speakers) > 1 else "Elena Verna"
                topic_match = last_user
                if " on " in lower_user:
                    topic_match = last_user.split(" on ")[-1].strip()
                elif " about " in lower_user:
                    topic_match = last_user.split(" about ")[-1].strip()
                return "", [{
                    "id": "mock_call_compare",
                    "name": "compare_perspectives",
                    "arguments": {
                        "speaker_a": spk_a,
                        "speaker_b": spk_b,
                        "topic": topic_match,
                    },
                }]
            return "", [{
                "id": "mock_call_search",
                "name": "search_lenny_transcripts",
                "arguments": {"query": last_user, "top_k": 3},
            }]

        # Turn 2: Synthesize final answer based on tool outputs
        if self.custom_reply:
            return self.custom_reply, []

        last_tool_msg = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "tool"), "")
        try:
            tool_data = json.loads(last_tool_msg) if last_tool_msg else {}
            if "status" in tool_data and "speaker_a" in tool_data and "content" in tool_data:
                return tool_data["content"], []
            if "content" in tool_data and "word_count" in tool_data:
                return tool_data["content"], []
            results = tool_data.get("results", [])
        except Exception:
            results = []

        if not results:
            return (
                "I don't have enough grounded material in Lenny's Podcast to answer confidently. "
                "The available podcast transcript archives do not contain sufficient evidence on this topic.",
                [],
            )

        guest = results[0].get("guest", "the guest")
        ep_title = results[0].get("episode_title", "the episode")
        return (
            f"Based on Lenny's Podcast discussion with **{guest}** in *{ep_title}*, "
            f"product-market fit and retention curves require establishing a flat cohort asymptote. "
            f"As {guest} explains, nothing else matters if your retention curve does not flatten.",
            [],
        )


class ProviderManager:
    """Manages provider resolution, health checks, and explicit fallback."""

    @staticmethod
    def get_provider_for_model(model_id: str) -> BaseLLMProvider:
        clean_id = (model_id or "openai-cloud").lower()
        if "mock" in clean_id:
            return MockAgentProvider()
        elif "ollama" in clean_id or "local" in clean_id:
            return OllamaProvider()
        else:
            if settings.app_env == "testing" and os.environ.get("USE_REAL_OPENAI") != "true":
                return MockAgentProvider()
            return OpenAIProvider()

    @staticmethod
    async def resolve_provider_with_fallback(
        model_id: str,
        fallback_enabled: Optional[bool] = None,
    ) -> Tuple[BaseLLMProvider, str, Optional[str]]:
        """
        Resolves provider. If requested provider is unavailable and fallback_enabled is True,
        falls back to secondary provider.
        Returns: (provider_instance, actual_provider_name, fallback_reason)
        """
        is_fallback_allowed = (
            fallback_enabled if fallback_enabled is not None else settings.model_fallback_enabled
        )
        primary = ProviderManager.get_provider_for_model(model_id)
        requested_provider = primary.provider_name

        # Test availability
        primary_available = await primary.is_available()
        if primary_available:
            return primary, requested_provider, None

        # If primary not available, check fallback
        if not is_fallback_allowed:
            # Fallback disabled -> raise structured provider error immediately
            if requested_provider == "openai":
                raise MissingProviderKeyError(provider="openai")
            else:
                raise ProviderUnavailableError(
                    provider="ollama",
                    reason=f"Ollama is offline on {settings.ollama_base_url} and fallback is disabled.",
                    details={"canSwitchToCloud": True},
                )

        # Fallback enabled: attempt secondary provider
        if requested_provider == "ollama":
            fallback = OpenAIProvider()
            if await fallback.is_available():
                fallback_reason = "Ollama unavailable; falling back to OpenAI Cloud"
                logger.warning(
                    f"[Fallback] requested_provider={requested_provider}, "
                    f"actual_provider=openai, reason='{fallback_reason}'"
                )
                return fallback, "openai", fallback_reason
        elif requested_provider == "openai":
            fallback = OllamaProvider()
            if await fallback.is_available():
                fallback_reason = "OpenAI key missing; falling back to Local Ollama"
                logger.warning(
                    f"[Fallback] requested_provider={requested_provider}, "
                    f"actual_provider=ollama, reason='{fallback_reason}'"
                )
                return fallback, "ollama", fallback_reason

        # If both unavailable, fail with primary error
        if requested_provider == "openai":
            raise MissingProviderKeyError(provider="openai")
        else:
            raise ProviderUnavailableError(
                provider="ollama",
                reason=f"Ollama is offline and cloud fallback also unavailable.",
                details={"canSwitchToCloud": False},
            )
