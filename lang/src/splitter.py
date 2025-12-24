from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from config import Settings


def split_markdown_documents(docs: list[Document], settings: Settings) -> list[Document]:
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "h1"),
            ("##", "h2"),
            ("###", "h3"),
            ("####", "h4"),
        ],
        strip_headers=False,
    )
    size_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    chunks: list[Document] = []
    for doc in docs:
        split_by_header = header_splitter.split_text(doc.page_content)
        for piece in split_by_header:
            merged_meta = dict(doc.metadata)
            merged_meta.update(piece.metadata or {})
            piece.metadata = merged_meta

        chunks.extend(size_splitter.split_documents(split_by_header))

    return chunks

