from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    chroma_dir: Path
    chroma_collection: str

    embedding_model: str
    embedding_device: str
    normalize_embeddings: bool

    gemini_api_key_env: str
    gemini_model: str

    chunk_size: int
    chunk_overlap: int
    top_k: int


def get_settings() -> Settings:
    root = Path(__file__).resolve().parent

    return Settings(
        data_dir=Path(os.getenv("DATA_DIR", str(root / "data"))),
        chroma_dir=Path(os.getenv("CHROMA_DIR", str(root / "chromadb"))),
        chroma_collection=os.getenv("CHROMA_COLLECTION", "kbase"),
        embedding_model=os.getenv("EMBEDDING_MODEL", str(root / "models" / "Xorbits" / "bge-m3")),
        embedding_device=os.getenv("EMBEDDING_DEVICE", "cpu"),
        normalize_embeddings=os.getenv("NORMALIZE_EMBEDDINGS", "1") == "1",
        gemini_api_key_env=os.getenv("GEMINI_API_KEY_ENV", "GEMINI_API_KEY"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3-flash-preview"),
        chunk_size=int(os.getenv("CHUNK_SIZE", "800")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "120")),
        top_k=int(os.getenv("TOP_K", "5")),
    )
