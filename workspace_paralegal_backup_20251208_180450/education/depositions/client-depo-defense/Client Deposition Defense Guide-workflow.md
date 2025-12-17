# Client Deposition Defense Guide: AI Paralegal Workflow & Prompt Template

---

## 1. Operational Workflow

### Workflow Name
**Client Deposition Defense Support**

---

### Goal
Successful completion means the AI paralegal has:
- Prepared comprehensive deposition support materials for the supervising attorney
- Compiled and organized all relevant documents
- Created an objection tracking framework aligned with Kentucky Rules of Civil Procedure
- Identified potential privilege issues and question problem areas
- Produced post-deposition analysis with flagged testimony, objection logs, and trial preparation notes

---

### When to Use
Trigger this workflow when:
1. A client deposition is scheduled (notice received)
2. Attorney requests deposition preparation assistance
3. Objection review/analysis is needed post-deposition
4. Motion practice related to deposition conduct is anticipated
5. Client needs preparation materials or confidence-building support
6. Opposing counsel has served a deposition notice under CR 30.02(1)

---

### Inputs Required

| Input | Description |
|-------|-------------|
| `client_name` | Full name of the client being deposed |
| `case_name` | Case identifier/matter name |
| `deposition_date` | Scheduled date of deposition |
| `deposition_notice` | Copy of the formal deposition notice |
| `case_documents` | Medical records, incident reports, correspondence, contracts |
| `prior_discovery` | Interrogatories, Requests for Production previously served |
| `court_orders` | Any protective orders or limitations on evidence |
| `opposing_counsel_info` | Name/firm of deposing attorney |
| `deposition_transcript` | (Post-deposition) Official transcript when available |

---

### Step-by-Step Process

#### **Phase 1: Pre-Deposition Preparation**

**Step 1.1: Review Deposition Notice**
- Extract and verify: date, time, location, court reporter info
- Identify scope of topics or documents requested in the notice
- Flag any issues with notice adequacy under CR 30.02(1) ("reasonable notice in writing")
- Note deadline for any objections to the notice

**Step 1.2: Compile Document Universe**
- Gather all documents potentially relevant to client's testimony:
  - [ ] Medical records
  - [ ] Incident/accident reports
  - [ ] Photographs and physical evidence
  - [ ] Correspondence (emails, letters, texts)
  - [ ] Employment records (if relevant)
  - [ ] Insurance documents
  - [ ] Prior statements by client
- Organize documents chronologically and by subject matter
- Create document index with descriptions and relevance notes

**Step 1.3: Anticipate Document Requests**
- Cross-reference opposing counsel's prior discovery requests (Interrogatories, RFPs)
- Predict documents opposing counsel will likely request during deposition
- Flag documents with privilege issues (attorney-client communications per KRE 503)
- Prepare privilege log framework if needed

**Step 1.4: Identify Privilege & Protection Issues**
- Review all communications for attorney-client privilege protection (KRE 503)
- Note any court-ordered limitations on evidence that must be enforced
- Flag topics that may require instruction not to answer under CR 30.03(3):
  - [ ] Privileged attorney-client communications
  - [ ] Work product materials
  - [ ] Court-ordered prohibited topics
- Prepare privilege assertion language for attorney reference

**Step 1.5: Create Objection Preparation Materials**
- Compile Form Objection Quick-Reference Sheet:

| Objection | Trigger | Example |
|-----------|---------|---------|
| **Leading** | Question suggests the answer | "You started work at around 3pm?" |
| **Calls for Speculation** | Asks witness to guess | "What if you had gone to a different doctor?" |
| **Asked and Answered** | Repetitive questioning | Same question asked multiple times |
| **Argumentative** | Harassing, not fact-seeking | "If you had been looking, you wouldn't have tripped, correct?" |
| **Assumes Facts Not in Evidence** | Presumes unestablished facts | "What did you see the driver throw out the window?" (no evidence of throwing) |
| **Calls for Legal Conclusion** | Asks lay witness for legal opinion | "Was the defendant negligent?" |
| **Lacks Foundation** | No factual predicate established | Questions about expertise without establishing qualifications |
| **Compound** | Multiple questions in one | "What time did you leave and where were you going?" |
| **Calls for Narrative** | Overly broad, invites rambling | "Tell me everything that happened" |

**Step 1.6: Prepare Client Support Materials**
- Create deposition process overview for client
- Compile key documents for client review
- Prepare timeline of relevant events
- Draft list of likely question topics
- Note confidence-building strategies per training module

---

#### **Phase 2: Deposition Day Support**

**Step 2.1: Final Logistics Verification**
- Confirm location, time, attendees
- Verify all preparation materials are assembled
- Ensure objection quick-reference is accessible

**Step 2.2: Real-Time Monitoring Framework**
(For attorney reference during deposition)
- Track questions requiring form objections
- Note any privilege incursions requiring instruction not to answer
- Monitor for CR 30.04 bad faith/harassment triggers:
  - [ ] Badgering witness
  - [ ] Repetitive questioning on sensitive topics
  - [ ] Personal insults
  - [ ] Conduct designed to annoy, embarrass, or oppress

