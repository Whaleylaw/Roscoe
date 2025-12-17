# Roscoe Workflow Engine

## Overview

The Roscoe Workflow Engine is a state machine-based system for tracking personal injury case progression. It guides users through the complete case lifecycle from intake through settlement or trial.

## Design Philosophy

1. **Agent as Guide**: The agent tells users what's needed next, processes what it can automatically, and clearly communicates when manual action is required.

2. **State Machine**: Cases progress through defined phases with clear entry/exit criteria. The engine tracks what's done, what's pending, and what's blocking.

3. **Graceful Degradation**: When tools aren't available for a step, the agent notes "waiting on [X] - manual action required" and continues tracking.

4. **User-Driven Progress**: Users provide information (documents, updates, decisions) and the agent processes and advances state accordingly.

## Directory Structure

```
workflow_engine/
├── README.md                    # This file
├── schemas/
│   ├── case_state.schema.json   # Master case state schema
│   ├── phase_definitions.json   # All phases with entry/exit criteria
│   ├── workflow_definitions.json # All workflows with steps
│   └── skill_definitions.json   # All skills with capabilities
├── orchestrator/
│   ├── state_machine.py         # Core state machine logic
│   ├── phase_manager.py         # Phase transition logic
│   ├── workflow_executor.py     # Workflow step execution
│   └── pending_tracker.py       # Tracks waiting/blocked items
├── templates/
│   ├── new_case_state.json      # Template for new cases
│   └── response_templates.md    # Agent response templates
└── gap_workflows/
    ├── file_setup/
    ├── treatment/
    ├── demand/
    ├── negotiation/
    └── settlement/
```

## How It Works

### 1. Case Initialization
```
User: "New case for John Smith, MVA on 12/1/2024"
Agent: Creates case_state.json, enters File Setup phase
       → "Case created. Starting intake workflow. I need:
          - Client contact information
          - Accident details
          - Known injuries
          - Insurance information (if known)
          Please provide what you have."
```

### 2. Progressive Information Gathering
```
User: [Provides client info and accident details]
Agent: Updates case_state.json
       → "Got it. I've recorded:
          - John Smith, 502-555-1234, john@email.com
          - MVA at 4th & Broadway, Louisville KY on 12/1/2024
          - Injuries: neck pain, back pain
          
          Next steps needed:
          □ Signed retainer agreement (manual: send via DocuSign)
          □ Signed HIPAA authorization (manual: send via DocuSign)
          □ Police report (manual: request from LMPD)
          
          Once you have the signed documents, let me know."
```

### 3. Processing User-Provided Documents
```
User: "Here's the police report" [attaches PDF]
Agent: Extracts information automatically
       → "I've processed the police report. Found:
          - At-fault party: Jane Doe
          - Her insurance: State Farm, Policy #SF123456
          - Witness: Bob Wilson, 502-555-9999
          
          I've added this to the file. Next steps:
          □ Open BI claim with State Farm (manual: call 800-STATE-FM)
          □ Open PIP claim with client's insurer (need: client's auto policy info)
          
          What's the client's auto insurance?"
```

### 4. Tracking What's Waiting
```
User: "What's the status of the Smith case?"
Agent: Reads case_state.json
       → "Smith v. Doe - File Setup Phase (60% complete)
          
          ✓ Completed:
            - Client intake
            - Accident report obtained
            - Insurance identified
          
          ⏳ Waiting on:
            - Signed retainer (sent 12/5, follow up 12/10)
            - BI claim acknowledgment (opened 12/6)
            - PIP claim opening (need client's policy number)
          
          🚫 Blocked:
            - Cannot proceed to Treatment phase until retainer signed
          
          Would you like me to draft a follow-up for the retainer?"
```

## State Machine Basics

### Phases (in order)
1. **File Setup** - Initial case setup, documents, insurance claims
2. **Treatment** - Monitoring medical care, gathering records
3. **Demand in Progress** - Assembling and sending demand
4. **Negotiation** - Back and forth with insurance
5. **Settlement** - Finalizing settlement, distribution
6. **Lien Phase** - Resolving outstanding liens (if needed)
7. **Complaint** - Filing suit (litigation track)
8. **Discovery** - Formal discovery process
9. **Mediation** - Settlement conference
10. **Trial Prep** - Preparing for trial
11. **Trial** - Conducting trial
12. **Closed/Archived** - Case complete

### Phase Transitions
- Each phase has **exit criteria** that must be met
- Some criteria are **hard blockers** (cannot proceed without)
- Some criteria are **soft blockers** (can proceed with attorney override)
- Phase transitions are logged with timestamps

### Workflow States
Each workflow step can be:
- `not_started` - Not yet begun
- `in_progress` - Currently being worked
- `waiting_on_user` - Needs user input/action
- `waiting_on_external` - Waiting for external party (insurance, provider, court)
- `completed` - Done
- `skipped` - Not applicable to this case
- `blocked` - Cannot proceed due to dependency

## Integration Points

### Existing Tools (from Tools/ directory)
- Calendar management (deadline tracking)
- Medical chronology generation
- Kentucky eCourts monitoring
- PDF processing
- UI components

### Manual Steps (agent guides user)
- DocuSign document sending
- Phone calls to insurance companies
- Letter mailing
- Court filings
- Check processing

### Future Integrations
- DocuSign API
- E-filing systems
- Insurance portals
- Medical records request services
