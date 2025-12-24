from __future__ import annotations

from config import Settings
from langchain_core.embeddings import Embeddings


try:
    from langchain_chroma import Chroma  # type: ignore
except Exception:  # pragma: no cover
    from langchain_community.vectorstores import Chroma


def get_vector_store(settings: Settings, embeddings: Embeddings) -> Chroma:
    return Chroma(
        collection_name=settings.chroma_collection,
        persist_directory=str(settings.chroma_dir),
        embedding_function=embeddings,
    )
