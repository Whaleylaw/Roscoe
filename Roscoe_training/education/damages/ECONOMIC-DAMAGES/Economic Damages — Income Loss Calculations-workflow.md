# Economic Damages — Income Loss Calculations

## Module Reference
**Source Report:** Economic Damages — Income Loss Calculations  
**Module Type:** Economic Damages Analysis  
**Last Updated:** December 2025

---

# 1. Operational Workflow

## Workflow Name
**Income Loss Economic Damages Analysis Workflow**

---

## Goal
Successful completion means the AI paralegal has:
1. Correctly identified whether the case warrants a **Past Lost Wages** claim, a **Future Loss of Earning Capacity** claim, or both
2. Established a defensible wage base supported by documentation
3. Calculated or projected economic losses using the appropriate methodology
4. Identified all missing evidence and documentation gaps
5. Flagged cases requiring expert witnesses (vocational rehabilitation expert, forensic economist)
6. Produced a comprehensive economic damages summary ready for attorney review and demand package inclusion

---

## When to Use
Trigger this workflow when:
- A client has missed work or will miss work due to injury
- Medical records indicate work restrictions or disability
- The case involves calculating economic damages for settlement demand or litigation
- Preparing the economic damages section of a demand package
- Evaluating whether to pursue lost wages vs. earning capacity theory
- Coordinating with vocational or economic experts
- A client has permanent injuries affecting future work capacity
- A client is young with high potential but limited work history
- A client has variable, informal, or self-employment income

---

## Inputs Required

### Mandatory Inputs
- [ ] Client name and case identifier
- [ ] Date of injury/incident
- [ ] Nature of injuries (temporary vs. permanent)
- [ ] Medical records with work restrictions and return-to-work status
- [ ] Employment status at time of injury (employed, self-employed, unemployed, student)

### Conditional Inputs (Based on Employment Type)

**For Formally Employed Individuals:**
- [ ] W-2 forms (past 5-10 years)
- [ ] Recent pay stubs (1-2 years preceding injury)
- [ ] HR letter verifying rate of pay, hours, employment dates
- [ ] Benefits documentation (health insurance, 401k contributions)

**For Variable Income (Commissions, Tips, Seasonal):**
- [ ] 5-10 years of earnings history
- [ ] Commission statements, tip records, bonus documentation
- [ ] Tax returns showing income patterns

**For Informally Employed Individuals:**
- [ ] Any available records (supervisor notebooks, informal logs)
- [ ] Witness affidavits regarding work schedule
- [ ] Bank deposit records showing regular income

**For Self-Employed Individuals:**
- [ ] Business tax returns (5+ years)
- [ ] Profit/loss statements
- [ ] Invoices and contracts
- [ ] Records of cancelled appointments or lost contracts

**For Future Earning Capacity Claims:**
- [ ] Educational transcripts, degrees, certifications
- [ ] Complete work history with performance reviews
- [ ] Evidence of career goals (applications, job postings, mentor communications)
- [ ] Medical expert report on permanency of injury
- [ ] Vocational rehabilitation expert report (if available)
- [ ] Forensic economist report (if available)

---

## Step-by-Step Process

### Phase 1: Initial Assessment & Theory Selection

**Step 1.1: Assess Injury Duration Impact**
Determine the temporal nature of the injury's impact on work capacity:
- **Temporary Injury**: Client has returned or is expected to return to previous job at full capacity → Primary claim is **Past Lost Wages**
- **Permanent Injury**: Client will never return to previous job or has reduced overall work ability → Primary claim is **Future Loss of Earning Capacity** (may also include past lost wages component)

**Step 1.2: Assess Employment Pattern**
Categorize the client's employment type:
- Formally employed (W-2, steady income)
- Variable income (commissions, tips, bonuses, seasonal)
- Informally employed (cash, off-the-books)
- Self-employed
- Student or recent graduate
- Unemployed with documented career trajectory

**Step 1.3: Apply Decision Tree**
Using the assessment from Steps 1.1 and 1.2:

