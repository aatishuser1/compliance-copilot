from fastapi import APIRouter

from app.config import settings
from app.exceptions import DocumentNotFoundError, ProcessingError
from app.rag.vector_store import index_exists
from app.schemas import SummaryRequest, SummaryResponse
from app.services import summary_service
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

    try:
        summary = summary_service.summarize(document_id)
    except Exception as exc:
        logger.exception("Summary failed for document %s", document_id)
        raise ProcessingError(f"Summary failed: {exc}") from exc

    logger.info(
        "Compliance intelligence generated for document %s (%d obligations, %d risks, %d penalties)",
        document_id,
        len(summary.obligations),
        len(summary.risks),
        len(summary.penalties),
    )
    return SummaryResponse(document_id=request.document_id, summary=summary)
