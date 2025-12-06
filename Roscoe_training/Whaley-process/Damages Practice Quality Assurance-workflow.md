# Damages Practice Quality Assurance Module

---

## 1. Operational Workflow

### Workflow Name
**Damages Claim Quality Assurance Review**

---

### Goal
Successful completion means the AI paralegal has systematically audited the case file against the eight critical damages pitfalls, identified all deficiencies and risks, generated specific remediation recommendations, and produced a comprehensive QA report that positions the claim for maximum value at the upcoming milestone.

---

### When to Use
This workflow is triggered at these critical case milestones:

| Trigger Condition | Description |
|-------------------|-------------|
| **Pre-Demand Preparation** | Before drafting a settlement demand package |
| **Pre-Mediation Review** | 2-4 weeks before scheduled mediation |
| **Pre-Trial Final Check** | During trial preparation to ensure all evidentiary gaps are closed |
| **Proactive Case Audit** | At 6-month intervals during case development to prevent pitfall accumulation |
| **Attorney Request** | When supervising attorney requests a damages quality review |

---

### Inputs Required

| Input | Description | Location |
|-------|-------------|----------|
| **Case Overview** | Project name, client name, incident date, case status | `overview.json` |
| **Medical Records Inventory** | List of all medical providers and records obtained | `Medical Records/` folder |
| **Treatment Chronology** | Timeline of medical treatment with key dates | Prior analysis or records |
| **Medical Bills Summary** | Itemized medical expenses with totals | Case file |
| **Employment Records** | W-2s, pay stubs, employer documentation | Case file |
| **Witness List** | Current list of identified witnesses | Case file |
| **Lien Register** | Known liens and subrogation claims | `liens.json` |
| **Insurance Information** | Policy limits, carrier, adjuster contact | `insurance.json` |
| **Prior Medical History** | Records predating incident (if obtained) | Case file |
| **Settlement Communications** | Offer/counter-offer history | Case file or notes |
| **Client MMI Status** | Whether treating physician has declared MMI | Medical records |

---

### Step-by-Step Process

#### **Phase 1: Pre-Audit Setup**

**Step 1.1 — Gather Case Context**
- Load case overview, contacts, and insurance information
- Identify current case phase (pre-litigation, litigation, pre-trial)
- Determine which milestone triggered the QA review
- Note any time constraints or deadlines

**Step 1.2 — Inventory Available Documentation**
- Catalog all medical records by provider
- List all employment/wage documentation
- Identify current witness roster
- Check lien register for known third-party claims
- Note any pending items or gaps in documentation

---

#### **Phase 2: Pitfall Analysis (8 Categories)**

**Step 2.1 — Pitfall 1: Premature Settlement Timing**
- [ ] Check if treating physician has declared Maximum Medical Improvement (MMI)
- [ ] Review medical records for prognoses regarding permanency and future care needs
- [ ] If pre-MMI settlement is contemplated, verify:
  - Written client advisement of risks exists
  - Clear strategic justification (e.g., catastrophic injury with obvious permanency)
- **Risk Flag**: Settlement discussions before MMI without documented justification

**Step 2.2 — Pitfall 2: Medical Documentation Adequacy**
- [ ] Verify all records from all providers obtained (including ancillary: PT, OT, nurses)
- [ ] Check for competent medical opinion linking injuries to incident (causation)
- [ ] Verify all lost work time claims supported by medical opinion of necessity
- [ ] Identify any ambiguous physician notes requiring clarification
- [ ] Check if supplemental reports needed for causation, prognosis, or future care
- [ ] Classify pain types documented in records:
  - Nociceptive (tissue damage: aching, throbbing, movement-worsened)
  - Neuropathic (nerve injury: burning, shooting, numbness)
  - Centrally Amplified (chronic/widespread after tissue healing)
- **Risk Flag**: Missing causation opinion, unsupported lost wage claims, ambiguous records

**Step 2.3 — Pitfall 3: Pre-Existing Conditions Strategy**
- [ ] Verify prior medical records obtained (minimum 5-10 years)
- [ ] Identify all documented pre-existing conditions
- [ ] Determine applicable legal doctrine:
  - **Eggshell Plaintiff**: Defendant liable for full harm despite plaintiff's unusual susceptibility
  - **Crumbling Skull**: Defendant liable only for aggravation/acceleration of deteriorating condition
- [ ] Check for medical expert opinion distinguishing new injuries from pre-existing
- [ ] Verify case narrative establishes functional baseline (before vs. after)
- **Risk Flag**: Unaddressed pre-existing conditions, no distinguishing medical opinion

