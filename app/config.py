from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(alias="DATABASE_URL")

    llm_provider: Literal["openai", "gemini"] = Field(default="openai", alias="LLM_PROVIDER")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")

    output_dir: str = Field(default="output", alias="OUTPUT_DIR")
    scraper_timeout_seconds: int = Field(default=15, alias="SCRAPER_TIMEOUT_SECONDS")
    scraper_max_retries: int = Field(default=2, alias="SCRAPER_MAX_RETRIES")
    scraper_user_agent: str = Field(default="content-summarizer-bot/1.0", alias="SCRAPER_USER_AGENT")

    source_urls_file: str = Field(default="source_urls.txt", alias="SOURCE_URLS_FILE")

    @property
    def output_path(self) -> Path:
        path = Path(self.output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
