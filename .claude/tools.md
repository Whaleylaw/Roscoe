# Agent Tools

## Script Execution

Scripts in `/Tools/` run via native Python subprocess on VM.

```python
execute_python_script(
    script_path="/Tools/create_file_inventory.py",
    case_name="Wilson-MVA-2024",
    script_args=["--output", "Reports/result.json"],
    timeout=300
)
```

## Tools Directory

```
/mnt/workspace/Tools/
├── research/              # Tavily web search
├── medical_research/      # PubMed, Semantic Scholar
├── legal_research/        # CourtListener API
├── document_processing/   # PDF extraction
└── reporting/             # Case reports
```

## Skills System

Skills in `/Skills/` folders with `SKILL.md` files. Auto-discovered via semantic matching.

```python
list_skills()      # List all available
refresh_skills()   # Rescan directory
```

## Middleware

| Middleware | Purpose |
|------------|---------|
| CaseContextMiddleware | Detects client names, injects case data from graph |
| WorkflowMiddleware | Injects phase/landmark status |
| SkillSelectorMiddleware | Semantic skill matching |
| UIContextMiddleware | Bridges frontend state |

## Model Configuration

In `src/roscoe/agents/paralegal/models.py`:

```python
MODEL_PROVIDER = "anthropic"  # Options: "anthropic", "openai", "google"
ENABLE_FALLBACK = True
FALLBACK_MODEL = "gemini-3-pro-preview"
```

**Always use getter functions:**
```python
from roscoe.agents.paralegal.models import get_agent_llm, get_multimodal_llm
model = get_agent_llm()  # NOT agent_llm (is None)
```
