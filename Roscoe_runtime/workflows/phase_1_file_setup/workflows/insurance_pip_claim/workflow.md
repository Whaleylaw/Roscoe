---
name: insurance_pip_claim
description: >
  Open and set up Personal Injury Protection (PIP) insurance claims. Runs the Kentucky
  PIP waterfall to determine correct carrier, completes KACP Application (ALWAYS required),
  sends Letter of Representation, follows up for acknowledgment, and confirms coverage
  ready to pay bills. When Claude needs to open a PIP claim, determine PIP carrier,
  complete PIP application, or verify PIP is paying bills. Use for MVA cases in Kentucky.
phase: file_setup
workflow_id: insurance_pip_claim
related_skills:
  - pip-waterfall
  - pip-application
  - lor-generator
related_tools:
  - pip_waterfall.py
  - generate_document.py
templates:
  - templates/2022 Whaley LOR to PIP Adjuster(1)(1) (1).docx
  - templates/KACP-Application-03.2021(1) (1).pdf
---

# PIP Claim Setup Workflow

## Purpose

Open and manage Personal Injury Protection (PIP) insurance claims for Kentucky MVA cases. This workflow:
1. Runs the PIP waterfall to determine the correct carrier
2. Completes the KACP Application (ALWAYS required)
3. Sends Letter of Representation to PIP carrier
4. Follows up for claim acknowledgment
5. Confirms coverage is ready to pay medical bills

**IMPORTANT:** The KACP Application is ALWAYS mandatory for PIP claims in Kentucky, regardless of which carrier provides coverage. All insurers accept this form.

---

## Trigger

This workflow is triggered when:
- MVA case is in Phase 1
- User mentions PIP or "medical payments"
- After police report identifies insurance
- When setting up insurance claims

---

## Prerequisites

Before starting this workflow, ensure:
- Case is MVA (PIP applies to motor vehicle accidents only)
- Case is in Kentucky (Kentucky-specific PIP rules)
- Client has signed HIPAA and contract (Phase 0 complete)
- Basic accident and client information available

---

## PIP Waterfall Logic (Kentucky)

The Kentucky PIP waterfall determines which insurer provides PIP coverage:

```
Step 1: Is client on TITLE of vehicle they were in?
        ├── YES → Is that vehicle INSURED?
        │         ├── YES → Vehicle's insurer provides PIP
        │         └── NO → ⚠️ CLIENT DISQUALIFIED FROM PIP
        └── NO → Continue to Step 2

Step 2: Was the vehicle client occupied INSURED?
        ├── YES → Vehicle's insurer provides PIP
        └── NO → Continue to Step 3

Step 3: Does CLIENT have own auto insurance?
        ├── YES → Client's insurer provides PIP
        └── NO → Continue to Step 4

Step 4: Does HOUSEHOLD MEMBER have auto insurance?
        ├── YES → Household member's insurer provides PIP
        └── NO → Continue to Step 5

Step 5: No coverage found → Kentucky Assigned Claims (KAC)
```

**CRITICAL DISQUALIFICATION:** If client is on the title of an UNINSURED vehicle they were occupying, they are DISQUALIFIED from PIP benefits entirely.

---

## Steps

### Step 1: Run PIP Waterfall

**Tool:** `tools/pip_waterfall.py`
**Skill:** `pip-waterfall`

**Actions:**
1. Gather waterfall inputs through questions
2. Run pip_waterfall.py tool
3. Record determination result

**Waterfall Questions:**
| Question | Used to Determine |
|----------|-------------------|
| Is client on TITLE of vehicle occupied? | Step 1 |
| Was that vehicle insured? | Step 1 check |
| Was the vehicle occupied insured? | Step 2 |
| Does client have own auto insurance? | Step 3 |
| Does household member have auto insurance? | Step 4 |

