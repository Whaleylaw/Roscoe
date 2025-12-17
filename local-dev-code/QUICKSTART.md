# Quick Start - Local Development

## Prerequisites

You now have everything needed to run locally:
- ✅ `local-dev-code/` - Source code
- ✅ `workspace_paralegal/` - Workspace (Tools, Skills, Database)

## Step 1: Install Dependencies

```bash
cd "/Volumes/X10 Pro/Roscoe/local-dev-code"

# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

## Step 2: Configure Environment

```bash
# Copy your existing .env from parent directory
cp ../.env .env

# Or create from example
cp .env.example .env
nano .env  # Add your API keys
```

Required keys:
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `TAVILY_API_KEY`
- `LANGSMITH_API_KEY`

## Step 3: Set Workspace Path

The code now automatically uses the workspace_paralegal in the repo root:

```bash
# No config needed! It uses:
# WORKSPACE_DIR env var (if set), or
# Falls back to: /Volumes/X10 Pro/Roscoe/workspace_paralegal
```

## Step 4: Run LangGraph Dev Server

```bash
cd "/Volumes/X10 Pro/Roscoe/local-dev-code"
langgraph dev
```

**Server URL**: http://localhost:2024

## Step 5: Test

Open browser to LangGraph Studio, or test via API:

```bash
curl -X POST http://localhost:2024/threads \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What'"'"'s the status of James Lanier"}
    ]
  }'
```

## Expected Behavior

With the bug fixes:
- ✅ Case context middleware prioritizes "James Lanier" (full name)
- ✅ Workflow state computer uses correct workspace path
- ✅ Loads case data from `../workspace_paralegal/Database/`
- ✅ Computes workflow state with blockers and next actions

## Troubleshooting

### "No module named 'roscoe'"
```bash
cd local-dev-code
pip install -e .
```

### "CaseData not found"
Check that workspace_paralegal exists:
```bash
ls -la ../workspace_paralegal/Tools/_adapters/case_data.py
```

### "Database not found"
Verify database files exist:
```bash
ls -lh ../workspace_paralegal/Database/
```

## Testing Specific Features

### Test Case Context Detection
```bash
# Query with client name
curl -X POST http://localhost:2024/assistants/roscoe_paralegal/threads \
  -d '{"messages": [{"role": "user", "content": "Status of Caryn McCay"}]}'
```

### Test Workflow State Computer
```bash
cd ..
python -c "
import sys
sys.path.insert(0, 'workspace_paralegal/Tools')
from roscoe.core.workflow_state_computer import compute_workflow_state

state = compute_workflow_state('James-Lanier-MVA-6-28-2025')
print(state.formatted_status)
"
```
