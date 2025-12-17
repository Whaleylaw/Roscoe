# Transcript Extraction for Rules-Based Testimony

## Overview

After completing depositions, extract and catalog all rule-based testimony for use at trial, in motions, and in closing argument.

---

## Extraction Categories

### 1. Rules Established

Capture every rule that was agreed to during deposition.

### 2. Response Classification

Categorize each response:
- **Agreement** - Witness agreed with rule
- **Disagreement** - Witness denied rule (may damage credibility)
- **Evasion** - Witness avoided clear answer

### 3. Strategic Notes

Note the implications for trial strategy.

---

## Extraction Template

For each rule-establishing exchange:

| Field | Data to Capture |
|-------|-----------------|
| Deposition Info | Witness name, date, case |
| Rule ID | R-001, R-002, etc. |
| Established Rule | Exact verbatim text |
| Rule Source | Statute, policy, common sense, etc. |
| Source Citation | Specific cite if available |
| Witness Response | Exact verbatim response |
| Response Class | Agreement / Disagreement / Evasion |
| Transcript Ref | Page:Line |
| Objection | Verbatim objection, if any |
| Strategic Notes | How to use at trial |

---

## JSON Format for Data Extraction

```json
{
  "deposition_info": {
    "witness_name": "John Smith",
    "deposition_date": "2024-03-15",
    "case_caption": "Jones v. ABC Company",
    "deposition_type": "corporate_representative"
  },
  "rules_established": [
    {
      "rule_id": "R-001",
      "established_rule": "A business owner must keep the premises reasonably safe",
      "rule_source": "Common Sense",
      "source_citation": null,
      "witness_response": "I agree with that, yes",
      "response_classification": "Agreement",
      "transcript_reference": "45:12-15",
      "opposing_counsel_objection": null,
      "case_type_context": "Premises Liability",
      "strategic_notes": "Strong admission for closing"
    }
  ],
  "closing_gambit": {
    "mistakes_acknowledged": "no",
    "response_verbatim": "No, I don't think any mistakes were made",
    "transcript_reference": "112:5-8",
    "strategic_implication": "Can argue conduct was intentional"
  }
}
```

---

## Rule Annotation Log

Maintain a master log across all depositions:

| Rule ID | Rule Text | Witness | Response | Page:Line | Trial Use |
|---------|-----------|---------|----------|-----------|-----------|
| R-001 | Business must keep premises safe | Smith (Corp Rep) | Agree | 45:12 | Closing |
| R-002 | Floors must be kept dry | Smith (Corp Rep) | Agree | 48:3 | Closing |
| R-003 | Spills must be cleaned promptly | Jones (Manager) | Agree | 32:15 | Summary judgment |

---

## Strategic Outcome Flags

### Rules Fully Admitted

**Implication:** Strong for summary judgment or directed verdict on that element.

**Example Use:**
> "The corporate representative admitted under oath that a business must keep the premises reasonably safe. [Cite: Smith Depo at 45:12-15]"

### Rules Disputed

**Implication:** Credibility issue for trial.

**Example Use:**
> "When asked if floors should be kept clean, the defendant's own manager disagreed. Members of the jury, who do you believe?"

### Rules Evaded

**Implication:** Possible impeachment, shows consciousness.

**Example Use:**
> "The witness couldn't bring himself to admit that simple principle. What does that tell you about his credibility?"

### "No Mistakes" Response

**Implication:** Powerful closing argument.

**Example Use:**
> "They said no mistakes were made. This was exactly what they trained their employees to do. They would do nothing different. And [Plaintiff] was seriously injured."

---

## Cross-Witness Consistency Check

Compare rules across witnesses:

| Rule | Witness 1 | Witness 2 | Witness 3 | Consistent? |
|------|-----------|-----------|-----------|-------------|
| R-001 | Agree | Agree | Agree | ✓ Yes |
| R-002 | Agree | Disagree | Agree | ✗ Conflict |
| R-003 | Evade | Agree | Agree | ⚠ Mixed |

**Exploit Conflicts:**
> "Witness 1 agreed that [rule]. But Witness 2 disagreed. They can't even agree among themselves about basic safety principles."

---

## Trial Preparation Outputs

### 1. Impeachment Package

For each witness:
- Rules they agreed to
- Rules they violated
- Page:line citations
- Questions for cross-examination

### 2. Closing Argument Framework

Structure:
1. These are the rules [defendant] agreed to
   - Rule 1: [Quote from deposition]
   - Rule 2: [Quote from deposition]
   - Rule 3: [Quote from deposition]

2. Here's how [defendant] violated each rule
   - Violation 1: [Evidence]
   - Violation 2: [Evidence]
   - Violation 3: [Evidence]

3. Here's how each violation caused [client's] harm
   - Causation evidence

4. They say no mistakes were made
   - [Quote "no mistakes" testimony]
   - This was exactly what they intended
   - They would do nothing different

### 3. Motion Support

**Summary Judgment:**
- List undisputed rules from depositions
- Show undisputed violations
- Argue no genuine issue of material fact

**Motion in Limine:**
- Rules to exclude contrary evidence
- Foundation for excluding defense theories

---

## Quality Checks

- [ ] All rules extracted verbatim
- [ ] Page:line citations verified
- [ ] Response classifications accurate
- [ ] No characterization beyond record
- [ ] Strategic implications noted
- [ ] Cross-witness consistency checked
- [ ] Closing gambit responses captured

