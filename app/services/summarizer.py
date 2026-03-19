from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.repository import Repository
from app.llm.base import LLMProviderError, build_provider
from app.services.exporter import export_summary_txt

SUMMARY_PROMPT = (
    "You summarize scraped web pages into clear plain text. "
    "Write a concise summary with key points and avoid hallucinations."
)


class SummarizationError(Exception):
    pass


class SummarizerService:
    def __init__(self, db: Session) -> None:
        self.settings = get_settings()
        self.repo = Repository(db)

    def _truncate_content(self, text: str, max_chars: int = 20000) -> str:
        if len(text) <= max_chars:
            return text
        return text[:max_chars]

    def summarize(self, *, content_id: int | None, url: str | None, provider: str | None) -> dict:
        content = None
        if content_id is not None:
            content = self.repo.get_content_by_id(content_id)
        elif url:
            content = self.repo.get_latest_content_by_url(url)

        if content is None:
            raise SummarizationError("No scraped content record found for the requested input")

        if not content.clean_text or not content.clean_text.strip():
            raise SummarizationError("Scraped content is empty and cannot be summarized")

        text = self._truncate_content(content.clean_text)

        try:
            llm_provider = build_provider(provider_override=provider)
            llm_result = llm_provider.summarize(text=text, prompt=SUMMARY_PROMPT)
        except LLMProviderError as exc:
            raise SummarizationError(str(exc)) from exc

        try:
            summary_file_path = export_summary_txt(
                output_dir=self.settings.output_path,
                content_id=content.id,
                title=content.page_title,
                source_url=content.url,
                provider_name=llm_result.provider_name,
                summary_text=llm_result.summary_text,
            )
        except OSError as exc:
            raise SummarizationError(f"Failed to write summary file: {exc}") from exc

        summary = self.repo.save_summary(
            scraped_content_id=content.id,
            provider_name=llm_result.provider_name,
            model_name=llm_result.model_name,
            prompt_used=SUMMARY_PROMPT,
            summary_text=llm_result.summary_text,
            summary_file_path=summary_file_path,
        )

        return {
            "status": "success",
            "content_id": content.id,
            "provider": summary.provider_name,
            "summary_id": summary.id,
            "summary_file": summary.summary_file_path,
        }
