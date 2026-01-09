"""
Model configuration for Medical Records Analysis Agent.

Uses Claude Sonnet for analysis tasks with fallback to Gemini.
Lazy initialization to avoid pickle errors with LangGraph checkpointing.
"""

from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI


# ============================================================================
# MODEL CONFIGURATION
# ============================================================================
PRIMARY_MODEL = "claude-sonnet-4-5-20250929"
FALLBACK_MODEL = "gemini-3-flash-preview"
ENABLE_FALLBACK = True
# ============================================================================


_agent_llm_instance = None


def _create_fallback_model():
    """Create fallback model (Gemini Flash)."""
    return ChatGoogleGenerativeAI(
        model=FALLBACK_MODEL,
        max_retries=3,
        temperature=0
    )


def _with_fallback(primary_model):
    """Wrap primary model with fallback support."""
    if ENABLE_FALLBACK:
        fallback = _create_fallback_model()
        return primary_model.with_fallbacks([fallback])
    return primary_model


def get_agent_llm():
    """
    Get the medical records analysis agent LLM (lazily initialized).

    Uses Claude Sonnet with Gemini Flash fallback for rate limit handling.
    """
    global _agent_llm_instance
    if _agent_llm_instance is None:
        primary = ChatAnthropic(
            model=PRIMARY_MODEL,
            max_retries=3,
            temperature=0,
            max_tokens=16000,
        )
        _agent_llm_instance = _with_fallback(primary)
        print(f"[MEDICAL_RECORDS] Model initialized: {PRIMARY_MODEL}")
    return _agent_llm_instance
