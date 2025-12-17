# Medicare Set-Asides (MSAs): Compliance and Strategy

## Operational Workflow

---

### Workflow Name
**MSA Compliance Evaluation and Strategy Workflow**

---

### Goal
Successfully evaluate whether a Medicare Set-Aside is required for a settling case, implement appropriate avoidance or reduction strategies where legally permissible, and ensure compliant documentation that protects the client from catastrophic Medicare payment denials.

---

### When to Use
- **During settlement negotiations** when client is a current Medicare beneficiary
- **When client has applied** for Social Security Disability benefits
- **When client will become Medicare-eligible** within 30 months of anticipated settlement
- **When demand letters or pleadings** include claims for future/permanent medical damages
- **Before finalizing any settlement release** that includes waiver of future medical claims

---

### Inputs Required

| Input | Source | Purpose |
|-------|--------|---------|
| Client Medicare eligibility status | Client intake, Medicare verification | Determines if MSA rules apply |
| SSDI application status | Client questionnaire | Assesses 30-month eligibility window |
| Demand letters and pleadings | Case file | Identifies future medical damage claims |
| Treating physician records | Medical records | Documents prognosis and future care needs |
| Current medication list | Pharmacy records, medical records | Calculates prescription component of MSA |
| Recommended surgeries/procedures | Specialist reports | Major cost drivers in allocation |
| Life expectancy factors | Medical records (comorbidities) | Potential for rated age reduction |
| Settlement amount and structure | Settlement negotiations | Determines CMS threshold applicability |

---

### Step-by-Step Process

#### **Step 1: Verify Medicare Beneficiary Status**
- [ ] Check case file for documentation of current Medicare Part A or Part B enrollment
- [ ] Query client directly: "Are you currently enrolled in Medicare?"
- [ ] Document Medicare Health Insurance Claim Number (HICN) or Medicare Beneficiary Identifier (MBI) if applicable
- [ ] **If YES → Proceed to Step 3**
- [ ] **If NO → Proceed to Step 2**

#### **Step 2: Assess Future Medicare Eligibility (30-Month Window)**
- [ ] Determine if client has applied for or is receiving Social Security Disability Insurance (SSDI)
- [ ] Calculate: Will client turn 65 within 30 months of anticipated settlement date?
- [ ] Assess if client could receive a "back award" of SSDI benefits that would accelerate eligibility
- [ ] Evaluate end-stage renal disease (ESRD) or ALS status (automatic Medicare qualification)
- [ ] **If reasonable expectation of eligibility within 30 months → Proceed to Step 3**
- [ ] **If NO reasonable expectation → Document finding; MSA not triggered by beneficiary status**

#### **Step 3: Analyze Damages Claimed for Future Medical Component**
Scan the following documents for triggering language:

| Document | Search Terms |
|----------|--------------|
| Demand letters | "future medical," "permanent medical," "lifetime medical," "ongoing care," "catastrophic medical needs" |
| Complaints/Pleadings | Same as above + general damages paragraphs |
| Discovery responses | Interrogatory answers regarding future treatment |
| Expert reports | Life care plans, future medical cost projections |

- [ ] **If future medical damages claimed → Proceed to Step 4**
- [ ] **If NO future medical damages claimed → Document finding; evaluate MSA avoidance pathway**

#### **Step 4: Review Treating Physician Prognosis**
- [ ] Obtain most recent treatment records from all treating providers
- [ ] Identify any documented plan of care for ongoing treatment
- [ ] Extract:
  - Recommended future office visits/follow-ups
  - Prescribed medications (current and anticipated)
  - Recommended surgeries or procedures
  - Physical therapy or rehabilitation needs
  - Durable Medical Equipment (DME) requirements
  - Diagnostic imaging needs

- [ ] **If physician documents need for future injury-related care → MSA likely required**
- [ ] **If physician indicates treatment complete → Evaluate Certification of No Future Treatment pathway**

#### **Step 5: Make MSA Necessity Determination**

Apply decision logic:

