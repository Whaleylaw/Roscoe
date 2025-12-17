# Litigation Tracking Guide

## Overview

**litigation.json** tracks litigation milestones and deadlines for the 43 cases in litigation phase.

## File Location

`${ROSCOE_ROOT}/Database/litigation.json`

## Structure

Array of litigation records, one per case:

```json
{
  "id": 3,
  "project_name": "Amy-Mills-Premise-04-26-2019",
  "client_name": "Amy Mills",
  "case_number": "20-CI-00456",
  "court": "Knox Circuit Court",
  "complaint_filed_date": "2020-04-26",
  "plaintiff_deposition_date": "2020-10-28",
  "mediation_date": "2022-03-11",
  "trial_date": "2024-09-15",
  ...
}
```

## Core Fields

### Case Information
- `id` - Unique record ID
- `project_name` - Case folder name (e.g., "Amy-Mills-Premise-04-26-2019")
- `client_name` - Client full name
- `case_number` - Court case number (e.g., "24-CI-12345")
- `court` - Court name (e.g., "Jefferson Circuit Court")
- `judge` - Assigned judge
- `opposing_counsel` - Defense attorney name
- `opposing_counsel_email` - Defense attorney email
- `opposing_counsel_phone` - Defense attorney phone

### Litigation Milestones

**Complaint/Answer**:
- `complaint_filed_date` - Date complaint/petition filed
- `complaint_served_date` - Date served on defendant
- `answer_filed_date` - Date defendant filed answer
- `answer_due_date` - Answer deadline

**Discovery - Plaintiff to Defendant**:
- `interrogatories_sent_to_defendant_date` - Date plaintiff sent interrogatories
- `requests_for_production_sent_to_defendant_date` - Date plaintiff sent RPD
- `defendant_reply_to_interrogatories_date` - Date defendant responded to interrogatories
- `defendant_reply_to_requests_for_production_date` - Date defendant responded to RPD

**Discovery - Defendant to Plaintiff**:
- `interrogatories_received_from_defendant_date` - Date defendant served interrogatories
- `requests_for_production_received_from_defendant_date` - Date defendant served RPD
- `plaintiff_reply_to_interrogatories_date` - Date plaintiff responded
- `plaintiff_reply_to_requests_for_production_date` - Date plaintiff responded

**Depositions**:
- `plaintiff_deposition_date` - Plaintiff deposition date
- `plaintiff_deposition_transcript_received` - true/false
- `defendant_deposition_date` - Defendant deposition date
- `defendant_deposition_transcript_received` - true/false
- `additional_depositions[]` - Array of other depositions (witnesses, experts)

**Deadlines**:
- `discovery_cutoff_date` - Discovery deadline
- `expert_designation_deadline` - Expert witness deadline
- `dispositive_motions_deadline` - Summary judgment deadline

**Mediation**:
- `mediation_scheduled` - true/false
- `mediation_date` - Scheduled date
- `mediation_completed` - true/false
- `mediation_result` - "settled", "impasse", "partial_settlement", "cancelled"

**Trial**:
- `trial_date` - Scheduled trial date
- `trial_continued_to` - New date if continued
- `pretrial_conference_date` - Pre-trial conference
- `next_court_date` - Next court appearance (any type)
- `next_court_date_purpose` - Purpose (e.g., "Status Conference", "Motion Hearing")

### Advanced Tracking

**Discovery Disputes** (`discovery_disputes[]`):
```json
{
  "dispute_type": "Motion to Compel",
  "filed_date": "2024-08-15",
  "status": "pending",
  "hearing_date": "2024-09-10",
  "resolution": null
}
```

**Motions Filed** (`motions_filed[]`):
```json
{
  "motion_type": "Motion for Summary Judgment",
  "filed_by": "defendant",
  "filed_date": "2024-07-01",
  "hearing_date": "2024-08-15",
  "ruling": "denied",
  "ruling_date": "2024-08-20"
}
```

**Settlement Offers** (`settlement_offers[]`):
```json
{
  "offer_date": "2024-06-15",
  "offered_by": "defendant",
  "amount": 75000,
  "response": "countered",
  "response_date": "2024-06-20"
}
```

## How to Update

### View All Litigation Cases

```bash
cat workspace_paralegal/Database/litigation.json | jq '.[] | {client: .client_name, case_number, trial_date, next_court_date}'
```

### Update a Specific Case

```bash
# Find Amy Mills record
cat workspace_paralegal/Database/litigation.json | jq '.[] | select(.client_name == "Amy Mills")'

# Update using jq (or edit file directly)
jq '(.[] | select(.project_name == "Amy-Mills-Premise-04-26-2019") | .complaint_filed_date) = "2020-04-26"' \
  workspace_paralegal/Database/litigation.json > temp.json && mv temp.json workspace_paralegal/Database/litigation.json
```

### Add New Litigation Case

If a case enters litigation phase after initial setup:

```bash
python3 initialize-litigation-tracking.py --project "New-Case-Name"
```

## Integration with Workflow State Computer

Once you add dates to litigation.json, update `workflow_state_computer.py` to derive litigation workflows:

```python
# In derive_workflow_completions():

# Load litigation data
litigation = case_data.litigation_data  # (need to add this to CaseData adapter)

if litigation:
    # === COMPLAINT ===
    if litigation.get("complaint_filed_date"):
        workflows["file_complaint"] = WorkflowStatus(
            workflow_id="file_complaint",
            phase="litigation",
            status="complete",
            details=f"Complaint filed {days_since(litigation['complaint_filed_date'])} days ago",
            linked_checklist="/workflow_engine/checklists/complaint_filing.md"
        )

    # === DISCOVERY ===
    if litigation.get("discovery_cutoff_date"):
        days_remaining = days_until(litigation["discovery_cutoff_date"])
        workflows["complete_discovery"] = WorkflowStatus(
            workflow_id="complete_discovery",
            phase="discovery",
            status="in_progress" if days_remaining > 0 else "complete",
            details=f"Discovery deadline: {days_remaining} days",
            linked_skill="/Skills/discovery/skill.md"
        )

    # === DEPOSITIONS ===
    if litigation.get("plaintiff_deposition_date"):
        workflows["plaintiff_deposition"] = WorkflowStatus(
            workflow_id="plaintiff_deposition",
            phase="discovery",
            status="complete",
            details=f"Plaintiff deposed on {litigation['plaintiff_deposition_date']}",
            linked_checklist="/workflow_engine/checklists/deposition_prep.md"
        )
```

## Querying Examples

### Cases with upcoming trial dates

```bash
cat workspace_paralegal/Database/litigation.json | jq '.[] | select(.trial_date != null) | {client: .client_name, trial_date, court}'
```

### Cases with overdue discovery

```bash
# Cases where discovery cutoff has passed
cat workspace_paralegal/Database/litigation.json | jq --arg today "$(date +%Y-%m-%d)" '.[] | select(.discovery_cutoff_date != null and .discovery_cutoff_date < $today)'
```

### Cases needing plaintiff depositions

```bash
cat workspace_paralegal/Database/litigation.json | jq '.[] | select(.plaintiff_deposition_date == null) | {client: .client_name, project: .project_name}'
```

## Next Steps

1. **Fill in known dates** for each litigation case by editing litigation.json
2. **Update CaseData adapter** to load litigation.json (in Tools/_adapters/case_data.py)
3. **Update workflow_state_computer.py** to derive litigation workflows from this data
4. **Upload to GCS** so production can use it:
   ```bash
   gcloud storage cp workspace_paralegal/Database/litigation.json gs://whaley_law_firm/Database/
   ```
