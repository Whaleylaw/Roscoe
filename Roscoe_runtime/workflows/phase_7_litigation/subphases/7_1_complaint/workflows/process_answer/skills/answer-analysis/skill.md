---
name: answer-analysis
description: >
  Analyze defendant's answer to complaint. Identifies denials, affirmative
  defenses, counterclaims, and third-party claims. Use when answer received
  to understand defense strategy and identify disputed issues.
---

# Answer Analysis Skill

## Overview

Systematically review defendant's answer to identify key defenses and claims requiring response.

## When to Use

Use when:
- Answer received from defendant
- Need to identify disputed facts
- Looking for affirmative defenses
- Checking for counterclaims

DO NOT use if:
- No answer received (use default process)
- Analyzing discovery responses (different skill)

## Workflow

### Step 1: Identify Response Type

| Response Type | Next Action |
|---------------|-------------|
| Answer only | Analyze defenses |
| Answer + Counterclaim | Must respond to counterclaim |
| Answer + Third-Party Complaint | Track new parties |
| Motion to Dismiss | Brief opposition |

### Step 2: Catalog Denials

List each denied allegation - these are contested facts for discovery.

### Step 3: Extract Affirmative Defenses

Common defenses in PI cases:
- Comparative fault
- Assumption of risk
- Statute of limitations
- Failure to mitigate

**See:** `references/affirmative-defenses.md` for response strategies.

### Step 4: Flag Counterclaims

If counterclaim filed:
- Deadline to respond (20 days)
- May need discovery on defense claims

**See:** `references/counterclaim-handling.md` for response process.

## Output Format

```markdown
## Answer Analysis: [Defendant Name]

**Filed:** [Date]
**Response Type:** [Answer / Answer + Counterclaim / etc.]

### Denials (Contested Facts)
- Paragraph [X]: [Allegation denied]
- Paragraph [Y]: [Allegation denied]

### Affirmative Defenses
1. [Defense name] - [Brief analysis]
2. [Defense name] - [Brief analysis]

### Counterclaims
- [ ] None filed
- [ ] Filed - Response due [date]

### Action Items
- [ ] [Required action]
```

## Related Skills

- `complaint-drafting` - For the document being answered
- `discovery-drafting` - For following up on disputed facts

