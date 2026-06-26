from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.config import INDEX_DIR


def _index_path(document_id: str) -> Path:
    return INDEX_DIR / document_id


def save_index(
    document_id: str,
    documents: list[Document],
    embeddings: Embeddings,
) -> None:
    store = FAISS.from_documents(documents, embeddings)
    store.save_local(str(_index_path(document_id)))


def load_index(document_id: str, embeddings: Embeddings) -> FAISS:
    path = _index_path(document_id)
    if not path.exists():
        raise FileNotFoundError(f"No index for document '{document_id}'")
    return FAISS.load_local(
        str(path),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def index_exists(document_id: str) -> bool:
    return _index_path(document_id).exists()
