import pytest
from backend.app.llm.llm_factory import LLMFactory
from backend.app.llm.gemini_provider import GeminiProvider
from backend.app.llm.openrouter_provider import OpenRouterProvider
from backend.app.rag.query_rewriter import QueryRewriter


def test_llm_factory_instantiation():
    gemini = LLMFactory.get_provider("gemini")
    assert isinstance(gemini, GeminiProvider)
    assert "Gemini" in gemini.get_provider_name()

    openrouter = LLMFactory.get_provider("openrouter")
    assert isinstance(openrouter, OpenRouterProvider)
    assert "OpenRouter" in openrouter.get_provider_name()


def test_missing_api_key_handling():
    provider = OpenRouterProvider(api_key="")
    with pytest.raises(ValueError) as exc:
        provider.generate_response("Hello")
    assert "OpenRouter API key is not configured" in str(exc.value)


def test_query_rewriter_follow_up():
    history = [
        {"role": "user", "content": "Tell me about W Residences in Dubai."},
        {"role": "assistant", "content": "W Residences Dubai Downtown is an exclusive tower by DarGlobal."}
    ]
    rewritten = QueryRewriter.rewrite_query("What amenities does it have?", history)
    assert "W Residences" in rewritten or "Dubai" in rewritten


def test_query_rewriter_standalone():
    rewritten = QueryRewriter.rewrite_query("What properties are in Riyadh?", [])
    assert rewritten == "What properties are in Riyadh?"
