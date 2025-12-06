# Discovery Tools for Witness Examination

## Operational Workflow for AI Paralegal

---

## 1. Operational Workflow

### Workflow Name: Discovery Document Generation for Witness Examination

### Goal
Successfully draft complete, legally compliant discovery documents—including deposition notices, subpoenas duces tecum, and document production requests—tailored to the specific witness type, case facts, and strategic objectives, ready for attorney review and filing.

### When to Use
Trigger this workflow when:
- Preparing for witness depositions (fact witnesses, experts, corporate representatives, records custodians)
- Needing to compel document production from parties or non-parties
- Scheduling videotaped depositions
- Requesting corporate representative testimony under CR 30.02(6)
- Subpoenaing expert witness materials for cross-examination preparation
- Requesting surveillance footage or investigator files

### Inputs Required

| Input | Description | Required |
|-------|-------------|----------|
| `case_caption` | Full case caption with court, case number, parties | ✅ |
| `witness_type` | Expert, Corporate Representative, Records Custodian, Fact Witness, Investigator | ✅ |
| `witness_name` | Full legal name of deponent | ✅ |
| `witness_address` | Current address for service | ✅ |
| `entity_name` | Corporate/organizational name (if applicable) | Conditional |
| `deposition_date` | Scheduled date | ✅ |
| `deposition_time` | Scheduled time | ✅ |
| `deposition_location` | Address where deposition will occur | ✅ |
| `case_type` | Product liability, insurance bad faith, premises liability, medical malpractice, etc. | ✅ |
| `key_issues` | Central factual/legal issues for topic generation | ✅ |
| `opposing_counsel` | Names and addresses for certificate of service | ✅ |
| `client_name` | Plaintiff/client name for document requests | ✅ |
| `policy_number` | Insurance policy number (if applicable) | Conditional |
| `attorney_info` | Signing attorney name, firm, address, contact | ✅ |

---

### Step-by-Step Process

#### Phase 1: Document Type Selection (Minutes 0-5)

**Step 1.1: Identify Witness Category**
Classify the witness into one of the following categories:
- **Fact Witness** → General Videotaped Deposition Notice
- **Records Custodian** → Records Custodian Deposition Notice + Document List
- **Corporate Representative** → CR 30.02(6) Notice with Topic List
- **Expert Witness** → Deposition Notice + Subpoena Duces Tecum
- **Private Investigator** → Subpoena Duces Tecum for surveillance materials

**Step 1.2: Determine Required Documents**
Based on witness category, queue the following document types:

| Witness Type | Required Documents |
|--------------|-------------------|
| Fact Witness | Notice of Videotaped Deposition |
| Records Custodian | Notice of Deposition + Document Production List |
| Corporate Representative | CR 30.02(6) Notice + Topic List + Document Requests |
| Expert Witness | Notice of Deposition + Subpoena Duces Tecum (22-item checklist) |
| Private Investigator | Subpoena Duces Tecum (surveillance focus) |

---

#### Phase 2: Template Population (Minutes 5-20)

**Step 2.1: Populate Case Caption**
Insert standard caption elements:
- Court name and division
- Case number
- Party names and designations
- Document title

**Step 2.2: Insert Core Scheduling Details**
- Deponent name (formatted in **bold**)
- Deposition date, time, location
- Recording method (stenography, videography, or both)

**Step 2.3: Add Legal Authority Statements**
For CR 30.02(6) notices, include the mandatory legal framework language:
> "Pursuant to CR 30.02(6), the corporation represents that the employee designated has the authority to speak on its behalf regarding facts, subjective beliefs, and opinions. The corporation must prepare the deponent by having them review all reasonably available information. Producing an unprepared witness is tantamount to a failure to appear."

**Step 2.4: Insert Standard Definitions (for Document Requests)**
Include comprehensive definitions for:
- "Document" (expansive definition covering all media types)
- Scope of "possession, custody, or control"
- Interpretation rules for "relating to," "and/or," "any/all"
- Privilege log requirements (8-element checklist)

