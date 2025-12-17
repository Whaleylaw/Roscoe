---
name: discovery-drafting
description: >
  Draft written discovery for Kentucky personal injury litigation. Creates
  interrogatories, requests for production, and requests for admission.
  Use when propounding discovery on defendants to obtain liability facts,
  insurance information, witness details, and documents.
---

# Discovery Drafting Skill

## Overview

Generate properly formatted Kentucky written discovery requests for personal injury cases.

## When to Use

Use when:
- Propounding discovery on defendant
- Need interrogatories, RFPs, or RFAs
- Must comply with Kentucky Civil Rules

DO NOT use if:
- Responding to discovery (use discovery-response skill)
- Drafting subpoenas to third parties

## Workflow

### Step 1: Identify Discovery Goals

| Category | What to Request |
|----------|-----------------|
| Liability | Witness info, statements, facts |
| Insurance | Policies, limits, coverage |
| Documents | Reports, photos, records |
| Damages | Defendant's contentions |

### Step 2: Select Discovery Type

| Type | Best For |
|------|----------|
| Interrogatories | Facts, contentions, identification |
| RFPs | Documents, tangible things |
| RFAs | Undisputed facts, authenticity |

**See:** `references/interrogatory-templates.md` for standard questions.

### Step 3: Draft with Proper Format

- Include definitions and instructions
- Number requests sequentially
- Stay within Kentucky limits (30 interrogatories)

**See:** `references/rfp-templates.md` for document requests.

### Step 4: Verify Compliance

- Check local rules
- Ensure proper service method
- Calculate response deadline

## Output Format

```markdown
## Discovery Request: [Type]

**To:** [Defendant Name]
**Served:** [Date]
**Response Due:** [Date + 30 days]

[Formatted discovery document]
```

## Related Skills

- `discovery-response` - For responding to their discovery
- `response-analysis` - For reviewing their responses

