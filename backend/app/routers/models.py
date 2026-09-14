import logging
from typing import Any, Dict, List
from fastapi import APIRouter
import httpx

from ..config import settings
from ..agent.providers import OpenAIProvider, OllamaProvider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/models", tags=["Models"])


@router.get("")
async def get_models() -> Dict[str, Any]:
    """
    Returns available and configured LLM providers and models.
    Does not expose API keys or secrets.
    """
    openai_provider = OpenAIProvider()
    ollama_provider = OllamaProvider()

    openai_available = await openai_provider.is_available()
    ollama_available = await ollama_provider.is_available()

    # Discover installed Ollama models if online
    ollama_models = [settings.ollama_model or "llama3.2:3b"]
    ollama_note = (
        f"Local — private inference ({settings.ollama_model or 'llama3.2:3b'} detected)"
        if ollama_available
        else "Local — Ollama not detected at localhost:11434"
    )

    if ollama_available:
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    discovered = [m["name"] for m in data.get("models", [])]
                    if discovered:
                        ollama_models = discovered
                        ollama_note = f"Local — private inference ({ollama_models[0]})"
        except Exception:
            pass

    openai_note = (
        f"Cloud — high reasoning capacity ({settings.openai_model or 'gpt-4o-mini'})"
        if openai_available
        else "Cloud — OPENAI_API_KEY required in backend/.env"
    )

    providers = [
        {
            "id": "openai-cloud",
            "name": "OpenAI",
            "provider": "Cloud",
            "model": settings.openai_model or "gpt-4o-mini",
            "available": openai_available,
            "modelIdentifier": f"OpenAI ({settings.openai_model or 'gpt-4o-mini'})",
            "note": openai_note,
            "models": [settings.openai_model or "gpt-4o-mini", "gpt-4o"],
        },
        {
            "id": "ollama-local",
            "name": "Ollama",
            "provider": "Local",
            "model": ollama_models[0],
            "available": ollama_available,
            "modelIdentifier": f"Ollama ({ollama_models[0]})",
            "note": ollama_note,
            "models": ollama_models,
        },
    ]

    return {
        "providers": providers,
        "fallbackEnabled": settings.model_fallback_enabled,
        "defaultModelId": "ollama-local" if (ollama_available and not openai_available) else "openai-cloud",
    }