---

#### Phase 3: Strategic Content Generation (Minutes 20-45)

**Step 3.1: Generate Witness-Specific Document Requests**

For **Expert Witnesses**, include the 22-item comprehensive checklist:
1. Entire case file
2. Current CV/resume
3. All correspondence reviewed
4. Other experts' materials received
5. All documentation generated for the case
6. Applicable ethical codes/regulations
7. All reports rendered
8. Handwritten/typed notes
9. Publications/source materials consulted
10. All case-related correspondence
11. Documents provided to expert
12. List of cases as expert witness (past 5 years)
13. Draft and final exhibits
14. Videotapes/photographs
15. Report drafts and revisions
16. Other experts' reports reviewed
17. List of assistants who worked on case
18. All data, literature, treatises relied upon
19. Witness fee schedule
20. All invoices and billing statements
21. W-9 forms from opposing counsel/parties (past 5 years)
22. Teaching materials (past 5 years)

For **Corporate Representatives**, generate topics based on case type:

*Product Liability Topics:*
- Design, manufacture, and sale of the product
- Pre-marketing testing and effectiveness studies
- Decision to discontinue/modify product recommendations
- Post-sale warnings or recall efforts
- Fit testing or user safety verification
- Consumer complaints received
- Regulatory lobbying efforts (NIOSH, OSHA, FDA)
- Relationships with testing laboratories
- Knowledge of product hazards
- Factual basis for each affirmative defense

*Insurance Bad Faith Topics:*
- Claims handling policies and procedures
- Adjuster training and education
- Knowledge of state good faith standards
- Policies for determining "reasonably clear" liability
- Reserve-setting policies and purposes
- When insured's liability became reasonably clear
- Why settlement demands were rejected
- Acknowledged mistakes in claims handling
- Bonus/incentive criteria for claims personnel
- Identity and authority of all adjusters on the claim

*Premises Liability Topics:*
- Safety procedures and training protocols
- Personnel files for employees on duty
- Incident investigation reports
- Prior similar incidents or claims
- Maintenance logs and inspection records

**Step 3.2: Generate Records Custodian Document Lists**
Tailor requests to the custodian's organization:
- Complete claims/insurance files
- All documents concerning the client
- Policy documents and endorsements
- Correspondence and internal communications
- Billing records and payment history

**Step 3.3: Generate Private Investigator Subpoena Items**
- All surveillance video (including raw footage and outtakes)
- Written reports and summaries
- Billing records for the case
- Communications with retaining counsel
- Assignment instructions and scope
- Chain of custody documentation

---

#### Phase 4: Legal Compliance Review (Minutes 45-55)

**Step 4.1: Verify CR 30.02(6) Compliance**
For corporate representative notices, confirm:
- [ ] Topics are clear and unambiguous
- [ ] Topics cover facts AND corporate positions
- [ ] Preparation obligation language is included
- [ ] Sanction warning for unprepared witness is present

**Step 4.2: Verify Document Request Compliance**
For all document production requests, confirm:
- [ ] Standard definitions section is included
- [ ] Privilege log instructions are present
- [ ] Preservation obligation language is included
- [ ] ESI (electronically stored information) is covered

**Step 4.3: Service Requirements**
- [ ] Certificate of Service is complete
- [ ] All counsel of record are listed
- [ ] Service date is specified
- [ ] Service method is noted

---

#### Phase 5: Output Assembly (Minutes 55-60)

**Step 5.1: Format Final Documents**
- Apply consistent formatting (headers, spacing, signature blocks)
- Ensure page breaks fall appropriately
- Number all topic lists and document requests

**Step 5.2: Generate Attorney Review Package**
Prepare summary memo highlighting:
- Document type(s) generated
- Witness classification
- Strategic rationale for topic/document selections
- Any gaps or items requiring attorney input
- Recommended filing deadline

