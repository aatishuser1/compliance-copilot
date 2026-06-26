from pathlib import Path

from fastapi import UploadFile

from app.config import PDF_MAGIC, settings
from app.exceptions import InvalidUploadError


def validate_pdf_upload(file: UploadFile, saved_path: Path) -> None:
    if not file.filename:
        raise InvalidUploadError("A filename is required.")

    if not file.filename.lower().endswith(".pdf"):
        raise InvalidUploadError("Only PDF files are supported.")

    content_type = (file.content_type or "").lower()
    if content_type and content_type not in {"application/pdf", "application/x-pdf"}:
        raise InvalidUploadError("Invalid content type. Upload a PDF file.")

    size = saved_path.stat().st_size
    if size == 0:
        raise InvalidUploadError("Uploaded file is empty.")

    if size > settings.max_upload_bytes:
        raise InvalidUploadError(
            f"File exceeds the {settings.max_upload_mb} MB upload limit."
        )

    with saved_path.open("rb") as handle:
        header = handle.read(4)
    if not header.startswith(PDF_MAGIC):
        raise InvalidUploadError("File content is not a valid PDF.")