**Possible Outcomes:**
| Outcome | PIP Insurer Type | Next Steps |
|---------|------------------|------------|
| Vehicle's insurer | `vehicle` | Proceed to Step 2 |
| Client's insurer | `client` | Proceed to Step 2 |
| Household insurer | `household` | Proceed to Step 2 |
| KAC | `kac` | Proceed to Step 2 (KAC process) |
| DISQUALIFIED | `disqualified` | Stop - no PIP available |

**Disqualification Handling:**
```
⚠️ CLIENT DISQUALIFIED FROM PIP BENEFITS

The client was occupying a vehicle titled in their name that was UNINSURED.
Under Kentucky law, owners of uninsured motor vehicles are not entitled to 
PIP benefits.

IMPLICATIONS:
- No PIP coverage available
- Medical bills must be paid through:
  - Health insurance
  - Out of pocket
  - BI settlement (eventually)
- Focus recovery efforts on BI claim against at-fault party

This is documented in the case file. Proceeding with BI claim only.
```

**Completion Check:** `insurance.pip.pip_insurer` is populated (or `is_disqualified == true`)

### Step 2: Complete KACP Application

**Template:** `templates/KACP-Application-03.2021(1) (1).pdf`
**Tool:** `generate_document.py`
**Skill:** `pip-application`

**IMPORTANT:** The KACP Application is ALWAYS required, even when PIP is through a private insurer. All carriers accept this form.

**Actions:**
1. Copy KACP Application to destination: `/{project}/Insurance/{pip_company}/KACP Application.pdf`
2. Call `generate_document.py` with the destination path
3. Tool auto-fills form fields from case data
4. Identify any missing required fields
5. Present to user for review/completion
6. User signs application
7. Submit to PIP carrier

**Document Generation Pattern:**
```bash
# Step 1: Copy PDF form to Insurance folder
cp "/templates/KACP-Application-03.2021(1) (1).pdf" \
   "/{project}/Insurance/{pip_company}/KACP Application.pdf"

# Step 2: Generate filled form (path provides context)
python generate_document.py "/{project}/Insurance/{pip_company}/KACP Application.pdf"
```

**Application Field Mapping:**
| PDF Field | Data Source |
|-----------|-------------|
| Your Name | overview.client_name |
| Home Phone | overview.client_phone |
| Your Address | overview.client_address |
| Date of Birth | contacts[type=client].dob |
| SSN | contacts[type=client].ssn |
| Date and Time of Accident | overview.accident_date |
| Brief Description | overview.case_summary |
| Insurance Company/Policy | pip determination result |
| Doctor's Name/Address | medical_providers[] |
| Employer Name/Address | contacts[type=employer] |

**Completion Check:** `insurance.pip.date_pip_application_sent` is populated

### Step 3: Send Letter of Representation

**Template:** `templates/2022 Whaley LOR to PIP Adjuster(1)(1) (1).docx`
**Tool:** `generate_document.py`
**Skill:** `lor-generator`

**Actions:**
1. Copy PIP LOR template to destination: `/{project}/Insurance/{pip_company}/LOR to PIP Adjuster.docx`
2. Call `generate_document.py` with the destination path
3. Tool auto-fills all placeholders from case data
4. Present filled document to user for review/approval
5. Send via email/fax (or user sends manually)
6. Record sent date

**Document Generation Pattern:**
```bash
# Step 1: Copy template to Insurance folder
cp "/templates/2022 Whaley LOR to PIP Adjuster(1)(1) (1).docx" \
   "/{project}/Insurance/{pip_company}/LOR to PIP Adjuster.docx"

# Step 2: Generate filled document
python generate_document.py "/{project}/Insurance/{pip_company}/LOR to PIP Adjuster.docx"
```

**PIP LOR Special Instructions:**
The template includes Kentucky-specific PIP instructions:
- "$6,000 reserve for bills as they come in"
- Exception for hospital or hospital-related bills
- Confirm this instruction with user (may vary by case)

**Completion Check:** `insurance.pip.date_lor_sent` is populated

### Step 4: Open Claim (if needed)

**Owner:** User (phone call to carrier)

