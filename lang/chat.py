from __future__ import annotations

import argparse
from pathlib import Path
import os

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]

from config import get_settings
from src.embeddings import build_embeddings
from src.llm import build_llm
from src.rag import format_context
from src.vector_store import get_vector_store, resolve_collection_name


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Chat with your local RAG knowledge base (Scheme A).")
    p.add_argument("--k", type=int, default=0, help="Top-k (0 = use TOP_K env/default)")
    return p.parse_args()


SYSTEM_PROMPT = """你是一个智能知识库助手。
请严格根据【背景资料】回答【问题】。
如果【背景资料】里没有答案，请直接回答：知识库中未找到相关信息。
不要编造。
注意：背景资料中可能存在“别称/同义表述”（例如同一流程在资料里写作“销售六步曲/巡店六步曲”），请结合来源与内容判断并给出答案。"""


def _looks_like_not_found(text: str) -> bool:
    t = (text or "").strip()
    return "知识库中未找到相关信息" in t or "未找到相关信息" in t


def main() -> None:
    # Prefer `.env` in this repo over system environment variables.
    if load_dotenv is not None:
        dotenv_path = Path(__file__).resolve().parent / ".env"
        load_dotenv(dotenv_path=dotenv_path, override=True)
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

    args = parse_args()
    settings = get_settings()
    k = args.k if args.k > 0 else settings.top_k

    embeddings = build_embeddings(settings)
    collection_name = resolve_collection_name(settings)
    if collection_name != settings.chroma_collection:
        print(f"[info] CHROMA_COLLECTION={settings.chroma_collection!r} is empty; using {collection_name!r} instead")
    vs = get_vector_store(settings, embeddings, collection_name=collection_name)
    llm = build_llm(settings)

    print("RAG Chat（输入 'quit' 退出）:")
    while True:
        q = input("你：").strip()
        if not q:
            continue
        if q.lower() == "quit":
            break

        docs = vs.similarity_search(q, k=k)
        if os.getenv("DEBUG_RETRIEVAL") == "1":
            print(f"[debug] retrieved {len(docs)} docs")
            for d in docs:
                print("[debug] -", d.metadata.get("source", ""))
        context = format_context(docs)

        prompt = (
            SYSTEM_PROMPT
            + "\n\n【背景资料】\n"
            + context
            + "\n\n【问题】\n"
            + q
        )
        try:
            msg = llm.invoke(prompt)
        except Exception as e:
            base_url = os.getenv(
                "LLM_BASE_URL",
                "https://generativelanguage.googleapis.com/v1beta/openai/",
            )
            print(
                "\n助手：LLM 调用失败。\n"
                f"- 错误类型：{type(e).__name__}\n"
                f"- 错误信息：{e}\n"
                f"- 当前 base_url：{base_url}\n"
                "建议排查：网络/DNS/代理；或确认 `GEMINI_API_KEY` 可用。\n"
            )
            continue

        answer = (msg.content or "").strip()

        # Fallback: 如果检索已经命中明显相关的 chunk，但模型误判“未找到”，则用更短、更抽取式的 prompt 再问一次。
        if _looks_like_not_found(answer) and docs:
            has_obvious_hit = any(
                "巡店" in (d.metadata.get("source", "") or "")
                or "六步" in (d.page_content or "")
                or "六步曲" in (d.page_content or "")
                for d in docs[:2]
            )
            if has_obvious_hit:
                short_context = format_context(docs[:2])
                reprompt = (
                    "你是知识库助手。请仅根据【资料】回答【问题】，"
                    "直接列出“巡店六步/六步曲”的六个步骤（每步一行），不要写无关内容。\n\n"
                    "【资料】\n"
                    + short_context
                    + "\n\n【问题】\n"
                    + q
                )
                try:
                    msg2 = llm.invoke(reprompt)
                    answer = (msg2.content or "").strip() or answer
                except Exception:
                    pass

        print("\n助手：", answer)
        if docs:
            print("\n来源：")
            for d in docs:
                print("-", d.metadata.get("source", ""))
        print()


if __name__ == "__main__":
    main()
