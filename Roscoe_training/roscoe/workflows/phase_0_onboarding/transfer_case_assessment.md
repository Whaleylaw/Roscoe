# Workflow: Transfer Case Assessment

## Phase: onboarding
## Goal: Assess a case transferred from another attorney and set appropriate phase

---

## When to Trigger

- User indicates case is from another attorney
- Case files exist but show signs of prior representation
- Agent detects existing work product without workflow state

---

## Inputs Required

- Case folder path
- Prior attorney information (if available)
- Existing case files and documents
- Current status as understood by client

---

## Step-by-Step Process

### Step 1: Review Existing Documentation
1. Inventory all existing documents in case folder
2. Identify what work has been completed:
   - Signed contracts/authorizations?
   - Insurance claims opened?
   - Medical records collected?
   - Demand sent?
   - Litigation filed?

### Step 2: Determine Current Phase
Based on existing work, determine which phase the case is in:

| If These Exist | Phase |
|----------------|-------|
| Nothing/minimal | intake |
| Contracts, initial docs | intake (late) |
| Insurance setup, some records | treatment |
| Complete records, damages compiled | demand |
| Demand sent, offers received | negotiation |
| Settlement agreement | settlement |
| Complaint filed | litigation |

### Step 3: Identify Gaps
1. List what's missing for current phase
2. Identify incomplete workflows
3. Note any red flags or concerns

### Step 4: Create Transfer Assessment Report
Generate `transfer_assessment.md` documenting:
- Prior work summary
- Current phase determination
- Gaps identified
- Recommended next steps
- Concerns or issues

### Step 5: Create Workflow State
1. Create `workflow_state.json` with appropriate phase
2. Mark completed workflows as completed
3. Set exit criteria based on what's done

### Step 6: Review with Attorney
1. Present assessment to supervising attorney
2. Get approval on phase determination
3. Confirm priority tasks

---

## Skills Used

- **fact-investigation**: Review existing case materials
- **document-organization**: Inventory and organize transferred files
- **medical-record-extraction**: Review any existing medical records
- **insurance-coverage-analysis**: Review existing insurance work

---

## Completion Criteria

- [ ] All existing documents inventoried
- [ ] Current phase determined
- [ ] Gaps identified and documented
- [ ] `transfer_assessment.md` created
- [ ] `workflow_state.json` created with correct phase
- [ ] Attorney reviewed and approved

---

## Outputs

- `workflow_state.json` - Workflow tracking initialized to correct phase
- `transfer_assessment.md` - Detailed assessment of transferred case
- Updated `overview.json` with phase field

---

## Phase Exit Contribution

This workflow satisfies:
- `workflow_state_initialized`
- `case_type_determined`

Upon completion, the onboarding phase advances to the determined phase.

---

## Special Considerations

### Red Flags to Watch For
- Missing or incomplete contracts
- Statute of limitations concerns
- Prior attorney conflict issues
- Client expectations mismatch
- Outstanding liens from prior representation

### Documentation Requests
May need to request from prior attorney:
- Complete client file
- Trust account records
- Correspondence log
- Research and work product

