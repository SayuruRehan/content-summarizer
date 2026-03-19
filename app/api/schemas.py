from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    content_id: int | None = Field(default=None)
    url: str | None = Field(default=None)
    provider: str | None = Field(default=None)


class SummarizeResponse(BaseModel):
    status: str
    content_id: int
    provider: str
    summary_id: int
    summary_file: str


class ScrapeNowResponse(BaseModel):
    status: str
    total: int
    success: int
    failed: int


class ContentResponse(BaseModel):
    id: int
    source_url_id: int | None
    url: str
    page_title: str | None
    http_status: int | None
    scraped_at: str
    processing_status: str
    error_message: str | None


class SummaryMetadataResponse(BaseModel):
    id: int
    scraped_content_id: int
    provider_name: str
    model_name: str
    summary_file_path: str
    created_at: str
