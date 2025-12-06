# Workflow: Case Initialization

## Phase: onboarding
## Goal: Create workflow state file and set initial phase for a new case

---

## When to Trigger

- New case is created
- User mentions a case that has no `workflow_state.json`
- Agent detects case folder without workflow tracking

---

## Inputs Required

- Case folder path (from detected case context)
- Client name
- Case type (auto accident, slip and fall, etc.)
- Date of incident

---

## Step-by-Step Process

### Step 1: Verify Case Folder Structure
1. Check that case folder exists in `/projects/`
2. Verify basic folder structure is in place
3. If `workflow_state.json` already exists, skip to transfer assessment or exit

### Step 2: Determine Case Type
1. Ask user or infer from context:
   - Is this a brand new case?
   - Is this a case transferred from another attorney?
2. If transferred, switch to `transfer_case_assessment` workflow

### Step 3: Create Workflow State
1. Create `workflow_state.json` in case folder:
```json
{
  "current_phase": "intake",
  "case_type": "new",
  "initialized_at": "[current timestamp]",
  "phase_history": [
    {
      "phase": "intake",
      "started": "[current timestamp]",
      "completed": null
    }
  ],
  "workflows": {},
  "exit_criteria_status": {}
}
```

### Step 4: Verify Overview File
1. Check if `overview.json` exists
2. If not, prompt user to provide basic case information
3. Ensure `phase` field is set to "intake"

### Step 5: Confirm Initialization
1. Report to user that case is initialized
2. Suggest first workflow: `client_intake_screening`

---

## Skills Used

- **fact-investigation**: Gather initial case information
- **document-organization**: Set up case folder structure

---

## Completion Criteria

- [ ] `workflow_state.json` created in case folder
- [ ] `overview.json` has `phase` field set
- [ ] Case folder structure verified

---

## Outputs

- `workflow_state.json` - Workflow tracking file
- Updated `overview.json` with phase field

---

## Phase Exit Contribution

This workflow satisfies:
- `workflow_state_initialized`
- `case_type_determined`

Upon completion, the onboarding phase auto-advances to intake phase.

