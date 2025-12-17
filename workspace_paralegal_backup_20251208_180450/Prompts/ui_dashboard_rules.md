# UI Dashboard vs Case Card Rules

When displaying case information visually, choose the appropriate UI type:

## Dashboard vs Case Card

| Type | When to Use | Data Source | Tool Calls |
|------|-------------|-------------|------------|
| **Dashboard** | Default when context is auto-injected, or user asks to "talk about" / "show" a client | ONLY injected context | ZERO additional tool calls |
| **Case Card** | User specifically asks for "case card" or "detailed view" or "deep dive" | May fetch additional details from files | OK to make tool calls |

## Dashboard Examples (NO extra tool calls)

- "Let's talk about Abby Sitgraves" → Auto-inject context → Generate dashboard immediately
- "Show me the Wilson case" → Auto-inject context → Generate dashboard immediately  
- "What's happening with McCay?" → Auto-inject context → Generate dashboard immediately

## Case Card Examples (MAY fetch more)

- "Show me a detailed case card for Abby Sitgraves" → May fetch additional files
- "Give me a deep dive on the Wilson case" → May fetch medical records, litigation status, etc.

## Auto-Generate UI Instruction

When case context has been automatically loaded, you SHOULD:

1. **DO NOT make additional tool calls** to fetch case information - it's already available!
2. **Call `render_ui_script`** to display this information visually
3. Use the appropriate UI script based on what the user asked for

## Available UI Scripts (call via `render_ui_script`)

- `UI/case_dashboard.py` - Full case dashboard with all sections
- `UI/case_snapshot.py` - Quick case summary (client, status, financials)
- `UI/medical_overview.py` - Medical providers with document links
- `UI/insurance_overview.py` - Insurance coverage with documents
- `UI/liens.py` - All liens for the case
- `UI/expenses.py` - All expenses for the case
- `UI/negotiations.py` - Active negotiations

Example: `render_ui_script("UI/case_dashboard.py", ["--project-name", "Client-Name"])`

If user just mentions a case without specific request, use `case_dashboard.py` for a comprehensive view.

