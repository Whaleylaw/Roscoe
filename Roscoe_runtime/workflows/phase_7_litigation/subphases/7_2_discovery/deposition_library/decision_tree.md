# Deposition Type Decision Tree

## Overview

Use this decision tree to select the appropriate deposition type, templates, and reference materials for your situation.

## Master Decision Flowchart

```mermaid
flowchart TD
    Start[Deposition Planning] --> Q1{Who is being deposed?}
    
    Q1 -->|Our Client| ClientDepo[Client Deposition Defense]
    Q1 -->|Adverse Party| AdverseQ{Individual or Corporation?}
    Q1 -->|Expert Witness| ExpertQ{Plaintiff's or Defense?}
    Q1 -->|Third Party| ThirdParty[Third-Party Witness Deposition]
    
    AdverseQ -->|Individual| IndividualDepo[Individual Party Deposition]
    AdverseQ -->|Corporation| CorpQ{What strategic goal?}
    
    CorpQ -->|Discovery Mapping| CorpRep[Corporate Rep 30.02(6)]
    CorpQ -->|Document Explanation| CorpRep
    CorpQ -->|Liability Pin-Down| CorpRep
    CorpQ -->|Insurance Coverage| InsQ{UM/UIM or PIP?}
    
    InsQ -->|UM/UIM| UIMCorpRep[UIM Corporate Rep]
    InsQ -->|PIP| PIPCorpRep[PIP Corporate Rep]
    
    ExpertQ -->|Plaintiff's Expert| PlaintiffExpert[Plaintiff Expert Prep]
    ExpertQ -->|Defense Expert| DefenseExpert[Defense Expert Deposition]
    
    %% Styling
    ClientDepo --> ClientRef[references/client_defense/]
    IndividualDepo --> RulesRef[references/rules_framework/]
    CorpRep --> CorpRef[references/corp_rep/]
    UIMCorpRep --> CorpRef
    PIPCorpRep --> CorpRef
    DefenseExpert --> ExpertRef[references/expert_depo/]
    ThirdParty --> RulesRef
```

## Step-by-Step Selection Guide

### Step 1: Identify the Deponent

| Deponent Type | Next Question |
|---------------|---------------|
| Our client | → Go to **Client Deposition Defense** |
| Adverse party (individual) | → Go to **Individual Party Deposition** |
| Adverse party (corporation) | → Step 2: Identify strategic goal |
| Defense expert | → Go to **Defense Expert Deposition** |
| Third-party witness | → Go to **Third-Party Witness Deposition** |

### Step 2: For Corporate Depositions - Identify Strategic Goal

| Strategic Goal | Template Set |
|----------------|--------------|
| Discovery mapping (find documents, identify custodians) | CR 30.02(6) Corp Rep |
| Document/database explanation | CR 30.02(6) Corp Rep |
| Liability pin-down (bind corporation to facts) | CR 30.02(6) Corp Rep |
| Insurance coverage (UM/UIM) | UIM Corporate Rep |
| Insurance coverage (PIP) | PIP Corporate Rep |
| ESI mapping and retention | CR 30.02(6) Corp Rep |
| Establish foundational rules | CR 30.02(6) Corp Rep |

---

## Deposition Type Details

### Client Deposition Defense

**Trigger:** Defense serves deposition notice on our client

**Templates:**
- `templates/client_prep/client_letter.md` - Pre-deposition letter
- `templates/client_prep/client_checklist.md` - Preparation checklist
- `templates/client_prep/privilege_review.md` - Privilege identification

**References:**
- `references/client_defense/pre_deposition.md`
- `references/client_defense/objections_guide.md`
- `references/client_defense/day_of_support.md`
- `references/client_defense/post_analysis.md`

**Workflow:** `client_deposition_prep`

---

### Individual Party Deposition

**Trigger:** Need to depose individual defendant or adverse witness

**Templates:**
- `templates/notices/notice_standard.md` - Standard NTTD
- `templates/notices/notice_video.md` - Video deposition notice
- `templates/outlines/outline_rules_based.md` - Rules-based examination

**References:**
- `references/rules_framework/rule_discovery.md`
- `references/rules_framework/question_frameworks.md`

**Workflow:** `party_depositions`

---

### Corporate Representative (CR 30.02(6))

**Trigger:** Need corporate testimony on specific topics

