from fastapi import APIRouter

from app.exceptions import DocumentNotFoundError, ProcessingError
from app.rag.vector_store import index_exists
from app.schemas import ChatRequest, ChatResponse
from app.services import chat_service
from app.utils.logging import get_logger

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = get_logger(__name__)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    document_id = str(request.document_id)

    if not index_exists(document_id):
        raise DocumentNotFoundError(document_id)

    try:
        answer, sources, found = chat_service.answer_question(
            document_id,
            request.question,
        )
    except FileNotFoundError as exc:
        raise DocumentNotFoundError(document_id) from exc
    except Exception as exc:
        logger.exception("Chat failed for document %s", document_id)
        raise ProcessingError(f"Chat failed: {exc}") from exc

    logger.info("Chat answered for document %s (found=%s)", document_id, found)
    return ChatResponse(answer=answer, sources=sources, found_in_document=found)
