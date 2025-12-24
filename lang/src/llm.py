from __future__ import annotations

import os

from config import Settings
from langchain_google_genai import ChatGoogleGenerativeAI


def build_llm(settings: Settings) -> ChatGoogleGenerativeAI:
    api_key = os.getenv(settings.gemini_api_key_env)
    if not api_key:
        raise RuntimeError(f"Missing env var: {settings.gemini_api_key_env}")
    return ChatGoogleGenerativeAI(api_key=api_key, model=settings.gemini_model)

