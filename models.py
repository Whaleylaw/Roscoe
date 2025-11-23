from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

# Define the agent and sub agent models
agent_llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", max_retries=3)
sub_agent_llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", max_retries=3)

# Medical sub-agents use Claude Haiku 4.5 (fast, cost-effective for analysis)
medical_sub_agent_llm = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    max_retries=3,
    temperature=0
)

# Fact investigator uses Google Gemini 3 Pro with native code execution
# Bind code execution tool for Python-based document processing
fact_investigator_llm = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    max_retries=3,
    temperature=0
).bind_tools([{"code_execution": {}}])

# Fallback model for fact investigator - Gemini 2.5 Pro with code execution
# Used if Gemini 3 Pro encounters server errors
fact_investigator_fallback_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    max_retries=3,
    temperature=0
).bind_tools([{"code_execution": {}}])

# Summary writer and causation analyzer use Claude Sonnet 4.5 for complex synthesis
summary_causation_llm = agent_llm  # Reuse Sonnet 4.5 configuration

# Multimodal model for image, audio, and video analysis
# Uses Gemini 3 Pro with native code execution for video summarization
multimodal_llm = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    max_retries=3,
    temperature=0
).bind_tools([{"code_execution": {}}])