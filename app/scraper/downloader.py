from dataclasses import dataclass

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.config import get_settings


@dataclass
class DownloadResult:
    url: str
    status_code: int | None
    response_text: str | None
    error_message: str | None


class Downloader:
    def __init__(self) -> None:
        settings = get_settings()
        self.timeout_seconds = settings.scraper_timeout_seconds
        self.user_agent = settings.scraper_user_agent

        retry = Retry(
            total=settings.scraper_max_retries,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
            raise_on_status=False,
        )

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def fetch(self, url: str) -> DownloadResult:
        try:
            response = self.session.get(url, timeout=self.timeout_seconds)
            return DownloadResult(
                url=url,
                status_code=response.status_code,
                response_text=response.text,
                error_message=None,
            )
        except requests.RequestException as exc:
            return DownloadResult(url=url, status_code=None, response_text=None, error_message=str(exc))
