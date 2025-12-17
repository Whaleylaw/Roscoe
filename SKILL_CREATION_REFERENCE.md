# Skill Creation Reference for Roscoe

## What is a Skill?

A **skill** is a modular, self-contained package that extends the AI agent's capabilities with specialized knowledge, workflows, or tool integrations.

**Think of skills as "onboarding guides"** - they transform Claude from a general-purpose agent into a specialized agent equipped with procedural knowledge.

### Skills Provide

1. **Specialized workflows** - Multi-step procedures for specific domains
2. **Tool integrations** - Instructions for working with specific file formats or APIs
3. **Domain expertise** - Company-specific knowledge, schemas, business logic
4. **Bundled resources** - Scripts, references, and assets for complex tasks

---

## Roscoe vs Anthropic Skills

### Anthropic API Skills

**Discovery method**: YAML frontmatter passed in API request
```yaml
---
name: xlsx
description: "Comprehensive spreadsheet creation..."
---
# XLSX creation, editing, and analysis
[skill content]
```

Skills are explicitly declared in the API call:
```python
response = client.beta.messages.create(
    container={
        "skills": [{"type": "anthropic", "skill_id": "xlsx"}]
    }
)
```

### Roscoe Skills

**Discovery method**: Dynamic semantic search via `SkillSelectorMiddleware`

**Structure**:
```json
// skills_manifest.json
{
  "name": "complaint-drafting",
  "description": "Use when drafting initial complaint...",
  "file": "litigation-pleadings/complaint-drafting-skill.md",
  "triggers": ["draft complaint", "file lawsuit", ...],
  "model_required": "sonnet"
}
```

**How it works**:
1. User query: "I need to draft a complaint"
2. Middleware embeds query + all skill descriptions
3. Computes cosine similarity
4. Loads top-matching skill's markdown into system prompt
5. Agent executes with skill guidance

**Key difference**: Skills are discovered automatically based on semantic matching, not explicit declaration. But the skill content and execution is identical to Anthropic's approach.

---

## Skill Anatomy

### Required: Skill Markdown File

**Location**: `Skills/{category}/{skill-name}.md` or `Skills/{category}/skill.md`

**Format** (for Anthropic - YAML frontmatter):
```markdown
---
name: skill-name
description: "When Claude needs to..."
---

# Skill Content

[Instructions here]
```

**Format** (for Roscoe - no YAML, registered in manifest):
```markdown
# Skill: Skill Name

## Purpose
[What this skill does]

## When to Use
[Trigger conditions]

## Step-by-Step Process

### Step 1: [Task]
**Use skill: sub-skill-name** (if applicable)

1. Do this
2. Do that

[Instructions here]
```

### Required: Manifest Entry (Roscoe Only)

**Location**: `Skills/skills_manifest.json`

**Entry structure**:
```json
{
  "name": "skill-name",
  "description": "Use when [trigger scenarios] - [what it does]",
  "file": "category/skill-name.md",
  "triggers": ["keyword1", "keyword2", "phrase"],
  "model_required": "sonnet",
  "canonical_phase": "phase_name",
  "canonical_workflow": "workflow_name",
  "tools_required": ["/Tools/tool.py"],
  "templates_available": ["/forms/template.md"],
  "output_location": "/path/to/output.ext"
}
```

**Critical fields**:
- `name`: Unique identifier
- `description`: Rich description for semantic matching (100-200 words)
- `file`: Path to skill markdown
- `triggers`: Keywords that should activate this skill
- `model_required`: "sonnet", "haiku", or "gemini-3-pro"

---

## Writing Effective Skills

### 1. Be Concise

**Anthropic guideline**: "Default assumption: Claude is already very smart"

❌ **Bad** (over-explaining):
```markdown
## What is a Complaint?
A complaint is a legal document filed with a court to initiate
a lawsuit. It contains factual allegations and legal claims...
[5 paragraphs explaining what a complaint is]
```

✅ **Good** (assumes intelligence):
```markdown
## Step 1: Analyze Case Type
Determine primary cause of action:
- MVA: Motor vehicle negligence
- Premises: Slip/fall, dangerous condition
- Product: Defective product
```

### 2. Set Appropriate Degrees of Freedom

**Match specificity to task complexity**:

**High freedom** (text instructions):
```markdown
### Step 2: Draft Liability Section
Explain how defendant was negligent:
- State duty owed
- Describe breach
- Connect to damages
```

