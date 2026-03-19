# Content Summarizer MVP

Simple modular backend that scrapes web pages, stores content in PostgreSQL, summarizes content with OpenAI or Gemini, exports summaries to TXT files, and schedules scraping with Apache Airflow.

## Stack
- Python + FastAPI
- Requests + BeautifulSoup
- PostgreSQL + SQLAlchemy + Alembic
- OpenAI and Gemini provider adapters
- Apache Airflow for scheduled scraping
- Docker Compose for local orchestration

## Project Layout
- app/: API, services, scraper, db, llm modules
- dags/: Airflow DAGs
- alembic/: DB migration config and revisions
- output/: generated summary text files

## Environment
1. Copy .env.example to .env.
2. Fill API keys and provider settings.

## Run with Docker Compose
1. Start services:
   docker compose up --build -d
2. Run migrations from API container:
   docker compose exec api alembic upgrade head
3. Create Airflow admin user:
   docker compose exec airflow-webserver airflow users create --username admin --firstname admin --lastname admin --role Admin --email admin@example.com --password admin

API: http://localhost:8000
Airflow: http://localhost:8080

## Seed URLs
- Preferred: insert URLs into source_urls table with is_active = true.
- Fallback: create source_urls.txt in project root, one URL per line.

## API Endpoints
- POST /summarize
  - body: {"content_id": 123, "provider": "openai"}
  - or: {"url": "https://example.com", "provider": "gemini"}
- GET /content/{id}
- GET /summary/{id}
- POST /scrape-now
- GET /health

## Airflow
DAG id: scrape_pipeline_dag
- Schedule: every 6 hours
- Task: scrape_and_store
- Retries: 2

## Notes
- Summarization is API-driven in MVP.
- Airflow is used for scrape orchestration only.
- Long content is truncated before provider request.

## PSQL Queries - Check scraped content
```
docker compose exec -T db psql -U scraper -d scraper_db -c "SELECT id, url, page_title, http_status, processing_status, scraped_at FROM scraped_content ORDER BY id DESC LIMIT 20;"
```

## PSQL Queries - Latest scraped content
```
docker compose exec -T db psql -U scraper -d scraper_db -c "SELECT id,url,http_status,processing_status,error_message,scraped_at FROM scraped_content WHERE processing_status <> 'success' ORDER BY id DESC;"

```
