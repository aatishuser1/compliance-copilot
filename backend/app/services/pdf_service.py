from pathlib import Path

import fitz

from app.utils.logging import get_logger

logger = get_logger(__name__)


def extract_pages(file_path: str | Path) -> tuple[list[tuple[int, str]], int]:
    """Return non-empty page text with 1-based page numbers."""
    path = Path(file_path)
    doc = fitz.open(str(path))
    pages: list[tuple[int, str]] = []

    for index, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        if text:
            pages.append((index, text))

    page_count = len(doc)
    doc.close()
    logger.info("Extracted %d non-empty pages from %s", len(pages), path.name)
    return pages, page_count