**Medium freedom** (pseudocode with parameters):
```markdown
### Step 3: Calculate Damages
```python
total_specials = medical_bills + lost_wages + property_damage
pain_suffering = total_specials * multiplier  # 2-5x typical
total_demand = total_specials + pain_suffering
```
Use multiplier based on injury severity.
```

**Low freedom** (specific script):
```markdown
### Step 4: Generate PDF
Run the complaint generator script:
```bash
python /Tools/complaints/generate_complaint.py \
  --template "$TEMPLATE" \
  --case "$CASE_NAME" \
  --output "/Litigation/Pleadings/complaint.pdf"
```
```

### 3. Use Progressive Disclosure

**Keep main skill file under 500 lines**.

Split complex content:

**SKILL.md** (main file, ~300 lines):
```markdown
# Skill: Medical Chronology

## Overview
Create comprehensive medical timeline from records.

## Process
[High-level steps]

## For detailed medical term research
See: `references/medical_terminology.md`

## For causation analysis guidelines
See: `references/causation_framework.md`
```

**references/medical_terminology.md** (loaded as needed):
```markdown
[10,000 lines of medical terminology]
```

**scripts/chronology_generator.py** (executed, not loaded):
```python
# Script that runs without context window cost
```

### 4. Structure Skills Clearly

**Recommended structure**:

```markdown
# Skill: [Name]

## Purpose
[One paragraph: what this skill does]

## When to Use
[Bullet list of trigger conditions]

## Prerequisites
[What must exist before using this skill]

## Step-by-Step Process

### Step 1: [Task Name]
**Use skill: related-skill** (if delegating to another skill)

1. Do X
2. Do Y
3. Check Z

### Step 2: [Next Task]
[Instructions]

## Skills Used
- **sub-skill-1**: What it does in this context
- **tool-name**: How it's used

## Completion Criteria
- [ ] Checklist item 1
- [ ] Checklist item 2

## Outputs
- File 1: Description
- File 2: Description

## Data Updates (if applicable)
```json
{
  "field_name": "value to update"
}
```
```

### 5. Write for Execution, Not Education

**Education content** (belongs in `references/`):
```markdown
## Kentucky Rules of Civil Procedure

CR 26.02(1) states that discovery may be had of any
non-privileged matter that is relevant to the claim or defense...

[15 pages of rule explanations, case law, examples]
```

**Execution content** (belongs in main skill):
```markdown
## Step 3: Check Discovery Scope
Verify request is proper under CR 26.02(1):
- [ ] Relevant to claim/defense
- [ ] Not privileged
- [ ] Proportional to case needs

For detailed rule analysis, see: `references/kentucky_discovery_rules.md`
```

---

## Skill Directory Structure (Roscoe)

```
Skills/
├── skills_manifest.json          # Registry (discovery)
│
├── {category}/                   # Skill category
│   ├── skill.md                  # Main skill (if simple)
│   ├── {skill-name}-skill.md     # Individual skills
│   ├── references/               # Detailed docs (optional)
│   │   ├── reference1.md
│   │   └── reference2.md
│   ├── scripts/                  # Executable code (optional)
│   │   └── script.py
│   └── assets/                   # Templates, files (optional)
│       └── template.docx
│
└── sub-agents/                   # Sub-agent skill definitions
    └── sub-skill-name.md
```

### Examples from Roscoe

**Simple skill** (single file):
```
Skills/
└── calendar-scheduling/
    └── skill.md              # All instructions in one file
```

**Complex skill** (multiple files):
```
Skills/
└── medical-records-analysis/
    ├── skill.md              # Main orchestration logic
    └── references/
        ├── medical_terminology.md
        └── causation_framework.md
```

**Skill with assets**:
```
Skills/
└── litigation-pleadings/
    ├── complaint-drafting-skill.md    # Main skill
    └── templates/                      # Referenced templates
        ├── mva_standard.md             # (Could be here or in /forms/)
        └── premises.md
```

---

## Skill Triggers (Roscoe-Specific)

In Anthropic, skills are explicitly declared. In Roscoe, skills are **automatically discovered** via triggers.

### Good Triggers

✅ **Specific task phrases**:
```json
"triggers": [
  "draft complaint",
  "file lawsuit",
  "complaint drafting",
  "write complaint"
]
```