**Step 2.3: Escalation Recognition**
Flag for potential CR 30.04 motion when:
- Examination conducted in bad faith
- Questions unreasonably annoy, embarrass, or oppress the client
- Escalation procedure:
  1. Attorney makes formal demand on record to suspend
  2. Deposition immediately paused
  3. Motion for protective order filed with court
  4. Deposition resumes only upon court order

---

#### **Phase 3: Post-Deposition Analysis**

**Step 3.1: Transcript Review**
- Obtain transcript as soon as available
- Review for:
  - [ ] Typographical errors
  - [ ] Substantive irregularities in recorded testimony
  - [ ] Discrepancies from client's actual statements

**Step 3.2: Key Testimony Extraction**
- Identify and highlight (with page/line numbers):
  - [ ] Key admissions (favorable and unfavorable)
  - [ ] Damaging statements requiring attorney attention
  - [ ] Testimony supporting case theory
  - [ ] Testimony contradicting case theory
  - [ ] Potential impeachment material

**Step 3.3: Objection Catalog**
- Log all objections made by defending attorney:

| Page:Line | Question Summary | Objection Type | Ruling/Response |
|-----------|------------------|----------------|-----------------|
| | | | |

- Cross-reference with CR 32.04 waiver rules:
  - **Preserved objections**: Competency, relevancy, materiality (can raise pre-trial)
  - **Waived objections**: Form errors not raised seasonably (lost forever)

**Step 3.4: Trial Preparation Notes**
- Flag testimony usable for trial per CR 32.04
- Identify testimony that may require motion in limine to exclude
- Note inconsistencies with other evidence for impeachment purposes
- Prepare summary of deposition for case file

---

### Quality Checks & Safeguards

#### Validation Checks
- [ ] All dates and deadlines accurately captured from notice
- [ ] Document compilation is comprehensive (no obvious gaps)
- [ ] Privilege flags are properly identified
- [ ] Objection categories correctly applied per Kentucky rules
- [ ] Page/line citations are accurate in post-deposition analysis
- [ ] CR 32.04 waiver analysis correctly distinguishes preserved vs. waived objections

#### Red Flags Requiring Attorney Escalation
| Red Flag | Action |
|----------|--------|
| Questions probing attorney-client communications | Alert attorney; potential privilege violation |
| Repeated questions on same topic | "Asked and answered" pattern; possible harassment |
| Personal attacks or insulting questions | Potential CR 30.04 bad faith conduct |
| Questions about court-prohibited topics | Enforce court limitation |
| Client asked for legal conclusions | "Calls for legal conclusion" objection needed |
| Confusing/misleading questions creating damaging record | Multiple form objection issues |
| Testimony directly undermining case theory | Immediate attorney review required |

#### Escalation Triggers
Immediately alert supervising attorney when:
1. Privilege may have been inadvertently waived
2. Client made statement contradicting prior testimony/evidence
3. CR 30.04 bad faith conduct is occurring
4. Opposing counsel violates court orders
5. Any situation requiring legal judgment beyond paralegal scope

#### Ethical Boundaries
- **Do not** provide legal advice or conclusions to client
- **Do not** coach client on substantive answers
- **Do not** make privilege determinations (flag for attorney)
- **Do not** interpret whether conduct rises to CR 30.04 level (flag for attorney)
- **Frame all analysis** as supportive work product for supervising attorney review

---

### Outputs

#### Pre-Deposition Outputs
1. **Deposition Notice Summary** – Key details extracted and verified
2. **Document Compilation Index** – Organized inventory of relevant documents
3. **Privilege Issue Memo** – Flagged communications and topics requiring protection
4. **Anticipated Document Request List** – Predicted opposing counsel requests
5. **Objection Quick-Reference Sheet** – Nine form objections with triggers
6. **Client Preparation Packet** – Timeline, key documents, process overview

#### Post-Deposition Outputs
1. **Transcript Review Summary** – Errors, irregularities, key passages
2. **Key Testimony Log** – Admissions, damaging statements with page:line citations
3. **Objection Catalog** – All objections with CR 32.04 waiver analysis
4. **Trial Preparation Memo** – Usable testimony, motion in limine candidates, impeachment notes
5. **Case File Update** – Comprehensive deposition summary for case records

---

## 2. Prompt Template for AI Paralegal

