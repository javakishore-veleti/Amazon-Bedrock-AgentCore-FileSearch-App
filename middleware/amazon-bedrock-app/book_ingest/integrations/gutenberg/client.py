import logging
import re

import requests
from bs4 import BeautifulSoup

from book_ingest.config.settings import BookIngestSettings
from common.di import component

LOGGER = logging.getLogger(__name__)

_EBOOK_RE = re.compile(r"/ebooks/(\d+)")
_COUNT_SUFFIX_RE = re.compile(r"\s*\(\d[\d,]*\)\s*$")


@component(key="GutenbergClient", depends_on=["BookIngestSettings"])
class GutenbergClient:
    """HTTP client for Project Gutenberg page fetching and URL resolution."""

    def __init__(self, settings: BookIngestSettings):
        self.settings = settings

    def _get(self, url: str) -> str:
        resp = requests.get(
            url, headers={"User-Agent": self.settings.gutenberg_user_agent}, timeout=30
        )
        resp.raise_for_status()
        return resp.text

    def fetch_top_100(self, url: str, limit: int = 100) -> list:
        """Parse the 'Top 100 EBooks yesterday' ranked list."""
        soup = BeautifulSoup(self._get(url), "html.parser")
        heading = next(
            (h for h in soup.find_all(["h2", "h3"])
             if "Top 100 EBooks yesterday" in h.get_text()),
            None,
        )
        if heading is None:
            LOGGER.warning("Could not find 'Top 100 EBooks yesterday' heading")
            return []

        ordered = heading.find_next("ol")
        items, seen = [], set()
        for anchor in ordered.find_all("a", href=True):
            match = _EBOOK_RE.search(anchor["href"])
            if not match:
                continue
            ebook_id = match.group(1)
            if ebook_id in seen:
                continue
            seen.add(ebook_id)
            title, author = self._split_title_author(anchor.get_text(strip=True))
            items.append({
                "ebook_id": ebook_id,
                "title": title,
                "author": author,
                "source_page_url": f"https://www.gutenberg.org/ebooks/{ebook_id}",
            })
            if len(items) >= limit:
                break
        return items

    @staticmethod
    def resolve_txt_url(ebook_id: str) -> str:
        return f"https://www.gutenberg.org/cache/epub/{ebook_id}/pg{ebook_id}.txt"

    def fetch_text(self, txt_url: str) -> str:
        return self._get(txt_url)

    @staticmethod
    def _split_title_author(text: str):
        text = _COUNT_SUFFIX_RE.sub("", text).strip()
        if " by " in text:
            title, author = text.rsplit(" by ", 1)
            return title.strip(), author.strip()
        return text, None
