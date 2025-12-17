# Database Schema Updates

## Changes Made - December 8, 2024

### 1. case_overview.json - Added Fields

**New fields added to all 110 case records**:
- `case_number` - Court case number (e.g., "24-CI-12345")
- `court` - Court name (e.g., "Jefferson Circuit Court")

**Total fields**: 19 (was 17, now 19)

**Structure**:
```json
{
  "project_name": "Amy-Mills-Premise-04-26-2019",
  "client_name": "Amy Mills",
  "case_number": "",           // ← NEW
  "court": "",                  // ← NEW
  "phase": "Litigation",
  "case_summary": "...",
  "current_status": "...",
  "accident_date": "2019-04-26",
  "total_medical_bills": 123456.78,
  ...
}
```

**Usage**:
```bash
# Find all cases with court info
cat Database/case_overview.json | jq '.[] | select(.court != "") | {client_name, case_number, court}'

# Update a specific case
jq '(.[] | select(.client_name == "Amy Mills") | .case_number) = "20-CI-00456"' \
  Database/case_overview.json > temp.json && mv temp.json Database/case_overview.json
```

### 2. litigation.json - New File Created

**Purpose**: Dedicated litigation tracking for 43 cases in litigation phase

**Fields** (see litigation_schema.json for complete spec):
- Basic info: case_number, court, judge, opposing_counsel
- Complaint: filed_date, served_date, answer_filed_date
- Discovery: all interrogatory and RPD dates (sent/received/replied)
- Depositions: plaintiff, defendant, additional
- Deadlines: discovery_cutoff, expert_designation, dispositive_motions
- Mediation: date, status, outcome
- Trial: trial_date, continued_to, pretrial_conference
- Advanced: discovery_disputes[], motions_filed[], settlement_offers[]

**Total records**: 43

**Example**:
```json
{
  "id": 3,
  "project_name": "Amy-Mills-Premise-04-26-2019",
  "client_name": "Amy Mills",
  "case_number": "20-CI-00456",
  "court": "Knox Circuit Court",
  "complaint_filed_date": "2020-04-26",
  "interrogatories_sent_to_defendant_date": "2020-03-13",
  "plaintiff_deposition_date": "2020-10-28",
  "mediation_date": "2022-03-11",
  "trial_date": "2024-09-15",
  ...
}
```

### 3. Litigation Folder Structure - Added to Projects

**Structure added to all 131 project folders**:
```
Litigation/
├── Pleadings/
├── Discovery/
│   ├── Depositions/
│   └── Interrogatories/
├── Motions/
├── Experts/
├── Mediation/
└── Trial/
```

**Total folders created**: 1,048

## Files Modified

- ✅ `Database/case_overview.json` - Added case_number and court to all 110 cases
- ✅ `Database/litigation.json` - Created with 43 litigation case records
- ✅ `Database/litigation_schema.json` - JSON schema definition
- ✅ `Database/litigation_template.json` - Template for new cases
- ✅ All 131 project folders - Litigation subfolder structure

## Integration Status

### Current State
- ✅ Data structure created
- ✅ Folder structure created
- ⏳ Fields need population (case numbers, dates, court info)
- ⏳ CaseData adapter needs litigation.json integration
- ⏳ workflow_state_computer.py needs litigation workflow derivation

### Next Steps

1. **Populate litigation.json** with known dates for each case
2. **Update CaseData adapter** (Tools/_adapters/case_data.py) to load litigation.json
3. **Update workflow_state_computer.py** to derive litigation workflows
4. **Upload to GCS** when ready:
   ```bash
   gcloud storage cp Database/litigation.json gs://whaley_law_firm/Database/
   gcloud storage cp Database/case_overview.json gs://whaley_law_firm/Database/
   ```

## Tools Created

- `initialize-litigation-tracking.py` - Initialize litigation records
- `add-litigation-structure.py` - Create folder structure
- `add-litigation-fields-to-overview.py` - Add fields to case_overview
