---
name: case_setup
description: >
  Creates the case folder structure and initializes all JSON tracking files.
  Triggered when user indicates a new case (e.g., "new client", "new file").
  Requires only 3 inputs: client name, case type, and accident date.
phase: onboarding
workflow_id: case_setup
related_skills: []
related_tools:
  - create_case.py
templates: []
---

# Case Setup Workflow

## Purpose

Create the complete case folder structure and initialize all JSON tracking files when a new case is opened. This is an automated process that requires minimal input.

---

## Trigger

This workflow is triggered when:
- User says "new client", "new file", "new case", or similar
- Agent recognizes intent to create a new case file

---

## Required Inputs

Gather exactly **3 pieces of information** from the user:

| # | Input | Format | Example | Purpose |
|---|-------|--------|---------|---------|
| 1 | Client Name | First Last | "John Doe" | Folder naming |
| 2 | Case Type | MVA / S&F / WC | "MVA" | Document selection, folder naming |
| 3 | Accident Date | MM-DD-YYYY | "01-15-2025" | Folder naming, SOL tracking |

### Case Types

| Code | Full Name | Description |
|------|-----------|-------------|
| MVA | Motor Vehicle Accident | Car accidents, motorcycle, truck, etc. |
| S&F | Slip and Fall | Premises liability, trip and fall |
| WC | Workers' Compensation | Workplace injuries |

---

## Steps

### Step 1: Recognize New Case Intent

**Trigger phrases to watch for:**
- "New client"
- "New file"
- "New case"
- "I just signed up [name]"
- "We have a new matter"
- "[Name] wants to hire us"

### Step 2: Gather Required Inputs

Ask the user for any missing information:

```
To set up the new case, I need:
1. Client's full name
2. Case type (MVA, S&F, or WC)
3. Date of the accident/incident (MM-DD-YYYY)
```

**Validation:**
- Client name: Must contain at least first and last name
- Case type: Must be one of: MVA, S&F, WC (case-insensitive)
- Date: Must be valid date in MM-DD-YYYY format

### Step 3: Run Create Case Tool

Execute `create_case.py` with the gathered inputs:

```python
result = create_case(
    client_name="John Doe",
    case_type="MVA",
    accident_date="01-15-2025"
)
```

**Tool Location:** `tools/create_case.py`

### Step 4: Confirm Success

Report to user:

```
Case folder created successfully:

📁 John-Doe-MVA-01-15-2025/
├── Case Information/ (with all JSON files initialized)
├── Client/
├── Insurance/
├── Medical Providers/
└── [other folders...]

Next step: Document Collection
```

### Step 5: Proceed to Document Collection

Automatically transition to `document_collection` workflow to begin gathering intake documents.

---

## Tool Reference

### create_case.py

**Location:** `workflows/case_setup/tools/create_case.py`

**Function Signature:**
```python
def create_case(client_name: str, case_type: str, accident_date: str) -> dict
```

**Parameters:**
| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| client_name | str | "John Doe" | Client's full name |
| case_type | str | "MVA" | One of: MVA, SF, WC |
| accident_date | str | "01-15-2025" | Date in MM-DD-YYYY format |

**Returns:**
```json
{
  "success": true,
  "case_path": "${ROSCOE_ROOT}/John-Doe-MVA-01-15-2025",
  "case_name": "John-Doe-MVA-01-15-2025",
  "next_workflow": "document_collection"
}
```

**What the tool creates:**

1. **Main folder:** `{Client-Name}-{CaseType}-{MM-DD-YYYY}/`

2. **Subfolders:**
   - `Case Information/`
   - `Client/`
   - `Expenses/`
   - `Insurance/BI/`, `Insurance/PIP/`
   - `Investigation/`
   - `Liens/`
   - `Litigation/` (with subfolders)
   - `Medical Providers/`
   - `Negotiation-Settlement/`
   - `Reports/`

3. **JSON Files in Case Information/:**
   - `overview.json` (pre-populated with client name, date, case type)
   - `contacts.json`
   - `expenses.json`
   - `insurance.json`
   - `liens.json`
   - `litigation.json`
   - `medical_providers.json`
   - `notes.json`
   - `pleadings.json`
   - `workflow_state.json` (initialized for Phase 0)

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Invalid case type | User entered something other than MVA/S&F/WC | Ask user to clarify case type |
| Invalid date format | Date not in MM-DD-YYYY format | Ask user to provide date correctly |
| Folder already exists | Case with same name exists | Confirm with user or add suffix |
| Permission error | Cannot write to projects folder | Report to user, check permissions |

---

## Output

**Deliverables:**
- Complete case folder structure created
- All JSON files initialized
- `workflow_state.json` set to Phase 0 with pending documents list

**Next Workflow:** `document_collection`

---

## Example Interaction

```
User: We have a new client, Jane Smith

Agent: Great! To set up the case file for Jane Smith, I need two more pieces of information:
       1. What type of case is this? (MVA, S&F, or WC)
       2. What was the date of the accident?

User: It's a car accident from December 5th

Agent: [Runs create_case.py with: "Jane Smith", "MVA", "12-05-2024"]

       Case folder created successfully!
       
       📁 Jane-Smith-MVA-12-05-2024/
       ├── Case Information/ (all tracking JSON initialized)
       ├── Client/
       ├── Insurance/
       ├── Medical Providers/
       └── ...
       
       Now let's collect the intake documents. I'll need:
       - New Client Information Sheet
       - Fee Agreement (MVA)
       - Medical Authorization (HIPAA)
       
       Would you like me to send a document request to the client, or do you have these ready?
```

