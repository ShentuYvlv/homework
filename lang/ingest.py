from __future__ import annotations

import argparse
from pathlib import Path

from config import get_settings
from src.embeddings import build_embeddings
from src.loader import load_markdown_files
from src.splitter import split_markdown_documents
from src.vector_store import get_vector_store


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Index markdown into ChromaDB (Scheme A).")
    p.add_argument("--data-dir", type=str, default=None, help="Override DATA_DIR")
    p.add_argument("--chroma-dir", type=str, default=None, help="Override CHROMA_DIR")
    p.add_argument("--collection", type=str, default=None, help="Override CHROMA_COLLECTION")
    p.add_argument("--limit", type=int, default=0, help="Limit number of files (0 = all)")
    p.add_argument("--batch-size", type=int, default=64, help="Documents per batch when writing to Chroma")
    p.add_argument("--max-chunks", type=int, default=0, help="Limit number of chunks (0 = all)")
    p.add_argument("--dry-run", action="store_true", help="Only print stats, do not write DB")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()

    if args.data_dir:
        settings = settings.__class__(**{**settings.__dict__, "data_dir": Path(args.data_dir)})
    if args.chroma_dir:
        settings = settings.__class__(**{**settings.__dict__, "chroma_dir": Path(args.chroma_dir)})
    if args.collection:
        settings = settings.__class__(**{**settings.__dict__, "chroma_collection": args.collection})

    docs = load_markdown_files(settings.data_dir)
    if args.limit and args.limit > 0:
        docs = docs[: args.limit]

    chunks = split_markdown_documents(docs, settings)
    print(f"Loaded files: {len(docs)}")
    print(f"Chunks: {len(chunks)}")

    if args.dry_run:
        return

    if args.max_chunks and args.max_chunks > 0:
        chunks = chunks[: args.max_chunks]
        print(f"Using chunks (limited): {len(chunks)}")

    embeddings = build_embeddings(settings)
    vs = get_vector_store(settings, embeddings)

    total = len(chunks)
    batch_size = max(1, int(args.batch_size))
    print(
        "Embedding + writing to Chroma... (首次运行会很慢；"
        "可通过设置 EMBEDDING_DEVICE=mps 加速 Mac)"
    )
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        vs.add_documents(chunks[start:end])
        print(f"Progress: {end}/{total}")

    print(f"Chroma directory: {settings.chroma_dir}")


if __name__ == "__main__":
    main()