```
IF (Current Medicare Beneficiary OR Expected Eligibility ≤ 30 months)
   AND
   (Future Medical Damages Claimed OR Physician Documents Future Care Needs)
THEN → MSA Required (Flag for Attorney Review)
ELSE → MSA May Be Avoided (Proceed to Step 6)
```

Document determination with supporting evidence citations.

#### **Step 6: Evaluate MSA Avoidance Strategies**

**Option A: Certification of No Future Treatment**
Requirements (ALL must be met):
- [ ] Letter from **treating physician** (NOT defense IME)
- [ ] On official **letterhead**, dated, and signed
- [ ] **Unequivocal language**: "No future care required for injury"
- [ ] **NO qualifying language** such as:
  - ❌ "at this time"
  - ❌ "as needed"  
  - ❌ "unlikely"
  - ❌ "probably not"

If certification obtained and meets all requirements → Document and proceed without MSA

**Option B: No Medical Damages Claimed**
- Applicable in wrongful death cases where damages are for living heirs
- Settlement must explicitly exclude future medical component
- Release language must be carefully crafted (escalate to attorney)

#### **Step 7: Implement MSA Reduction Strategies (If MSA Required)**

**Strategy 7A: Rated Age Assessment**
- [ ] Identify comorbidities unrelated to injury (diabetes, heart disease, cancer history, etc.)
- [ ] Refer client to life underwriting company for rated age calculation
- [ ] Obtain written assessment with medical justification
- [ ] Apply rated age to recalculate lifetime care costs

**Strategy 7B: Medication Review**
- [ ] List all injury-related medications with current costs
- [ ] Identify brand-name drugs with generic equivalents
- [ ] Consult with treating physician on substitution approval
- [ ] Document physician approval for generic switches
- [ ] Recalculate prescription component with reduced costs

**Strategy 7C: Surgery Election Documentation**
- [ ] If client definitively declines recommended surgery:
  - [ ] Obtain written statement from client documenting refusal
  - [ ] Obtain physician statement acknowledging client's informed decision
- [ ] ⚠️ **CAVEAT**: CMS not legally bound to accept this election
- [ ] Present as negotiation tool with full disclosure of risk to client

#### **Step 8: Calculate MSA Allocation**

Include all reasonably foreseeable Medicare-covered expenses:

| Category | Items to Include |
|----------|------------------|
| Office visits | All injury-related follow-ups |
| Diagnostics | MRIs, X-rays, CT scans, lab work |
| Prescriptions | Medications + refills × life expectancy |
| Surgeries | Recommended procedures + revision surgeries |
| Therapy | Physical therapy, occupational therapy |
| DME | Equipment + replacements over lifetime |

#### **Step 9: Determine Administration Structure**

Present options to attorney and client:

| Structure | Pros | Cons |
|-----------|------|------|
| **Lump Sum / Self-Administered** | Lowest cost, client control | High burden, compliance risk, annual reporting required |
| **Lump Sum / Professional Admin** | Reduced burden, expert compliance | Setup and ongoing fees |
| **Structured Annuity / Professional** | Cost savings for long-term care | Less flexibility for unexpected expenses |

#### **Step 10: Document and Package for Attorney Review**

Compile MSA analysis package:
- [ ] MSA Necessity Evaluation (with decision logic documented)
- [ ] Beneficiary status verification
- [ ] Damages analysis with supporting citations
- [ ] Treating physician prognosis summary
- [ ] Avoidance strategy evaluation (if applicable)
- [ ] Reduction strategy documentation (if applicable)
- [ ] MSA allocation calculation worksheet
- [ ] Administration recommendation
- [ ] Risk disclosures for client review

---

### Quality Checks & Safeguards

#### Pre-Submission Validation
- [ ] Verify Medicare status documentation is current (< 30 days)
- [ ] Confirm all claimed medications appear in treating records
- [ ] Cross-reference surgery recommendations with specialist reports
- [ ] Validate life expectancy calculations (standard or rated age)
- [ ] Ensure all costs reflect Medicare-covered services only

#### Red Flag Escalation Triggers