**Templates:**
- `templates/notices/notice_corp_rep.md` - CR 30.02(6) notice
- `templates/outlines/outline_corp_rep.md` - Topic-by-topic outline

**References:**
- `references/corp_rep/strategic_goals.md`
- `references/corp_rep/topic_drafting.md`
- `references/corp_rep/know_nothing.md`
- `references/corp_rep/sample_topics.md`

**Workflow:** `corp_rep_deposition`

**Key Considerations:**
- Topics must have "reasonable particularity"
- Corporation must designate knowledgeable witness
- Testimony binds the corporation
- "Know-nothing" witness = strategic opportunity

---

### PIP Corporate Representative

**Trigger:** Need to depose PIP carrier about coverage, claims handling

**Templates:**
- `templates/notices/notice_corp_rep_pip.md` - PIP-specific topics
- `templates/outlines/outline_corp_rep.md` - Topic outline

**References:**
- `references/corp_rep/strategic_goals.md`
- `references/corp_rep/sample_topics.md` (PIP section)

**Workflow:** `corp_rep_deposition`

---

### UIM Corporate Representative

**Trigger:** Need to depose UIM carrier about coverage, valuation, claims handling

**Templates:**
- `templates/notices/notice_corp_rep_uim.md` - UIM-specific topics
- `templates/outlines/outline_corp_rep.md` - Topic outline

**References:**
- `references/corp_rep/strategic_goals.md`
- `references/corp_rep/sample_topics.md` (UIM section)

**Workflow:** `corp_rep_deposition`

---

### Defense Expert Deposition

**Trigger:** Defendants disclose expert witness (DME/IME, liability expert, etc.)

**Templates:**
- `templates/notices/notice_expert.md` - Expert deposition notice with trial-use language
- `templates/outlines/outline_expert.md` - Expert cross-examination outline

**References:**
- `references/expert_depo/dossier_compilation.md`
- `references/expert_depo/conflict_mapping.md`
- `references/expert_depo/juror_archetypes.md`
- `references/expert_depo/trial_preservation.md`

**Workflow:** `defense_expert_depo`

**Key Considerations:**
- Include trial-use language in notice
- Send KRE 804 notice before deposition
- Compile expert dossier (prior testimony, publications)
- Identify conflict opportunities by juror archetype

---

### Third-Party Witness Deposition

**Trigger:** Need to depose non-party witness (employer, eyewitness, records custodian)

**Templates:**
- `templates/notices/notice_standard.md` - Standard NTTD
- `templates/outlines/outline_rules_based.md` - Examination outline
- Subpoena Duces Tecum (from forms library)

**References:**
- `references/rules_framework/rule_discovery.md`
- `references/rules_framework/question_frameworks.md`

**Workflow:** `third_party_deposition`

**Key Considerations:**
- Must serve subpoena (cannot just notice non-party)
- Consider subpoena duces tecum for documents
- Calculate mileage if >100 miles from courthouse

---

## Quick Selection Matrix

| Scenario | Notice Template | Outline | Skill |
|----------|-----------------|---------|-------|
| Client noticed for deposition | N/A | N/A | `deposition-defense` |
| Deposing at-fault driver | `notice_standard.md` | `outline_rules_based.md` | `rules-based-examination` |
| Deposing trucking company | `notice_corp_rep.md` | `outline_corp_rep.md` | `corp-rep-deposition` |
| Deposing PIP carrier (coverage) | `notice_corp_rep_pip.md` | `outline_corp_rep.md` | `corp-rep-deposition` |
| Deposing UIM carrier (bad faith) | `notice_corp_rep_uim.md` | `outline_corp_rep.md` | `corp-rep-deposition` |
| Deposing DME/IME doctor | `notice_expert.md` | `outline_expert.md` | `expert-deposition` |
| Deposing employer (scope) | `notice_corp_rep.md` | `outline_corp_rep.md` | `corp-rep-deposition` |
| Deposing eyewitness | `notice_standard.md` + SDT | `outline_rules_based.md` | `rules-based-examination` |

---

## Timeline Considerations

| Activity | Timing |
|----------|--------|
| Serve RFP to expert | 60+ days before deposition |
| Serve deposition notice | Per CR 30.02(1) reasonable notice |
| Send KRE 804 notice (experts) | 3-5 days before deposition |
| Client prep sessions | Schedule 2-3 sessions before |
| Final logistics confirm | Day before deposition |

