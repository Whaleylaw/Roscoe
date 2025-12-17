# Roscoe Agent Response Templates

These templates guide how the agent should respond to users during workflow execution.

## Status Inquiries

### "What's the status of [case]?"

```
**[Client Name]** - Case [ID]
Phase: [Phase Name] ([X]% complete)

[If alerts exist:]
⚠️ **Alerts:**
  🚨 [Critical alerts]
  ⚠️ [Warning alerts]

✅ **Completed:**
  - [Recent completed items, last 5]

⏳ **Waiting on:**
  - [owner] [description] (BLOCKING if applicable)

📋 **Next Actions:**
  - [owner] [description]
    📝 [prompt if applicable]
```

## New Case Creation

### "New case for [client name]"

```
Case created for [Client Name].

I need some information to get started:

**Basic Info Needed:**
□ Client's contact information (phone, email, address)
□ Date of the accident
□ What happened? (brief description)
□ What injuries does the client have?

**Also helpful to know:**
□ Where has the client received medical treatment?
□ Does the client have auto insurance?
□ Was a police report filed?

Please provide what you have, and I'll guide you through the rest.
```

## Document Processing

### When user provides police report

```
I've processed the police report. Here's what I found:

**Parties Identified:**
- At-fault: [Name]
- Insurance: [Company], Policy #[number]

**Witnesses:**
- [Name], [phone] (if available)

**Officer Notes:**
[Key notes from narrative]

I've added this information to the file.

**Next Steps:**
□ Open BI claim with [Insurance Company]
  → Manual: Call [phone], report accident, get claim #
□ Open PIP claim with [Client's insurer]
  → Manual: Call [phone], report accident, get claim #

Would you like me to prepare the Letters of Representation?
```

### When user provides medical records

```
I've processed the medical records from [Provider].

**Key Information:**
- Treatment dates: [first] to [last]
- Diagnoses: [ICD codes and descriptions]
- Treatments: [procedures, visits]
- Total billed: $[amount]

**Added to medical chronology.**

**Provider Status:** [Active/Complete]

[If treatment complete:]
Records and bills now available for demand package.

[If still treating:]
I'll request updated records once treatment completes.
```

## Waiting Notifications

### When waiting on user action

```
I'm ready to continue with [workflow], but I need you to:

**Action Required:**
[Description of what user needs to do]

[Specific instructions or template location if applicable]

Let me know when this is done, or if you need help with it.
```

### When waiting on external party

```
Currently waiting on: [party] for [item]

**Submitted:** [date]
**Typical wait time:** [X] days
**Follow-up date:** [date]

I'll remind you to follow up if we don't hear back by [date].
```

## Phase Transitions

### Completing a phase

```
✅ **[Phase Name] Complete!**

We've finished:
- [List of completed workflows]

**Moving to: [Next Phase Name]**

This phase involves:
- [Brief description of next phase]

**First steps:**
1. [First action needed]

Ready to continue?
```

## Error Handling

### When tool not available

```
I can help with [task], but I don't have automated tools for this step.

**Manual Process:**
[Step-by-step manual instructions]

[Template location if applicable]

Let me know when you've completed this, and I'll update the file.
```

### When missing required information

```
I can't proceed with [workflow] because I'm missing:

**Required:**
□ [Missing item 1]
□ [Missing item 2]

Can you provide this information?
```

## Client Communication Templates

### Check-in reminder

```
**Client Check-In Due**

It's been [X] days since the last check-in with [Client Name].

**Questions to ask:**
1. Are you still treating with your doctors?
2. Have you seen any new specialists?
3. Any new symptoms or changes?
4. Have you been able to return to work?
5. [Any case-specific follow-ups]

Would you like me to draft an email/text, or will you call them?
```

### Demand sent notification to client

```
**Template: Demand Sent Notification**

Subject: Update on Your Case - Demand Submitted

Dear [Client Name],

Good news! We've submitted our demand letter to [Insurance Company] today.

**What happens next:**
- The insurance company typically responds within 30 days
- They may make an offer, request more information, or deny the claim
- I'll contact you immediately when we hear back

**What you can do:**
- Continue following your doctor's treatment plan
- Let us know if anything changes with your health or situation
- Feel free to reach out with any questions

We'll be in touch soon.

Best regards,
[Firm Name]
```

## Settlement Processing

### Settlement reached

```
🎉 **Settlement Reached!**

**Details:**
- Settlement Amount: $[amount]
- Insurance: [Company]
- Claim #: [number]

**Breakdown (estimated):**
- Gross Settlement: $[amount]
- Attorney Fee ([X]%): $[fee]
- Case Expenses: $[expenses]
- Liens: $[liens]
- **Net to Client: $[net]**

**Next Steps:**
1. Prepare Authorization to Settle for client signature
2. Confirm settlement with adjuster
3. Receive and process release
4. Receive and deposit check
5. Pay liens and distribute funds

Ready to proceed?
```

## SOL Warnings

### Critical SOL (< 60 days)

```
🚨 **CRITICAL: STATUTE OF LIMITATIONS**

Case: [Client Name] - [ID]
SOL Expires: [Date] ([X] days remaining)

**IMMEDIATE ACTION REQUIRED:**
Either file suit OR decline representation.

There are NO exceptions to this rule.

**Options:**
1. File Complaint immediately
2. Decline case with written notification to client

Which would you like to proceed with?
```

### Warning SOL (< 180 days)

```
⚠️ **SOL Warning**

Case: [Client Name] - [ID]
SOL Expires: [Date] ([X] days remaining)

**Recommended Actions:**
- Evaluate case for immediate demand OR
- Prepare for litigation if no settlement likely

Please review and advise on strategy.
```
