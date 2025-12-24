from __future__ import annotations

from langchain_core.documents import Document


def format_context(docs: list[Document]) -> str:
    parts: list[str] = []
    for i, d in enumerate(docs, start=1):
        source = d.metadata.get("source", "")
        h1 = d.metadata.get("h1")
        h2 = d.metadata.get("h2")
        h3 = d.metadata.get("h3")
        header = " / ".join([x for x in [h1, h2, h3] if x])
        prefix = f"[{i}] {source}"
        if header:
            prefix += f" ({header})"
        parts.append(prefix + "\n" + d.page_content.strip())
    return "\n\n---\n\n".join(parts)

