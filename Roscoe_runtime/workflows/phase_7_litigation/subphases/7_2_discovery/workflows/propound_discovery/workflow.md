---
name: propound_discovery
description: >
  Draft and serve written discovery on defendant. Includes interrogatories,
  requests for production, and requests for admission. Use after answer filed
  to gather liability facts, damages information, and documents.
phase: 7.2_discovery
workflow_id: propound_discovery
related_skills:
  - discovery-drafting
related_tools:
  - generate_document.py
library_reference: discovery_library/propounding/
templates:
  - discovery_library/propounding/templates/interrogatories/
  - discovery_library/propounding/templates/rfps/
  - discovery_library/propounding/templates/rfas/
---

# Propound Discovery Workflow

## Overview

Draft, review, and serve written discovery requests on defendant to obtain information needed for case development. Uses the Discovery Library for template selection.

## Entry Criteria

- Answer filed
- Discovery period open
- Discovery strategy determined

## Discovery Library Reference

**Primary Resources:**
- [Discovery Library README](../../discovery_library/README.md) - Library overview and index
- [Propounding Decision Tree](../../discovery_library/propounding/decision_tree.md) - Template selection flowchart

## Steps

### 1. Plan Discovery Strategy

**Owner:** Agent  
**Action:** Identify what information is needed:
- Liability facts and witnesses
- Insurance information and coverage
- Documents (photos, statements, policies)
- Expert information

### 2. Select Appropriate Templates

**Owner:** Agent  
**Reference:** [Propounding Decision Tree](../../discovery_library/propounding/decision_tree.md)  
**Action:** Use the decision tree to select the appropriate templates based on:
- Case type (MVA, premises, bad faith)
- Defendant type (individual, trucking, employer, insurance carrier)
- Specific needs (cell phone, experts, prior incidents)

**Template Selection Matrix:**

| Case Type | Defendant | Interrogatory Template | RFP Template |
|-----------|-----------|----------------------|--------------|
| MVA | Individual driver | `mva_standard.md` | `mva_standard.md` |
| MVA | CDL driver | `mva_trucking_driver.md` | `mva_trucking.md` |
| MVA | Trucking company | `mva_trucking_company.md` | `mva_trucking.md` |
| MVA | Employer | `mva_respondeat_superior.md` | `mva_standard.md` |
| MVA | UM/UIM carrier | `mva_um_uim.md` | `bad_faith.md` |
| MVA | PIP carrier | `mva_pip.md` | `bad_faith.md` |
| Premises | Property owner | `premises_standard.md` | `premises_standard.md` |
| Bad Faith | Insurance carrier | `bad_faith.md` | `bad_faith.md` |

### 3. Add Modular Question Sets (If Needed)

**Owner:** Agent  
**Reference:** [Modular Question Sets](../../discovery_library/propounding/modules/)  
**Action:** Review case facts and add relevant modules:

| Module | When to Add |
|--------|-------------|
| `mod_witness_identification.md` | Need comprehensive witness list |
| `mod_insurance_coverage.md` | Coverage disputes, limits unknown |
| `mod_expert_disclosure.md` | Anticipate expert testimony |
| `mod_prior_incidents.md` | Premises, pattern evidence |
| `mod_cell_phone.md` | Distraction suspected |
| `mod_employment_scope.md` | Vicarious liability at issue |

### 4. Draft Interrogatories

**Owner:** Agent  
**Skill:** `discovery-drafting`  
**Tool:** `generate_document.py`  
**Action:** Copy selected template, fill case-specific information, generate document.

**Document Generation Pattern:**
```bash
# 1. Copy template from library to project
cp "../../discovery_library/propounding/templates/interrogatories/mva_standard.md" \
   "/{project}/Litigation/Discovery/Interrogatories.md"

# 2. Agent fills placeholders (case number, parties, case-specific questions)

# 3. Generate DOCX/PDF
python generate_document.py "/{project}/Litigation/Discovery/Interrogatories.md"
```

**Kentucky Limits:** 30 interrogatories including subparts. Three "free" questions per CR 33.01(3).

### 5. Draft Requests for Production

**Owner:** Agent  
**Skill:** `discovery-drafting`  
**Tool:** `generate_document.py`  
**Action:** Copy RFP template, fill case-specific details, generate document.

```bash
cp "../../discovery_library/propounding/templates/rfps/mva_standard.md" \
   "/{project}/Litigation/Discovery/Requests_for_Production.md"
python generate_document.py "/{project}/Litigation/Discovery/Requests_for_Production.md"
```

### 6. Draft Requests for Admission (Strategic Timing)

**Owner:** Agent  
**Reference:** [RFA Templates](../../discovery_library/propounding/templates/rfas/)  
**Action:** RFAs may be served with initial discovery OR held for strategic timing (post-deposition, pre-MSJ).

**Timing Considerations:**
- **With initial discovery:** Basic facts, liability admissions
- **After depositions:** Lock in testimony
- **Before summary judgment:** Establish undisputed facts
- **Cost-of-proof:** CR 36.02 sanctions for unreasonable denials

```bash
cp "../../discovery_library/propounding/templates/rfas/mva_liability.md" \
   "/{project}/Litigation/Discovery/Requests_for_Admission.md"
python generate_document.py "/{project}/Litigation/Discovery/Requests_for_Admission.md"
```

### 7. Attorney Review

**Owner:** User (Attorney)  
**Action:** Review and approve discovery before service:
- [ ] Questions within 30-question limit
- [ ] Case-specific details accurate
- [ ] Strategic objectives addressed
- [ ] Format complies with local rules

### 8. Serve Discovery

**Owner:** User  
**Action:** Serve discovery via permitted method, calendar response deadline.
- Service method per CR 5.02
- Calendar 30-day response deadline
- Note: 45 days if served with complaint

## Exit Criteria

- [ ] Interrogatories served
- [ ] RFPs served
- [ ] RFAs served (if applicable)
- [ ] Response deadline calendared (30 days from service)

## Discovery Library Templates

### Interrogatory Templates
Location: `discovery_library/propounding/templates/interrogatories/`

| Template | Use Case |
|----------|----------|
| `mva_standard.md` | Individual driver MVA |
| `mva_trucking_driver.md` | CDL/commercial driver |
| `mva_trucking_company.md` | Motor carrier |
| `mva_um_uim.md` | UM/UIM claims |
| `mva_respondeat_superior.md` | Employer liability |
| `mva_pip.md` | PIP disputes |
| `premises_standard.md` | Premises liability |
| `bad_faith.md` | Bad faith claims |

### RFP Templates
Location: `discovery_library/propounding/templates/rfps/`

| Template | Use Case |
|----------|----------|
| `mva_standard.md` | Standard MVA documents |
| `mva_trucking.md` | Trucking case documents |
| `premises_standard.md` | Premises documents |
| `bad_faith.md` | Claims file, guidelines |

### RFA Templates
Location: `discovery_library/propounding/templates/rfas/`

| Template | Use Case |
|----------|----------|
| `mva_liability.md` | Liability admissions |
| `mva_damages.md` | Damages admissions |
| `premises_liability.md` | Premises admissions |
| `bad_faith.md` | Bad faith admissions |

## Related Workflows

- **Triggers:** `review_responses` (when responses received)
- **Related:** `respond_to_discovery` (when defendant propounds)