```
IF injury is temporary AND plaintiff returning to full capacity:
    → Pursue PAST LOST WAGES claim
    → IF steady formal employment: use mechanical calculation
    → IF variable/informal employment: establish wage base through multi-year averaging
    
IF injury is permanent AND prevents return to previous work:
    → Pursue FUTURE LOSS OF EARNING CAPACITY claim
    → ALSO include past lost wages component for time missed
    → IF young person with strong credentials: build claim around proven potential
    → IF long steady work history: calculate difference between pre-injury trajectory and residual capacity
    → IF sporadic work history: vocational expert is CRITICAL
```

**Step 1.4: Document Theory Selection Rationale**
Record the reasoning for the chosen damages theory, citing:
- Employment pattern classification
- Injury horizon (temporary vs. permanent)
- Potential vs. performance analysis
- Supporting evidence available

---

### Phase 2: Past Lost Wages Calculation (If Applicable)

**Step 2.1: Establish Wage Base**
Calculate the Defensible Annualized Earnings (DAE) figure:

*For Formally Employed:*
- Extract hourly/salary rate from HR records and pay stubs
- Verify against W-2 forms
- Include overtime patterns if regular
- Document benefits value (health insurance, retirement contributions)

*For Variable Income:*
- Compile 5-10 years of earnings data
- Calculate weighted average, accounting for trends
- Document methodology for averaging
- Flag need for economist testimony if complex

*For Informal Employment:*
- Gather all available documentation (notebooks, witness statements)
- Cross-reference with bank deposits if available
- Document credibility factors for each evidence source
- Flag any off-the-books income risks

**Step 2.2: Calculate Time Missed**
Document the medically necessary absence period:
- Extract work restriction dates from medical records
- Obtain physician's notes explicitly stating inability to work
- Gather employer records confirming absence dates
- Ensure continuous medical nexus (no unexplained treatment gaps)

**Step 2.3: Perform Calculation**
Apply the formula:
```
Lost Wages = Wage Rate × Time Missed
```

Include:
- Base wages lost
- Overtime lost (if regularly scheduled)
- Benefits lost (health insurance, 401k match, other perquisites)
- Any partial return-to-work adjustments

**Step 2.4: Document Special Considerations**
Address and document:
- Pre-existing conditions and their differentiation from new injury
- Partial return to work scenarios (calculate wage differential)
- Full benefits and perquisites valuation
- Self-employment complications

---

### Phase 3: Future Loss of Earning Capacity Analysis (If Applicable)

**Step 3.1: Assess Plaintiff Profile**
Categorize the client:
- Young person with high potential, limited work history
- Individual with sporadic/non-traditional employment
- Worker unable to return to specific occupation
- Individual with permanent cognitive/physical impairments

**Step 3.2: Build Pre-Injury Earning Potential Profile**
Gather and organize evidence of:
- Educational credentials and achievements
- Work history with progression indicators
- Specialized skills and certifications
- Documented career goals and aspirations
- Industry/labor market data for plaintiff's field

**Step 3.3: Assess Post-Injury Residual Capacity**
Document:
- Medical evidence of permanent limitations
- Types of work plaintiff can no longer perform
- Types of work plaintiff may still be able to perform
- Need for vocational rehabilitation expert assessment

**Step 3.4: Identify Expert Requirements**
Flag need for:
- **Vocational Rehabilitation Expert**: To assess pre-injury trajectory, post-injury limitations, and residual earning capacity
- **Forensic Economist**: To calculate present value of lost capacity, applying discount rates and wage growth assumptions

**Step 3.5: Credibility Assessment**
Apply the "Jane vs. John" test:
- Does the projection align with plaintiff's actual education, skills, and documented ambitions?
- Is there objective evidence supporting the claimed trajectory?
- Would a jury find this projection credible given plaintiff's profile?
- Flag any speculative elements that could undermine case credibility

---

### Phase 4: Present Value Calculation (Future Capacity Claims)

**Step 4.1: Understand Time Value of Money**
Document that future losses must be reduced to present value because:
- A dollar today is worth more than a dollar in the future
- The lump sum award can be invested
- This is a legally required adjustment

**Step 4.2: Identify Calculation Variables**
Note the key variables that experts will dispute:
- Discount rate assumptions
- Wage growth projections
- Inflation adjustments
- Work life expectancy

