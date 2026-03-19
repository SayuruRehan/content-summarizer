from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ScrapedContent, SourceUrl, Summary


class Repository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active_source_urls(self) -> list[SourceUrl]:
        stmt = select(SourceUrl).where(SourceUrl.is_active.is_(True)).order_by(SourceUrl.id.asc())
        return list(self.db.scalars(stmt).all())

    def create_source_url(self, url: str) -> SourceUrl:
        record = SourceUrl(url=url, is_active=True)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_or_create_source_url(self, url: str) -> SourceUrl:
        stmt = select(SourceUrl).where(SourceUrl.url == url)
        existing = self.db.scalar(stmt)
        if existing:
            return existing
        return self.create_source_url(url)

    def get_content_by_id(self, content_id: int) -> ScrapedContent | None:
        return self.db.get(ScrapedContent, content_id)

    def get_latest_content_by_url(self, url: str) -> ScrapedContent | None:
        stmt = (
            select(ScrapedContent)
            .where(ScrapedContent.url == url)
            .order_by(ScrapedContent.scraped_at.desc(), ScrapedContent.id.desc())
        )
        return self.db.scalar(stmt)

    def save_scraped_content(
        self,
        *,
        source_url_id: int | None,
        url: str,
        page_title: str | None,
        raw_html: str | None,
        clean_text: str | None,
        http_status: int | None,
        processing_status: str,
        error_message: str | None,
    ) -> ScrapedContent:
        content = ScrapedContent(
            source_url_id=source_url_id,
            url=url,
            page_title=page_title,
            raw_html=raw_html,
            clean_text=clean_text,
            http_status=http_status,
            processing_status=processing_status,
            error_message=error_message,
            scraped_at=datetime.utcnow(),
        )
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content

    def save_summary(
        self,
        *,
        scraped_content_id: int,
        provider_name: str,
        model_name: str,
        prompt_used: str,
        summary_text: str,
        summary_file_path: str,
    ) -> Summary:
        summary = Summary(
            scraped_content_id=scraped_content_id,
            provider_name=provider_name,
            model_name=model_name,
            prompt_used=prompt_used,
            summary_text=summary_text,
            summary_file_path=summary_file_path,
        )
        self.db.add(summary)
        self.db.commit()
        self.db.refresh(summary)
        return summary

    def get_summary_by_id(self, summary_id: int) -> Summary | None:
        return self.db.get(Summary, summary_id)


def load_urls_from_file(path: str) -> list[str]:
    source = Path(path)
    if not source.exists():
        return []

    urls: list[str] = []
    for line in source.read_text(encoding="utf-8").splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue

        parsed = urlparse(trimmed)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            urls.append(trimmed)

    return urls
