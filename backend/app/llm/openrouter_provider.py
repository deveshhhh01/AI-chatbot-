import json
from typing import AsyncIterator, Optional
import httpx
from openai import OpenAI, AsyncOpenAI
from backend.app.llm.base_provider import BaseLLMProvider
from backend.app.core.config import settings
from backend.app.core.logging import logger


class OpenRouterProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model = model or settings.OPENROUTER_MODEL
        self.base_url = "https://openrouter.ai/api/v1"

    def _get_headers(self) -> dict:
        return {
            "HTTP-Referer": "https://darglobal.co.uk",
            "X-Title": "DarGlobal & Wasalt Real Estate Intelligence",
            "Authorization": f"Bearer {self.api_key}"
        }

    def _ensure_api_key(self):
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is not configured. Please set OPENROUTER_API_KEY in your .env file."
            )

    def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        self._ensure_api_key()
        client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            default_headers=self._get_headers()
        )
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                top_p=0.95
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error("[OpenRouterProvider] Generation error: %s", e)
            raise e

    async def generate_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> AsyncIterator[str]:
        self._ensure_api_key()
        client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            default_headers=self._get_headers()
        )
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                stream=True
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
        except Exception as e:
            logger.error("[OpenRouterProvider] Streaming error: %s", e)
            yield f"\n[Error generating response: {str(e)}]"

    def validate_connection(self) -> bool:
        if not self.api_key:
            return False
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(
                    "https://openrouter.ai/api/v1/auth/key",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return resp.status_code == 200
        except Exception as e:
            logger.warning("[OpenRouterProvider] Validation error: %s", e)
            return False

    def get_provider_name(self) -> str:
        return f"OpenRouter ({self.model})"
