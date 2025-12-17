---
name: accident_report
description: >
  Request and process police/accident report for motor vehicle accidents.
  This workflow identifies the reporting agency, requests the report,
  and extracts key information including parties, insurance, witnesses,
  and liability indicators using the police-report-analysis skill.
phase: file_setup
workflow_id: accident_report
related_skills:
  - document-pdf
  - police-report-analysis
  - insurance
related_tools:
  - read_pdf (tools/read_pdf.py)
  - lexis_crash_order (tools/lexis_crash_order.py)
templates: []
tools_available:
  read_pdf: "tools/read_pdf.py - Convert PDF to markdown for agent reading"
  lexis_crash_order: "tools/lexis_crash_order.py - Order reports from LexisNexis BuyCrash"
condition: accident.type == 'mva' OR accident.police_called
---

# Accident Report Workflow

## Overview

This workflow obtains and processes the police/crash report for motor vehicle accidents. The report is a critical source of information about the at-fault party, insurance coverage, witnesses, and liability determination.

**Workflow ID:** `accident_report`  
**Phase:** `file_setup`  
**Owner:** Agent/User (mixed)  
**Repeatable:** No  
**Conditional:** Only for MVA or when police were called

---

## Prerequisites

- Intake workflow complete
- Accident type is MVA or police report exists
- Basic accident information collected (date, location)

---

## Condition Check

This workflow only runs if:
```
accident.type == 'mva' OR accident.police_called == true
```

If condition not met, workflow is marked N/A and skipped.

---

## Workflow Steps

### Step 1: Identify Reporting Agency

**Step ID:** `identify_agency`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Determine which law enforcement agency responded to the accident.

**Agent Prompt:**
> "Which law enforcement agency responded to the accident? (e.g., LMPD, KSP, Sheriff's Department)"

**Collect:**
- `accident.police_report.agency` - Name of reporting agency

**Common Kentucky Agencies:**
| Agency | Jurisdiction |
|--------|--------------|
| LMPD | Louisville Metro |
| Lexington PD | Lexington-Fayette |
| KSP | State roads, unincorporated areas |
| County Sheriff | County roads |
| City Police | Within city limits |

**Data Target:** `Case Information/overview.json` → `accident.police_report.agency`

---

### Step 2: Get Report Number

**Step ID:** `get_report_number`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Obtain the report number if the client has it.

**Agent Prompt:**
> "Do you have the police report number? (May be on paperwork given at scene)"

**Collect:**
- `accident.police_report.report_number` - Report/case number

**Note:** Report number may be unknown at this stage. Continue to request even without it.

**Data Target:** `Case Information/overview.json` → `accident.police_report.report_number`

---

### Step 3: Request Accident Report

**Step ID:** `request_report`  
**Owner:** User  
**Automatable:** No

**Action:**
Submit request for the accident report to the appropriate agency.

**Manual Process:**
1. Identify agency's records request method
2. Complete request form (online portal, mail, or in-person)
3. Pay fee (typically $5-15)
4. Note request date

**Agency Contact Information:**
| Agency | Request Method | URL/Contact |
|--------|---------------|-------------|
| LMPD | Online Portal | https://louisville-police.org/records |
| KSP | Online Portal | https://kentuckystatepolice.org/records |
| Lexington PD | Online/Mail | Records Division |
| County Sheriff | Contact directly | Varies by county |

**Agent Prompt to User:**
> "Please request the accident report from {{accident.police_report.agency}}. Update when requested."

**Updates on Completion:**
```json
{
  "accident.police_report.requested_date": "{{today}}"
}
```

**Data Target:** `Case Information/overview.json` → `accident.police_report.requested_date`

---

### Step 4: Receive Accident Report

**Step ID:** `receive_report`  
**Owner:** User  
**Automatable:** No  
**Waiting On:** External (agency)

**Expected Wait Time:** 5-10 business days

**Action:**
Receive and upload the accident report when it arrives.

**Agent Prompt to User:**
> "Waiting for accident report. Typically takes 5-10 business days. Upload when received."

**On Receipt:**
1. Upload PDF to case file
2. Update received date

**Updates on Completion:**
```json
{
  "accident.police_report.received_date": "{{today}}",
  "accident.police_report.file_path": "{{uploaded_path}}"
}
```

**Data Target:** `Case Information/overview.json` → `accident.police_report`

---

### Step 5: Extract Report Information

**Step ID:** `extract_report_info`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Parse the accident report to extract key information using the police-report-analysis skill.

**CRITICAL: PDF Conversion Required**

The agent cannot read PDFs directly. Must convert first:

