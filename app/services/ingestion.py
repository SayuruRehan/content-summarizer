import logging
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.db.repository import Repository, load_urls_from_file
from app.scraper.downloader import Downloader
from app.scraper.parser import HtmlParser

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, db: Session, source_urls_file: str) -> None:
        self.repo = Repository(db)
        self.downloader = Downloader()
        self.parser = HtmlParser()
        self.source_urls_file = source_urls_file

    def _resolve_urls(self) -> list[tuple[int | None, str]]:
        active = self.repo.get_active_source_urls()
        if active:
            return [(row.id, row.url) for row in active]

        fallback_urls = load_urls_from_file(self.source_urls_file)
        return [(None, url) for url in fallback_urls]

    def run(self) -> dict[str, int]:
        urls = self._resolve_urls()
        success = 0
        failed = 0

        for source_url_id, url in urls:
            parsed_url = urlparse(url)
            if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
                failed += 1
                self.repo.save_scraped_content(
                    source_url_id=source_url_id,
                    url=url,
                    page_title=None,
                    raw_html=None,
                    clean_text=None,
                    http_status=None,
                    processing_status="failed",
                    error_message="Invalid URL",
                )
                continue

            result = self.downloader.fetch(url)
            if result.error_message:
                failed += 1
                self.repo.save_scraped_content(
                    source_url_id=source_url_id,
                    url=url,
                    page_title=None,
                    raw_html=None,
                    clean_text=None,
                    http_status=result.status_code,
                    processing_status="failed",
                    error_message=result.error_message,
                )
                logger.warning("Download failed for %s: %s", url, result.error_message)
                continue

            assert result.response_text is not None
            parsed = self.parser.parse(result.response_text)

            status = "success"
            error_message = None
            if len(parsed.clean_text) < 40:
                status = "empty"
                error_message = "Extracted content is empty or near-empty"

            self.repo.save_scraped_content(
                source_url_id=source_url_id,
                url=url,
                page_title=parsed.title,
                raw_html=result.response_text,
                clean_text=parsed.clean_text,
                http_status=result.status_code,
                processing_status=status,
                error_message=error_message,
            )

            if status == "success":
                success += 1
            else:
                failed += 1

        return {"total": len(urls), "success": success, "failed": failed}
