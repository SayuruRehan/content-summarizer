from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas import (
    ContentResponse,
    ScrapeNowResponse,
    SummarizeRequest,
    SummarizeResponse,
    SummaryMetadataResponse,
)
from app.config import get_settings
from app.db.connection import get_db_session
from app.db.repository import Repository
from app.services.ingestion import IngestionService
from app.services.summarizer import SummarizationError, SummarizerService

router = APIRouter()


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(payload: SummarizeRequest, db: Session = Depends(get_db_session)) -> SummarizeResponse:
    if payload.content_id is None and payload.url is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either content_id or url must be provided",
        )

    service = SummarizerService(db)
    try:
        result = service.summarize(content_id=payload.content_id, url=payload.url, provider=payload.provider)
    except SummarizationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return SummarizeResponse(**result)


@router.get("/content/{content_id}", response_model=ContentResponse)
def get_content(content_id: int, db: Session = Depends(get_db_session)) -> ContentResponse:
    repo = Repository(db)
    content = repo.get_content_by_id(content_id)
    if content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

    return ContentResponse(
        id=content.id,
        source_url_id=content.source_url_id,
        url=content.url,
        page_title=content.page_title,
        http_status=content.http_status,
        scraped_at=content.scraped_at.isoformat() + "Z",
        processing_status=content.processing_status,
        error_message=content.error_message,
    )


@router.get("/summary/{summary_id}", response_model=SummaryMetadataResponse)
def get_summary(summary_id: int, db: Session = Depends(get_db_session)) -> SummaryMetadataResponse:
    repo = Repository(db)
    summary = repo.get_summary_by_id(summary_id)
    if summary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found")

    return SummaryMetadataResponse(
        id=summary.id,
        scraped_content_id=summary.scraped_content_id,
        provider_name=summary.provider_name,
        model_name=summary.model_name,
        summary_file_path=summary.summary_file_path,
        created_at=summary.created_at.isoformat() + "Z",
    )


@router.post("/scrape-now", response_model=ScrapeNowResponse)
def scrape_now(db: Session = Depends(get_db_session)) -> ScrapeNowResponse:
    settings = get_settings()
    service = IngestionService(db, source_urls_file=settings.source_urls_file)
    result = service.run()
    return ScrapeNowResponse(status="success", **result)
