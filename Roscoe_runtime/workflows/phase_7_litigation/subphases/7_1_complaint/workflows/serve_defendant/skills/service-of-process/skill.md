---
name: service-of-process
description: >
  Execute proper service of process under Kentucky law. Use when serving
  complaints, determining service methods, tracking service attempts,
  or filing proof of service. Covers personal service, certified mail,
  warning orders, and service on corporations.
---

# Service of Process Skill

## Overview

Properly serve defendants under Kentucky Civil Rules, track attempts, and document completion.

## When to Use

Use when:
- Need to serve complaint on defendant
- Determining proper service method
- Defendant evading service
- Serving corporate or out-of-state defendant

DO NOT use if:
- Defendant already served
- Need to serve discovery (different rules)

## Workflow

### Step 1: Identify Service Method

| Defendant Type | Primary Method | Alternative |
|----------------|----------------|-------------|
| Individual (KY) | Personal / Sheriff | Certified mail |
| Individual (out-of-state) | Personal | Secretary of State |
| Corporation (KY) | Registered agent | Officer/managing agent |
| Corporation (out-of-state) | Secretary of State | Personal |
| Unknown location | Warning order | - |

**See:** `references/service-methods.md` for detailed requirements.

### Step 2: Execute Service

- Contact sheriff or process server
- Provide summons and complaint
- Track 90-day deadline from filing

### Step 3: Document Result

Record for each attempt:
- Date
- Method
- Result (served/not served)
- Notes

### Step 4: File Proof

Once served, file proof of service with court.

**See:** `references/proof-of-service.md` for requirements.

## Output Format

```markdown
## Service Status: [Defendant Name]

| Attempt | Date | Method | Result |
|---------|------|--------|--------|
| 1 | [date] | [method] | [result] |

**Status:** [Pending/Completed]
**Proof Filed:** [Yes/No]
**Answer Deadline:** [date]
```

## Related Skills

- `complaint-drafting` - For the document being served
- `answer-analysis` - For processing the response

