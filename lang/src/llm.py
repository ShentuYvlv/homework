from __future__ import annotations

import os

from config import Settings
from langchain_openai import ChatOpenAI


def build_llm(settings: Settings) -> ChatOpenAI:
    api_key = os.getenv(settings.gemini_api_key_env)
    if not api_key:
        raise RuntimeError(f"Missing env var: {settings.gemini_api_key_env}")

    base_url = os.getenv(
        "LLM_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    return ChatOpenAI(api_key=api_key, base_url=base_url, model=settings.gemini_model)

