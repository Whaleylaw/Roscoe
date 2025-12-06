# Workflow: Client Intake & Screening

## Metadata
- **ID**: client_intake_screening
- **Phase**: intake
- **Priority**: 1 (First workflow in phase)

---

## Goal

Successful completion means:
- All required client and incident information captured using six-question framework
- Comprehensive conflicts check performed against all current, former, and prospective clients
- Case viability and client reliability red flags identified and documented
- Clear recommendation (accept, decline, or escalate) prepared for supervising attorney
- If declining, proper non-engagement procedures followed

---

## When to Trigger

- New potential client contacts the firm seeking representation
- Existing client refers a new individual for consultation
- Prospective client transferred from another intake channel (web form, marketing lead)
- Firm asked to evaluate case from external referral source
- Any person begins sharing case-related information with the firm

---

## Inputs Required

| Input | Description |
|-------|-------------|
| Initial Contact Information | Name, phone number, email (if available) |
| Referral Source | How the prospective client found the firm |
| Preliminary Incident Description | Basic facts shared during initial contact |
| Access to Conflicts Database | Current clients, former clients, prospective/declined clients |
| Relevant Documents | Police reports, medical records, photos, insurance information (if provided) |

---

## Step-by-Step Process

### Step 1: Pre-Interview Preparation
1. Generate new intake record with timestamp and unique identifier
2. Document referral source and initial contact method
3. Set expectations: no attorney-client relationship until engagement agreement signed

### Step 2: Six-Question Information Gathering

**WHO** — Identify All Parties:
- [ ] Full legal name of prospective client
- [ ] All potential claimants (passengers, spouse for loss of consortium)
- [ ] All adverse parties (drivers, vehicle owners, employers, property owners)
- [ ] Known witnesses with contact information

**WHAT** — Capture Incident Narrative:
- [ ] Detailed description in caller's own words
- [ ] Type of incident (MVA, slip and fall, premises liability, etc.)
- [ ] Sequence of events
- [ ] Any admissions or apologies made at scene

**WHEN** — Establish Timeline:
- [ ] Exact date and time of incident
- [ ] Time elapsed since incident (statute of limitations check)
- [ ] Relevant dates (first medical visit, symptom onset)

**WHERE** — Determine Location:
- [ ] Precise location (street address, intersection)
- [ ] City, county, state (jurisdiction)
- [ ] Property type and conditions

**WHY** — Understand Client Goals:
- [ ] Desired outcome and expectations
- [ ] Why seeking attorney now

**HOW** — Referral and Payment:
- [ ] Referral source details
- [ ] Prior attorney consultations
- [ ] Understanding of contingency fee

### Step 3: Critical Data Collection
- [ ] Client demographics (name, DOB, SSN, address, phone, email)
- [ ] Employment details
- [ ] Insurance information (auto, health, Medicare/Medicaid status)
- [ ] Medical information (injuries, treatment, providers)
- [ ] Initial damages assessment

### Step 4: Conflicts Check
1. Prepare search terms (all party names)
2. Search current, former, and prospective client databases
3. Analyze for Rule 1.7 (current clients), 1.9 (former clients), 1.10 (imputation)
4. Document findings

### Step 5: Red Flag Analysis

**Case Viability Red Flags:**
- [ ] Inconsistent narrative vs. evidence
- [ ] Statute of limitations concerns
- [ ] Significant pre-existing conditions
- [ ] Unclear or minimal damages

**Client Reliability Red Flags:**
- [ ] Poor cooperation during intake
- [ ] Unrealistic expectations
- [ ] Prior attorney issues

### Step 6: Generate Recommendation
- **ACCEPT** if: Conflicts clear, no significant red flags, damages justify investment
- **ESCALATE** if: Potential conflict, significant red flags, complex legal issues
- **DECLINE** if: Clear conflict, multiple red flags, SOL expired

---

## Skills Used

| Skill | Purpose |
|-------|---------|
| fact-investigation | Analyzing documents provided during intake |

---

## Completion Criteria

- [ ] Six-question framework fully addressed
- [ ] Client demographics complete
- [ ] Conflicts check performed and documented
- [ ] Insurance information captured
- [ ] Red flag analysis completed
- [ ] Recommendation prepared

---

## Outputs

| Output | Format | Location |
|--------|--------|----------|
| Intake Summary Report | JSON | `case_information/intake_form.json` |
| Conflicts Check Results | JSON | `case_information/conflicts_check.json` |
| Red Flag Analysis | Markdown | `Reports/intake_red_flags.md` |
| Recommendation Memo | Markdown | `Reports/intake_recommendation.md` |

---

## Phase Exit Contribution

This workflow contributes to:
- `client_documents_signed` (triggers document collection workflow)

---

## Escalation Triggers

Immediately notify supervising attorney if:
1. Any potential conflict of interest identified
2. Deliberate lie or credibility issue detected
3. Statute of limitations imminent (within 30 days) or expired
4. Case involves government entity defendant
5. High-value case (severe injuries, wrongful death)
6. Any allegation of medical malpractice or product defect
7. Minor children or incapacitated adults involved

