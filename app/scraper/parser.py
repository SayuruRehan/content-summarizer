from dataclasses import dataclass

from bs4 import BeautifulSoup

from app.scraper.cleaner import extract_text


@dataclass
class ParsedContent:
    title: str | None
    clean_text: str


class HtmlParser:
    def parse(self, html: str) -> ParsedContent:
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.get_text(strip=True) if soup.title else None
        clean_text = extract_text(soup)
        return ParsedContent(title=title, clean_text=clean_text)
