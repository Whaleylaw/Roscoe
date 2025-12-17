"""
Model configurations for the Paralegal Agent.

To change the model provider, edit the MODEL_PROVIDER constant below.
No environment variables needed - just edit this file and redeploy.

Options:
- "anthropic": Claude Sonnet 4.5 (recommended for legal analysis)
- "openai": GPT-5.2 via Responses API (reasoning-heavy tasks, high effort)
- "google": Gemini 3 Pro Preview (multimodal, large context)

OpenAI Configuration (GPT-5.2):
- Uses Responses API (not Chat Completions) for enhanced reasoning control
- reasoning.effort = "high" for deep legal analysis
- text.verbosity = "medium" for balanced output detail

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
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from typing import Any, AsyncIterator, Iterator, Optional

# ============================================================================
# CHANGE THIS TO SWITCH MODELS
# Options: "anthropic", "openai", "google"
# ============================================================================
MODEL_PROVIDER = "openai"
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


class _MessageNormalizingWrapper(Runnable):
    """
    Wrap a Runnable/ChatModel and normalize message inputs before invoking it.

    IMPORTANT:
    We intentionally avoid composing `RunnableLambda | model` because that produces a
    `RunnableSequence`, which does not expose ChatModel conveniences like `.bind_tools()`.
    Some parts of the agent stack expect `.bind_tools()` to exist.
    """

    def __init__(self, inner: Any):
        self._inner = inner

    def bind_tools(self, *args, **kwargs):
        if not hasattr(self._inner, "bind_tools"):
            raise AttributeError(f"{type(self._inner).__name__!r} has no attribute 'bind_tools'")
        return _MessageNormalizingWrapper(self._inner.bind_tools(*args, **kwargs))

    def with_fallbacks(self, *args, **kwargs):
        if not hasattr(self._inner, "with_fallbacks"):
            raise AttributeError(f"{type(self._inner).__name__!r} has no attribute 'with_fallbacks'")
        return _MessageNormalizingWrapper(self._inner.with_fallbacks(*args, **kwargs))

    def invoke(self, inp: Any, config: Optional[dict] = None, **kwargs):
        return self._inner.invoke(_normalize_messages_input(inp), config=config, **kwargs)

    async def ainvoke(self, inp: Any, config: Optional[dict] = None, **kwargs):
        return await self._inner.ainvoke(_normalize_messages_input(inp), config=config, **kwargs)

    def stream(self, inp: Any, config: Optional[dict] = None, **kwargs) -> Iterator[Any]:
        return self._inner.stream(_normalize_messages_input(inp), config=config, **kwargs)

    async def astream(self, inp: Any, config: Optional[dict] = None, **kwargs) -> AsyncIterator[Any]:
        async for chunk in self._inner.astream(_normalize_messages_input(inp), config=config, **kwargs):
            yield chunk

    def __getattr__(self, item: str):
        # Delegate everything else to the inner runnable/model
        return getattr(self._inner, item)


def _stringify_message_content(content) -> str:
    """
    Convert rich content blocks (e.g., OpenAI Responses API parts) into plain text.

    This is important when switching providers mid-thread. Some providers (notably Anthropic)
    reject unknown content part types like {"type": "reasoning"}.
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                # Rare but handle defensively
                parts.append(part)
                continue
            if not isinstance(part, dict):
                continue

            part_type = part.get("type")
            # Drop non-user-facing / provider-specific internal reasoning
            if part_type in {"reasoning", "thinking", "redacted_thinking"}:
                continue

            # OpenAI Responses API: {"type":"text","text":"..."}
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                parts.append(text)
                continue

            # Fallbacks some SDKs may emit
            alt = part.get("content")
            if isinstance(alt, str) and alt.strip():
                parts.append(alt)
                continue

        return "\n".join([p for p in parts if p]).strip()

    # Last resort: stringify
    return str(content)


