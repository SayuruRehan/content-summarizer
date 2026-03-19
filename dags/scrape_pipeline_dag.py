from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.services.ingestion import IngestionService

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def run_scrape_job() -> dict[str, int]:
    db = SessionLocal()
    try:
        service = IngestionService(db, source_urls_file=settings.source_urls_file)
        result = service.run()
        return result
    finally:
        db.close()


with DAG(
    dag_id="scrape_pipeline_dag",
    start_date=datetime(2026, 1, 1),
    schedule="0 */6 * * *",
    catchup=False,
    default_args={
        "owner": "content-summarizer",
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["scraper", "mvp"],
) as dag:
    scrape = PythonOperator(
        task_id="scrape_and_store",
        python_callable=run_scrape_job,
    )

    scrape
