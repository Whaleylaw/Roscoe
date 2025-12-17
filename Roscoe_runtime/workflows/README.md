# Workflows Directory

This directory contains workflow documentation organized by case phase.

## Structure

```
workflows/
├── phase_0_onboarding/     # Case initialization workflows
├── phase_1_intake/         # Intake and file setup
├── phase_2_treatment/      # Treatment monitoring
├── phase_3_demand/         # Demand preparation
├── phase_4_negotiation/    # Settlement negotiation
├── phase_5_settlement/     # Settlement processing
└── phase_6_litigation/     # Litigation workflows
```

## Workflow Document Format

Each workflow document follows this structure:

```markdown
# Workflow: [Name]
## Phase: [phase_id]
## Goal: [What successful completion looks like]

## When to Trigger
- [Trigger condition 1]
- [Trigger condition 2]

## Inputs Required
- [Required input 1]
- [Required input 2]

## Step-by-Step Process
### Step 1: [Name]
[Instructions]

## Skills Used
- [skill_id]: [How it's used]

## Completion Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Outputs
- [Output file/artifact]

## Phase Exit Contribution
[How this workflow contributes to phase exit criteria]
```

## Workflow State

Each case maintains a `workflow_state.json` file tracking:
- Current phase
- Workflow completion status
- Exit criteria status
- Phase history

See `sample_workflow_state.json` for format example.

