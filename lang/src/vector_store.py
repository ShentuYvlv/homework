from __future__ import annotations

from config import Settings
from langchain_core.embeddings import Embeddings

import chromadb


try:
    from langchain_chroma import Chroma  # type: ignore
except Exception:  # pragma: no cover
    from langchain_community.vectorstores import Chroma


def resolve_collection_name(settings: Settings) -> str:
    client = chromadb.PersistentClient(path=str(settings.chroma_dir))
    names = [c.name for c in client.list_collections()]
    if not names:
        return settings.chroma_collection

    def safe_count(name: str) -> int:
        try:
            return client.get_collection(name=name).count()
        except Exception:
            return 0

    preferred = settings.chroma_collection
    if safe_count(preferred) > 0:
        return preferred

    best = max(names, key=safe_count)
    if safe_count(best) > 0:
        return best
    return preferred


def get_vector_store(settings: Settings, embeddings: Embeddings, *, collection_name: str | None = None) -> Chroma:
    return Chroma(
        collection_name=collection_name or settings.chroma_collection,
        persist_directory=str(settings.chroma_dir),
        embedding_function=embeddings,
    )
