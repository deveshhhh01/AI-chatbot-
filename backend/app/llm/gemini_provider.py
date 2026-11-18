import asyncio
from typing import AsyncIterator, Optional
from google import genai
from google.genai import types
from backend.app.llm.base_provider import BaseLLMProvider
from backend.app.core.config import settings
from backend.app.core.logging import logger


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self._client: Optional[genai.Client] = None
        if self.api_key:
            self._client = genai.Client(api_key=self.api_key)

    def _ensure_client(self) -> genai.Client:
        if not self.api_key:
            raise ValueError(
                "Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file."
            )
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        client = self._ensure_client()
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction if system_instruction else None,
                temperature=0.2,
                top_p=0.95
            )
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            return response.text or ""
        except Exception as e:
            logger.error("[GeminiProvider] Generation error: %s", e)
            raise e

    async def generate_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> AsyncIterator[str]:
        client = self._ensure_client()
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction if system_instruction else None,
                temperature=0.2,
                top_p=0.95
            )
            # Run stream generation
            response_stream = client.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=config
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
                    await asyncio.sleep(0.01)
        except Exception as e:
            logger.error("[GeminiProvider] Streaming error: %s", e)
            yield f"\n[Error generating response: {str(e)}]"

    def validate_connection(self) -> bool:
        if not self.api_key:
            return False
        try:
            client = self._ensure_client()
            resp = client.models.generate_content(
                model=self.model,
                contents="Ping. Reply with 'OK'.",
                config=types.GenerateContentConfig(max_output_tokens=10)
            )
            return bool(resp and resp.text)
        except Exception as e:
            logger.warning("[GeminiProvider] Connection validation failed: %s", e)
            return False

    def get_provider_name(self) -> str:
        return f"Gemini ({self.model})"
