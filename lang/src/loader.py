from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document


def load_markdown_files(data_dir: Path) -> list[Document]:
    if not data_dir.exists():
        raise FileNotFoundError(f"DATA_DIR not found: {data_dir}")

    paths = sorted(p for p in data_dir.rglob("*.md") if p.is_file())
    docs: list[Document] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="ignore")
        docs.append(Document(page_content=text, metadata={"source": str(path)}))
    return docs

