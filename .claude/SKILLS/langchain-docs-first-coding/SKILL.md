---
name: langchain-docs-first-coding
description: Forces Python agents to query LangChain/LangGraph documentation via the `langchain-docs` MCP server or "Docs by LangChain.md" BEFORE writing or editing ANY LangChain/LangGraph code. Ensures correct modern APIs (2025+) and produces verifiable citations.
---

# LangChain Docs–First Coding (Python)

## Purpose

LangChain and LangGraph have undergone major API changes in late 2025.  
Model pretraining is outdated.  
**This skill enforces a strict workflow: discover via docs first → design → write code → verify → cite.**

This ensures correctness, prevents hallucinated APIs, and gracefully adapts to the continuous LangChain/LangGraph evolution.

---

# When to Use This Skill

Use **every time** the task involves Python **LangChain** or **LangGraph**, including:

- Building new agents, graphs, tools, or LCEL components  
- Migrating old code  
- Fixing LangChain errors  
- Designing orchestrations/graphs/tool calls  
- Any code with `import langchain` or `import langgraph`  

**Hard rule:**  
> If LangChain/LangGraph *might* be involved, assume yes and activate this skill.

Do *not* use for:
- Pure Python utilities  
- ML/LLM code not involving LangChain/LangGraph  
- API calls using OpenAI/Anthropic clients directly without LangChain  

---

# Strict Workflow

## 1. Clarify & Scope
Before touching any code:

- Restate the user’s goal  
- Identify environment: **Python only**  
- Note expected components: tools, graphs, LCEL, Runnables, agents, memory, retrievers, etc.  
- If unsure whether LangChain is involved → treat as yes.

---

## 2. Enumerate Unknowns
List **concrete questions that MUST be checked in the docs**, such as:

- What is the *current* recommended way to define a tool?  
- What is the correct import path for `StateGraph` / `MessageGraph`?  
- What does the **2025 update** say about nodes, edges, channels, state typing, etc.?  
- How does LCEL interact with LangGraph now?  
- What arguments are required or deprecated?

These questions become your doc-search checklist.

---

## 3. **REQUIRED**: Query the `langchain-docs` MCP server  
**No imports and no code may be produced until at least one doc query is executed.**

### Protocol:

1. Inspect available tools, choose the **`langchain-docs`** server.
2. Use the search or query method (e.g. `langchain-docs.search`).
3. Perform **targeted** queries — one per unknown from Step 2.

Example:
- `"Python LangGraph StateGraph 2025 update"`
- `"LangChain tools decorator latest"`
- `"LangChain 2025 LCEL graph integration"`
- `"LangChain agent patterns 2025"`

### Required Output

After calling the doc tool, the agent must:

- Summarize relevant findings in bullet points  
- Extract:
  - Correct imports  
  - Function signatures  
  - Required parameters  
  - Best-practice patterns  
  - Deprecated items  
- If nothing appears, explicitly state the gap and label future code as **speculative**.

---

## 4. Plan Code Based on Docs (Before Writing Code)
Use a short bullet list to map the design to the retrieved docs.

Example:
- “Use `StateGraph` from `langgraph.graph` per docs section *XYZ*”  
- “Define tools using the new `@tool` decorator (docs: Tools → Python → Decorator method)”  
- “Graph nodes use the `invoke()` runnable interface (docs: LCEL update 2025)”  

---

## 5. Write Code Incrementally (Python Only)
After planning, write code in **small, validated slices**:

- Begin with imports the docs explicitly confirmed  
- Define tools → graph → edges → compilation → run example  
- Keep code minimal, runnable, and grounded in the doc evidence  
- No speculative APIs unless the docs were missing — clearly label if so

---

## 6. Verify Against Docs
Review code:

- Names, signatures, required args  
- Deprecation notices  
- Recommended usage patterns  
- Graph structure correctness  
- Tool registration & invocation patterns  

If changes are needed based on docs, rewrite.

---

## 7. Cite Sources
At the end of the answer:

### **References**
Use block format:

- `- LangChain docs: "<Page Title>" – section "<Section Name>" (query: "<query>", tool: langchain-docs)`  
- `- LangGraph docs: "<Page Title>" – "<Section>" (query: "...")`  
- `- If speculative: "Docs did not cover <X>. Behavior inferred from <Y> (speculative)."`

---

# Behavioral Tests

## Test 1 – Building a Graph  
**User:** “Create a Python LangGraph that routes between two tools.”

**Expected agent behavior:**
- Activates this skill  
- Lists unknowns (tool creation, routing, imports)  
- Queries `langchain-docs` *before any code*  
- Summarizes guidance  
- Designs graph per docs  
- Writes code  
- Provides a References block  

---

## Test 2 – Updating Old Code  
**User:** “Migrate my old LCEL chain to the new LangChain version.”

**Expected behavior:**
- Detects LangChain → uses this skill  
- Queries docs for migration changes  
- Identifies deprecated classes  
- Produces a refactored version aligned with current docs  
- Includes citations  

---

## Test 3 – Missing Documentation  
**User:** “Integrate LangGraph with a custom orchestrator not referenced in docs.”

**Expected behavior:**
- Searches docs twice  
- Fails to find authoritative information  
- States: “Docs lack direct guidance for <X>”  
- Provides a speculative pattern based on nearby docs  
- Clearly labels speculative content  
- Cites related docs anyway  

