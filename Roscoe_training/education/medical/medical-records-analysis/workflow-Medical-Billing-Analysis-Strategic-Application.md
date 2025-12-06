# Medical Billing Analysis & Strategic Application

## Operational Workflow

---

### Workflow Name
**Medical Billing Analysis & Reasonableness Evaluation**

---

### Goal
Successfully analyze medical bills to establish the **reasonable value** of medical services (not merely the billed amount), identify technical billing errors, benchmark charges against geographic market data, and produce a defensible damages analysis that can withstand legal scrutiny under Daubert and collateral source rule challenges.

---

### When to Use
- After medical records have been organized and treatment chronology drafted
- During damages calculation phase of personal injury litigation
- When preparing for settlement negotiations requiring defensible medical expense valuations
- Prior to expert witness coordination for damages testimony
- When opposing counsel challenges the reasonableness of medical charges
- When verifying that billed services align with documented diagnoses and treatment

---

### Inputs Required

| Input | Description |
|-------|-------------|
| **Medical Bills** | Itemized bills from all providers (hospitals, physicians, imaging centers, PT/OT, pharmacy, DME) |
| **Medical Records** | Corresponding clinical documentation to validate services billed |
| **Provider Information** | NPI numbers and practice zip codes for each provider |
| **Diagnosis Codes** | ICD-10 codes from billing statements |
| **Procedure Codes** | CPT, HCPCS, NDC, DRG codes from all bills |
| **Dates of Service** | Exact dates for each billed service |
| **Payment Information** | If available: amounts accepted from Medicare, Medicaid, or commercial insurers |
| **Case Context** | Injury type, accident date, jurisdiction |

---

### Step-by-Step Process

#### **Phase 1: Technical Audit (Prong 1)**

**Step 1.1 — Organize and Index All Bills**
- Compile all medical bills into a master spreadsheet
- Index by provider, date of service, and service type
- Link each bill to corresponding medical records

**Step 1.2 — Verify Code Accuracy**
- Confirm CPT, HCPCS, NDC, or DRG codes match services documented in medical records
- Cross-reference procedure descriptions with clinical notes
- Flag any codes that don't align with documented care

**Step 1.3 — Screen for Unbundling**
- Identify services billed separately that should be bundled under a single code
- Cross-reference against National Correct Coding Initiative (NCCI) edits
- Document any unbundling violations

**Step 1.4 — Validate Modifiers**
- Review all two-digit CPT modifiers for correct usage
- Verify modifiers are justified by clinical documentation
- Flag improper modifier usage

**Step 1.5 — Screen for Upcoding**
- Compare level of service billed (e.g., E&M complexity levels) against medical record documentation
- Verify documentation supports the billed complexity level
- Flag instances where billing exceeds documented complexity

**Step 1.6 — Check Medically Unlikely Edits (MUEs)**
- Verify units of service don't exceed typical maximums for single-day services
- Flag any services exceeding MUE thresholds

**Step 1.7 — Verify Medical Necessity**
- Confirm ICD-10 diagnosis codes justify the procedures billed
- Verify services were appropriate for injuries sustained
- Document any medically unnecessary services

---

#### **Phase 2: Geographic Pricing Analysis (Prong 2)**

**Step 2.1 — Isolate Key Data Points for Each Service**
- Extract validated CPT code
- Record exact date of service
- Identify provider's zip code (from NPI registry)

**Step 2.2 — Query National Pricing Databases**
- Input key data points into authoritative pricing databases:
  - PMIC Medical Fees
  - Wasserman's Physicians Fee Reference
  - Optum's National Fee Analyzer
  - American Hospital Directory (for DRGs)

**Step 2.3 — Document Percentile Charges**
- Record 50th percentile (median) charge
- Record 75th percentile charge
- Record 90th percentile charge
- Note the geographic region and time period for each benchmark

**Step 2.4 — Compare Billed Charges to Benchmarks**
- Create comparison showing where each provider's charge falls relative to percentiles
- Calculate percentage above/below each benchmark
- Identify statistical outliers (charges significantly above 90th percentile)

---

#### **Phase 3: Local Market Validation (Prong 3)**

**Step 3.1 — Review Hospital Price Transparency Data**
- Check local hospital websites for published chargemaster rates
- Document negotiated rates with different payers for same/similar services
- Note any publicly available pricing data

**Step 3.2 — Consult Government Fee Schedules**
- Review Medicare fee schedules for the geographic region
- Check state-specific Workers' Compensation fee schedules
- Use government rates as additional benchmarks

**Step 3.3 — Cross-Reference and Validate**
- Confirm data-driven values align with local market realities
- Document any discrepancies between database benchmarks and local validation sources
- Adjust reasonable value conclusions if local data suggests different norms

---

