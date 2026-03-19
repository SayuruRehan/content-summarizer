from openai import OpenAI

from app.llm.base import LLMProvider, LLMProviderError, LLMResponse


class OpenAIProvider(LLMProvider):
    provider_name = "openai"

    def __init__(self, api_key: str, model: str) -> None:
        self.model = model
        self.client = OpenAI(api_key=api_key)

    def summarize(self, text: str, prompt: str) -> LLMResponse:
        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": [{"type": "input_text", "text": prompt}]},
                    {"role": "user", "content": [{"type": "input_text", "text": text}]},
                ],
                max_output_tokens=500,
            )
        except Exception as exc:  # noqa: BLE001
            raise LLMProviderError(f"OpenAI request failed: {exc}") from exc

        output = response.output_text.strip() if response.output_text else ""
        if not output:
            raise LLMProviderError("OpenAI returned an empty summary")

        return LLMResponse(provider_name=self.provider_name, model_name=self.model, summary_text=output)