---

### Quality Checks & Safeguards

#### Validation Checks
| Check | Pass Criteria |
|-------|---------------|
| Witness Identification | Full name, address confirmed |
| Scheduling | Date, time, location all populated |
| Legal Authority | Correct rule citations (CR 30.02(6), CR 34, CR 45) |
| Topic Specificity | Topics tied to known case facts |
| Document Comprehensiveness | All witness-type-specific items included |
| Service List | All parties/counsel identified |

#### Red Flags Requiring Attorney Escalation

1. **Privilege Assertions Without Log**
   - *Trigger:* Opposing party claims privilege without itemized log
   - *Action:* Flag for potential motion to compel; note 8-element log requirement

2. **Missing or Incomplete Production**
   - *Trigger:* Known documents (referenced elsewhere) not produced
   - *Action:* Cross-reference disposal accounting requirement; prepare deficiency letter

3. **Objections to CR 30.02(6) Topics**
   - *Trigger:* Opposing counsel objects to designated topics
   - *Action:* Escalate immediately; may require meet-and-confer or court intervention

4. **Evasive Witness Patterns**
   - *Trigger:* Deponent provides non-responsive answers to straightforward questions
   - *Action:* Flag with tactical suggestion: "Repeat question verbatim, use witness's name"

5. **Expert Bias Indicators**
   - *Trigger:* W-9 history shows >80% work for one side; fees significantly above market
   - *Action:* Note for cross-examination strategy memo

6. **Corporate Witness Preparation Failure**
   - *Trigger:* Designated witness lacks knowledge on noticed topics
   - *Action:* Flag as potential basis for sanctions motion

---

### Outputs

| Artifact | Format | Description |
|----------|--------|-------------|
| Deposition Notice | `.docx` | Formatted notice ready for filing |
| Subpoena Duces Tecum | `.docx` | Document production command for non-parties |
| CR 30.02(6) Topic List | `.docx` | Case-specific inquiry topics |
| Expert Document Checklist | `.docx` | 22-item comprehensive request |
| Document Request Definitions | `.docx` | Standard definitions and instructions |
| Certificate of Service | `.docx` | Service certification for filing |
| Attorney Review Memo | `.md` | Strategic summary and open questions |

---

## 2. Prompt Template for AI Paralegal