#### **Phase 4: Service-Specific Analysis**

**Step 4.1 — Professional Services**
- Audit using CPT codes and NCCI edits
- Apply standard E&M coding guidelines

**Step 4.2 — Anesthesia Services**
- Apply ASA formula: Base + Time + Modifying units
- Verify time documentation supports billed units

**Step 4.3 — Inpatient Facility Services**
- Audit based on DRG codes
- Validate against American Hospital Directory data
- Compare to typical Medicare and commercial rates for the DRG

**Step 4.4 — Outpatient Facility Services**
- Audit using CPT and APC codes
- Benchmark against UCR values

**Step 4.5 — Pharmaceuticals**
- Audit using NDC codes
- Benchmark against Average Wholesale Price (AWP)
- Reference IBM Micromedex RED BOOK

**Step 4.6 — Durable Medical Equipment (DMEPOS)**
- Audit using HCPCS codes
- Compare against state-specific fee schedules

---

#### **Phase 5: Synthesis and Reporting**

**Step 5.1 — Calculate Reasonable Value**
- For each billed service, determine reasonable value based on:
  - Technical audit findings (correct code, correct units)
  - Geographic benchmark analysis (percentile positioning)
  - Local market validation

**Step 5.2 — Document Overcharges and Errors**
- Create itemized list of billing errors identified
- Quantify difference between billed charges and reasonable values
- Categorize issues (unbundling, upcoding, statistical outliers, etc.)

**Step 5.3 — Prepare Defensible Summary**
- Structure findings to withstand Daubert challenges
- Document methodology clearly
- Prepare for collateral source rule objections

---

### Quality Checks & Safeguards

#### **Validation Checks**
- [ ] Every CPT code verified against medical record documentation
- [ ] All data points extracted accurately (dates, NPIs, zip codes)
- [ ] Percentile benchmarks from correct geographic region and time period
- [ ] Local validation sources documented
- [ ] Methodology traceable and reproducible

#### **Red Flags Requiring Escalation**

| Red Flag | Action |
|----------|--------|
| **Upcoding identified** | Flag for attorney review; may indicate fraud |
| **Significant unbundling** | Document for potential billing adjustment negotiation |
| **Charges >50% above 90th percentile** | Highlight as extreme outlier; requires strong defense preparation |
| **Missing documentation for services** | Cannot validate reasonableness; flag for records request |
| **Inconsistent coding across providers** | Review for potential defense arguments |
| **Suspiciously high pharmacy charges** | Compare to AWP; may indicate markup issues |

#### **Escalate to Supervising Attorney When:**
- Billing fraud indicators present (systematic upcoding, unbundling patterns)
- Total damages reduction exceeds $50,000 from billing analysis
- Collateral source rule implications need legal strategy
- Expert witness coordination required
- Opposing counsel has raised Daubert challenge
- Jurisdiction-specific rules affect reasonableness standards

---

### Outputs

| Deliverable | Description |
|-------------|-------------|
| **Master Billing Analysis Spreadsheet** | Itemized analysis of all bills with codes, dates, providers, billed amounts, percentile benchmarks, and reasonable values |
| **Technical Audit Summary** | List of all coding errors, unbundling, upcoding, and MUE violations identified |
| **Geographic Pricing Report** | Percentile comparisons for each service showing market positioning |
| **Reasonable Value Summary** | Total billed charges vs. total reasonable value with line-item breakdown |
| **Methodology Documentation** | Clear explanation of three-pronged methodology for Daubert defense |
| **Issues & Red Flags Memo** | Summary of significant findings requiring attorney attention |
| **Expert Coordination Brief** | Key data points and findings for damages expert preparation |

---

## Prompt Template for AI Paralegal

