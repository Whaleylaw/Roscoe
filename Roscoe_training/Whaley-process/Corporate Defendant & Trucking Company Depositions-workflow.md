# Corporate Defendant & Trucking Company Depositions
## AI Paralegal Operational Workflow & Prompt Template

**Source Report:** `witness-report-Corporate Defendant & Trucking Company Depositions.txt`  
**Module Type:** Deposition Preparation  
**Applicable Case Types:** Premises Liability, Trucking/Motor Carrier Litigation

---

## Table of Contents

1. [Operational Workflow](#1-operational-workflow)
   - [Workflow Overview](#workflow-overview)
   - [When to Use](#when-to-use)
   - [Inputs Required](#inputs-required)
   - [Step-by-Step Process](#step-by-step-process)
   - [Quality Checks & Safeguards](#quality-checks--safeguards)
   - [Outputs](#outputs)
2. [Prompt Template](#2-prompt-template-for-ai-paralegal)
3. [Reference Materials](#3-reference-materials)
   - [Five Core Duties Framework](#five-core-duties-framework-premises-liability)
   - [Dual-Prong Framework](#dual-prong-framework-trucking-cases)
   - [Miller Mousetrap Sequence](#miller-mousetrap-sequence)
   - [Sample 30.02(6) Topics](#sample-30026-topics)

---

# 1. Operational Workflow

## Workflow Overview

| Field | Value |
|-------|-------|
| **Workflow Name** | Corporate Defendant Deposition Preparation |
| **Goal** | Produce a comprehensive deposition preparation package for a 30.02(6) corporate representative deposition including: topic list, examination outline with safety rule sequences, document checklist, red-flag guide, and prior incidents discovery roadmap |
| **Success Criteria** | Attorney receives court-ready materials that systematically establish defendant's standard of care, demonstrate violations, and expose patterns of negligence |

---

## When to Use

### Trigger Conditions

- [ ] Attorney requests preparation for a corporate defendant deposition
- [ ] Case involves **premises liability** (slip/fall, unsafe conditions) OR **trucking/motor carrier** defendants
- [ ] A 30.02(6) or equivalent corporate designee notice is being prepared
- [ ] Discovery phase requires examination of corporate policies, safety systems, or employee conduct
- [ ] Attorney needs to develop questioning strategy for corporate witness

---

## Inputs Required

| Input | Description | Required |
|-------|-------------|----------|
| `case_type` | Premises liability OR trucking company (determines examination focus) | ✓ |
| `incident_summary` | Brief description of what happened, when, where | ✓ |
| `defendant_identity` | Name and type of corporate defendant (retailer, property owner, trucking carrier, etc.) | ✓ |
| `location_details` | Specific area/premises or vehicle/route involved | ✓ |
| `employee_involvement` | Names/roles of employees potentially involved | ○ |
| `documents_received` | List of documents already produced in discovery | ○ |
| `documents_outstanding` | Known gaps in document production | ○ |
| `prior_incident_intel` | Any known history of similar incidents | ○ |
| `case_theory` | Attorney's working theory of liability | ✓ |

**Legend:** ✓ = Required | ○ = Optional but recommended

---

## Step-by-Step Process

### Step 1: Case Classification & Framework Selection

**Objective:** Determine the appropriate legal framework for examination strategy.

**Actions:**
1. Classify case as **premises liability** or **trucking company**
2. Select framework:
   - **Premises Liability** → Activate Five Core Duties Framework
   - **Trucking Company** → Activate Dual-Prong Framework (FMCSA + Rules of the Road)
3. Identify any hybrid elements (e.g., trucking company's premises, delivery driver on customer property)

**Framework Reference:**

| Case Type | Framework | Core Elements |
|-----------|-----------|---------------|
| Premises Liability | Five Core Duties | Avoid endangerment, discover dangers, remove dangers, warn, make visible |
| Trucking Company | Dual-Prong | FMCSA corporate compliance + general rules of the road |

---

### Step 2: Construct 30.02(6) Topic List

**Objective:** Generate case-specific deposition topics for corporate designee notice.

#### Premises Liability Topics

1. Safety principles, procedures, protocols, and training for fall/hazard precautions for employees and customers
2. Policy and procedure for training new and existing employees regarding safety
3. Current whereabouts of all employees on duty at time of incident
4. Company's knowledge of facts and circumstances of incident as described in Complaint
5. 10-year history of lawsuits and claims against the company

#### Trucking Company Topics

1. Company's understanding of trucking industry standards regulated by FMCSA
2. Policy, procedure, methods, criteria, and content used in hiring the driver involved
3. Complete employment file of driver (personnel, training, disciplinary, qualification file)
4. Details of company's investigation of the crash, including determination of cause
5. Whether crash was determined preventable and what driver should have done differently

---

### Step 3: Design Safety Rule Acknowledgment Sequence

**Objective:** Draft the "Miller Mousetrap" question sequence to commit witness to safety standards.

**Sequence Structure:**

```
┌─────────────────────────────────────────────────────────────┐
│  MILLER MOUSETRAP - SAFETY RULE ACKNOWLEDGMENT SEQUENCE    │
├─────────────────────────────────────────────────────────────┤
│  1. ESTABLISH THE RULE                                      │
│     Present undeniable safety rule as statement of fact     │
│     Example: "A company can never needlessly endanger       │
│     the public."                                            │
├─────────────────────────────────────────────────────────────┤
│  2. CONFIRM UNIVERSAL APPLICATION                           │
│     Secure agreement this is standard rule for many years   │
├─────────────────────────────────────────────────────────────┤
│  3. CONFIRM IMPORTANCE                                      │
│     Get agreement rule is important and all employees       │
│     are expected to follow it                               │
├─────────────────────────────────────────────────────────────┤
│  4. ESTABLISH CONSEQUENCE OF VIOLATION                      │
│     Secure agreement that if someone breaks a safety rule,  │
│     people can get hurt and rule-breaker is responsible     │
├─────────────────────────────────────────────────────────────┤
│  5. FRAME THE VIOLATION                                     │
│     Elicit agreement that breaking established safety       │
│     rules is, by definition, unsafe and reckless            │
└─────────────────────────────────────────────────────────────┘
```

**Application:** Map each safety rule to the specific violation alleged in the case.

---

### Step 4: Develop Key Questioning Protocols

**Objective:** Prepare detailed question sequences for each subject area.

#### Premises Liability Protocols

| Subject Area | Key Questions |
|--------------|---------------|
| **Inspection Protocols** | Who is responsible for inspecting the area? How often are inspections supposed to occur? Are written records kept? |
| **Hazard Identification** | What training do employees receive on identifying hazards? What is the policy when an employee sees an unsafe condition? |
| **Post-Incident Investigation** | Who investigated the incident? Were photographs taken? Were witnesses interviewed and statements recorded? |
| **Remedial Measures** | After the incident, were any changes made to the area or procedures to prevent similar incidents? |

#### Trucking Company Protocols

| Subject Area | Key Questions |
|--------------|---------------|
| **Hiring & Training** | What is the policy and criteria for hiring new drivers? What safety training was the driver provided? |
| **FMCSA Compliance** | What is the company's understanding of FMCSA safety standards? |
| **Maintenance** | What are the maintenance and inspection protocols for the specific tractor and trailer involved? |
| **Crash Investigation** | What was the company's internal determination of cause? Was it deemed preventable? What should the driver have done differently? |

---

### Step 5: Create Document Request Checklist

**Objective:** Generate comprehensive document checklist with strategic rationale.

| Document Category | Specific Items | Strategic Purpose |
|-------------------|----------------|-------------------|
| **Corporate Safety Policies** | Employee handbooks, safety manuals, training manuals, materials related to incident type | Establishes company's own stated standard of care to demonstrate employee failures |
| **Inspection/Maintenance Records** | Inspection schedules, daily logs, maintenance reports, repair histories for specific area/vehicle | Absence creates negligence inference ("if not documented, didn't happen") |
| **Employee/Driver Files** | Complete personnel file, qualification file (trucking), training records, disciplinary actions, hiring documentation | Establishes patterns of poor conduct, negligent hiring/retention, lack of training |
| **Incident-Specific Information** | Internal reports, photographs, surveillance video, witness statements, investigation files | Locks in defendant's version, identifies admissions or inconsistencies |
| **History of Similar Incidents** | Records, claims, data on prior lawsuits/claims for similar incidents (10 years) | Proves notice of recurring danger—elevates from simple negligence to reckless disregard |

---

### Step 6: Map Prior Similar Incidents Discovery Strategy

**Objective:** Structure escalating scope inquiry to uncover patterns.

```
PRIOR SIMILAR INCIDENTS - ESCALATING SCOPE

Level 1: NARROWEST
├── Same area
└── Same location
         │
         ▼
Level 2: SAME LOCATION, BROADER AREA
├── Same manner of incident
└── Other areas of same location
         │
         ▼
Level 3: OTHER LOCATIONS, SAME AREA TYPE
├── Same area type
└── Other company locations
         │
         ▼
Level 4: WIDEST - COMPANY-WIDE PATTERN
├── Same manner of incident
└── Other areas at ALL company locations
```

**Cross-Reference:** Align with document requests for 10-year claims history.

---

### Step 7: Compile Red-Flag Monitoring Guide

**Objective:** Create watch-list for testimony and document review.

#### Red Flags to Monitor

| Red Flag | Significance | Response |
|----------|--------------|----------|
| **Missing Safety/Maintenance Documentation** | Implies procedures not performed OR evidence withheld | Flag for motion to compel; argue adverse inference |
| **Post-Incident Discipline or Termination** | Implicit admission by company that employee violated policy and was at fault | Explore details; request discipline records |
| **Pattern of Similar Incidents** | Company had direct knowledge of recurring danger but failed to act | Build notice argument; request all related claims |
| **Evasive/Unresponsive Witness** | Improper preparation (rule violation) OR deliberate concealment | Apply witness control techniques |

#### Witness Control Techniques for Evasive Responses

1. Pause and make direct eye contact
2. Repeat the question verbatim, slowly
3. Ask the court reporter to read back the pending question
4. Ask: "What question did I ask you?"

---

### Step 8: Assemble Final Deposition Preparation Package

**Objective:** Compile all outputs into structured deliverable.

**Package Contents:**

1. ☐ Executive summary of examination strategy
2. ☐ Formal 30.02(6) topic list (court-ready)
3. ☐ Safety Rule Acknowledgment Sequence (scripted)
4. ☐ Examination outline with question protocols
5. ☐ Document checklist with tracking status
6. ☐ Red-flag monitoring guide
7. ☐ Prior incidents discovery roadmap
8. ☐ Open questions / gaps for attorney review

---

## Quality Checks & Safeguards

| Check | Description | Status |
|-------|-------------|--------|
| **Jurisdiction Verification** | Confirm 30.02(6) or equivalent rule applies; flag if different mechanism needed | ☐ |
| **Legal Conclusion Prohibition** | Ensure all outputs are factual preparation work product, NOT legal advice | ☐ |
| **Document Gap Alerting** | If critical documents missing from production, explicitly flag for attorney | ☐ |
| **Theory Alignment** | Verify examination outline supports attorney's stated case theory | ☐ |
| **Red-Flag Escalation** | If pattern evidence, severe document gaps, or potential spoliation found, escalate immediately | ☐ |
| **FMCSA Regulation Gap** | Note: Specific FMCSA regulation text not in training; attorney must provide citations | ☐ |
| **Completeness Review** | Ensure all framework elements (5 duties or dual-prong) are addressed | ☐ |

### Escalation Triggers

> **ESCALATE TO SUPERVISING ATTORNEY IMMEDIATELY IF:**
> - Evidence of spoliation or document destruction
> - Pattern of 3+ similar incidents discovered
> - Post-incident termination of key employee
> - Corporate designee claims ignorance of basic company policies
> - Significant regulatory violations identified

---

## Outputs

| Deliverable | Format | Description |
|-------------|--------|-------------|
| **30.02(6) Topic List** | Numbered list, formal language | Court-ready notice topics for corporate designee |
| **Safety Rule Sequence** | Scripted Q&A format | Miller Mousetrap questions mapped to case facts |
| **Examination Outline** | Hierarchical outline | Full question protocols organized by subject area |
| **Document Checklist** | Table with status column | All required documents with strategic purpose and production status |
| **Red-Flag Guide** | Bullet list with triggers | Warning signs to monitor during deposition |
| **Prior Incidents Map** | Escalating scope diagram | Discovery progression from specific to company-wide |
| **Open Questions / Gaps** | Flagged list | Areas requiring attorney input or additional research |

---

# 2. Prompt Template for AI Paralegal

```markdown
You are an AI Paralegal operating under the "Corporate Defendant & Trucking Company Depositions" module.

## Reference

- You have been trained on the "Corporate Defendant & Trucking Company Depositions" report, which defines the concepts, checklists, red flags, and procedures for preparing 30.02(6) corporate representative depositions in premises liability and trucking company cases.
- This report establishes:
  - The five core duties framework for premises liability (avoid endangerment, discover dangers, remove dangers, warn, make dangers visible)
  - The dual-prong framework for trucking cases (FMCSA corporate compliance + general rules of the road)
  - The Safety Rule Acknowledgment Sequence ("Miller Mousetrap") for committing witnesses to safety standards
  - Key questioning protocols organized by case type
  - Critical document categories and their strategic purposes
  - Red flags and escalation triggers for identifying corporate negligence

## Task

Prepare a comprehensive deposition preparation package for a 30.02(6) corporate representative deposition that will equip the supervising attorney to systematically establish the defendant's standard of care, demonstrate violations, and expose patterns of negligence.

## Inputs

- **Client:** {{client_name}}
- **Case Type:** {{case_type}} (premises liability OR trucking company)
- **Defendant:** {{defendant_name_and_type}}
- **Incident Summary:** {{incident_description_with_date_and_location}}
- **Employees Involved:** {{employee_names_and_roles}}
- **Documents Received:** {{list_of_documents_already_produced}}
- **Documents Outstanding:** {{known_document_gaps}}
- **Prior Incident Intelligence:** {{any_known_history_of_similar_incidents}}
- **Case Theory:** {{attorney_working_theory_of_liability}}

## Instructions

1. **Follow the "Corporate Defendant Deposition Preparation" workflow step by step.**

2. **Apply the appropriate framework based on case type:**
   - For premises liability: Apply the five core duties and focus examination on inspection protocols, hazard identification, post-incident investigation, and remedial measures
   - For trucking company: Apply the dual-prong FMCSA/rules-of-the-road framework and focus examination on hiring, training, compliance, maintenance, and crash investigation

3. **Construct a Safety Rule Acknowledgment Sequence** using the Miller Mousetrap technique:
   - Establish undeniable safety rules as statements
   - Confirm universal application and importance
   - Establish consequences of violation
   - Frame the alleged violation

4. **Generate a formal 30.02(6) topic list** using the report's example applications as models, customized to the specific case facts.

5. **Create a document checklist** identifying all required document categories from the report, noting which have been produced, which are outstanding, and the strategic purpose of each.

6. **Map the prior similar incidents discovery strategy** using the escalating scope approach (same area/same location → same manner/other areas → other locations).

7. **Compile a red-flag monitoring guide** with specific warning signs from the report, including:
   - Missing documentation
   - Post-incident discipline or termination
   - Pattern of similar incidents
   - Evasive witness behavior and control techniques

8. **Do not provide legal advice or final legal conclusions.** Frame all analysis as supportive work product for a supervising attorney. Flag any areas where attorney judgment or additional research is required.

## Output

Provide a structured markdown report with the following sections:

### 1. Executive Summary
Brief overview of examination strategy aligned with case theory

### 2. 30.02(6) Topic List
Formal, numbered deposition topics ready for filing

### 3. Safety Rule Acknowledgment Sequence
Scripted Miller Mousetrap questions tailored to case facts

### 4. Examination Outline
Detailed question protocols organized by subject area (inspection, training, incident investigation, etc.)

### 5. Document Checklist
| Document Category | Specific Items | Strategic Purpose | Status |
Table format with all required documents

### 6. Prior Incidents Discovery Map
Escalating scope inquiry from specific location to company-wide patterns

### 7. Red-Flag Monitoring Guide
Warning signs to watch for during deposition with response techniques

### 8. Open Questions / Gaps for Attorney Review
- Missing information needed
- Areas requiring legal judgment
- Regulatory citations to research (especially FMCSA specifics)

---

**Important Notes:**
- If any input is missing or unclear, note the gap and proceed with reasonable assumptions clearly labeled as such
- The report does not include specific FMCSA regulation text; flag any trucking-specific regulatory questions for attorney research
- All work product is preliminary and subject to attorney review and modification
```

---

# 3. Reference Materials

## Five Core Duties Framework (Premises Liability)

The fundamental duties a company must actively uphold:

| Duty | Description |
|------|-------------|
| **1. Avoid Endangerment** | The duty to avoid needlessly endangering the public—foundational principle supporting all other rules |
| **2. Discover Dangers** | Affirmative responsibility to inspect premises and identify potential hazards; cannot claim ignorance |
| **3. Remove Dangers** | Once hazard is known, must take prompt action to eliminate it |
| **4. Warn About Dangers** | If hazard cannot be eliminated, must provide clear and adequate warnings |
| **5. Make Dangers Visible** | Ensure any hazard is conspicuous enough for reasonably attentive person to see and avoid in time |

---

## Dual-Prong Framework (Trucking Cases)

### Prong 1: FMCSA Corporate Compliance

Topics for corporate designee examination:
- Company's understanding of Federal Motor Carrier Safety Administration standards
- Driver qualification files
- Hiring and training procedures
- Safety programs and audits
- Equipment maintenance records
- Electronic logging devices and telematics
- Accident review boards and preventability determinations

> **Note:** The training report establishes FMCSA standards as critical topics but does not include the specific regulatory text. Attorney must provide or research specific citations.

### Prong 2: General Rules of the Road

All commercial drivers must adhere to these baseline standards:

1. A driver must drive carefully at all times
2. A driver must keep a proper lookout ahead for other vehicles and road conditions
3. A driver cannot operate a vehicle faster than traffic and circumstances safely allow
4. A driver must exercise ordinary care to avoid a collision with other people or vehicles

---

## Miller Mousetrap Sequence

**Purpose:** Commit the witness to endorsing safety rules BEFORE discussing specific facts, making it logically impossible to later justify violations.

### Scripted Sequence Template

**Step 1 - Establish the Rule:**
> "You would agree that [COMPANY NAME] can never needlessly endanger the public?"

**Step 2 - Confirm Universal Application:**
> "And that's been a standard safety rule for many years, hasn't it?"

**Step 3 - Confirm Importance:**
> "It's an important rule, and all [COMPANY NAME] employees are expected to follow it?"

**Step 4 - Establish Consequence:**
> "If someone breaks a safety rule, people can get hurt, and the person who broke the rule is responsible for the harm that results, correct?"

**Step 5 - Frame the Violation:**
> "So you'd agree that breaking established safety rules is, by definition, unsafe and reckless?"

---

## Sample 30.02(6) Topics

### Premises Liability Defendant

1. Safety principles, procedures, protocol, training and instruction used, adopted by or implemented by the company regarding fall precautions for employees and customers.
2. The company's policy and procedure for training new and existing employees regarding the safety of its employees and customers.
3. The current whereabouts of all of its employees that were on duty the day of the fall.
4. The company's knowledge of the facts and circumstances surrounding the plaintiff's fall as described in the Complaint.
5. Lawsuits and claims against the company for the previous 10 years.

### Trucking Company Defendant

1. The company's understanding of trucking industry standards regulated by the Federal Motor Carriers Safety Administration/Regulations.
2. The company's policy, procedure, methods, criteria and content used in hiring the driver involved in the crash.
3. The entire employment file of the driver, including personnel records, training records, disciplinary records, and the driver's qualification file.
4. Details of the company's investigation of the wreck described in the Complaint, including its determination of the cause.
5. Whether this was determined to be a preventable crash and what, if anything, should have been done differently by the driver to avoid it.

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-02 | AI Paralegal System | Initial workflow and prompt template created from source report |

---

*This document is work product prepared for attorney review. It does not constitute legal advice. All analysis is supportive work product subject to supervising attorney modification.*

