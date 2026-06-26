import json
from pathlib import Path

from app.config import STORAGE_DIR

METADATA_DIR = STORAGE_DIR / "metadata"
METADATA_DIR.mkdir(parents=True, exist_ok=True)


def save_metadata(
    document_id: str,
    *,
    filename: str,
    page_count: int,
    chunk_count: int,
) -> None:
    path = METADATA_DIR / f"{document_id}.json"
    path.write_text(
        json.dumps(
            {
                "filename": filename,
                "page_count": page_count,
                "chunk_count": chunk_count,
            }
        ),
        encoding="utf-8",
    )


def load_metadata(document_id: str) -> dict | None:
    path = METADATA_DIR / f"{document_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_document_ids() -> list[str]:
    return sorted(path.stem for path in METADATA_DIR.glob("*.json"))
