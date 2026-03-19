from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.config import get_settings


class LLMProviderError(Exception):
    pass


@dataclass
class LLMResponse:
    provider_name: str
    model_name: str
    summary_text: str


class LLMProvider(ABC):
    provider_name: str

    @abstractmethod
    def summarize(self, text: str, prompt: str) -> LLMResponse:
        raise NotImplementedError


class MissingAPIKeyError(LLMProviderError):
    pass


def build_provider(provider_override: str | None = None) -> LLMProvider:
    from app.llm.gemini_provider import GeminiProvider
    from app.llm.openai_provider import OpenAIProvider

    settings = get_settings()
    selected = (provider_override or settings.llm_provider).lower()

    if selected == "openai":
        if not settings.openai_api_key:
            raise MissingAPIKeyError("OPENAI_API_KEY is not configured")
        return OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_model)

    if selected == "gemini":
        if not settings.gemini_api_key:
            raise MissingAPIKeyError("GEMINI_API_KEY is not configured")
        return GeminiProvider(api_key=settings.gemini_api_key, model=settings.gemini_model)

    raise LLMProviderError(f"Unsupported provider: {selected}")
