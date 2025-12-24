from __future__ import annotations

import argparse

from config import get_settings
from src.embeddings import build_embeddings
from src.llm import build_llm
from src.rag import format_context
from src.vector_store import get_vector_store


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Chat with your local RAG knowledge base (Scheme A).")
    p.add_argument("--k", type=int, default=0, help="Top-k (0 = use TOP_K env/default)")
    return p.parse_args()


SYSTEM_PROMPT = """你是一个智能知识库助手。
请严格根据【背景资料】回答【问题】。
如果【背景资料】里没有答案，请直接回答：知识库中未找到相关信息。
不要编造。"""


def main() -> None:
    args = parse_args()
    settings = get_settings()
    k = args.k if args.k > 0 else settings.top_k

    embeddings = build_embeddings(settings)
    vs = get_vector_store(settings, embeddings)
    llm = build_llm(settings)

    print("RAG Chat（输入 'quit' 退出）:")
    while True:
        q = input("你：").strip()
        if not q:
            continue
        if q.lower() == "quit":
            break

        docs = vs.similarity_search(q, k=k)
        context = format_context(docs)

        prompt = (
            SYSTEM_PROMPT
            + "\n\n【背景资料】\n"
            + context
            + "\n\n【问题】\n"
            + q
        )
        msg = llm.invoke(prompt)

        print("\n助手：", msg.content)
        if docs:
            print("\n来源：")
            for d in docs:
                print("-", d.metadata.get("source", ""))
        print()


if __name__ == "__main__":
    main()