**Step 4.3: Flag for Expert Calculation**
This calculation requires forensic economist testimony. Document:
- All data gathered for expert use
- Questions about methodology for attorney to address with expert
- Anticipated defense expert counter-arguments

---

### Phase 5: Documentation Assembly & Gap Analysis

**Step 5.1: Complete Documentation Checklist**
Use the appropriate checklist based on claim type(s):

**Past Lost Wages Checklist:**
- [ ] W-2/1099 forms (5-10 years)
- [ ] Pay stubs (1-2 years pre-injury)
- [ ] HR/employer verification letter
- [ ] Variable income documentation (5-10 years if applicable)
- [ ] Informal employment evidence (if applicable)
- [ ] Self-employment records (if applicable)
- [ ] Physician work restriction notes
- [ ] Medical records with specific limitations
- [ ] Employer absence confirmation
- [ ] Health insurance contribution records
- [ ] Retirement plan contribution records
- [ ] Other perquisite documentation

**Future Earning Capacity Checklist:**
- [ ] Academic transcripts (all levels)
- [ ] Diplomas, degrees, certifications
- [ ] Specialized training/license records
- [ ] Complete work history with reviews
- [ ] Career goal evidence
- [ ] Medical permanency report
- [ ] Vocational expert report (or need flagged)
- [ ] Forensic economist report (or need flagged)
- [ ] Labor market data
- [ ] Pre-injury medical records (pre-existing conditions)
- [ ] Witness statements on skills/potential

**Step 5.2: Identify Missing Evidence**
Create itemized list of:
- Documents not yet obtained
- Documents that may not exist
- Alternative evidence sources to pursue
- Witnesses who could provide supporting testimony

**Step 5.3: Flag Evidence Gaps to Attorney**
Prioritize gaps by impact on claim credibility and defensibility.

---

### Phase 6: Output Generation

**Step 6.1: Prepare Economic Damages Summary**
Create a structured summary including:
- Theory of damages selected and rationale
- Wage base calculation with supporting evidence
- Time missed calculation with medical support
- Total past lost wages (if applicable)
- Future earning capacity analysis (if applicable)
- Expert witness requirements
- Documentation status
- Missing evidence list
- Red flags and vulnerabilities

**Step 6.2: Prepare Demand Package Section**
Draft the economic damages narrative for inclusion in demand package:
- Clear statement of economic losses claimed
- Supporting documentation references
- Calculation methodology explanation
- Total economic damages figure

---

## Quality Checks & Safeguards

### Validation Checks

**For All Claims:**
- [ ] Medical nexus established between injury and work absence/limitation
- [ ] No unexplained gaps in medical treatment during claimed lost work period
- [ ] Employer records consistent with medical records and plaintiff testimony
- [ ] All income claimed is properly documented and reportable

**For Past Lost Wages:**
- [ ] Wage base derived from verifiable documents
- [ ] Time missed supported by physician's explicit statements
- [ ] Benefits/perquisites properly valued and documented
- [ ] Partial return-to-work properly accounted for

**For Future Earning Capacity:**
- [ ] Projection grounded in plaintiff's actual credentials and trajectory
- [ ] Expert witnesses identified for vocational and economic testimony
- [ ] Pre-existing conditions addressed and differentiated
- [ ] Residual earning capacity realistically assessed (not assumed to be zero without basis)

### Red Flags — Escalate to Attorney

**Immediate Escalation Required:**
- ⚠️ Off-the-books income being claimed (tax/immigration liability risks)
- ⚠️ Significant discrepancies between medical records, employer records, and plaintiff statements
- ⚠️ Evidence that plaintiff worked during claimed disability period
- ⚠️ Projection appears speculative or not grounded in plaintiff's actual profile ("John, The Immigrant Laborer" scenario)
- ⚠️ Pre-existing conditions that significantly overlap with claimed limitations
- ⚠️ Missing critical documentation with no alternative evidence sources

**Advisory Flags:**
- ⚡ Complex variable income requiring economist testimony
- ⚡ Self-employment with incomplete business records
- ⚡ Plaintiff's career trajectory requires expert to establish credibility
- ⚡ Anticipated significant dispute over present value assumptions
- ⚡ Multiple pre-existing conditions requiring careful differentiation