```
You are an AI Paralegal operating under the "Medical Billing Analysis & Strategic Application" module.

## Reference

You have been trained on the "Medical Billing Analysis & Strategic Application" report, which defines:
- The three-pronged methodology for establishing reasonable value of medical services
- Technical audit protocols for identifying coding errors (unbundling, upcoding, MUEs)
- Geographic pricing analysis using national databases and percentile benchmarks
- Local market validation procedures
- Service-specific audit standards (professional, anesthesia, inpatient, outpatient, pharmacy, DME)
- Legal defense strategies for Daubert challenges and collateral source rule objections
- Critical data points: CPT/HCPCS/NDC/DRG codes, dates of service, NPI/zip codes, billed vs. accepted payments, ICD-10 diagnosis codes

## Task

Analyze the provided medical bills to establish the reasonable value of medical services, identify technical billing errors, benchmark charges against geographic market data, and produce a defensible damages analysis that distinguishes between billed charges and legally recoverable reasonable values.

## Inputs

- **Client:** {{client_name}}
- **Case Context:** {{case_context}} (injury type, accident date, jurisdiction)
- **Medical Bills:** {{uploaded_bills_or_data}}
- **Medical Records:** {{uploaded_records_for_validation}}
- **Provider Information:** {{provider_NPIs_and_locations}}

## Instructions

Follow the "Medical Billing Analysis & Reasonableness Evaluation" workflow step by step:

### Phase 1: Technical Audit (Prong 1)
1. Organize and index all bills by provider, date, and service type
2. Verify code accuracy against medical records
3. Screen for unbundling violations (check NCCI edits)
4. Validate modifier usage
5. Identify upcoding (compare billed complexity to documentation)
6. Check for Medically Unlikely Edits (MUE) violations
7. Verify medical necessity (ICD-10 codes justify procedures)

### Phase 2: Geographic Pricing Analysis (Prong 2)
1. Extract CPT code, date of service, and provider zip code for each service
2. Query national pricing databases for 50th, 75th, and 90th percentile benchmarks
3. Compare billed charges to percentile benchmarks
4. Identify statistical outliers

### Phase 3: Local Market Validation (Prong 3)
1. Reference hospital price transparency data where available
2. Consult Medicare and Workers' Compensation fee schedules
3. Validate data-driven conclusions against local market realities

### Phase 4: Apply Service-Specific Standards
- Professional services: CPT + NCCI edits
- Anesthesia: ASA formula (Base + Time + Modifying units)
- Inpatient: DRG validation against American Hospital Directory
- Outpatient: CPT + APC codes vs. UCR
- Pharmacy: NDC codes vs. AWP (RED BOOK)
- DME: HCPCS vs. state fee schedules

### Phase 5: Synthesize Findings
1. Calculate reasonable value for each service
2. Document all errors and overcharges
3. Prepare methodology documentation for legal defense

## Constraints

- Do not provide legal advice or final legal conclusions
- Frame all analysis as supportive work product for a supervising attorney
- Flag ambiguities or gaps in documentation rather than making assumptions
- Cite specific codes, percentiles, and data sources for all conclusions
- Acknowledge limitations where pricing database access is unavailable

## Output

Provide a structured markdown report with the following sections:

### 1. Executive Summary
- Total billed charges
- Total reasonable value (calculated)
- Total potential overcharge identified
- Key findings summary

### 2. Technical Audit Findings
- Coding errors identified (unbundling, upcoding, MUEs)
- Medical necessity issues
- Documentation gaps

### 3. Geographic Pricing Analysis
- Table of services with billed amount, 50th/75th/90th percentile benchmarks, and reasonable value
- Statistical outliers highlighted

### 4. Service-by-Service Analysis
- Detailed breakdown by provider/service category
- Methodology applied to each

### 5. Red Flags & Issues for Attorney Review
- Billing irregularities requiring escalation
- Defense vulnerabilities
- Missing information needed

### 6. Methodology Documentation
- Clear explanation of three-pronged approach
- Data sources used
- Basis for reasonable value conclusions (for Daubert defense)

### 7. Recommendations
- Suggested reasonable value for settlement purposes
- Areas requiring expert witness input
- Additional documentation needed
```

---

## Quick Reference: Key Legal Standards

### The Reasonableness Mandate
> "A plaintiff's recovery for medical expenses is limited to the **reasonable value** of the necessary services, not automatically the amount billed."

- Billed charges ≠ usual and customary charges
- 46+ jurisdictions require reasonableness proof for medical expense recovery
- "Other evidence" beyond the bill itself is required

### Daubert Defense Points
The three-pronged methodology satisfies Federal Rule of Evidence 702 because it is:
1. **Based on sufficient facts** — begins with actual bills and records
2. **Product of reliable methods** — uses federally standardized codes (CPT, DRG) and aggregated national databases
3. **Applied reliably** — systematic, reproducible, data-driven comparison process

### Collateral Source Rule Defense
The expert opinion does not violate the collateral source rule because it is:
- Not derived from payments by a collateral source (insurance)
- Grounded in industry principles and broad market data
- An analysis of the charge itself, not what any specific insurer paid

---

## Service-Specific Code Reference

| Service Category | Key Codes | Audit Standard |
|------------------|-----------|----------------|
| Professional Services | CPT | NCCI edits |
| Anesthesia | CPT + Time Units | ASA formula |
| Inpatient Facility | DRG | American Hospital Directory |
| Outpatient Facility | CPT + APC | UCR values |
| Pharmaceuticals | NDC | AWP (RED BOOK) |
| DME/DMEPOS | HCPCS | State fee schedules |

---

*This workflow is derived from the "Medical Billing Analysis & Strategic Application" training report. All analysis should be performed under attorney supervision. The AI paralegal does not provide legal advice or final legal conclusions.*