```bash
# Step 5a: Convert PDF to markdown
python tools/read_pdf.py "{case_path}/Reports/crash_report.pdf" --pretty

# Step 5b: Read the converted markdown
read_file("{case_path}/Reports/crash_report.md")
```

**Skill:** `skills/police-report-analysis/skill.md`  
**Tools:** 
- `tools/read_pdf.py` - Convert PDF to readable markdown
- Kentucky codes reference: `skills/police-report-analysis/references/kentucky_codes.md`

**Tool Available:** ✅ Yes

**Extract:**
| Field | Description | Data Target |
|-------|-------------|-------------|
| At-fault parties | Names, addresses, DOB | `at_fault_parties[]` |
| At-fault insurance | Carrier, policy number | `liability.at_fault_parties[].insurance` |
| Witnesses | Names, contact info | `witnesses[]` |
| Officer info | Name, badge number | `accident.police_report.officer_name` |
| Citations issued | Who was cited, for what | `citations[]` |
| Contributing factors | Weather, road conditions, driver actions | `contributing_factors` |
| PIP waterfall inputs | Vehicle occupancy, ownership | `pip_waterfall_inputs` |

**Agent Action:**
> "I'll use the police-report-analysis skill to extract: parties, insurance companies, witnesses, liability indicators, and PIP eligibility information."

**Key Extraction Points:**
- Unit 1 vs Unit 2 designation
- "At Fault" or "Contributing Factor" indicators
- Insurance policy numbers and carriers
- Witness statements summary
- Diagram of accident scene
- Weather/road conditions

---

### Step 6: Update Case with Report Information

**Step ID:** `update_case`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Add extracted information to case file and create insurance entries.

**Skill:** `Skills/insurance/insurance-claim-setup/SKILL.md`

**Creates:**
- Insurance entries in `insurance.json` for each identified carrier
- At-fault party entries in `contacts.json`
- Witness entries in `contacts.json`

**Triggers:** `open_insurance_claims` workflow

**Agent Action:**
> "I've extracted information from the police report and created insurance claim entries in insurance.json. PIP source: {{pip_carrier}}, BI source: {{bi_carrier}}. Next: open these claims to get claim numbers."

**Data Targets:**
- `Case Information/insurance.json` - Insurance entries
- `Case Information/contacts.json` - Parties and witnesses
- `Case Information/overview.json` - Accident details

---

## Outputs

### Information Extracted

| Category | Data Created |
|----------|--------------|
| Insurance | BI, PIP, UM sources identified |
| Parties | At-fault party contact info |
| Witnesses | Witness names and contact info |
| Liability | Contributing factors, citations |
| PIP | Waterfall position determined |

### Workflows Triggered

| Trigger | Workflow |
|---------|----------|
| Insurance sources identified | `open_insurance_claims` |

---

## Completion Criteria

### Required
- `accident.police_report.received_date` populated

### Recommended
- `liability.at_fault_parties.length > 0`
- At least one insurance source identified

---

## State Updates

On workflow completion, update `case_state.json`:
```json
{
  "workflows": {
    "accident_report": {
      "status": "complete",
      "completed_date": "{{today}}",
      "report_received": true,
      "parties_identified": {{count}},
      "insurance_sources_identified": {{count}}
    }
  }
}
```

---

## Related Workflows

- **Triggered By:** `intake` (if MVA)
- **Triggers:** `open_insurance_claims`

---

## Skills & Tools Used

| Skill/Tool | Purpose | Location |
|------------|---------|----------|
| `read_pdf.py` | Convert PDF to markdown (REQUIRED) | `tools/read_pdf.py` |
| `lexis_crash_order.py` | Order reports from BuyCrash | `tools/lexis_crash_order.py` |
| `police-report-analysis` | Extract structured data from crash report | `skills/police-report-analysis/skill.md` |
| `insurance` | Create insurance entries, apply PIP waterfall | See Phase 1 insurance workflows |

**Important:** The agent cannot read PDFs natively. Always convert to markdown first using `read_pdf.py`.

---

## Kentucky-Specific Notes

### PIP Waterfall (KRS 304.39-040)
PIP coverage follows this order:
1. Vehicle in which injured party was occupant
2. Vehicle owned by injured party (if pedestrian)
3. Vehicle owned by resident relative
4. Any other applicable policy

### Citation Information
Kentucky crash reports include:
- Contributing factors codes
- Citations issued (statute numbers)
- "At Fault" determination (advisory, not binding)

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Report not available yet | Check typical processing time for agency. Follow up after expected date. |
| Report number unknown | Can usually request by date/location/parties |
| Poor quality scan | Request better copy or transcribe manually |
| Missing insurance info | Follow up with parties directly or through defense counsel later |
| Disputed liability | Note for attorney review. May affect case evaluation. |

