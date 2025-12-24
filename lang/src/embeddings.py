from __future__ import annotations

from config import Settings
from langchain_huggingface import HuggingFaceEmbeddings


def build_embeddings(settings: Settings) -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": settings.embedding_device},
        encode_kwargs={"normalize_embeddings": settings.normalize_embeddings},
    )