**Actions:**
1. If claim not already assigned:
   - User calls PIP carrier
   - Reports accident and injury
   - Provides client info, policy info, accident date
   - Carrier assigns claim number
2. Record claim number and date

**For KAC Cases:**
- Submit KACP Application to Kentucky Assigned Claims Plan
- KAC will assign an insurer to handle the claim
- May take longer than direct insurer

**Completion Check:** `insurance.pip.claim_number` is populated

### Step 5: Confirm Claim Acknowledgment

**Timeline:** 3-5 business days after LOR sent

**Actions:**
1. Monitor for response from PIP carrier
2. If no response in 5 days → Prompt user to call
3. Obtain adjuster name and contact information
4. Confirm claim is active

**Data to Update:**
```json
{
  "claim_acknowledged": true,
  "date_claim_acknowledged": "2024-12-04",
  "adjuster_name": "Bob PIP-Adjuster",
  "adjuster_phone": "800-555-9999",
  "adjuster_email": "bob@insurance.com"
}
```

**Completion Check:** `insurance.pip.claim_acknowledged == true`

### Step 6: Verify Ready to Pay Bills

**Timeline:** Within 7-10 days of LOR

**Actions:**
1. Contact PIP adjuster
2. Confirm PIP coverage is active
3. Obtain coverage limits ($10,000 standard in Kentucky)
4. Confirm any deductible
5. Verify PIP is ready to pay bills as received
6. Document billing instructions

**Data to Update:**
```json
{
  "coverage_limit": 10000,
  "deductible_amount": 0,
  "ready_to_pay_bills": true,
  "date_verified_payment_ready": "2024-12-06",
  "billing_instructions": "Send bills directly to adjuster"
}
```

**Completion Check:** `insurance.pip.ready_to_pay_bills == true`

---

## Skills Reference

### pip-waterfall

**Location:** `skills/pip-waterfall/skill.md`
**Purpose:** Run Kentucky PIP waterfall determination
**Tool:** Uses `pip_waterfall.py`

### pip-application

**Location:** `skills/pip-application/skill.md`
**Purpose:** Complete KACP Application form
**Tool:** Uses `generate_document.py` - path-based PDF form filling

### lor-generator

**Location:** `../insurance_bi_claim/skills/lor-generator/skill.md`
**Purpose:** Generate Letter of Representation by copying template to destination
**Tool:** Uses `generate_document.py` - path-based context detection

---

## Templates Reference

### PIP LOR Template

**Location:** `templates/2022 Whaley LOR to PIP Adjuster(1)(1) (1).docx`
**Registry ID:** `lor_pip`
**Purpose:** Letter of Representation to PIP carrier
**Includes:** $6,000 reserve instruction (Kentucky-specific)
**Destination:** Copy to `/{project}/Insurance/{company}/LOR to PIP Adjuster.docx` before generating

### KACP Application

**Location:** `templates/KACP-Application-03.2021(1) (1).pdf`
**Registry ID:** `pip_application`
**Purpose:** Kentucky PIP Application (universal form)
**Note:** Always required, all insurers accept this form
**Destination:** Copy to `/{project}/Insurance/{company}/KACP Application.pdf` before generating

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Client disqualified from PIP | Document and proceed with BI only |
| No insurance info available | Run waterfall with available info, may result in KAC |
| KAC required | Longer processing time, different contact info |
| PIP carrier unresponsive | Follow up persistently, document all attempts |
| Coverage limit exhausted | Monitor usage, inform client when approaching limit |

---

## Output

**Deliverables:**
- PIP carrier determined via waterfall
- KACP Application completed and submitted
- LOR sent to PIP carrier
- Claim acknowledged and ready to pay bills

**Landmark Sub-Steps Completed:**
- 3f: PIP carrier determined
- 3g: PIP Application submitted
- 3h: LOR sent
- 3i: Claim acknowledged
- 3j: Ready to pay bills

**Next:** After PIP is set up, verify bills are being paid as treatment occurs. Monitor PIP usage to ensure limit ($10,000) is not exhausted prematurely.