✅ **Domain terminology**:
```json
"triggers": [
  "interrogatories",
  "requests for production",
  "discovery requests",
  "RPD"
]
```

✅ **Action + object combinations**:
```json
"triggers": [
  "medical chronology",
  "treatment timeline",
  "chronology report"
]
```

### Bad Triggers

❌ **Too generic** (matches everything):
```json
"triggers": ["case", "lawsuit", "legal"]
```

❌ **Too specific** (never matches):
```json
"triggers": ["draft a Jefferson Circuit Court MVA complaint with UM/UIM and bad faith claims"]
```

### Trigger Strategy

**Coverage**: 5-15 triggers per skill
**Mix**:
- 3-5 core phrases (main ways users ask)
- 3-5 synonyms (alternate wordings)
- 2-5 domain terms (technical vocabulary)

**Example** (complaint-drafting):
```json
"triggers": [
  "draft complaint",        // Core phrase
  "file lawsuit",           // Core phrase
  "write complaint",        // Synonym
  "prepare complaint",      // Synonym
  "litigation complaint",   // Domain term
  "petition",               // Domain term (KY uses "petition")
  "complaint template"      // Related term
]
```

---

## Skill Best Practices (from Anthropic)

### 1. Name Skills with Gerund Form

✅ Good: "processing-pdfs", "drafting-complaints", "analyzing-medical-records"
❌ Bad: "pdf-processor", "complaint-drafter", "medical-analysis"

**Reasoning**: Gerund emphasizes the action/process

### 2. Write Descriptions in Third Person

✅ Good: "Use when drafting complaints for litigation..."
❌ Bad: "I help you draft complaints..."

### 3. Assume Claude is Smart

Only include what Claude doesn't know:
- Your specific templates
- Your firm's procedures
- Your database schemas
- Your tool locations

Don't include:
- General legal concepts
- Common sense procedures
- Things Claude already knows

### 4. Use Checklists for Validation

```markdown
## Completion Criteria
- [ ] All parties correctly identified
- [ ] Jurisdictional allegations sufficient
- [ ] All elements alleged
- [ ] Jury demand included
```

### 5. Link to Related Resources

```markdown
## Related Workflows
- file_complaint.md - Next step after drafting

## Related Skills
- service-of-process - For serving complaint

## Templates Available
- /forms/complaints/mva_standard.md
- /forms/complaints/premises.md
```

---

## Common Patterns

### Pattern 1: Template Selection Skill

```markdown
# Skill: Template Selection

## Step 1: Analyze Requirements
Determine:
- Case type
- Claims involved
- Special circumstances

## Step 2: Select Template
Based on analysis:
| Case | Template |
|------|----------|
| MVA standard | template1.md |
| MVA with UM | template2.md |

## Step 3: Apply Template
Populate fields with case data
```

### Pattern 2: Multi-Phase Skill

```markdown
# Skill: Medical Records Analysis

## Phase 1: Organization
Inventory all records

## Phase 2: Extraction
Extract visit data from each record
**Sub-skill**: record-extraction

## Phase 3: Synthesis
Compile into chronology
**Sub-skill**: chronology-generation
```

### Pattern 3: Tool Integration Skill

```markdown
# Skill: Court Docket Monitoring

## Tool Available
`/Tools/kyecourts_docket.py`

## Process
1. Identify case number
2. Run tool:
```bash
python /Tools/kyecourts_docket.py \
  --county "JEFFERSON" \
  --case-number "25-CI-000133"
```
3. Parse results
4. Update tracking
```

---

## Anti-Patterns to Avoid

### ❌ Don't Offer Too Many Options

**Bad**:
```markdown
You could:
- Option A: Do this
- Option B: Or do that
- Option C: Maybe this
- Option D: Possibly that
[10 more options]
```

**Good**:
```markdown
Based on case type:
- MVA → Use template A
- Premises → Use template B
```

### ❌ Don't Duplicate Information

**Bad**:
```markdown
# SKILL.md
[Full Kentucky discovery rules - 50 pages]

# references/discovery_rules.md
[Same Kentucky discovery rules - 50 pages]
```

**Good**:
```markdown
# SKILL.md
Check if proper under CR 26.02(1) (see references/discovery_rules.md for details)

# references/discovery_rules.md
[Full Kentucky discovery rules - 50 pages]
```

### ❌ Don't Create Auxiliary Documentation

