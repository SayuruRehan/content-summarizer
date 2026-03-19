import re

from bs4 import BeautifulSoup


REMOVE_SELECTORS = ["script", "style", "noscript", "svg", "footer", "header", "nav", "aside"]


def normalize_whitespace(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    return normalized


def extract_text(soup: BeautifulSoup) -> str:
    for selector in REMOVE_SELECTORS:
        for node in soup.select(selector):
            node.decompose()

    body = soup.body or soup
    text = body.get_text(separator=" ", strip=True)
    return normalize_whitespace(text)