**Step 2.4 — Pitfall 4: 360-Degree Witness Analysis**
- [ ] Review current witness list
- [ ] Assess witness coverage across plaintiff's life circles:
  - Immediate family (spouse, parents, children)
  - Extended family
  - Close friends
  - Co-workers/colleagues
  - Neighbors
  - Community contacts (church, clubs, regular service providers)
- [ ] Check for witnesses who can testify to "the delta" (before vs. after comparison)
- [ ] Verify non-family, disinterested third-party witnesses identified
- [ ] Assess plaintiff "likability strategy" — is testimony role defined?
- **Risk Flag**: Witnesses limited to immediate family only, no delta testimony developed

**Step 2.5 — Pitfall 5: Damages Theory Selection**
- [ ] Analyze plaintiff profile:
  - Age at time of injury
  - Education level
  - Employment history stability
  - Injury permanence
- [ ] Determine appropriate damages theory:

| Factor | Favors Lost Wages | Favors Loss of Earning Capacity |
|--------|-------------------|--------------------------------|
| Work History | Steady employment | Limited/no work history |
| Injury Type | Temporary, finite recovery | Permanent restrictions |
| Age | Older, established career | Young, high potential |
| Calculation | Arithmetic (known wage × time) | Projection (vocational + economist) |

- [ ] Verify supporting evidence for chosen theory:
  - **Lost Wages**: W-2s, pay stubs, employer records, medical necessity documentation
  - **Earning Capacity**: Educational records, vocational expert, economist report
- [ ] For permanent injuries: Check if hybrid approach warranted (past wages + future capacity)
- **Risk Flag**: Theory mismatch with plaintiff profile, missing key expert evidence

**Step 2.6 — Pitfall 6: Liens and Subrogation Claims**
- [ ] Identify all potential lienholders:
  - Medicare/Medicaid
  - Private health insurers (including ERISA plans)
  - Hospital liens
  - Workers' compensation (if any)
  - Other statutory liens
- [ ] Verify notice of representation sent to all lienholders
- [ ] Check for conditional payment letters/final lien amounts
- [ ] Assess lien negotiation status and reduction arguments:
  - Procurement costs
  - Common-fund principles
  - Made-whole doctrine (where applicable)
- **Risk Flag**: Unidentified lienholders, no written lien amounts, unreduced liens pre-settlement

**Step 2.7 — Pitfall 7: Demand Package Organization**
- [ ] If demand package exists, assess structure:
  - Concise summary of liability, injuries, damages at beginning
  - Table of contents/index
  - Chronological organization
  - Bates-stamping
  - Bookmarked/indexed documents
- [ ] Check for algorithm optimization (for Colossus-type systems):
  - Key diagnoses with ICD codes front-loaded
  - Top 60 value-driving factors highlighted early
  - Limited to 7 most significant diagnoses
- [ ] Identify injuries requiring human review (outside algorithmic evaluation):
  - Severe scarring/disfigurement
  - PTSD/psychological injuries
  - Inner ear injuries
  - Other non-standard damages
- [ ] For disfigurement claims: Check for staged photos + social consequence testimony
- **Risk Flag**: Disorganized package, no summary, algorithm factors buried, human-review items unmarked

**Step 2.8 — Pitfall 8: Communication Documentation**
- [ ] Verify written record of all settlement offers conveyed to client
- [ ] Verify written record of client instructions (accept/reject) for each offer
- [ ] Check for follow-up confirmation of significant phone conversations
- [ ] Review insurance communications log (offers, counter-offers, adjuster contact)
- [ ] Verify case strategy discussions documented in file memos
- **Risk Flag**: Missing offer/instruction documentation, no communications log

---

#### **Phase 3: Risk Assessment & Remediation**

**Step 3.1 — Compile Risk Summary**
- Aggregate all risk flags from Phase 2
- Categorize by severity:
  - **Critical**: Could derail settlement or expose to liability
  - **High**: Will significantly undervalue claim
  - **Medium**: Creates vulnerability in negotiations
  - **Low**: Best practice gap, should address if time permits

**Step 3.2 — Generate Remediation Recommendations**
For each identified risk, provide specific remediation action:
- What needs to be done
- Who needs to do it (attorney, paralegal, expert, client)
- Suggested timeline
- Resources or documents needed

**Step 3.3 — Strategic Observations**
Based on case study patterns from the training report:
- Identify framing opportunities (heroism vs. victimhood for severe injuries)
- Note anchoring strategies for non-economic damages (convert intangible losses to market rates)
- Flag negotiation tactics (strategic evidence withholding, litigation filing as leverage)

---

#### **Phase 4: Output Generation**