| Red Flag | Risk Level | Required Action |
|----------|------------|-----------------|
| Settlement release waives future medicals without MSA analysis | 🔴 CRITICAL | Immediate escalation to supervising attorney |
| Certification of No Future Treatment contains qualifying language ("at this time," "as needed") | 🔴 CRITICAL | Reject certification; obtain compliant version or establish MSA |
| "Evidence-Based" or "Non-Submit" MSA proposed without CMS submission | 🟠 HIGH | Ensure full client consent with documented risk acknowledgment |
| Client refuses to fund adequate MSA | 🟠 HIGH | Document refusal; escalate for attorney guidance on liability exposure |
| CMS threshold exceeded but no formal submission planned (Workers' Comp) | 🟠 HIGH | Flag for threshold review ($25K current beneficiary / $250K expected) |
| Settlement contains "entire settlement" general release | 🟡 MODERATE | Verify MSA or valid certification in place |

#### Compliance Checkpoints
- [ ] Never advise client they can skip MSA without proper legal basis
- [ ] Always document rationale for MSA avoidance decisions
- [ ] Preserve all correspondence with treating physicians
- [ ] Maintain audit trail for all calculations

---

### Outputs

| Artifact | Format | Purpose |
|----------|--------|---------|
| **MSA Necessity Evaluation Report** | Markdown/PDF | Documents decision logic and supporting evidence |
| **Medicare Eligibility Verification** | Summary with source citations | Establishes beneficiary status |
| **Damages Analysis Summary** | Table with document references | Identifies triggering language in pleadings |
| **Certification of No Future Treatment** | Formal letter (if obtained) | Supports MSA avoidance |
| **MSA Reduction Strategy Memo** | Narrative with supporting documentation | Justifies reduced allocation |
| **MSA Allocation Worksheet** | Spreadsheet/Table | Itemized cost calculation |
| **Administration Recommendation** | Memo with options analysis | Guides funding structure decision |
| **Client Risk Disclosure** | Template with signature line | Documents informed consent |
| **Attorney Action Items** | Checklist | Prioritized next steps |

---

## Prompt Template for AI Paralegal

```
You are an AI Paralegal operating under the "Medicare Set-Asides (MSAs): Compliance and Strategy" module.

Reference:
- You have been trained on the "Medicare Set-Asides (MSAs): Compliance and Strategy" report, which defines the legal basis, triggering conditions, avoidance and reduction strategies, compliance procedures, and catastrophic risks of non-compliance with Medicare Secondary Payer Act obligations.

Task:
- {{task_description, e.g., "Evaluate whether an MSA is required for this settling case, identify available avoidance or reduction strategies, and produce a compliance analysis for attorney review."}}

Inputs:
- Client: {{client_name}}
- Case Context: {{case_context, e.g., "Personal injury MVA, client age 64, settlement negotiations at $175,000"}}
- Medicare Status: {{medicare_status, e.g., "Not currently enrolled; SSDI application pending"}}
- Damages Claimed: {{damages_summary, e.g., "Demand letter claims 'permanent injury requiring ongoing care'"}}
- Documents Available: {{uploaded_documents_or_data, e.g., "Demand letter, treating physician records, current medication list"}}

Instructions:
1. Follow the "MSA Compliance Evaluation and Strategy Workflow" step by step.

2. Apply the following key decision points from the report:
   - MSA triggered when: (Medicare beneficiary OR expected eligibility ≤ 30 months) AND (future medical damages claimed OR physician documents future care needs)
   - Avoidance requires: Treating physician certification with NO qualifying language ("at this time," "as needed," "unlikely")
   - Reduction strategies: Rated age, generic medication substitution, documented surgery refusal

3. Evaluate these critical red flags:
   - Settlement releases future medicals without MSA analysis → CRITICAL ESCALATION
   - Weak certification language → Certification invalid
   - "Evidence-based" MSA without CMS submission → Client must acknowledge risk
   - Client refusal to fund adequate MSA → Document and escalate

4. Apply CMS threshold awareness:
   - Workers' Comp: $25,000 (current beneficiary) or $250,000 (expected within 30 months) triggers formal CMS review option
   - Liability/No-Fault: No formal CMS review process; settling parties bear full compliance burden

5. Calculate MSA allocation components if required:
   - Future Medicare-covered treatment only
   - Medications including refills × life expectancy
   - Surgeries including revisions
   - DME with replacement schedule
   - Diagnostic imaging and therapy

6. Do not provide legal advice or final legal conclusions. Frame all analysis as supportive work product for a supervising attorney. Flag uncertainties and present options rather than making binding determinations.

Output:
Provide a structured markdown report with the following sections:

## 1. Executive Summary
- MSA determination: Required / Avoidable / Uncertain (escalate)
- Key risk factors identified
- Recommended next steps

## 2. Medicare Eligibility Analysis
- Current beneficiary status with verification source
- 30-month eligibility window assessment
- Supporting documentation citations

## 3. Damages Analysis
- Future medical claims identified in pleadings
- Triggering language extracted (with document/page references)
- Treating physician prognosis summary

## 4. MSA Determination
- Decision logic applied
- Supporting evidence for determination
- Confidence level and any uncertainties

## 5. Avoidance Strategy Evaluation (if applicable)
- Certification of No Future Treatment feasibility
- Language requirements assessment
- Treating physician contact recommendation

## 6. Reduction Strategy Options (if MSA required)
- Rated age opportunity assessment
- Medication review recommendations
- Surgery election documentation status

## 7. MSA Allocation Estimate (if MSA required)
| Category | Projected Cost | Calculation Basis |
|----------|----------------|-------------------|
| [itemized] | [amount] | [source/methodology] |

## 8. Red Flags & Escalation Items
- Issues requiring immediate attorney attention
- Risk disclosures needed for client

## 9. Open Questions / Missing Information
- Data gaps that prevent complete analysis
- Documents or information to request

## 10. Recommended Attorney Action Items
- Prioritized next steps with rationale
```

---

## Quick Reference: MSA Decision Matrix

| Client Status | Future Medicals Claimed? | Physician Documents Future Care? | MSA Required? |
|---------------|--------------------------|----------------------------------|---------------|
| Current Medicare beneficiary | Yes | Yes | **YES** |
| Current Medicare beneficiary | Yes | No | **Likely YES** - verify prognosis |
| Current Medicare beneficiary | No | Yes | **Likely YES** - review release language |
| Current Medicare beneficiary | No | No | Possible avoidance with strong certification |
| Expected eligible ≤ 30 months | Yes | Yes | **YES** |
| Expected eligible ≤ 30 months | Yes | No | **Likely YES** |
| Expected eligible ≤ 30 months | No | No | Possible avoidance with strong certification |
| Not eligible, no expectation | Any | Any | **No MSA required** (document status) |

---

## Template: Certification of No Future Treatment Request

```
[Date]

[Treating Physician Name], M.D.
[Practice Name]
[Address]

RE: Medical Certification Request
    Patient: [Client Name]
    DOB: [Date of Birth]
    Date of Injury: [Date]

Dear Dr. [Name]:

We represent [Client Name] in a personal injury matter arising from [brief incident description] on [date]. As part of settlement negotiations, we require a certification regarding [his/her] future medical needs related to this injury.

If applicable, please provide a letter on your official letterhead stating whether [Client Name] requires any future medical treatment, medication, therapy, or follow-up care for injuries sustained in this incident.

IMPORTANT: If you determine that no future treatment is required, your certification must:
- Be printed on your official letterhead
- Be dated and signed
- Use clear, unequivocal language (e.g., "No future medical treatment will be required for these injuries")
- Avoid any qualifying phrases such as "at this time," "as needed," or "unlikely"

Please contact our office if you have questions or need additional information.

Sincerely,

[Attorney Name]
[Firm Name]
```

---

## Consequence Reminder

⚠️ **CRITICAL CLIENT RISK**: If an MSA is required but not established, CMS may deem the entire settlement primary to Medicare. The client will be denied Medicare payment for ALL injury-related medical services until they can prove they have exhausted an amount equal to their entire net settlement on that medical care. This forces the client to use funds intended for pain and suffering, lost wages, and other damages to pay for medical treatment before Medicare resumes coverage.

This outcome is **irreversible** and represents the primary failure scenario this workflow is designed to prevent.



