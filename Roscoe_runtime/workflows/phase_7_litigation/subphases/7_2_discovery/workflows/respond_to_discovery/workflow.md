---
name: respond_to_discovery
description: >
  Respond to defendant's written discovery requests. Reviews requests,
  gathers information, drafts responses and objections, prepares document
  production. Use when discovery received from defendant.
phase: 7.2_discovery
workflow_id: respond_to_discovery
related_skills:
  - discovery-response
library_reference: discovery_library/responding/
templates:
  - discovery_library/responding/templates/response_shell.md
  - discovery_library/responding/templates/general_objections.md
references:
  - discovery_library/responding/references/valid_objections.md
  - discovery_library/responding/references/privilege_log.md
  - discovery_library/responding/references/verification_page.md
---

# Respond to Discovery Workflow

## Overview

Prepare timely and complete responses to defendant's written discovery requests. Uses the Discovery Library for response templates and objection guidance.

## Entry Criteria

- Discovery requests received from defendant
- 30-day deadline approaching (45 days if served with complaint)

## Discovery Library Reference

**Primary Resources:**
- [Responding Decision Tree](../../discovery_library/responding/decision_tree.md) - Response strategy flowchart
- [Response Shell Template](../../discovery_library/responding/templates/response_shell.md) - Standard response format
- [Valid Objections Guide](../../discovery_library/responding/references/valid_objections.md) - When objections apply

## Steps

### 1. Calendar Deadline

**Owner:** Agent  
**Action:** Calculate and calendar response deadline.

| Situation | Deadline |
|-----------|----------|
| Served after answer filed | 30 days from service |
| Served with complaint | 45 days from service |
| Extension by agreement | Per stipulation |

**Warning:** Failure to respond to RFAs results in deemed admissions (CR 36.01).

### 2. Review Each Request

**Owner:** Agent  
**Skill:** `discovery-response`  
**Reference:** [Responding Decision Tree](../../discovery_library/responding/decision_tree.md)  
**Action:** For each request, determine:

| Question | If Yes |
|----------|--------|
| Is it understandable? | Proceed to next question |
| Is it objectionable? | Note objection type |
| Is it privileged? | Prepare privilege log |
| Can we respond? | Draft substantive response |

### 3. Identify Valid Objections

**Owner:** Agent  
**Reference:** [Valid Objections Guide](../../discovery_library/responding/references/valid_objections.md)  
**Action:** Review each request for valid objection grounds:

| Objection Type | When Valid |
|---------------|------------|
| Attorney-Client Privilege | Confidential attorney communications |
| Work Product | Documents prepared for litigation |
| Overbroad | Excessive scope or time period |
| Unduly Burdensome | Disproportionate effort required |
| Vague/Ambiguous | Cannot determine what is sought |
| Irrelevant | No connection to claims/defenses |

**Note:** Even if objecting, should respond to extent request is valid.

### 4. Gather Information

**Owner:** Agent/User  
**Action:** Collect information needed to respond:
- Client interview for factual questions
- Medical records and bills
- Employment/wage documentation
- Insurance information
- Other relevant documents

### 5. Draft Responses

**Owner:** Agent  
**Skill:** `discovery-response`  
**Template:** [Response Shell](../../discovery_library/responding/templates/response_shell.md)  
**Action:** Draft responses using library templates.

**Document Generation Pattern:**
```bash
# 1. Copy response shell to project
cp "../../discovery_library/responding/templates/response_shell.md" \
   "/{project}/Litigation/Discovery/Responses_to_Defendants_Discovery.md"

# 2. Agent fills responses for each request

# 3. Generate DOCX/PDF
python generate_document.py "/{project}/Litigation/Discovery/Responses_to_Defendants_Discovery.md"
```

**Response Format:**
```markdown
**INTERROGATORY NO. X:**
[Quote interrogatory]

**OBJECTION:** [If applicable - be specific]
[State specific objection with legal basis]

**ANSWER:**
Subject to and without waiving the foregoing objections, Plaintiff responds:
[Substantive response]
```

### 6. Prepare Document Production

**Owner:** Agent  
**Action:** Organize responsive documents:
- [ ] Identify all responsive documents
- [ ] Bates stamp if required
- [ ] Organize by request OR as maintained
- [ ] Create production log

### 7. Prepare Privilege Log (If Withholding Documents)

**Owner:** Agent  
**Reference:** [Privilege Log Template](../../discovery_library/responding/references/privilege_log.md)  
**Action:** If withholding documents on privilege, create log containing:
- Date of document
- Author and recipients
- Document type
- Subject matter (without revealing privileged content)
- Privilege asserted
- Basis for privilege

### 8. Attorney/Client Review

**Owner:** User  
**Action:** Review responses with client:
- [ ] Verify factual accuracy
- [ ] Client signs verification (required for interrogatories)
- [ ] Approve objections
- [ ] Confirm document production complete

### 9. Obtain Verification

**Owner:** User (Client must sign)  
**Reference:** [Verification Page Template](../../discovery_library/responding/references/verification_page.md)  
**Action:** Interrogatory responses MUST be verified under oath by the party.

```
VERIFICATION

I, [Client Name], verify that I am the Plaintiff in this action, that I have 
read the foregoing Responses to Defendant's Interrogatories, and that the 
answers are true and correct to the best of my knowledge, information, and belief.

_____________________________
[Client Name]

Subscribed and sworn before me this ___ day of _________, 20__.

_____________________________
Notary Public
```

### 10. Serve Responses

**Owner:** User  
**Action:** Serve responses and production timely:
- [ ] All responses served before deadline
- [ ] Documents produced or date set for production
- [ ] Verification attached to interrogatory responses
- [ ] Privilege log included (if claiming privilege)

## Exit Criteria

- [ ] Responses served within deadline
- [ ] Document production complete
- [ ] Privilege log provided (if withholding documents)
- [ ] Verification signed and attached

## Discovery Library Templates

### Response Templates
Location: `discovery_library/responding/templates/`

| Template | Purpose |
|----------|---------|
| `response_shell.md` | Standard response format with general objections |
| `general_objections.md` | Boilerplate objection language |

### Reference Materials
Location: `discovery_library/responding/references/`

| Reference | Purpose |
|-----------|---------|
| `valid_objections.md` | When each objection type applies |
| `privilege_log.md` | Template and guide for privilege logs |
| `verification_page.md` | Verification language and notarization |

## Common Pitfalls to Avoid

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Late responses | Objections waived | Calendar and track deadline |
| Missing verification | Invalid responses | Get client signature early |
| Boilerplate objections | May be deemed waived | Be specific for each request |
| No privilege log | Privilege may be waived | Create log for all withheld docs |
| Incomplete answers | Invites motion to compel | Answer completely subject to objection |

## Related Workflows

- **Triggered By:** Receipt of defendant's discovery
- **Related:** `propound_discovery` (our discovery to defendant)
- **May Trigger:** Motion practice if disputes arise
