import shutil
import uuid
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, File, UploadFile

from app.config import UPLOAD_DIR, settings
from app.exceptions import DocumentNotFoundError, InvalidUploadError, ProcessingError
from app.rag.chunking import split_pages
from app.schemas import DocumentInfo, UploadResponse
from app.services import pdf_service, retrieval_service
from app.utils.logging import get_logger
from app.utils.metadata import list_document_ids, load_metadata, save_metadata
from app.utils.upload_validation import validate_pdf_upload

router = APIRouter(prefix="/api/upload", tags=["upload"])
logger = get_logger(__name__)


@router.post("", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)) -> UploadResponse:
    if not settings.openai_api_key:
        raise ProcessingError("OpenAI API key is not configured.")

    document_id = uuid.uuid4()
    filename = Path(file.filename or "document.pdf").name
    dest = UPLOAD_DIR / f"{document_id}_{filename}"

    try:
        with dest.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        validate_pdf_upload(file, dest)
        logger.info("Upload received: %s (%s)", filename, document_id)

        pages, page_count = pdf_service.extract_pages(dest)
        if not pages:
            raise InvalidUploadError("Could not extract text from the PDF.")

        chunks = split_pages(pages, str(document_id))
        retrieval_service.index_document(str(document_id), chunks)
        save_metadata(
            str(document_id),
            filename=filename,
            page_count=page_count,
            chunk_count=len(chunks),
        )

        logger.info(
            "Upload complete: %s pages, %s chunks (%s)",
            page_count,
            len(chunks),
            document_id,
        )
        return UploadResponse(
            document_id=document_id,
            filename=filename,
            page_count=page_count,
            chunk_count=len(chunks),
        )
    except InvalidUploadError:
        dest.unlink(missing_ok=True)
        raise
    except Exception as exc:
        dest.unlink(missing_ok=True)
        logger.exception("Upload failed for %s", filename)
        raise ProcessingError(f"Upload processing failed: {exc}") from exc


@router.get("/documents", response_model=list[DocumentInfo])
async def list_documents() -> list[DocumentInfo]:
    documents: list[DocumentInfo] = []

    for document_id in list_document_ids():
        metadata = load_metadata(document_id)
        if metadata is None:
            continue
        documents.append(
            DocumentInfo(
                document_id=UUID(document_id),
                filename=metadata["filename"],
                page_count=metadata.get("page_count"),
                chunk_count=metadata.get("chunk_count"),
            )
        )

    return documents
