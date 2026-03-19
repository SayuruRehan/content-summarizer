from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.db.connection import Base


class SourceUrl(Base):
    __tablename__ = "source_urls"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    scraped_contents = relationship("ScrapedContent", back_populates="source_url")


class ScrapedContent(Base):
    __tablename__ = "scraped_content"

    id = Column(Integer, primary_key=True, index=True)
    source_url_id = Column(Integer, ForeignKey("source_urls.id"), nullable=True)
    url = Column(Text, index=True, nullable=False)
    page_title = Column(Text, nullable=True)
    raw_html = Column(Text, nullable=True)
    clean_text = Column(Text, nullable=True)
    http_status = Column(Integer, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processing_status = Column(Text, default="pending", nullable=False)
    error_message = Column(Text, nullable=True)

    source_url = relationship("SourceUrl", back_populates="scraped_contents")
    summaries = relationship("Summary", back_populates="scraped_content")


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    scraped_content_id = Column(Integer, ForeignKey("scraped_content.id"), nullable=False)
    provider_name = Column(Text, nullable=False)
    model_name = Column(Text, nullable=False)
    prompt_used = Column(Text, nullable=False)
    summary_text = Column(Text, nullable=False)
    summary_file_path = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    scraped_content = relationship("ScrapedContent", back_populates="summaries")