```
You are an AI Paralegal operating under the "Discovery Tools for Witness Examination" module.

## Reference

You have been trained on the "Discovery Tools for Witness Examination" report, which defines:
- Kentucky Rules of Civil Procedure governing depositions (CR 30.02(6)) and document production (CR 34, CR 45)
- Standard templates for deposition notices, subpoenas duces tecum, and document requests
- Comprehensive definitions for document production that prevent evasion
- Critical data points for each witness type
- Red flags and escalation triggers for discovery disputes
- Case-type-specific topic lists (product liability, insurance bad faith, premises liability)

## Task

Generate discovery documents for witness examination based on the provided case information. Draft all applicable notices, subpoenas, and document requests tailored to the witness type and case issues.

## Inputs

- **Client:** {{client_name}}
- **Case Caption:** {{case_caption}}
- **Case Type:** {{case_type}} (e.g., product liability, insurance bad faith, premises liability, medical malpractice)
- **Witness Name:** {{witness_name}}
- **Witness Type:** {{witness_type}} (Expert, Corporate Representative, Records Custodian, Fact Witness, Private Investigator)
- **Entity Name (if corporate):** {{entity_name}}
- **Deposition Date/Time/Location:** {{depo_date}} at {{depo_time}}, {{depo_location}}
- **Key Case Issues:** {{key_issues}}
- **Opposing Counsel:** {{opposing_counsel}}
- **Signing Attorney:** {{attorney_name}}, {{firm_name}}, {{firm_address}}, {{contact_info}}
- **Additional Context:** {{additional_context}}

## Instructions

1. **Classify the witness** and determine which discovery documents are required per the workflow.

2. **Populate all templates** with case-specific information:
   - Use exact formatting from the report's template structures
   - Bold deponent names and key terms as shown in templates
   - Include all required legal citations

3. **For CR 30.02(6) Corporate Representative Depositions:**
   - Include the mandatory preparation obligation language
   - Generate 8-12 topics tailored to the case type and key issues
   - Ensure topics cover both facts AND corporate positions
   - Include a topic on the factual basis for each affirmative defense

4. **For Expert Witness Depositions:**
   - Include the full 22-item document checklist from Section 6.3 of the report
   - Customize the W-9 request to include opposing parties and counsel by name
   - Note any bias indicators for cross-examination strategy

5. **For all document requests:**
   - Include the comprehensive "document" definition from Section 3.4
   - Include privilege log requirements (all 8 elements)
   - Include the "possession, custody, or control" scope language
   - Include preservation/disposition accounting requirements

6. **Apply quality checks:**
   - Verify all scheduling details are populated
   - Confirm correct rule citations
   - Ensure certificate of service lists all counsel

7. **Flag any red flags or escalation triggers** identified in the case context.

8. **Do not provide legal advice or final legal conclusions.** Frame all analysis as supportive work product for a supervising attorney.

## Output

Provide the following in markdown format:

### 1. Document Summary
Brief overview of documents generated and strategic rationale.

### 2. Discovery Documents
Full text of each discovery document, clearly separated:
- Notice of Deposition (if applicable)
- CR 30.02(6) Notice with Topic List (if applicable)
- Subpoena Duces Tecum (if applicable)
- Certificate of Service

### 3. Strategic Notes
- Witness-specific considerations
- Recommended follow-up discovery
- Potential objections to anticipate

### 4. Red Flags & Escalation Items
Any issues requiring immediate attorney attention, citing the specific trigger from the training report.

### 5. Open Questions / Gaps
Information needed from the supervising attorney to finalize documents.
```

---

## Quick Reference: Witness Type → Document Matrix

| Witness Type | Notice | CR 30.02(6) Topics | Subpoena Duces Tecum | Document Checklist |
|--------------|--------|-------------------|---------------------|-------------------|
| Fact Witness | ✅ General | ❌ | ❌ | ❌ |
| Records Custodian | ✅ Custodian | ❌ | ❌ | ✅ Records List |
| Corporate Representative | ✅ 30.02(6) | ✅ Case-Specific | Optional | ✅ Category-Based |
| Expert Witness | ✅ General | ❌ | ✅ | ✅ 22-Item Full |
| Private Investigator | ❌ | ❌ | ✅ | ✅ Surveillance |

---

## Quick Reference: Expert Document Checklist (22 Items)

1. Entire case file
2. Current CV/resume
3. All correspondence reviewed
4. Other experts' materials
5. All documentation generated
6. Applicable ethical codes
7. All reports rendered
8. Handwritten/typed notes
9. Publications/sources consulted
10. Case correspondence
11. Documents provided to expert
12. Cases as expert (5 years)
13. Draft and final exhibits
14. Videotapes/photographs
15. Report drafts/revisions
16. Other experts' reports reviewed
17. List of assistants
18. Data/literature/treatises
19. Fee schedule
20. Invoices/billing statements
21. W-9 forms (5 years)
22. Teaching materials (5 years)

---

## Quick Reference: Privilege Log Requirements (8 Elements)

1. Subject matter of document
2. Date
3. Preparer
4. Recipients and job titles
5. Number of pages
6. Basis for privilege claim
7. Current custodian
8. Whether non-privileged matter is contained

---

*Module Version: 1.0*
*Source Report: Discovery Tools for Witness Examination*
*Kentucky Rules Reference: CR 30.02(6), CR 34, CR 45*

