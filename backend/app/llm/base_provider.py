from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """Generate complete LLM text response."""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Generate streaming response chunks."""
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """Verify API key and connectivity with provider."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider identifier (e.g. 'gemini' or 'openrouter')."""
        pass
