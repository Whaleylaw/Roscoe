# Lien Fundamentals & Classification — Operational Workflow & Prompt Template

---

## 1. Operational Workflow

### Workflow Name
**Lien Identification & Classification Workflow**

---

### Goal
Successfully identify, categorize, and document all third-party claims (liens, subrogation rights, assignments, and reimbursement rights) against a client's potential recovery at case intake. Classification must be accurate to determine applicable law, available defenses, and negotiation strategy.

**Success Criteria:**
- All potential third-party claims are inventoried
- Each claim is correctly classified as Statutory, Contractual, or Combination
- Critical data points are captured for each lien
- Red flags are identified and escalated appropriately
- A structured lien summary is produced for attorney review

---

### When to Use
- **Primary Trigger:** New case intake involving personal injury or any matter with potential third-party claims
- **Secondary Triggers:**
  - Discovery of new medical treatment or insurance coverage mid-case
  - Receipt of lien notice or demand letter from a third party
  - Settlement negotiations begin (to ensure complete lien inventory)
  - Client reports new government benefits (Medicare, Medicaid, VA, Workers' Comp)
  - Preparing for mediation or final settlement distribution

---

### Inputs Required

| Input | Description |
|-------|-------------|
| Client intake information | Name, DOB, contact details, case type |
| Medical treatment history | List of all providers, dates of service, treatment types |
| Insurance coverage details | Health insurance (private, employer-sponsored, government), auto insurance (MedPay, PIP) |
| Government benefits status | Medicare enrollment, Medicaid eligibility, VA benefits, Workers' Comp claims |
| Contracts/Agreements | Letters of Protection (LOPs), litigation funding agreements, insurance policies, plan documents, SPDs |
| Existing lien notices | Any filed hospital liens, statutory notices, or third-party demands received |
| Case damages estimate | Total claimed damages and anticipated recovery range |

---

### Step-by-Step Process

#### **Step 1: Conduct Initial Lien Discovery**

**1.1 Review Client Medical & Insurance History**
- Document all medical providers who rendered treatment related to the injury
- Identify all insurance coverage: private health, employer-sponsored, auto (MedPay/PIP), government programs
- Verify Medicare/Medicaid enrollment status (especially for clients 65+ or disabled)
- Check for any Workers' Compensation claims related to the incident
- Note any child support obligations that may create automatic liens

**1.2 Contact Providers and Insurers**
- Send inquiries to all known medical providers regarding:
  - Outstanding balances
  - Whether treatment was paid by insurance (and which insurer)
  - Any Letters of Protection or assignments on file
- Contact health insurers to request:
  - Payment history for accident-related claims
  - Notice of subrogation/reimbursement rights assertion
  - Plan documents and Summary Plan Description (SPD)

**1.3 Search Public Records**
- Check county records for filed hospital lien notices
- Search for any recorded statutory liens (varies by jurisdiction)
- Document filing dates and compliance with statutory requirements

**1.4 Create Lien Inventory**
- Compile master list of all identified or potential claims
- Include: claimant name, amount asserted, claim type (if known), date identified

---

#### **Step 2: Classify Each Claim Using Decision Tree**

For each identified claim, process through this classification logic:

```
┌─────────────────────────────────────────────────────────────────┐
│ Q1: Is the claim based on a specific state or federal statute? │
│     (e.g., Hospital Lien Act, Medicare Secondary Payer Act,    │
│     Workers' Comp statute, Child Support statute)              │
└─────────────────────────────────────────────────────────────────┘
           │                              │
          YES                             NO
           │                              │
           ▼                              ▼
   ┌───────────────┐        ┌─────────────────────────────────────┐
   │   STATUTORY   │        │ Q2: Is the claim based on a signed  │
   │     LIEN      │        │ agreement (LOP, insurance policy,   │
   └───────────────┘        │ litigation funding contract)?       │
                            └─────────────────────────────────────┘
                                      │                │
                                     YES               NO
                                      │                │
                                      ▼                ▼
                           ┌───────────────┐   ┌──────────────────┐
                           │  CONTRACTUAL  │   │ Q3: Is it from   │
                           │     LIEN      │   │ an employee      │
                           └───────────────┘   │ benefit plan     │
                                               │ (ERISA/FEHBP)?   │
                                               └──────────────────┘
                                                    │        │
                                                   YES       NO
                                                    │        │
                                                    ▼        ▼
                                           ┌─────────────┐ ┌─────────────┐
                                           │ COMBINATION │ │  ESCALATE   │
                                           │    LIEN     │ │ TO ATTORNEY │
                                           └─────────────┘ └─────────────┘
```

**Classification Reference:**

| Classification | Examples | Governing Authority |
|----------------|----------|---------------------|
| **Statutory** | Hospital liens, Workers' Comp liens, Medicare/Medicaid liens, Child Support liens, VA liens | Specific state or federal statute |
| **Contractual** | Letters of Protection, Private health insurance agreements, Litigation funding assignments | Contract terms + general insurance/contract law |
| **Combination** | ERISA health benefit plans, FEHBP (Federal Employee Health Benefits) | Federal statute (ERISA/FEHBA) + Plan document language |

---

#### **Step 3: Capture Critical Data Points for Each Lien**

For every classified claim, document the following structured data:

**3.1 Universal Data Points (All Liens)**
| Field | Description |
|-------|-------------|
| Claimant Name | Entity asserting the claim |
| Claim Type | Lien, Subrogation, Assignment, or Reimbursement |
| Classification | Statutory / Contractual / Combination |
| Amount Asserted | Dollar amount claimed |
| Date Asserted | When claim was first communicated |
| Supporting Documents | List all documents received/obtained |
| Contact Information | Claims rep name, phone, email, mailing address |

**3.2 Statutory Lien Data Points**
| Field | Description |
|-------|-------------|
| Governing Statute | Exact citation (e.g., KRS 216.820) |
| Perfection Status | Has lien been properly filed/perfected? |
| Perfection Deadline | Statutory deadline for filing |
| Filing Date | When lien notice was filed (if applicable) |
| Filing Location | County, court, or registry where filed |
| Required Notice | Any statutory notice requirements to plaintiff/attorney |
| Reduction Rights | Does statute allow pro-rata attorney fee deduction? |

**3.3 Contractual Lien Data Points**
| Field | Description |
|-------|-------------|
| Contract Type | LOP / Insurance Policy / Funding Agreement |
| Date Signed | When agreement was executed |
| Key Terms | Payment triggers, interest provisions, assignment scope |
| Governing State Law | Jurisdiction's contract/insurance law applies |

**3.4 Combination Lien Data Points (ERISA/FEHBP)**
| Field | Description |
|-------|-------------|
| Plan Name | Official name of employee benefit plan |
| Plan Type | Self-Funded or Fully-Funded |
| Plan Sponsor | Employer or union sponsoring the plan |
| Plan Administrator | TPA or insurance company administering claims |
| Subrogation Language | Exact plan language re: recovery rights |
| Reimbursement Language | Exact plan language re: reimbursement |
| Made Whole Override? | Does plan language specifically override Made Whole Doctrine? |
| Common Fund Override? | Does plan language specifically override Common Fund Doctrine? |
| Documents Obtained | SPD, Plan Document, Certificate of Coverage |

---

#### **Step 4: Analyze Strategic Implications**

For each classified lien, note the strategic implications:

**Statutory Liens:**
- [ ] Verify perfection—unperfected lien may be unenforceable against recovery
- [ ] Check for statutory reduction rights (attorney fee sharing)
- [ ] Note: underlying debt may still exist even if lien is unenforceable
- [ ] Identify any hardship or pro-rata reduction provisions

**Contractual Liens:**
- [ ] Review contract for negotiation flexibility
- [ ] Check if state insurance regulations apply
- [ ] Identify proportionality/hardship arguments available
- [ ] Note any interest accrual provisions

**Combination Liens:**
- [ ] Determine self-funded vs. fully-funded status (critical for preemption analysis)
- [ ] If self-funded: Made Whole and Common Fund may NOT apply (federal preemption)
- [ ] If fully-funded: State insurance laws may apply via ERISA "savings clause"
- [ ] Flag for attorney review of plan language interpretation

---

#### **Step 5: Identify Red Flags & Escalate**

**Immediately escalate to supervising attorney if:**

| Red Flag | Why It Matters |
|----------|----------------|
| **Unclear Classification** | Cannot definitively categorize as Statutory/Contractual/Combination; or claim has competing characteristics |
| **Complex ERISA Plan** | Plan documents are ambiguous, incomplete, or self-funded vs. fully-funded status cannot be determined |
| **Multiple Competing Liens** | Several different lien types against limited recovery fund—creates complex distribution and negotiation scenario |
| **Disputed Validity/Perfection** | Evidence suggests lien was not properly perfected or underlying debt is invalid/unreasonable |
| **Potential Ethical Conflict** | Referral agreement with provider that guarantees settlement share; may compromise attorney's duty of loyalty |
| **Federal Government Lien (Medicare/Medicaid)** | "Super lien" status—attorneys can face double damages for non-compliance |
| **Large Liens Exceeding Anticipated Recovery** | Total liens approach or exceed expected settlement; requires strategic planning |

---

#### **Step 6: Compile Lien Summary Report**

Generate a structured report containing:

1. **Executive Summary**
   - Total number of liens identified
   - Total amount asserted across all liens
   - Classification breakdown (# Statutory, # Contractual, # Combination)
   - Critical flags requiring attorney attention

2. **Lien Detail Table**
   - One row per lien with all captured data points
   - Classification and strategic notes

3. **Missing Information / Open Questions**
   - Documents still needed
   - Verification steps pending
   - Clarifications required from client

4. **Preliminary Strategy Notes**
   - Initial observations on negotiation leverage
   - Potential perfection issues or defenses
   - Preemption concerns for combination liens

---

### Quality Checks & Safeguards

**Before Finalizing Lien Inventory:**
- [ ] All medical providers cross-referenced against treatment records
- [ ] Medicare/Medicaid enrollment verified (not assumed)
- [ ] All insurance policies reviewed for subrogation clauses
- [ ] Public records search completed for statutory lien filings
- [ ] Client confirmed no additional providers or benefits

**Classification Validation:**
- [ ] Each classification includes citation to governing authority (statute or contract)
- [ ] ERISA plans include self-funded/fully-funded determination with supporting evidence
- [ ] Perfection status verified for all statutory liens

**Documentation Standards:**
- [ ] All assertions backed by documentation (not just verbal claims)
- [ ] Amounts verified against itemized statements
- [ ] Key contractual terms quoted directly from source documents

**Ethical Safeguards:**
- [ ] No legal conclusions or advice provided—analysis framed as supportive work product
- [ ] All red flags escalated to supervising attorney
- [ ] Client-paid amounts distinguished from insurer-paid amounts

---

### Outputs

| Deliverable | Format | Description |
|-------------|--------|-------------|
| **Lien Inventory Spreadsheet** | Table/CSV | Master list of all identified liens with core data points |
| **Lien Classification Summary** | Markdown Report | Detailed analysis of each lien with classification rationale |
| **Critical Data Capture Form** | Structured Form | Complete data points for each lien category |
| **Red Flag Alert List** | Bulleted List | Items requiring immediate attorney review |
| **Missing Documents Tracker** | Checklist | Documents needed and status of requests |
| **Strategy Implications Memo** | Narrative | Preliminary observations on negotiation leverage and defenses |

---

## 2. Prompt Template for AI Paralegal

```
You are an AI Paralegal operating under the "Lien Fundamentals & Classification" module.

## Reference

You have been trained on the "Lien Fundamentals & Classification" report, which defines:
- Core legal concepts: lien, subrogation, assignment, right of reimbursement
- The three-category classification system: Statutory, Contractual, Combination
- Classification decision tree and procedures
- Critical data points to capture for each lien type
- Red flags and escalation triggers
- Strategic implications of each classification

## Task

Identify, classify, and document all third-party claims (liens, subrogation rights, assignments, and reimbursement rights) against the client's potential recovery. Produce a comprehensive lien inventory and classification summary following the "Lien Identification & Classification Workflow."

## Inputs

- **Client:** {{client_name}}
- **Case Context:** {{case_context}} (e.g., MVA, slip and fall, premises liability)
- **Date of Injury:** {{date_of_injury}}
- **Anticipated Recovery Range:** {{recovery_range}}
- **Medical Providers:** {{list_of_medical_providers}}
- **Insurance Coverage:** {{insurance_coverage_details}}
- **Government Benefits:** {{government_benefits_status}}
- **Documents Provided:** {{uploaded_documents_or_data}}
- **Existing Lien Notices:** {{known_lien_assertions}}

## Instructions

1. **Conduct Initial Lien Discovery**
   - Review all provided medical and insurance information
   - Identify all potential claimants (providers, insurers, government programs)
   - Note any public record searches needed for statutory lien filings
   - Create an initial inventory of all potential claims

2. **Classify Each Claim Using the Decision Tree**
   - Apply the three-category classification system from the report
   - For each claim, determine: Is it Statutory, Contractual, or Combination?
   - Document the specific governing authority (statute citation or contract type)
   - For ERISA/FEHBP plans, note self-funded vs. fully-funded status if determinable

3. **Capture Critical Data Points**
   - Complete the appropriate data capture template for each lien type
   - For Statutory liens: verify perfection status and governing statute
   - For Contractual liens: document key agreement terms
   - For Combination liens: extract exact plan language on subrogation/reimbursement

4. **Identify Red Flags**
   - Flag any unclear classifications for attorney review
   - Note complex ERISA situations requiring plan document analysis
   - Identify competing liens against limited recovery
   - Highlight any potential perfection failures or validity disputes
   - Alert to any ethical concerns (referral arrangements, conflicts)

5. **Compile Lien Summary Report**
   - Executive summary with totals and critical flags
   - Detailed table with all liens and captured data
   - Missing information and open questions
   - Preliminary strategic observations

## Quality Standards

- Apply the checklists, critical data points, and red-flag rules from the "Lien Fundamentals & Classification" report
- Verify all classifications against the report's definitions
- Distinguish between facts (documented) and inferences (requiring verification)
- Do NOT provide legal advice or final legal conclusions
- Frame all analysis as supportive work product for a supervising attorney

## Output Format

Provide a markdown report with the following sections:

### 1. Executive Summary
- Total liens identified: [count]
- Total amount asserted: $[amount]
- Classification breakdown: [X Statutory, Y Contractual, Z Combination]
- Critical items requiring attorney review: [list]

### 2. Lien Inventory Table

| # | Claimant | Type | Classification | Amount | Status | Priority Issues |
|---|----------|------|----------------|--------|--------|-----------------|
| 1 | [name] | [type] | [class] | $[amt] | [status] | [notes] |

### 3. Detailed Classification Analysis
For each lien:
- **Claimant:** [name]
- **Classification:** [Statutory/Contractual/Combination]
- **Governing Authority:** [statute/contract reference]
- **Amount Asserted:** $[amount]
- **Key Data Points:** [per category requirements]
- **Strategic Notes:** [observations]

### 4. Red Flags & Escalation Items
[Bulleted list of items requiring attorney attention]

### 5. Missing Information & Open Questions
[What still needs to be obtained or verified]

### 6. Preliminary Strategic Observations
[Initial thoughts on negotiation leverage, defenses, potential issues—framed as observations for attorney consideration, not legal conclusions]

---

**Important Limitations:**
- This analysis is based on information provided and the framework in the training report
- Classification determinations require attorney verification
- Strategic implications are preliminary observations, not legal advice
- All red flag items must be escalated before proceeding with lien negotiation
```

---

## Appendix: Quick-Reference Glossary

| Term | Definition |
|------|------------|
| **Assignment** | Contractual transfer of recovery rights from injured party to third party (e.g., provider, funding company) |
| **Common Fund Doctrine** | Equitable principle requiring lienholders benefiting from recovery to share proportionally in attorney's fees/costs |
| **Contractual Lien** | Lien created through specific agreement between parties (e.g., LOP) |
| **ERISA Plan** | Employee benefit plan governed by federal Employee Retirement Income Security Act |
| **Fully-Funded Plan** | ERISA plan where employer purchases insurance policy; may be subject to state laws via "savings clause" |
| **Lien** | Legal claim or interest on plaintiff's recovery in personal injury case |
| **Made Whole Doctrine** | Equitable rule preventing reimbursement until injured person fully compensated |
| **Medicare Set-Aside (MSA)** | Allocation from settlement for future Medicare-covered expenses |
| **Perfection** | Legal steps (e.g., filing notice) necessary to make statutory lien enforceable |
| **Preemption** | Federal law superseding conflicting state law (critical in ERISA context) |
| **Right of Reimbursement** | Benefit provider's claim for direct repayment from plaintiff's settlement |
| **Self-Funded Plan** | ERISA plan where employer assumes financial risk; exempt from state insurance regulations |
| **Statutory Lien** | Lien created by specific state or federal law |
| **Subrogation** | Right of third party to "step into shoes" of injured party to pursue tortfeasor |

---

## Appendix: Classification Quick-Reference Card

| If Claim Is From... | Classification | Key Considerations |
|---------------------|----------------|-------------------|
| Hospital (with filed lien) | **Statutory** | Check perfection; review state hospital lien act |
| Workers' Compensation carrier | **Statutory** | State WC statute governs; usually mandatory reimbursement |
| Medicare | **Statutory** | "Super lien"—strict compliance required; MSA may be needed |
| Medicaid | **Statutory** | State-specific rules; may allow pro-rata reductions |
| Child Support enforcement | **Statutory** | Automatic liens on settlements; limited negotiation |
| Private health insurer (individual policy) | **Contractual** | Policy terms + state insurance regulations |
| Medical provider with LOP | **Contractual** | Agreement terms govern; negotiate based on proportionality |
| Litigation funding company | **Contractual** | Assignment terms govern; review interest/fees |
| Employer-sponsored health plan | **Combination** | Determine self-funded vs. fully-funded; obtain plan docs |
| FEHBP (federal employee) | **Combination** | Federal preemption applies; plan language controls |
| VA/TRICARE | **Statutory/Combination** | Federal statute governs; strict compliance required |

