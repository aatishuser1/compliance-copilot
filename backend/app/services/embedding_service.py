from langchain_openai import OpenAIEmbeddings

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


def get_embeddings() -> OpenAIEmbeddings:
    logger.debug("Creating embedding client for model %s", settings.embedding_model)
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key or None,
    )
