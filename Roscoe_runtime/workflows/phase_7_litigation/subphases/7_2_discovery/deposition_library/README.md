# Deposition Library

## Overview

The Deposition Library provides comprehensive resources for planning, conducting, and analyzing depositions in personal injury litigation. This library is organized to support all deposition types from client defense through expert cross-examination.

## Structure

```
deposition_library/
├── README.md                    # This file
├── decision_tree.md             # Master deposition type selection
├── templates/
│   ├── notices/                 # Deposition notice templates
│   │   ├── notice_standard.md           # Standard NTTD
│   │   ├── notice_corp_rep.md           # CR 30.02(6) with topics
│   │   ├── notice_corp_rep_pip.md       # PIP carrier corporate rep
│   │   ├── notice_corp_rep_uim.md       # UIM carrier corporate rep
│   │   ├── notice_expert.md             # Defense expert notice
│   │   └── notice_video.md              # Video deposition notice
│   ├── client_prep/             # Client preparation materials
│   │   ├── client_letter.md             # Pre-deposition letter to client
│   │   ├── client_checklist.md          # Preparation checklist
│   │   └── privilege_review.md          # Privilege identification template
│   ├── outlines/                # Deposition outline frameworks
│   │   ├── outline_rules_based.md       # Rules-based questioning framework
│   │   ├── outline_corp_rep.md          # Corporate rep topic examination
│   │   └── outline_expert.md            # Expert cross-examination structure
│   └── tracking/                # Scheduling and tracking
│       ├── depo_schedule.md             # Master deposition schedule
│       └── testimony_tracker.md         # Key testimony tracking
├── references/
│   ├── client_defense/          # Client deposition defense
│   │   ├── README.md                    # Overview
│   │   ├── pre_deposition.md            # Pre-depo preparation
│   │   ├── objections_guide.md          # Form objections reference
│   │   ├── day_of_support.md            # Day-of procedures
│   │   └── post_analysis.md             # Post-depo analysis
│   ├── corp_rep/                # Corporate representative (30.02(6))
│   │   ├── README.md                    # Overview
│   │   ├── strategic_goals.md           # Strategic objective identification
│   │   ├── topic_drafting.md            # Topic drafting with particularity
│   │   ├── know_nothing.md              # Know-nothing witness handling
│   │   └── sample_topics.md             # Sample topics by case type
│   ├── expert_depo/             # Defense expert depositions
│   │   ├── README.md                    # Overview
│   │   ├── dossier_compilation.md       # Expert dossier creation
│   │   ├── conflict_mapping.md          # Conflict identification
│   │   ├── juror_archetypes.md          # Targeting by juror type
│   │   └── trial_preservation.md        # KRE 804 procedures
│   └── rules_framework/         # Rules-based examination
│       ├── README.md                    # Overview
│       ├── rule_discovery.md            # Identifying rules from sources
│       ├── question_frameworks.md       # Question templates by case type
│       └── transcript_extraction.md     # Extracting rules from transcripts
└── skills/
    ├── deposition-defense/      # Client deposition defense skill
    ├── corp-rep-deposition/     # Corporate rep examination skill
    ├── expert-deposition/       # Expert cross-examination skill
    └── rules-based-examination/ # Rules-based questioning skill
```

## Quick Reference by Deposition Type

| Deposition Type | Notice Template | Outline | Key Reference |
|-----------------|-----------------|---------|---------------|
| **Client Defense** | N/A (we receive notice) | N/A | `references/client_defense/` |
| **Adverse Party** | `notice_standard.md` | `outline_rules_based.md` | `references/rules_framework/` |
| **Corporate Rep (30.02(6))** | `notice_corp_rep.md` | `outline_corp_rep.md` | `references/corp_rep/` |
| **PIP Corp Rep** | `notice_corp_rep_pip.md` | `outline_corp_rep.md` | `references/corp_rep/` |
| **UIM Corp Rep** | `notice_corp_rep_uim.md` | `outline_corp_rep.md` | `references/corp_rep/` |
| **Defense Expert** | `notice_expert.md` | `outline_expert.md` | `references/expert_depo/` |
| **Third-Party Witness** | `notice_standard.md` + SDT | `outline_rules_based.md` | `references/rules_framework/` |

## Kentucky Rules Quick Reference

| Rule | Purpose |
|------|---------|
| **CR 30.02(1)** | Deposition notice requirements |
| **CR 30.02(6)** | Corporate representative designation |
| **CR 30.03(3)** | Objection conduct rules |
| **CR 30.04** | Termination/limitation for bad faith |
| **CR 32.01** | Deposition use at trial |
| **CR 32.04** | Objection waiver rules |
| **KRE 503** | Attorney-client privilege |
| **KRE 803(18)** | Learned treatise exception |
| **KRE 804** | Former testimony exception |

## How to Use This Library

### 1. Identify Deposition Type

Consult [decision_tree.md](decision_tree.md) to determine which deposition type applies.

### 2. Select Templates

Based on deposition type, gather:
- Notice template (if we're noticing)
- Outline template
- Client prep materials (if client deposition)

### 3. Reference Detailed Guidance

Each deposition type has a reference folder with:
- Strategic considerations
- Step-by-step procedures
- Quality checklists

### 4. Use Skills for Agent Actions

Skills provide specific agent instructions for:
- Document preparation
- Question drafting
- Analysis tasks

## Document Generation

All templates in this library use the unified document generation system:

```bash
python ${ROSCOE_ROOT}/Tools/document_generation/generate_document.py \
    "/{project}/Litigation/Discovery/Deposition_Notice.md"
```

## Related Workflows

| Workflow | Purpose |
|----------|---------|
| `client_deposition_prep` | Prepare client for their deposition |
| `party_depositions` | Plan and conduct adverse party depositions |
| `corp_rep_deposition` | Corporate representative (30.02(6)) depositions |
| `defense_expert_depo` | Defense expert/DME/IME depositions |
| `third_party_deposition` | Third-party witness depositions with subpoena |

## Quality Standards

All deposition materials should:
- Include proper Kentucky rule citations
- Use the unified document generation pattern
- Follow progressive disclosure principles
- Be reviewed by supervising attorney before use

