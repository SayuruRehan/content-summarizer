"""Initial schema

Revision ID: 20260316_0001
Revises:
Create Date: 2026-03-16 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260316_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "source_urls",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("url", sa.Text(), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_source_urls_id", "source_urls", ["id"])

    op.create_table(
        "scraped_content",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_url_id", sa.Integer(), sa.ForeignKey("source_urls.id"), nullable=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("page_title", sa.Text(), nullable=True),
        sa.Column("raw_html", sa.Text(), nullable=True),
        sa.Column("clean_text", sa.Text(), nullable=True),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.Column("processing_status", sa.Text(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.create_index("ix_scraped_content_id", "scraped_content", ["id"])
    op.create_index("ix_scraped_content_url", "scraped_content", ["url"])

    op.create_table(
        "summaries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scraped_content_id", sa.Integer(), sa.ForeignKey("scraped_content.id"), nullable=False),
        sa.Column("provider_name", sa.Text(), nullable=False),
        sa.Column("model_name", sa.Text(), nullable=False),
        sa.Column("prompt_used", sa.Text(), nullable=False),
        sa.Column("summary_text", sa.Text(), nullable=False),
        sa.Column("summary_file_path", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_summaries_id", "summaries", ["id"])


def downgrade() -> None:
    op.drop_index("ix_summaries_id", table_name="summaries")
    op.drop_table("summaries")
    op.drop_index("ix_scraped_content_url", table_name="scraped_content")
    op.drop_index("ix_scraped_content_id", table_name="scraped_content")
    op.drop_table("scraped_content")
    op.drop_index("ix_source_urls_id", table_name="source_urls")
    op.drop_table("source_urls")