### Credibility Stress Tests

Before finalizing, apply these tests:
1. **Documentation Test**: Can every claimed dollar be traced to a document?
2. **Medical Nexus Test**: Does a physician explicitly connect every missed day to the injury?
3. **Consistency Test**: Do all records (medical, employer, plaintiff testimony) align?
4. **Jury Credibility Test**: Would a reasonable juror accept this claim as realistic?
5. **Defense Attack Test**: What are the obvious attack points, and are they addressed?

---

## Outputs

### Primary Outputs

1. **Economic Damages Analysis Report**
   - Markdown document with structured sections
   - Includes all calculations with supporting citations
   - Theory selection rationale
   - Evidence inventory with status

2. **Calculation Worksheet**
   - Itemized breakdown of all economic damages claimed
   - Formula application shown
   - Source document citations for each figure

3. **Documentation Gap Report**
   - Missing evidence itemized
   - Alternative evidence suggestions
   - Priority ranking for document collection

4. **Expert Witness Coordination Memo**
   - Experts required (vocational, economist)
   - Data package for expert review
   - Questions for expert to address

5. **Demand Package Economic Section**
   - Narrative summary of economic losses
   - Total figure with breakdown
   - Supporting documentation index

### Secondary Outputs (As Needed)

- Timeline of work absence with medical support citations
- Pre-injury earnings history summary table
- Career trajectory analysis (for earning capacity claims)
- Present value calculation data package for economist
- Rebuttal preparation notes on anticipated defense arguments

---

# 2. Prompt Template for AI Paralegal

```
You are an AI Paralegal operating under the "Economic Damages — Income Loss Calculations" module.

## Reference

- You have been trained on the "Economic Damages — Income Loss Calculations" report, which defines the complete methodology for calculating income-related economic damages, including:
  - Past Lost Wages: mechanical, backward-looking calculation
  - Future Loss of Earning Capacity: forward-looking actuarial projection
  - Decision frameworks for theory selection
  - Documentation checklists and evidence requirements
  - Expert witness coordination protocols
  - Red flags and credibility safeguards

## Task

{{task_description}}

Examples:
- "Analyze the provided employment and medical records to calculate past lost wages and identify missing documentation."
- "Evaluate whether this case supports a future loss of earning capacity claim and outline the expert witness requirements."
- "Prepare the economic damages section for the demand package."
- "Review the economic damages calculation for completeness and flag any credibility vulnerabilities."

## Inputs

- **Client:** {{client_name}}
- **Case Context:** {{case_context}}
  - Date of Injury: {{date_of_injury}}
  - Nature of Injuries: {{injury_description}}
  - Injury Status: {{temporary_or_permanent}}
  - Employment Type at Injury: {{employment_type}}
  - Return to Work Status: {{return_to_work_status}}
- **Documents Provided:** {{uploaded_documents_or_data}}
  - Employment records: {{employment_records_list}}
  - Medical records: {{medical_records_list}}
  - Expert reports: {{expert_reports_list}}

## Instructions

1. **Follow the "Income Loss Economic Damages Analysis Workflow"** step by step:
   - Phase 1: Assess injury duration and employment pattern; select damages theory
   - Phase 2: Calculate past lost wages (if applicable)
   - Phase 3: Analyze future earning capacity (if applicable)
   - Phase 4: Address present value calculation requirements
   - Phase 5: Complete documentation checklist and gap analysis
   - Phase 6: Generate required outputs

2. **Apply the decision tree** from the report:
   - Assess whether injury is temporary or permanent
   - Classify employment pattern
   - Select appropriate theory (or combination)
   - Document rationale for theory selection

3. **Use the documentation checklists** to verify evidence completeness:
   - For Past Lost Wages: wage documentation, time missed documentation, benefits documentation
   - For Future Earning Capacity: foundational plaintiff evidence, medical/vocational evidence, economic evidence

4. **Apply red-flag rules** from the report:
   - Flag off-the-books income risks
   - Flag speculative projections not grounded in plaintiff's actual profile
   - Flag documentation gaps and inconsistencies
   - Apply the "Jane vs. John" credibility test

5. **Identify expert witness requirements:**
   - Vocational rehabilitation expert for career trajectory and residual capacity
   - Forensic economist for present value calculations

6. **Do not provide legal advice or final legal conclusions.** Frame all analysis as supportive work product for a supervising attorney. Flag all issues requiring attorney judgment or decision.

## Output

Provide a markdown report with the following sections:

### Economic Damages Analysis Report

**1. Executive Summary**
- Damages theory selected (Past Lost Wages / Future Earning Capacity / Both)
- Total economic damages claimed (or projected range)
- Key supporting evidence summary
- Critical gaps or issues requiring attorney attention

**2. Theory Selection Analysis**
- Injury duration assessment (temporary vs. permanent)
- Employment pattern classification
- Decision tree application and rationale
- Credibility assessment of selected theory

**3. Past Lost Wages Calculation** (if applicable)
- Wage base establishment
  - Rate of pay with source citation
  - Benefits and perquisites valuation
- Time missed calculation
  - Dates of absence
  - Medical support citations
- Total calculation with formula shown
- Special considerations addressed

**4. Future Loss of Earning Capacity Analysis** (if applicable)
- Plaintiff profile assessment
- Pre-injury earning potential evidence
- Post-injury residual capacity assessment
- Expert witness requirements
- Credibility stress test results

**5. Documentation Status**
- Checklist completion status
- Documents obtained (with locations/citations)
- Documents missing
- Alternative evidence sources to pursue

**6. Red Flags & Vulnerabilities**
- Issues requiring attorney attention (prioritized)
- Anticipated defense arguments
- Recommended mitigation strategies

**7. Expert Witness Coordination**
- Experts required
- Data package contents for expert review
- Key questions for expert testimony

**8. Demand Package Draft Section** (if requested)
- Economic damages narrative
- Total figure with breakdown
- Supporting documentation index

**9. Open Questions / Missing Information**
- Unresolved factual questions
- Documents needed to strengthen claim
- Client clarifications required

---

## Formatting Requirements

- Use headers and subheaders for clear organization
- Include tables for calculations and comparisons
- Cite source documents with specificity (document name, page number, date)
- Use checkboxes for actionable items
- Bold key figures and conclusions
- Use ⚠️ for red flags and ⚡ for advisory notes
```