**Step 4.1 — Generate QA Report**
Compile findings into structured report with:
- Executive summary
- Milestone-specific checklist completion status
- Detailed pitfall analysis findings
- Risk register with severity ratings
- Prioritized remediation action items
- Strategic recommendations

---

### Quality Checks & Safeguards

#### Validation Checks
| Check | Validation |
|-------|------------|
| **Completeness** | All 8 pitfall categories analyzed |
| **Evidence-Based** | All findings cite specific documents or gaps |
| **Actionable** | Each risk has corresponding remediation |
| **Prioritized** | Risks rated by severity |
| **Milestone-Appropriate** | Analysis tailored to triggering milestone |

#### Red Flags Requiring Attorney Escalation
- Settlement discussions occurring without MMI and no documented client waiver
- Missing causation opinion with trial date set
- Unidentified liens discovered during QA review
- No written record of settlement offers/client instructions
- Pre-existing condition likely to trigger crumbling skull defense with no expert opinion
- Damages theory fundamentally mismatched with plaintiff profile
- Demand package to be submitted without required supporting evidence

#### Ethical Boundaries
- AI paralegal does not provide legal advice or final legal conclusions
- AI paralegal does not recommend specific settlement amounts
- AI paralegal does not evaluate whether a settlement should be accepted
- All strategic recommendations framed as supportive work product for attorney review
- Client communication recommendations are for attorney consideration only

---

### Outputs

| Artifact | Description | Format |
|----------|-------------|--------|
| **QA Executive Summary** | 1-page overview of review findings and critical action items | Markdown section |
| **Pitfall Analysis Matrix** | 8-category analysis with checklist status and findings | Table |
| **Risk Register** | All identified risks with severity rating and remediation | Table |
| **Remediation Action Plan** | Prioritized list of corrective actions with assignments and timelines | Numbered list |
| **Milestone Checklist** | Completed master checklist appropriate to case milestone | Checklist |
| **Strategic Recommendations** | Case-specific tactical observations from case study patterns | Narrative section |
| **Documentation Gaps Log** | List of missing documents with acquisition recommendations | Table |

---

---

## 2. Prompt Template for AI Paralegal

```
You are an AI Paralegal operating under the "Damages Practice — Pitfalls & Quality Checklist" module.

## Reference

You have been trained on the "Damages Practice — Pitfalls & Quality Checklist" report, which defines the eight critical pitfalls that can derail or undervalue damages claims in personal injury litigation:

1. Premature Settlement Discussions (settling before MMI)
2. Inadequate Medical Documentation (missing causation, unsupported claims)
3. Failure to Address Pre-Existing Conditions Proactively (eggshell vs. crumbling skull)
4. Overlooking the 360-Degree Witness Analysis (limited to family witnesses)
5. Choosing the Wrong Damages Theory (lost wages vs. earning capacity mismatch)
6. Ignoring Liens and Subrogation Claims (unidentified or unresolved liens)
7. Poor Organization of Demand Package (disorganized, not algorithm-optimized)
8. Failure to Document File Communications (missing offer/instruction records)

You also have access to three case studies demonstrating strategic application:
- The Young Professional (earning capacity, heroism framing)
- The Retiree (non-economic anchoring to market rates)
- The Failed Negotiation (strategic evidence withholding, litigation filing)

## Task

Conduct a comprehensive Damages Claim Quality Assurance Review for the case file. Systematically audit the case against all eight pitfall categories, identify deficiencies and risks, and produce a prioritized remediation plan to position the claim for maximum value.

## Inputs

- **Client**: {{client_name}}
- **Case Context**: {{case_context}}
- **Current Milestone**: {{milestone}} (Pre-Demand / Pre-Mediation / Pre-Trial / Proactive Audit)
- **Documents/Data Available**: {{uploaded_documents_or_data}}
- **Specific Concerns**: {{attorney_concerns}} (if any)

## Instructions

1. **Follow the "Damages Claim Quality Assurance Review" workflow step by step.**

2. **Phase 1 — Pre-Audit Setup**:
   - Load case context and inventory available documentation
   - Note the milestone triggering this review and any time constraints

3. **Phase 2 — Pitfall Analysis**:
   - Work through each of the 8 pitfall categories systematically
   - For each category, apply the specific quality check questions from the training report
   - Document findings: what's present, what's missing, what's deficient
   - Flag risks with severity assessment

4. **Phase 3 — Risk Assessment & Remediation**:
   - Compile all risk flags by severity (Critical / High / Medium / Low)
   - Generate specific, actionable remediation recommendations
   - Include strategic observations from case study patterns where applicable

5. **Apply these key concepts from the report**:
   - **MMI Timing**: No settlement discussions until MMI unless documented strategic exception
   - **Pain Mechanisms**: Classify documented pain (nociceptive, neuropathic, centrally amplified)
   - **Eggshell vs. Crumbling Skull**: Determine applicable doctrine for pre-existing conditions
   - **360-Degree Witnesses**: Evaluate coverage across plaintiff's life circles
   - **Lost Wages vs. Earning Capacity**: Match theory to plaintiff profile
   - **Algorithm Optimization**: Assess demand package for Colossus-type system alignment
   - **Human Review Triggers**: Flag disfigurement, PTSD, inner ear, and other non-standard injuries

6. **Ethical Boundaries**:
   - Do not provide legal advice or final legal conclusions
   - Do not recommend specific settlement amounts or whether to accept offers
   - Frame all analysis as supportive work product for the supervising attorney
   - Escalate critical risks requiring attorney decision

## Output

Provide a comprehensive markdown report with these sections:

### 1. Executive Summary
Brief overview (3-5 sentences) of overall case readiness and critical findings.

### 2. Milestone Checklist Status
Complete the appropriate master checklist from the report:
- Pre-Demand Preparation checklist (if pre-demand)
- Demand Package Assembly checklist (if assembling demand)
- Settlement Negotiation & Resolution checklist (if in negotiations)

### 3. Pitfall Analysis Matrix
Table format showing each of the 8 pitfalls with:
| Pitfall | Status | Key Findings | Severity |
|---------|--------|--------------|----------|

### 4. Risk Register
All identified risks with:
| Risk | Pitfall Category | Severity | Impact if Unaddressed |
|------|------------------|----------|----------------------|

### 5. Remediation Action Plan
Prioritized list with:
- Action item description
- Responsible party (attorney/paralegal/expert/client)
- Suggested timeline
- Resources needed

### 6. Documentation Gaps
Table of missing documents:
| Document/Information | Why Needed | Priority | Acquisition Method |
|---------------------|------------|----------|-------------------|

### 7. Strategic Recommendations
Case-specific tactical observations, including:
- Framing opportunities (if applicable)
- Anchoring strategies for damages valuation
- Negotiation tactics to consider
- Case study parallels that may apply

### 8. Attorney Escalation Items
List of decisions/actions requiring attorney input, flagged by urgency.
```