**Bad**:
```
skill-name/
├── SKILL.md
├── README.md           ← Don't create
├── INSTALLATION.md     ← Don't create
├── CHANGELOG.md        ← Don't create
└── QUICKSTART.md       ← Don't create
```

**Good**:
```
skill-name/
├── SKILL.md            ← Only this
└── references/         ← (if needed)
    └── detail.md
```

---

## Creating a Skill in Roscoe (Step-by-Step)

### Step 1: Create Skill Directory

```bash
mkdir -p Skills/{category}
```

### Step 2: Write Skill Markdown

```bash
# Create Skills/{category}/{skill-name}-skill.md

---
# Skill: Skill Name

## Purpose
[What this skill does]

## When to Use
- [Trigger condition 1]
- [Trigger condition 2]

## Step-by-Step Process

### Step 1: [Task]
[Instructions]

## Completion Criteria
- [ ] Item 1
- [ ] Item 2

## Outputs
- File or data produced
---
```

**Keep under 500 lines!** If longer, split into references/.

### Step 3: Register in Manifest

```bash
# Edit Skills/skills_manifest.json

{
  "skills": [
    ...existing skills...,
    {
      "name": "skill-name",
      "description": "Use when [scenarios] - [what it does]",
      "file": "category/skill-name-skill.md",
      "triggers": ["trigger1", "trigger2", "trigger3"],
      "model_required": "sonnet"
    }
  ]
}
```

### Step 4: Test Discovery

```python
# Test if skill is discovered
from roscoe.core.skill_middleware import SkillSelectorMiddleware

middleware = SkillSelectorMiddleware(
    skills_dir="workspace_paralegal/Skills",
    manifest_path="workspace_paralegal/Skills/skills_manifest.json"
)

# This would happen automatically in agent, but testing:
query = "I need to draft a complaint"
# Middleware would find "complaint-drafting" skill
```

### Step 5: Test Execution

Run the agent with a query that should trigger the skill and verify:
- Skill loads into context
- Agent follows skill instructions
- Outputs are created correctly

---

## Skill Content Guidelines

### What to Include

✅ **Your specific procedures**
```markdown
## Step 2: Select Template
Based on case type:
- MVA → /forms/complaints/mva_standard.md
- Premises → /forms/complaints/premises.md
```

✅ **Your tool locations**
```markdown
## Tools Available
- /Tools/kyecourts_docket.py - Fetch docket data
```

✅ **Your data schemas**
```markdown
## Output Format
```json
{
  "complaint_filed_date": "YYYY-MM-DD",
  "case_number": "XX-CI-XXXXXX"
}
```
```

✅ **Your workflow references**
```markdown
## Related Workflow
After completion, proceed to:
→ /workflow_engine/workflows/phase_6_litigation/file_complaint.md
```

### What NOT to Include

❌ **General knowledge Claude already has**
```markdown
## What is Negligence?
Negligence is a failure to exercise reasonable care...
[Legal textbook content]
```

❌ **Over-explaining obvious steps**
```markdown
## How to Read a File
First, you need to understand what a file is. A file is...
Then, to open a file, you use the Read tool...
```

❌ **Time-sensitive information**
```markdown
## Current Rules (as of 2024)
[These will be outdated]
```

---

## Examples: Good vs Bad

### Example: Complaint Drafting Skill

#### ❌ Bad (Too verbose, over-explains)

```markdown
---
name: complaint-drafting
description: Drafting complaints
---

# Complaint Drafting

## Introduction
In the legal system, a complaint is the initial pleading that starts a lawsuit.
It is filed with the court and served on the defendant. The complaint must allege
facts that, if true, would entitle the plaintiff to relief.

## What is a Complaint?
A complaint contains several key components:
1. Caption - This identifies the parties and the court
2. Jurisdictional Statement - This explains why the court has jurisdiction
3. Factual Allegations - This is where you tell the story
4. Counts - These are the legal claims
5. Prayer for Relief - This is what you're asking for

[Continues for 2000 lines explaining legal basics]

## How to Draft
First, you need to understand the facts of the case. Ask the user questions...
[Another 1000 lines of obvious procedural steps]
```

#### ✅ Good (Concise, assumes intelligence)