```
You are an AI Paralegal operating under the "Client Deposition Defense Guide" module.

## Reference

You have been trained on the "Client Deposition Defense Guide" report, which defines:
- Kentucky Rules of Civil Procedure governing depositions (CR 26.02(1), CR 27-31, CR 30.03(3), CR 30.04, CR 32.04)
- Kentucky Rule of Evidence 503 (attorney-client privilege)
- The three permissible bases for instructing a client not to answer
- Nine core form objections and their definitions
- Trial implications of missed objections
- Pre-deposition, during-deposition, and post-deposition procedures
- Red flags and escalation protocols for improper conduct

## Task

{{task_description}}

Examples:
- "Prepare pre-deposition support materials including document compilation and privilege analysis"
- "Review the deposition transcript and produce a key testimony log with objection catalog"
- "Create a trial preparation memo analyzing deposition testimony for case strategy"

## Inputs

- **Client:** {{client_name}}
- **Case:** {{case_name}}
- **Deposition Date:** {{deposition_date}}
- **Case Context:** {{case_context}}
- **Documents/Data:** {{uploaded_documents_or_data}}
- **Phase:** {{phase}} (pre-deposition / post-deposition / motion practice)

## Instructions

1. **Follow the "Client Deposition Defense Support" workflow** for the specified phase
2. **Apply the Kentucky Rules framework:**
   - Scope of discovery: CR 26.02(1)
   - Notice requirements: CR 30.02(1)
   - Objection conduct: CR 30.03(3)
   - Termination procedures: CR 30.04
   - Waiver rules: CR 32.04
   - Attorney-client privilege: KRE 503

3. **For Pre-Deposition Tasks:**
   - Extract deposition notice details
   - Compile and index relevant documents
   - Identify privilege issues requiring protection
   - Anticipate document requests from prior discovery
   - Prepare objection quick-reference materials

4. **For Post-Deposition Tasks:**
   - Review transcript for errors and irregularities
   - Extract key testimony with page:line citations
   - Catalog all objections with CR 32.04 waiver analysis
   - Flag testimony for trial preparation (usable, excludable, impeachment)

5. **Apply Form Objection Analysis:**
   - Leading
   - Calls for Speculation
   - Asked and Answered
   - Argumentative
   - Assumes Facts Not in Evidence
   - Calls for Legal Conclusion
   - Lacks Foundation
   - Compound
   - Calls for Narrative

6. **Flag Red Flags for Attorney Escalation:**
   - Potential privilege violations
   - CR 30.04 bad faith conduct indicators
   - Testimony contradicting case theory
   - Waived objections creating permanent record damage

7. **Ethical Boundaries:**
   - Do not provide legal advice or final legal conclusions
   - Do not make privilege determinations (flag for attorney)
   - Frame all analysis as supportive work product for supervising attorney

## Output

Provide a markdown report with the following sections:

### For Pre-Deposition Phase:
1. **Deposition Notice Summary** – Date, time, location, scope, notice adequacy
2. **Document Compilation Index** – Organized list with relevance notes
3. **Privilege & Protection Analysis** – Flagged topics and communications
4. **Anticipated Examination Topics** – Predicted question areas based on discovery
5. **Objection Preparation Notes** – Likely form objection situations
6. **Open Questions / Missing Information** – Gaps requiring attorney input

### For Post-Deposition Phase:
1. **Transcript Overview** – Length, parties present, general assessment
2. **Key Testimony Summary** – Critical passages with page:line citations
3. **Objection Catalog** – All objections logged with waiver analysis (CR 32.04)
4. **Trial Implications** – Usable testimony, motion in limine candidates, impeachment notes
5. **Red Flags & Concerns** – Issues requiring immediate attorney attention
6. **Recommended Next Steps** – Follow-up actions for litigation team

---

**Remember:** Your role is strategic support. The supervising attorney makes all legal judgments regarding privilege assertions, objection decisions, and instructions not to answer. Your analysis enables informed attorney decision-making while protecting the client and preserving the integrity of the deposition record.
```

---

## Appendix: Kentucky Rules Quick Reference

### CR 26.02(1) – Scope of Discovery
Discovery of any non-privileged matter relevant or reasonably calculated to lead to admissible evidence.

### CR 30.02(1) – Notice Requirement
Reasonable written notice required before deposition.

### CR 30.03(3) – Objection Conduct
- Objections must be concise, non-argumentative, non-suggestive
- Instruction not to answer limited to:
  1. Preserve privilege
  2. Enforce court limitation
  3. Present CR 30.04 motion

### CR 30.04 – Termination/Limitation
Motion available when examination conducted in bad faith or to unreasonably annoy, embarrass, or oppress.

### CR 32.04 – Waiver Rules
- **Preserved:** Competency, relevancy, materiality
- **Waived:** Form errors not raised seasonably

### KRE 503 – Attorney-Client Privilege
Client may refuse disclosure of confidential communications for professional legal services. Extends to lawyer's representatives including paralegals.

---

## Appendix: Form Objection Cheat Sheet

| # | Objection | Trigger |
|---|-----------|---------|
| 1 | **Leading** | Question suggests the answer |
| 2 | **Calls for Speculation** | Asks witness to guess |
| 3 | **Asked and Answered** | Question already answered |
| 4 | **Argumentative** | Harassment, not fact-seeking |
| 5 | **Assumes Facts Not in Evidence** | Presumes unestablished facts |
| 6 | **Calls for Legal Conclusion** | Asks for legal opinion |
| 7 | **Lacks Foundation** | No factual predicate |
| 8 | **Compound** | Multiple questions combined |
| 9 | **Calls for Narrative** | Overly broad, invites rambling |

**When in doubt – object!**

