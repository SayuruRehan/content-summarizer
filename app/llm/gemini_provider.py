import google.generativeai as genai

from app.llm.base import LLMProvider, LLMProviderError, LLMResponse


class GeminiProvider(LLMProvider):
    provider_name = "gemini"

    def __init__(self, api_key: str, model: str) -> None:
        self.model = model
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model_name=model)

    def summarize(self, text: str, prompt: str) -> LLMResponse:
        try:
            response = self.client.generate_content(f"{prompt}\n\n{text}")
        except Exception as exc:  # noqa: BLE001
            raise LLMProviderError(f"Gemini request failed: {exc}") from exc

        output = (response.text or "").strip()
        if not output:
            raise LLMProviderError("Gemini returned an empty summary")

        return LLMResponse(provider_name=self.provider_name, model_name=self.model, summary_text=output)
