from fastapi import APIRouter

from app.config import find_upload, settings
from app.exceptions import DocumentNotFoundError, ProcessingError
from app.rag.vector_store import index_exists
from app.schemas import SummaryRequest, SummaryResponse
from app.services import pdf_service, summary_service
from app.utils.logging import get_logger

router = APIRouter(prefix="/api/summary", tags=["summary"])
logger = get_logger(__name__)


@router.post("", response_model=SummaryResponse)
async def generate_summary(request: SummaryRequest) -> SummaryResponse:
    if not settings.openai_api_key:
        raise ProcessingError("OpenAI API key is not configured.")

    document_id = str(request.document_id)

    if not index_exists(document_id):
        raise DocumentNotFoundError(document_id)

    upload_path = find_upload(document_id)
    if upload_path is None:
        raise DocumentNotFoundError(document_id)

    pages, _ = pdf_service.extract_pages(upload_path)
    if not pages:
        raise ProcessingError("Could not extract text from the uploaded PDF.")

    full_text = "\n\n".join(text for _, text in pages)

    try:
        summary = summary_service.summarize(full_text)
    except Exception as exc:
        logger.exception("Summary failed for document %s", document_id)
        raise ProcessingError(f"Summary failed: {exc}") from exc

    logger.info("Summary generated for document %s", document_id)
    return SummaryResponse(document_id=request.document_id, summary=summary)