---

## Quick Reference: Master Checklist by Milestone

### Pre-Demand Preparation
- [ ] Prior medical records (5-10 years) obtained and reviewed
- [ ] 360-degree witness analysis conducted
- [ ] Appropriate damages theory selected
- [ ] All potential lienholders identified and notified

### Demand Package Assembly
- [ ] Client at MMI (or documented strategic exception)
- [ ] Package organized with summary, TOC, chronology, Bates-stamps, indexes
- [ ] Lost work time supported by medical necessity opinion
- [ ] Algorithm factors front-loaded (top diagnoses, first 60 factors)
- [ ] Human-review injuries flagged separately
- [ ] Medical expert opinion on pre-existing conditions

### Settlement Negotiation & Resolution
- [ ] All offers and client responses documented in writing
- [ ] Final written lien amounts obtained
- [ ] All liens negotiated for reduction
- [ ] Settlement agreement addresses lien satisfaction
- [ ] Client provided fully informed consent to final terms

---

## Appendix: Pain Mechanism Classification Guide

| Type | Cause | Description | Corroborating Evidence |
|------|-------|-------------|----------------------|
| **Nociceptive** | Tissue damage (fracture, tear, inflammation) | Aching, throbbing, movement-worsened | Swelling, limited ROM, imaging |
| **Neuropathic** | Nerve injury (radiculopathy, herniation) | Burning, shooting, electric, numbness | Dermatomal changes, weakness, EMG/NCS |
| **Centrally Amplified** | CNS over-sensitization | Widespread pain after tissue healing | Clinical diagnosis, pain out of proportion |

---

## Appendix: Damages Theory Decision Matrix

| Factor | Lost Wages | Loss of Earning Capacity |
|--------|------------|-------------------------|
| **Focus** | Past/present actual losses | Future projected losses |
| **Calculation** | Arithmetic (wage × time) | Projection (vocational + economist) |
| **Best For** | Steady job + temporary injury | Young/high potential OR permanent injury |
| **Key Evidence** | W-2s, pay stubs, employer records | Education, vocational expert, economist |
| **Vulnerability** | Doesn't capture future loss | Speculative without expert support |

---

*Module Version: 1.0*
*Source Report: Damages Practice — Pitfalls & Quality Checklist*
*Last Updated: December 2025*

