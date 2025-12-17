# Phase 0: Onboarding

## Overview

Phase 0 handles the initial setup when a new case is opened. This phase is triggered when a user indicates they have a new client (e.g., "new client", "new file", "new case").

**Key Functions:**
1. **Case Setup** - Create the case folder structure and initialize tracking JSON
2. **Document Collection** - Gather required intake documents from client

---

## Phase Metadata

| Property | Value |
|----------|-------|
| **Phase ID** | `onboarding` |
| **Phase Number** | 0 |
| **Display Name** | Onboarding |
| **Typical Duration** | 1-3 days |

---

## Entry Criteria

This phase is triggered when:
- User says "new client", "new file", "new case", or similar
- A referral is received and the firm has decided to take the case

---

## Required Inputs

Only **3 pieces of information** are needed to start:

| Input | Example | Purpose |
|-------|---------|---------|
| Client Name | "John Doe" | Folder naming, case identification |
| Case Type | MVA / S&F / WC | Determines required documents |
| Accident Date | 01-15-2025 | Folder naming, statute of limitations tracking |

These inputs determine the case folder name: `{client-name}-{casetype}-{mm-dd-yyyy}`

---

## Exit Criteria

This phase is complete when all **3 landmark documents** are received:
- [ ] New Client Information Sheet
- [ ] Fee Agreement (Contract)
- [ ] Medical Authorization (HIPAA)

---

## Workflows in This Phase

| Workflow ID | Name | Description | When to Use |
|-------------|------|-------------|-------------|
| `case_setup` | Case Setup | Create folder structure and initialize JSON files | Immediately upon new case |
| `document_collection` | Document Collection | Gather required intake documents | After case setup |

---

## Workflow Sequence

```
┌─────────────────────────────────┐
│  User: "New client" / "New file" │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│  Gather 3 Inputs:               │
│  1. Client Name                 │
│  2. Case Type (MVA/S&F/WC)      │
│  3. Accident Date               │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│  case_setup workflow            │
│  → Run create_case.py tool      │
│  → Creates folders + JSON       │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│  document_collection workflow   │
│  → Check case type              │
│  → Generate document checklist  │
│  → Request/collect documents    │
└───────────────┬─────────────────┘
                │
                ▼
        ┌───────┴───────┐
        │               │
        ▼               ▼
┌──────────────┐ ┌──────────────┐
│ 3 Landmarks  │ │ Missing Docs │
│ Complete     │ │ → Blocker    │
└──────┬───────┘ └──────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Phase 1: File Setup            │
└─────────────────────────────────┘
```

---

## Landmarks

See [landmarks.md](landmarks.md) for detailed milestone definitions.

| # | Landmark | Document | Required? |
|---|----------|----------|-----------|
| 1 | Client Info Received | New Client Information Sheet | **YES** |
| 2 | Contract Signed | Fee Agreement | **YES** |
| 3 | Medical Auth Signed | HIPAA Authorization | **YES** |

---

## Documents by Case Type

| Document | MVA | S&F | WC | Landmark? |
|----------|:---:|:---:|:--:|:---------:|
| New Client Information Sheet | ✓ | ✓ | ✓ | **YES** |
| Fee Agreement (case-specific) | ✓ | ✓ | ✓ | **YES** |
| Medical Authorization (HIPAA) | ✓ | ✓ | ✓ | **YES** |
| Medical Treatment Questionnaire | ✓ | ✓ | ✓ | No |
| Digital Signature Authorization | ✓ | ✓ | ✓ | No |
| MVA Accident Detail Sheet | ✓ | - | - | No |
| S&F Accident Detail Sheet | - | ✓ | - | No |
| Wage & Salary Verification | * | * | ✓ | No |
| CMS Medicare Verification | * | * | * | No |

`*` = Conditional (if employed, if Medicare)

---

## Tools Used

| Tool | Location | Purpose |
|------|----------|---------|
| `create_case.py` | `workflows/case_setup/tools/` | Creates folder structure and JSON files |
| `docusign_send.py` | `workflows/document_collection/skills/docusign-send/tools/` | Send documents for e-signature |

---

## Skills Used

| Skill | Purpose |
|-------|---------|
| `document-request` | Send document requests to client |
| `document-intake` | Process and file received documents |
| `docusign-send` | Send documents for electronic signature via DocuSign |

---

## Templates

| Template | Location | Purpose |
|----------|----------|---------|
| Document Checklist | `workflows/document_collection/templates/` | Track document status |
| Request Email | `workflows/document_collection/templates/` | Client document request |

---

## Next Phase

Upon completion (all 3 landmarks met), cases proceed to:
- **Phase 1: File Setup** - Insurance claims, medical provider setup, additional documentation