---

# Appendix: Quick Reference

## Formula Reference

**Past Lost Wages:**
```
Lost Wages = Wage Rate × Time Missed + Benefits Lost
```

**Future Loss of Earning Capacity:**
```
Lost Capacity = (Pre-Injury Earning Potential - Post-Injury Residual Capacity) × Work Life Expectancy
Present Value = Lost Capacity adjusted for discount rate, wage growth, and inflation
```

## Decision Matrix Quick Reference

| Factor | Past Lost Wages | Future Earning Capacity |
|--------|-----------------|-------------------------|
| Temporal Focus | Past → Present | Future (lifetime) |
| Calculation | Mechanical arithmetic | Actuarial projection |
| Key Evidence | Pay stubs, W-2s, employer records | Education, vocational analysis, market data |
| Certainty | High (verifiable data) | Lower (projections) |
| Ideal Plaintiff | Steady job, temporary injury | High potential, permanent impairment |
| Expert Required | Often not required | Almost always required |

## Expert Witness Quick Reference

| Expert | Role | When Required |
|--------|------|---------------|
| Vocational Rehabilitation | Assess pre-injury trajectory, post-injury limitations, residual capacity | Future earning capacity claims |
| Forensic Economist | Calculate present value of lost capacity | Future earning capacity claims |
| CPA/Accountant | Complex variable income analysis | Variable income past lost wages |

## Red Flag Quick Reference

| Red Flag | Risk Level | Action |
|----------|------------|--------|
| Off-the-books income | 🔴 Critical | Escalate immediately — legal/tax risks |
| Speculative projection | 🔴 Critical | Reassess theory or ground in evidence |
| Treatment gaps | 🟡 High | Investigate and prepare explanation |
| Record inconsistencies | 🟡 High | Reconcile before finalizing |
| Missing wage docs | 🟡 High | Pursue alternatives or adjust claim |
| Complex variable income | 🟢 Advisory | Consider expert testimony |

