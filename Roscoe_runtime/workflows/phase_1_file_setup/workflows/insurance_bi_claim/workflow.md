---
name: insurance_bi_claim
description: >
  Open and set up Bodily Injury (BI) insurance claims against at-fault parties.
  Sends Letter of Representation, follows up for acknowledgment, obtains liability
  determination, and confirms coverage limits. When Claude needs to open a BI claim,
  send LOR to insurance carrier, check liability status, or verify BI coverage.
  Use for at-fault party insurance setup in MVA cases. Flags user when liability
  is not 100% accepted for potential additional claims.
phase: file_setup
workflow_id: insurance_bi_claim
related_skills:
  - lor-generator
  - liability-analysis
related_tools:
  - generate_document.py
templates:
  - templates/2022 Whaley LOR to BI Adjuster(1)(1)(1) (1).docx
---

# BI Claim Setup Workflow

## Purpose

Open and manage Bodily Injury (BI) insurance claims against at-fault parties. This workflow:
1. Identifies at-fault party insurance from police report or client info
2. Sends Letter of Representation to BI carrier
3. Follows up for claim acknowledgment
4. Obtains liability determination
5. Confirms coverage and policy limits
6. Flags user when liability is disputed for potential additional claims

---

## Trigger

This workflow is triggered when:
- Police report is received and at-fault party identified
- User mentions BI claim or at-fault party insurance
- Accident report workflow completes
- Case is in Phase 1 and BI claim not yet opened

---

## Prerequisites

Before starting this workflow, ensure:
- Case is in Phase 1 (File Setup)
- At-fault party has been identified (from police report or client)
- Client has signed HIPAA and contract (Phase 0 complete)

---

## Steps

### Step 1: Identify At-Fault Party Insurance

**Source:** Police report, property damage claim, or client communication

**Actions:**
1. If police report exists → Extract at-fault driver insurance using `police-report-analysis` skill
2. If no police report → Ask user for at-fault party insurance information
3. Create insurance entry in `insurance.json`
4. Create contact entry for at-fault party in `contacts.json`

**Data to Collect:**
| Field | Source | Required |
|-------|--------|:--------:|
| Insurance company name | Police report or user | Yes |
| Insurance company phone | User or lookup | Yes |
| Insurance company address | User or lookup | Yes |
| Policy number | Police report (if listed) | No |
| At-fault driver name | Police report | Yes |
| At-fault driver address | Police report | No |

**Completion Check:** `insurance.bi.insurance_company.name` is populated

### Step 2: Send Letter of Representation

**Template:** `templates/2022 Whaley LOR to BI Adjuster(1)(1)(1) (1).docx`
**Tool:** `generate_document.py`
**Skill:** `lor-generator`

**Actions:**
1. Copy LOR template to destination: `/{project}/Insurance/{insurance_company}/LOR to BI Adjuster.docx`
2. Call `generate_document.py` with the destination path
3. Tool auto-fills all placeholders from case data (path provides context)
4. Present filled document to user for review/approval
5. Send via email/fax (or user sends manually)
6. Record sent date

**Document Generation Pattern:**
```bash
# Step 1: Copy template to Insurance/{company}/ folder
cp "/templates/2022 Whaley LOR to BI Adjuster(1)(1)(1) (1).docx" \
   "/{project}/Insurance/{insurance_company}/LOR to BI Adjuster.docx"

# Step 2: Generate filled document (path provides all context)
python generate_document.py "/{project}/Insurance/{insurance_company}/LOR to BI Adjuster.docx"
```

**Template Placeholders:**
| Placeholder | Data Source |
|-------------|-------------|
| `{{TODAY_LONG}}` | Current date (e.g., "January 15, 2024") |
| `{{insurance.insuranceAdjuster.name}}` | Adjuster name (or "Claims Department") |
| `{{insurance.insuranceCompany.addressBlock}}` | Full company address |
| `{{client.name}}` | Client full name |
| `{{insurance.claimNumber}}` | Claim number (if assigned) |
| `{{incidentDate}}` | Accident date |
| `{{primary}}` | Attorney name |

**LOR Content Notes:**
The BI LOR includes a statutory request for:
1. Policy effective date and liability limits
2. Uninsured motorist limits
3. Copy of insurance policy
4. Any coverage defenses
5. Medical payment coverage available

**Completion Check:** `insurance.bi.date_lor_sent` is populated

### Step 3: Open Claim (if not already open)

**Owner:** User (phone call to carrier)

**Actions:**
1. If claim number not already assigned:
   - User calls BI carrier claims line
   - Reports accident on behalf of client
   - Provides: At-fault driver name, policy number, client name, accident date
   - Carrier assigns claim number
