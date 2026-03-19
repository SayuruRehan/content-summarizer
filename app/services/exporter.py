from datetime import datetime
from pathlib import Path


def export_summary_txt(
    *,
    output_dir: Path,
    content_id: int,
    title: str | None,
    source_url: str,
    provider_name: str,
    summary_text: str,
) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"summary_{content_id}_{timestamp}.txt"
    file_path = output_dir / filename

    body = (
        f"Title: {title or 'N/A'}\n"
        f"Source URL: {source_url}\n"
        f"Provider: {provider_name}\n"
        f"Generated At: {datetime.utcnow().isoformat()}Z\n\n"
        f"Summary:\n{summary_text}\n"
    )

    file_path.write_text(body, encoding="utf-8")
    return str(file_path)
