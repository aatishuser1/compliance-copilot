from langchain_core.documents import Document

from app.config import settings
from app.rag import vector_store
from app.rag.headings import heading_match_boost, rerank_with_headings
from app.services.embedding_service import get_embeddings
from app.utils.logging import get_logger

logger = get_logger(__name__)

MAX_CHUNKS_PER_PAGE = 2


def index_document(document_id: str, chunks: list[Document]) -> None:
    logger.info("Generating embeddings for document %s", document_id)
    embeddings = get_embeddings()
    vector_store.save_index(document_id, chunks, embeddings)
    logger.info("Saved FAISS index for document %s", document_id)


def _select_diverse_chunks(
    results: list[tuple[Document, float]],
    *,
    max_results: int,
) -> list[tuple[Document, float]]:
    """Prefer relevant chunks spread across pages before backfilling by score."""
    selected: list[tuple[Document, float]] = []
    page_counts: dict[int, int] = {}
    seen_ids: set[int] = set()

    for document, score in results:
        page = int(document.metadata.get("page", 0))
        if page_counts.get(page, 0) >= MAX_CHUNKS_PER_PAGE:
            continue
        selected.append((document, score))
        seen_ids.add(id(document))
        page_counts[page] = page_counts.get(page, 0) + 1
        if len(selected) >= max_results:
            return selected

    for document, score in results:
        if id(document) in seen_ids:
            continue
        selected.append((document, score))
        if len(selected) >= max_results:
            break

    return selected


def retrieve_with_scores(
    document_id: str,
    query: str,
) -> list[tuple[Document, float]]:
    embeddings = get_embeddings()
    store = vector_store.load_index(document_id, embeddings)

    candidates = store.similarity_search_with_score(
        query,
        k=settings.retrieval_fetch_k,
    )

    filtered: list[tuple[Document, float]] = []
    relaxed_limit = settings.similarity_threshold + settings.heading_match_threshold_margin

    for document, score in candidates:
        boost = heading_match_boost(query, document)
        if score <= settings.similarity_threshold:
            filtered.append((document, score))
        elif boost >= 10.0 and score <= relaxed_limit:
            # Keep strong heading matches that vector search ranks slightly below threshold.
            filtered.append((document, score))
            logger.debug(
                "Kept heading match page=%s chunk=%s score=%.3f boost=%.0f",
                document.metadata.get("page"),
                document.metadata.get("chunk"),
                score,
                boost,
            )

    if not filtered:
        if candidates:
            best_score = min(score for _, score in candidates)
            logger.info(
                "All %d candidates above threshold %.2f for document %s (best=%.3f)",
                len(candidates),
                settings.similarity_threshold,
                document_id,
                best_score,
            )
        return []

    ranked = rerank_with_headings(query, filtered)
    strong_matches = [
        item for item in ranked if heading_match_boost(query, item[0]) >= 10.0
    ]
    pool = strong_matches if len(strong_matches) >= 2 else ranked
    selected = _select_diverse_chunks(pool, max_results=settings.top_k)

    score_summary = ", ".join(
        f"{score:.3f}(h={heading_match_boost(query, doc):.0f})"
        for doc, score in selected
    )
    logger.info(
        "Retrieved %d chunks for document %s (candidates=%d, filtered=%d, scores=[%s])",
        len(selected),
        document_id,
        len(candidates),
        len(filtered),
        score_summary,
    )
    return selected