```markdown
# Skill: Complaint Drafting

## Purpose
Draft initial complaint by analyzing case type/claims and applying appropriate template.

## When to Use
- Filing lawsuit
- Demand rejected
- SOL approaching

## Step 1: Analyze Case

Determine:
- Type: MVA, premises, product
- Claims: Negligence, bad faith, UM/UIM, vicarious liability

## Step 2: Select Template

| Case Type | Claims | Template |
|-----------|--------|----------|
| MVA | Simple negligence | /forms/complaints/mva_standard.md |
| MVA | + UM/UIM | /forms/complaints/mva_um.md |
| MVA | + Vicarious | /forms/complaints/mva_respondeat.md |
| Premises | Standard | /forms/complaints/premises.md |
| Premises | Dog bite | /forms/complaints/premises_dog.md |

## Step 3: Populate Template

Required fields:
- {{PLAINTIFF_NAME}}
- {{DEFENDANT_NAME}}
- {{INCIDENT_DATE}}
- {{INCIDENT_LOCATION}}
- {{INJURIES_DESCRIPTION}}
- {{TOTAL_DAMAGES}}

## Step 4: Verify Elements

Kentucky fact pleading requires:
- [ ] Specific facts (not conclusions)
- [ ] All elements alleged (duty, breach, causation, damages)
- [ ] Jury demand included

## Output
`/Litigation/Pleadings/complaint_draft.docx`

## Related Workflow
→ /workflow_engine/workflows/phase_6_litigation/file_complaint.md
```

---

## Skill vs Workflow vs Tool

### Skill
- **What**: Comprehensive guidance for a task domain
- **Size**: 100-500 lines (+ optional references)
- **Contains**: Procedures, decision trees, templates, examples
- **Example**: complaint-drafting-skill.md (how to draft any type of complaint)

### Workflow
- **What**: Simple checklist for specific workflow execution
- **Size**: 50-200 lines
- **Contains**: Steps with skill references
- **Example**: file_complaint.md (checklist: draft → file → serve)

### Tool
- **What**: Executable script
- **Size**: Code file
- **Contains**: Python/bash that does specific task
- **Example**: kyecourts_docket.py (fetches docket from eCourts)

### Relationship

```
User: "Draft complaint for Amy Mills"
    ↓
Skill Selector: Loads "complaint-drafting" skill
    ↓
Skill: Analyzes case (premises liability)
       Selects template (/forms/complaints/premises.md)
       Guides drafting process
    ↓
Agent: Creates draft complaint
    ↓
Workflow: file_complaint.md
    ↓
Tools: /Tools/docx/generate.py (if needed for automation)
```

---

## Testing Skills

### 1. Semantic Matching Test

Does the skill description + triggers match user queries?

```
Query: "I need to draft a complaint"
Should match: complaint-drafting ✓

Query: "Create a medical timeline"
Should match: medical-chronology ✓

Query: "What's the case status?"
Should NOT match: complaint-drafting ✓
```

### 2. Execution Test

Does the skill provide clear guidance?

- Load skill manually into prompt
- Ask Claude to follow it
- Verify output is correct

### 3. Integration Test

Does the skill integrate properly?

- Tools referenced exist?
- Templates referenced exist?
- Workflows referenced exist?
- Data fields exist in schema?

---

## Roscoe Skill Checklist

When creating a skill in Roscoe:

- [ ] **Skill file created** in `Skills/{category}/`
- [ ] **Under 500 lines** (or split into references/)
- [ ] **Concise** (assumes Claude is smart)
- [ ] **Clear structure** (Purpose, When to Use, Steps, Outputs)
- [ ] **Manifest entry** added to `skills_manifest.json`
- [ ] **Good triggers** (5-15 relevant keywords/phrases)
- [ ] **Description** is rich (for semantic matching)
- [ ] **Tools/templates referenced** exist and have correct paths
- [ ] **Related workflows** linked
- [ ] **Model specified** (sonnet/haiku/gemini)
- [ ] **Tested** (verify discovery and execution)

---

## Quick Reference

**To create a skill**:
1. Write markdown file (Skills/{category}/skill-name.md)
2. Add to skills_manifest.json
3. Test with agent

**To write skill content**:
- Be concise (assume Claude is smart)
- Use progressive disclosure (main skill < 500 lines)
- Provide clear steps with skill/tool references
- Include checklists for validation
- Link to templates, tools, workflows

**To make discoverable**:
- Rich description (100-200 words)
- Good triggers (5-15 keywords)
- Semantic relevance (matches how users ask)

That's it! Skills extend the agent's capabilities through focused, well-structured guidance.
