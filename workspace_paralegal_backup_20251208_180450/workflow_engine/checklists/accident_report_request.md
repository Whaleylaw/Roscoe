# Accident Report Request Checklist (Gap #3)

## Overview
Process for ordering police/accident reports from law enforcement agencies.

---

## Report Ordering Options

### 1. LexisNexis BuyCrash (Preferred)
- **Tool**: `/Tools/crash_reports/lexis_crash_order.py`
- **Cost**: ~$15-20 per report
- **Turnaround**: Instant to 24 hours
- **Coverage**: Most Kentucky reports

```bash
# Order via automation tool
python /Tools/crash_reports/lexis_crash_order.py \
  --report-number "{{report_number}}" \
  --output /{{case_name}}/police_report/
```

### 2. Direct from Agency
- Contact agency records department
- May be cheaper but slower
- Some rural areas not on BuyCrash

---

## Kentucky Agency Contacts

### Louisville Metro (LMPD)
- **Records**: (502) 574-7111
- **Address**: 633 W. Jefferson St, Louisville, KY 40202
- **Cost**: $10
- **Method**: Online, in-person, or mail

### Kentucky State Police (KSP)
- **Records**: (502) 782-1800
- **Address**: 919 Versailles Rd, Frankfort, KY 40601
- **Cost**: $8
- **Method**: Mail or online

### Jefferson County Sheriff
- **Records**: (502) 574-5400
- **Cost**: $10
- **Method**: In-person or mail

### Other Counties
- Contact local sheriff or police department
- Costs typically $5-15
- May require written request

---

## Information Needed to Order

### From Client/BuyCrash Slip
- [ ] Report number (e.g., "20-123456")
- [ ] Date of accident
- [ ] Location of accident
- [ ] Client's last name (for verification)

### If No Report Number
- Search by:
  - Client last name
  - Accident date
  - Accident location

---

## Request Letter Template (for direct requests)

```markdown
RE: Accident Report Request

Agency: {{agency_name}}
Date of Accident: {{accident_date}}
Location: {{accident_location}}
Parties Involved: {{client_name}}, {{other_party_name}}
Report Number (if known): {{report_number}}

Dear Records Department:

Please provide a copy of the above-referenced accident report.

Enclosed: Check for ${{amount}}

Please mail to:
{{law_firm_name}}
{{law_firm_address}}

Thank you,
{{attorney_name}}
```

---

## Processing After Receipt

### 1. Save Report
- File in: `/{{case_name}}/police_report/`
- Name: `police_report_{{date}}.pdf`

### 2. Extract Information
Use Police Report Analysis Skill:
- Accident details
- Party information
- Insurance companies
- Witness information
- Liability indicators

### 3. Update Case File
- Add insurance companies to insurance.json
- Add witnesses to contacts
- Note vehicle owner for PIP waterfall

---

## Common Issues

### Report Not Available Yet
- Reports may take 5-10 days to process
- Check back in a week

### Report Not Found
- Verify report number
- Try searching by name/date
- Contact agency directly

### Supplemental Reports
- Some accidents have supplements
- Request "all supplements" when ordering