2. User records claim number and date

**Completion Check:** `insurance.bi.claim_number` is populated

### Step 4: Confirm Claim Acknowledgment

**Timeline:** 3-5 business days after LOR sent

**Actions:**
1. Monitor for response from BI carrier
2. If no response in 5 days → Prompt user to call
3. Obtain adjuster name and contact information
4. Confirm claim is active

**Data to Update:**
```json
{
  "claim_acknowledged": true,
  "date_claim_acknowledged": "2024-12-05",
  "adjuster_name": "Jane Adjuster",
  "adjuster_phone": "800-555-5678",
  "adjuster_email": "jane@insurance.com"
}
```

**Completion Check:** `insurance.bi.claim_acknowledged == true`

### Step 5: Obtain Liability Determination

**Timeline:** Varies - can be immediate to weeks/months

**Actions:**
1. Request liability investigation status from adjuster
2. Follow up every 7-14 days if "under investigation"
3. Obtain written liability decision when available
4. Document liability status

**Liability Status Values:**
| Status | Meaning | Action |
|--------|---------|--------|
| `accepted` | 100% liability accepted | Proceed normally |
| `denied` | Liability denied | FLAG USER - may need UM/UIM claim |
| `partial` | Comparative fault | FLAG USER - multiple claims possible |
| `investigating` | Still determining | Continue follow-up |

**FLAG USER Logic:**
If liability is NOT 100% accepted:
```
⚠️ LIABILITY NOT FULLY ACCEPTED

The BI carrier has indicated: [liability_status]
Reason: [liability_denial_reason or investigation notes]

This may indicate:
- Need for UM/UIM claim under client's policy
- Multiple liable parties (especially in passenger cases)
- Disputed facts that require documentation

RECOMMENDED ACTIONS:
1. Review accident report for additional liable parties
2. Check if client has UM/UIM coverage
3. Document all facts supporting liability

Do you want me to help analyze potential additional claims?
```

**Completion Check:** `insurance.bi.liability_status` is populated (not "investigating")

### Step 6: Confirm Coverage and Policy Limits

**Timeline:** Can take 30+ days after LOR (statutory disclosure period)

**Actions:**
1. LOR includes statutory request for limits disclosure
2. Follow up if not received within 30 days
3. Obtain BI limits per person / per accident
4. Check for umbrella/excess policies
5. Document any exclusions

**Data to Update:**
```json
{
  "policy_limits_disclosed": true,
  "date_policy_limits_received": "2024-12-15",
  "coverage_limit_per_person": 25000,
  "coverage_limit_per_accident": 50000,
  "um_uim_limits": 25000,
  "umbrella_policy": false
}
```

**Completion Check:** `insurance.bi.policy_limits_disclosed == true`

---

## Skills Reference

### lor-generator

**Location:** `skills/lor-generator/skill.md`
**Purpose:** Generate Letter of Representation by copying template to destination and using unified generator
**Tool:** Uses `generate_document.py` - path-based context detection

### liability-analysis

**Location:** `skills/liability-analysis/skill.md`
**Purpose:** Analyze liability status and identify additional claims
**Flags user when:** Liability not 100% accepted

---

## Templates Reference

### BI LOR Template

**Location:** `templates/2022 Whaley LOR to BI Adjuster(1)(1)(1) (1).docx`
**Registry ID:** `lor_bi`
**Purpose:** Letter of Representation to at-fault party's insurance carrier
**Includes:** Statutory disclosure request for policy limits
**Destination:** Copy to `/{project}/Insurance/{company}/LOR to BI Adjuster.docx` before generating

---

## Error Handling

| Situation | Action |
|-----------|--------|
| No at-fault party identified | Cannot open BI claim - need police report or client info |
| Insurance company unknown | Prompt user to obtain from property damage claim or at-fault party |
| LOR bounced/returned | Verify address, try alternative contact method |
| No response to follow-ups | Escalate timeline, consider formal demand |
| Liability denied | FLAG USER for UM/UIM analysis |

---

## Output

**Deliverables:**
- BI claim opened with carrier
- LOR sent and acknowledged
- Liability status documented
- Policy limits confirmed

**Landmark Sub-Steps Completed:**
- 3a: At-fault insurance identified
- 3b: LOR sent
- 3c: Claim acknowledged
- 3d: Liability status obtained
- 3e: Coverage confirmed

**Next:** If this is the only claim needed, proceed to Provider Setup. If multiple vehicles/parties, repeat workflow for each.