def _normalize_messages_input(inp):
    """
    Normalize model input so provider SDKs receive valid message formats.

    Supports:
    - list[BaseMessage]
    - dict with {"messages": [...]}
    """
    if isinstance(inp, dict) and "messages" in inp:
        msgs = inp.get("messages")
        if isinstance(msgs, list):
            inp = dict(inp)
            inp["messages"] = _normalize_messages_input(msgs)
            return inp
        return inp

    if not isinstance(inp, list):
        return inp

    normalized: list[BaseMessage | dict] = []
    for m in inp:
        # LangChain message objects
        if isinstance(m, BaseMessage):
            if isinstance(m.content, list):
                # Recreate the message with string content, preserving tool calls/metadata
                normalized.append(
                    m.__class__(
                        content=_stringify_message_content(m.content),
                        additional_kwargs=getattr(m, "additional_kwargs", None) or {},
                        response_metadata=getattr(m, "response_metadata", None) or {},
                        name=getattr(m, "name", None),
                        id=getattr(m, "id", None),
                        tool_calls=getattr(m, "tool_calls", None),
                        invalid_tool_calls=getattr(m, "invalid_tool_calls", None),
                        usage_metadata=getattr(m, "usage_metadata", None),
                    )
                )
            else:
                normalized.append(m)
            continue

        # Dict message format
        if isinstance(m, dict) and isinstance(m.get("content"), list):
            m2 = dict(m)
            m2["content"] = _stringify_message_content(m.get("content"))
            normalized.append(m2)
            continue

        normalized.append(m)

    return normalized


def _wrap_with_message_normalization(model):
    """Ensure messages are sanitized before hitting provider SDKs."""
    return _MessageNormalizingWrapper(model)


def _create_fallback_model():
    """Create the fallback model (Gemini 3 Pro Preview)."""
    return _wrap_with_message_normalization(
        ChatGoogleGenerativeAI(
            model=FALLBACK_MODEL,
            max_retries=3,
            temperature=0,
        )
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
        return _wrap_with_message_normalization(
            ChatAnthropic(
                model_name="claude-sonnet-4-5-20250929",
                max_retries=3,
                temperature=0,
                # Enable 1M token context window (requires tier 4 or custom limits)
                # Default is 200k, this extends to 1,000,000 tokens
                betas=["context-1m-2025-08-07"],
            )
        )
    elif MODEL_PROVIDER == "openai":
        # GPT-5.2 via Responses API with high reasoning effort and medium verbosity
        return _wrap_with_message_normalization(
            ChatOpenAI(
                model="gpt-5.2",
                max_retries=3,
                temperature=0,
                use_responses_api=True,
                reasoning={"effort": "high"},
                model_kwargs={
                    "text": {"verbosity": "medium"},
                },
            )
        )
    elif MODEL_PROVIDER == "google":
        return _wrap_with_message_normalization(
            ChatGoogleGenerativeAI(
                model="gemini-3-pro-preview",
                max_retries=3,
                temperature=0,
            )
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

    ALWAYS uses Gemini 3 Pro Preview for multimodal analysis because it has
    the best native support for audio, video, and image understanding.
    This is independent of MODEL_PROVIDER setting.

    Code execution is enabled via Gemini's built-in code_execution tool,
    allowing the multimodal agent to execute Python code for data processing,
    analysis, and multimedia file manipulation.

    Use this instead of importing multimodal_llm directly to avoid pickle errors
    with LangGraph checkpointing.
    """
    global _multimodal_llm_instance
    if _multimodal_llm_instance is None:
        # Always use Gemini 3 Pro for multimodal - best native video support
        # Code execution enabled for data processing tasks
        # NOTE: Audio transcription uses Whisper (separate tool) since code_execution
        # conflicts with Gemini's audio processing
        _multimodal_llm_instance = ChatGoogleGenerativeAI(
            model="gemini-3-pro-preview",
            max_retries=3,
            temperature=0,
        ).bind_tools([{"code_execution": {}}])
        print("🎬 Multimodal model: Gemini 3 Pro Preview with code execution")
    return _multimodal_llm_instance


def get_summarization_llm():
    """
    Get the summarization LLM (Claude Haiku - fast and cost-effective).

    Used by SummarizationMiddleware to compress conversation history.
    Haiku is ideal for this task: fast, cheap, and good at summarization.
    """
    global _summarization_llm_instance
    if _summarization_llm_instance is None:
        _summarization_llm_instance = _wrap_with_message_normalization(
            ChatAnthropic(
                model_name="claude-haiku-4-5-20251001",
                max_retries=3,
                temperature=0,
            )
        )
        print("📝 Summarization model: Claude Haiku 4.5 (lazy init)")
    return _summarization_llm_instance


_logged_init = False


def _log_model_init(model_name: str):
    """Log model initialization (only once per session)."""
    global _logged_init
    if not _logged_init:
        fallback_status = (
            f" → fallback: {FALLBACK_MODEL}" if ENABLE_FALLBACK and MODEL_PROVIDER != "google" else ""
        )
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
