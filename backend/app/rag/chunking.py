from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.rag.headings import split_page_into_sections
from app.utils.logging import get_logger

logger = get_logger(__name__)

CHUNK_SEPARATORS = ["\n\n", "\n", ". ", "; ", " ", ""]


def split_pages(
    pages: list[tuple[int, str]],
    document_id: str,
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=CHUNK_SEPARATORS,
    )

    chunks: list[Document] = []
    chunk_index = 0
    carried_parent: str | None = None

    for page_number, page_text in pages:
        sections, carried_parent = split_page_into_sections(
            page_text,
            initial_parent=carried_parent,
        )

        for section_heading, parent_section, section_text in sections:
            page_chunks = splitter.create_documents(
                [section_text],
                metadatas=[
                    {
                        "document_id": document_id,
                        "page": page_number,
                        "section_heading": section_heading,
                        "parent_section": parent_section or "",
                    }
                ],
            )
            for chunk in page_chunks:
                chunk.metadata["chunk"] = chunk_index
                chunk_index += 1
                chunks.append(chunk)

    logger.info(
        "Created %d chunks from %d pages for document %s",
        len(chunks),
        len(pages),
        document_id,
    )
    return chunks
