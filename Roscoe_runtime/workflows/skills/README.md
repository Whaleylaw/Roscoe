# Workflow Skills

This folder contains all skills used across workflow phases, copied here for central access.

## Quick Start

1. **Read the manifest** to discover available skills:
   ```
   skills/skills_manifest.json
   ```

2. **Find skills by keyword** - search the manifest for task-related keywords

3. **Load the skill** from `skills/{path}`

4. **Follow skill instructions** and use referenced tools from `tools/`

## Folder Structure

```
skills/
├── skills_manifest.json
├── phase_0_onboarding/
│   ├── docusign-send/
│   ├── document-intake/
│   └── document-request/
├── phase_1_file_setup/
│   ├── pip-waterfall/
│   ├── pip-application/
│   ├── lor-generator/
│   ├── liability-analysis/
│   ├── medical-records-request/
│   └── police-report-analysis/
├── phase_2_treatment/
│   ├── medical-records-request/
│   ├── medical-chronology-generation/
│   ├── lien-classification/
│   └── calendar-scheduling/
├── phase_3_demand/
│   ├── medical-chronology-generation/
│   ├── lien-classification/
│   ├── damages-calculation/
│   ├── demand-letter-generation/
│   └── calendar-scheduling/
├── phase_4_negotiation/
│   ├── negotiation-strategy/
│   ├── calendar-scheduling/
│   ├── offer-evaluation/
│   ├── lien-negotiation/
│   └── offer-tracking/
├── phase_5_settlement/
│   ├── settlement-statement/
│   ├── docusign-send/
│   ├── lien-classification/
│   └── lien-resolution/
├── phase_6_lien/
│   ├── final-lien-request/
│   ├── lien-reduction/
│   └── supplemental-statement/
└── phase_7_litigation/
    ├── 7_1_complaint/
    │   ├── complaint-drafting/
    │   ├── service-of-process/
    │   └── answer-analysis/
    ├── 7_2_discovery/
    │   ├── discovery-drafting/
    │   ├── discovery-response/
    │   ├── response-analysis/
    │   ├── deposition-defense/
    │   ├── deposition-planning/
    │   ├── corp-rep-deposition/
    │   ├── expert-deposition/
    │   └── rules-based-examination/
    ├── 7_3_mediation/
    │   ├── mediation-prep/
    │   └── mediation-strategy/
    ├── 7_4_trial_prep/
    │   ├── expert-coordination/
    │   └── trial-exhibit-prep/
    └── 7_5_trial/
        └── trial-presentation/
```

## Skills by Phase

| Phase | Count | Key Skills |
|-------|-------|------------|
| Phase 0 - Onboarding | 3 | docusign-send, document-intake |
| Phase 1 - File Setup | 6 | pip-waterfall, lor-generator, police-report-analysis |
| Phase 2 - Treatment | 4 | medical-chronology-generation, lien-classification |
| Phase 3 - Demand | 5 | demand-letter-generation, damages-calculation |
| Phase 4 - Negotiation | 5 | negotiation-strategy, offer-evaluation |
| Phase 5 - Settlement | 4 | settlement-statement, lien-resolution |
| Phase 6 - Lien | 3 | final-lien-request, lien-reduction |
| Phase 7 - Litigation | 17 | complaint-drafting, discovery-drafting, deposition skills |

## Skill Categories

| Category | Purpose |
|----------|---------|
| `insurance` | Insurance claim and coverage skills |
| `document_generation` | Creating documents from templates |
| `document_processing` | Reading and parsing documents |
| `analysis` | Analyzing documents and data |
| `calculation` | Financial and damages calculations |
| `scheduling` | Calendar and deadline management |
| `strategy` | Case and negotiation strategy |
| `negotiation` | Settlement and lien negotiations |
| `tracking` | Progress and offer tracking |
| `litigation` | Litigation-specific procedures |
| `esignature` | Electronic signature workflows |

## Progressive Disclosure

Each skill folder contains:
- `skill.md` - High-level instructions (always load first)
- `references/` - Detailed guidance (load on demand)
- `tools/` - Tool integrations (if any)
