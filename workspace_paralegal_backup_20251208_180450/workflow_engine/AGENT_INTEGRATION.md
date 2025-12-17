# Roscoe Workflow Engine - Agent Integration Guide

## Overview

This guide explains how the Roscoe agent should use the workflow engine to manage PI cases.

## Core Concept

The workflow engine is a **state machine** that tracks:
1. **Where the case is** (current phase)
2. **What's been done** (completed workflows/steps)
3. **What's waiting** (pending items with owners)
4. **What's next** (next actions, who owns them)

The agent uses this to:
- Answer status questions accurately
- Guide users through next steps
- Track manual actions the user completes
- Know when to prompt for missing information

## Key Principles

### 1. The Agent Guides, Users Execute (Often)

Many steps require human action (phone calls, DocuSign, mailing). The agent:
- Tells the user what needs to happen
- Provides instructions or templates
- Updates state when user confirms completion
- Follows up on pending items

```
Agent: "Next step is to open a BI claim with State Farm. 
        Call 1-800-STATE-FM, report the accident, and get a claim number. 
        Let me know when you've done this."

User: "Done. Claim number is 123456, adjuster is Bob Smith"

Agent: [Updates case state with claim info]
       "Got it. Claim opened. I've added Bob Smith as the adjuster. 
        Next, we need to send the Letter of Representation..."
```

### 2. State Is the Source of Truth

The case JSON file is the authoritative record. When the user asks "what's the status?", the agent reads the state and reports what it finds - it doesn't guess or make things up.

### 3. Clear Ownership of Actions

Every action has an owner:
- **agent**: Agent can do this (with or without tools)
- **user**: User/attorney must do this
- **client**: Waiting on client
- **external**: Waiting on insurance/provider/court

The agent clearly communicates who needs to do what.

### 4. Graceful Tool Absence

When a tool isn't available:
```
Agent: "I can help draft the demand letter, but I don't have 
        automated tools for this yet. Here's the manual process:
        
        1. Open the template at forms/demand_letter_template.docx
        2. Fill in the placeholders with case information
        3. Attach all medical records and bills
        4. Have the attorney review before sending
        
        Let me know when it's ready and I'll update the file."
```

## Common Scenarios

### Scenario 1: New Case

```
User: "New case - John Smith, car wreck on December 1st"

Agent: 
1. Creates new case state with case_id, client name, accident date
2. Sets current_phase = "file_setup"
3. Starts intake workflow

Response:
"Case created for John Smith.

I need some information to get started:
□ Client's phone and email
□ What happened in the accident?
□ What injuries does he have?
□ Where has he received medical treatment?

Please provide what you have."
```

### Scenario 2: Status Check

```
User: "What's the status of the Smith case?"

Agent reads case state, responds:

"**John Smith** - Case 2024-0042
Phase: File Setup (40% complete)

✅ Completed:
  - Client intake
  - Accident report obtained

⏳ Waiting on:
  - [client] Signed retainer (sent 12/5, BLOCKING)
  - [insurance] BI claim acknowledgment (opened 12/6)

📋 Next Actions:
  - [user] Follow up on retainer if not signed by 12/10
  - [user] Once retainer signed, send HIPAA for signature

Would you like me to draft a follow-up for the retainer?"
```

### Scenario 3: Document Provided

```
User: "Here's the police report for Smith" [attaches PDF]

Agent:
1. Processes PDF (if tool available) or asks for key info
2. Extracts: at-fault party, insurance, witnesses
3. Updates case state with extracted info
4. Triggers next workflow (open insurance claims)

Response:
"I've processed the police report. Found:
- At-fault: Jane Doe
- Her insurance: State Farm, Policy #SF-123
- Witness: Bob Wilson, 502-555-9999

Added to the file. 

Next steps:
□ Open BI claim with State Farm (call 1-800-782-8332)
□ Open PIP claim - need client's auto insurance info first

What's the client's auto insurance?"
```

### Scenario 4: User Completes Manual Step

```
User: "Opened the BI claim. Number is 2024-BI-789, 
       adjuster is Sarah Claims, sarah@statefarm.com"

Agent:
1. Updates insurance_claims array with new claim
2. Marks step complete
3. Adds pending item for acknowledgment
4. Identifies next action

Response:
"Got it. BI claim opened with State Farm.

I've recorded:
- Claim #: 2024-BI-789
- Adjuster: Sarah Claims (sarah@statefarm.com)

Next:
□ Send Letter of Representation to Sarah
□ Open PIP claim

Shall I prepare the LOR for State Farm?"
```

### Scenario 5: SOL Warning

```
Agent (automatically when case accessed):

"⚠️ **SOL Warning**

Case: John Smith
SOL Expires: 2026-01-15 (165 days remaining)

This case is entering the warning zone. Consider:
- Is the client done treating?
- Should we prepare a demand now?
- Is litigation likely?

Please advise on strategy."
```

## Integration with Existing Workflows

The workflow engine references the existing workflow files in `/workflows/`:

- `phase_1_intake/` → Maps to `file_setup` phase
- `phase_2_treatment/` → Maps to `treatment` phase
- `phase_3_demand/` → Maps to `demand_in_progress` phase
- etc.

When executing a workflow, the agent should also reference the detailed workflow file for procedural guidance while using the state machine for tracking.

## State Updates

### When to Update State

1. **After collecting information**: Update relevant fields
2. **After completing a step**: Mark step complete, check workflow completion
3. **After workflow completion**: Mark workflow complete, check phase completion
4. **After user confirms manual action**: Update relevant fields and step status
5. **When adding pending item**: Add to pending_items array
6. **When resolving pending item**: Add resolved_at timestamp

### What NOT to Update

- Don't mark things complete until actually done
- Don't advance phases until exit criteria met
- Don't assume actions happened without confirmation
- Don't overwrite user-provided data without reason

## Error Handling

### Missing Required Information

```
Agent: "I can't proceed with the demand because I'm missing:

Required:
□ Medical records from Norton Orthopedics
□ Final bills from University Hospital

Can you request these, or should I prepare the records requests?"
```

### Conflicting Information

```
Agent: "I notice the police report says the accident was on 12/1, 
        but the intake has 12/2. Which is correct? 
        
        I'll use the police report date (12/1) unless you tell me otherwise."
```

### Blocked Progress

```
Agent: "This case is blocked because the retainer hasn't been signed.

The client received the retainer on 12/5 (7 days ago).

Options:
1. Follow up with client
2. Close case due to no response

Which would you like to do?"
```

## Best Practices for Agent

1. **Always check state first** before answering status questions
2. **Be specific about owners** - who needs to do what
3. **Provide clear instructions** for manual steps
4. **Follow up on pending items** - remind about overdue items
5. **Explain blocking items** - why can't we proceed?
6. **Celebrate completions** - acknowledge when phases complete
7. **Watch for alerts** - SOL, no client contact, overdue items
8. **Don't make up information** - if not in state, ask or say unknown
