"""
Model configurations for the Paralegal Agent.

To change the model provider, edit the MODEL_PROVIDER constant below.
No environment variables needed - just edit this file and redeploy.

Options:
- "anthropic": Claude Sonnet 4.5 (recommended for legal analysis)
- "openai": GPT-5.1 Thinking (reasoning-heavy tasks)
- "google": Gemini 3 Pro Preview (multimodal, large context)

Fallback Configuration:
- When ENABLE_FALLBACK=True, rate limit errors on the primary model
  will automatically fallback to Gemini 3 Pro Preview

IMPORTANT: Models are lazily initialized to avoid pickle errors with LangGraph
checkpointing. Use get_agent_llm(), get_sub_agent_llm(), get_multimodal_llm()
instead of importing the model variables directly.
"""

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# ============================================================================
# CHANGE THIS TO SWITCH MODELS
# Options: "anthropic", "openai", "google"
# ============================================================================
MODEL_PROVIDER = "anthropic"
# ============================================================================

# ============================================================================
# FALLBACK CONFIGURATION
# When enabled, rate limit errors will fallback to the specified model
# ============================================================================
ENABLE_FALLBACK = True
FALLBACK_MODEL = "gemini-3-pro-preview"  # Google's Gemini 3 Pro Preview (Nov 2025)
# ============================================================================

# ============================================================================
# LAZY MODEL INITIALIZATION
# Models are created on first access to avoid pickle errors with LangGraph
# checkpointing. HTTP clients in model objects contain thread locks that
# can't be serialized.
# ============================================================================

_agent_llm_instance = None
_sub_agent_llm_instance = None
_multimodal_llm_instance = None
_summarization_llm_instance = None


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


def _create_primary_model():
    """Create the primary model based on MODEL_PROVIDER."""
    if MODEL_PROVIDER == "anthropic":
        return ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
            max_retries=3,
            temperature=0,
            # Enable 1M token context window (requires tier 4 or custom limits)
            # Default is 200k, this extends to 1,000,000 tokens
            extra_headers={"anthropic-beta": "context-1m-2025-08-07"}
        )
    elif MODEL_PROVIDER == "openai":
        return ChatOpenAI(
            model="gpt-5.1",
            max_retries=3,
            temperature=0
        )
    elif MODEL_PROVIDER == "google":
        return ChatGoogleGenerativeAI(
            model="gemini-3-pro-preview",
            max_retries=3,
            temperature=0
        )
    else:
        raise ValueError(
            f"Unknown MODEL_PROVIDER: '{MODEL_PROVIDER}'. "
            f"Valid options: 'anthropic', 'openai', 'google'"
        )


def get_agent_llm():
    """
    Get the main agent LLM (lazily initialized).
    
    Use this instead of importing agent_llm directly to avoid pickle errors
    with LangGraph checkpointing.
    """
    global _agent_llm_instance
    if _agent_llm_instance is None:
        primary = _create_primary_model()
        _agent_llm_instance = _with_fallback(primary)
        _log_model_init("agent_llm")
    return _agent_llm_instance


def get_sub_agent_llm():
    """
    Get the sub-agent LLM (lazily initialized).
    
    Use this instead of importing sub_agent_llm directly to avoid pickle errors
    with LangGraph checkpointing.
    """
    global _sub_agent_llm_instance
    if _sub_agent_llm_instance is None:
        primary = _create_primary_model()
        _sub_agent_llm_instance = _with_fallback(primary)
        _log_model_init("sub_agent_llm")
    return _sub_agent_llm_instance


def get_multimodal_llm():
    """
    Get the multimodal LLM (lazily initialized).
    
    Use this instead of importing multimodal_llm directly to avoid pickle errors
    with LangGraph checkpointing.
    """
    global _multimodal_llm_instance
    if _multimodal_llm_instance is None:
        primary = _create_primary_model()
        _multimodal_llm_instance = _with_fallback(primary)
        _log_model_init("multimodal_llm")
    return _multimodal_llm_instance


def get_summarization_llm():
    """
    Get the summarization LLM (Claude Haiku - fast and cost-effective).
    
    Used by SummarizationMiddleware to compress conversation history.
    Haiku is ideal for this task: fast, cheap, and good at summarization.
    """
    global _summarization_llm_instance
    if _summarization_llm_instance is None:
        _summarization_llm_instance = ChatAnthropic(
            model="claude-haiku-4-5-20251001",
            max_retries=3,
            temperature=0
        )
        print("📝 Summarization model: Claude Haiku 4.5 (lazy init)")
    return _summarization_llm_instance


_logged_init = False

def _log_model_init(model_name: str):
    """Log model initialization (only once per session)."""
    global _logged_init
    if not _logged_init:
        fallback_status = f" → fallback: {FALLBACK_MODEL}" if ENABLE_FALLBACK and MODEL_PROVIDER != "google" else ""
        print(f"🤖 Model provider: {MODEL_PROVIDER.upper()}{fallback_status} (lazy init)")
        _logged_init = True


# ============================================================================
# BACKWARDS COMPATIBILITY
# These are set to None and should NOT be used directly.
# Use the getter functions instead: get_agent_llm(), get_sub_agent_llm(), etc.
# Keeping these for any legacy imports, but they will be None.
# ============================================================================
agent_llm = None
sub_agent_llm = None
multimodal_llm = None
