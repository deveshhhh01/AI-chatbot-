from typing import Optional
from backend.app.llm.base_provider import BaseLLMProvider
from backend.app.llm.gemini_provider import GeminiProvider
from backend.app.llm.openrouter_provider import OpenRouterProvider
from backend.app.core.config import settings
from backend.app.core.logging import logger


class LLMFactory:
    _current_provider_name: Optional[str] = None
    _cached_instance: Optional[BaseLLMProvider] = None

    @classmethod
    def get_provider(cls, force_provider: Optional[str] = None) -> BaseLLMProvider:
        provider_name = (force_provider or settings.LLM_PROVIDER).strip().lower()

        # If provider changed or instance not created yet
        if cls._cached_instance is None or cls._current_provider_name != provider_name:
            if provider_name == "gemini":
                logger.info("[LLMFactory] Initializing Gemini Provider (Model: %s)", settings.GEMINI_MODEL)
                cls._cached_instance = GeminiProvider(
                    api_key=settings.GEMINI_API_KEY,
                    model=settings.GEMINI_MODEL
                )
            elif provider_name in ["openrouter", "open_router"]:
                logger.info("[LLMFactory] Initializing OpenRouter Provider (Model: %s)", settings.OPENROUTER_MODEL)
                cls._cached_instance = OpenRouterProvider(
                    api_key=settings.OPENROUTER_API_KEY,
                    model=settings.OPENROUTER_MODEL
                )
            else:
                logger.warning(
                    "[LLMFactory] Unknown provider '%s'. Defaulting to Gemini.", provider_name
                )
                cls._cached_instance = GeminiProvider(
                    api_key=settings.GEMINI_API_KEY,
                    model=settings.GEMINI_MODEL
                )
                provider_name = "gemini"

            cls._current_provider_name = provider_name
            logger.info("[LLMFactory] Active LLM provider switched to: %s", cls._cached_instance.get_provider_name())

        return cls._cached_instance

    @classmethod
    def get_active_provider_name(cls) -> str:
        provider = cls.get_provider()
        return provider.get_provider_name()
