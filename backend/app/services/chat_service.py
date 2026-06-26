from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from app.config import load_prompt, settings
from app.schemas import SourceChunk
from app.services.retrieval_service import retrieve_with_scores
from app.utils.logging import get_logger

logger = get_logger(__name__)

NOT_FOUND_ANSWER = (
    "I could not find information about that in the uploaded document."
)


def _build_sources(documents: list[Document]) -> list[SourceChunk]:
    seen: set[tuple[int, int]] = set()
    sources: list[SourceChunk] = []

    for document in documents:
        page = int(document.metadata.get("page", 0))
        chunk = int(document.metadata.get("chunk", 0))
        key = (page, chunk)
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            SourceChunk(
                page=page,
                chunk=chunk,
                excerpt=document.page_content[:280].strip(),
                section=document.metadata.get("section_heading")
                or document.metadata.get("parent_section")
                or None,
            )
        )
    return sources


def _format_context(documents: list[Document]) -> str:
    sections: list[str] = []
    for document in documents:
        page = document.metadata.get("page", "?")
        chunk = document.metadata.get("chunk", "?")
        section = document.metadata.get("section_heading") or document.metadata.get(
            "parent_section"
        )
        label = f"[Page {page} | Chunk {chunk}"
        if section:
            label += f" | {section}"
        label += "]"
        sections.append(f"{label}\n{document.page_content.strip()}")
    return "\n\n---\n\n".join(sections)


def answer_question(document_id: str, question: str) -> tuple[str, list[SourceChunk], bool]:
    results = retrieve_with_scores(document_id, question)
    if not results:
        logger.info("Low-confidence retrieval for document %s", document_id)
        return NOT_FOUND_ANSWER, [], False

    documents = [document for document, _ in results]
    sources = _build_sources(documents)
    context = _format_context(documents)

    system_prompt, user_template = load_prompt("qa")
    prompt = user_template.format(context=context, question=question)

    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openai_api_key or None,
        temperature=0.1,
    )
    logger.info("Sending chat request for document %s", document_id)
    response = llm.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
    )
    return str(response.content), sources, True
