"""
Model configurations for the Second Brain Agent.

Uses lazy initialization to avoid pickle errors with LangGraph checkpointing.
Defaults to Claude Sonnet with Gemini fallback.
"""

from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI


# Model configuration
MODEL_PROVIDER = "anthropic"
ENABLE_FALLBACK = True
FALLBACK_MODEL = "gemini-3-pro-preview"


# Lazy-initialized instances
_agent_llm_instance = None
_classification_llm_instance = None


def _create_fallback_model():
    """Create the fallback model (Gemini 3 Pro Preview)."""
    return ChatGoogleGenerativeAI(
        model=FALLBACK_MODEL,
        max_retries=3,
        temperature=0
    )


def _with_fallback(primary_model):
    """Wrap a model with fallback support if enabled."""
    if ENABLE_FALLBACK and MODEL_PROVIDER != "google":
        fallback = _create_fallback_model()
        return primary_model.with_fallbacks([fallback])
    return primary_model


def get_agent_llm():
    """
    Get the main agent LLM (lazily initialized).

    Uses Claude Sonnet for the main agent interactions.
    """
    global _agent_llm_instance
    if _agent_llm_instance is None:
        primary = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
            max_retries=3,
            temperature=0,
        )
        _agent_llm_instance = _with_fallback(primary)
        print("🧠 Second Brain model: Claude Sonnet 4.5 (lazy init)")
    return _agent_llm_instance


def get_classification_llm():
    """
    Get the classification LLM (Claude Haiku - fast and cheap).

    Used for auto-detecting capture opportunities.
    """
    global _classification_llm_instance
    if _classification_llm_instance is None:
        _classification_llm_instance = ChatAnthropic(
            model="claude-haiku-4-5-20251001",
            max_retries=2,
            temperature=0
        )
        print("🏷️ Classification model: Claude Haiku 4.5 (lazy init)")
    return _classification_llm_instance
