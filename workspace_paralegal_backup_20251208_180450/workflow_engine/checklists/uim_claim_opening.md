# UM/UIM Claim Opening Checklist (Gap #7)

## Overview
Process for opening Uninsured/Underinsured Motorist claims on client's own policy.

---

## Existing Data Fields (insurance.json)
- `insurance_type` = "Uninsured/Underinsured Motorist (UM/UIM)"
- `claim_number`
- `insurance_company_name`
- `insurance_adjuster_name`
- `coverage_confirmation`
- `date_coots_letter_sent` - CRITICAL for UIM
- `date_coots_letter_acknowledged`

---

## UM vs UIM Determination

| Type | When to Open |
|------|--------------|
| **UM (Uninsured)** | At-fault driver has NO insurance |
| **UIM (Underinsured)** | At-fault driver has insurance but limits insufficient |

### UIM Timing
- Open AFTER BI claim exhausted or settled at limits
- Must send COOTS letter before settling BI

---

## UM Claim Process

### Step 1: Verify UM Coverage
- [ ] Client's dec page shows UM coverage
- [ ] Note UM limits

### Step 2: Open Claim
- [ ] Call client's insurance company
- [ ] Report accident under UM coverage
- [ ] Get claim number and adjuster

### Step 3: Send LOR
- [ ] Send Letter of Representation
- [ ] Request dec page confirmation

### Step 4: Track
- Update insurance.json with claim details
- Proceed like BI claim

---

## UIM Claim Process (More Complex)

### Step 1: Verify UIM Coverage
- [ ] Client's dec page shows UIM coverage
- [ ] Note UIM limits
- [ ] Confirm UIM limits exceed BI limits

### Step 2: COOTS Letter (CRITICAL)
**Before settling BI claim:**
- [ ] Send COOTS letter to UIM carrier
- [ ] Template: `/forms/insurance/UIM/coots_letter_TEMPLATE.md`
- [ ] Update `date_coots_letter_sent`
- [ ] Allow 30 days for response

### Step 3: COOTS Response Options

| Response | Meaning | Action |
|----------|---------|--------|
| **Consent** | OK to settle BI | Proceed with BI settlement |
| **Preserve Rights** | They may subrogate | Document, proceed |
| **Pay Limits** | UIM pays BI limits | Accept and open UIM claim |
| **No Response** | Consent implied | Document, proceed after 30 days |

### Step 4: After BI Settlement
- [ ] Open UIM claim formally
- [ ] Provide BI settlement docs to UIM
- [ ] Send demand to UIM carrier

---

## COOTS Letter Template

```markdown
RE: COOTS Notice - UIM Claim
    Client: {{client_name}}
    Claim: {{bi_claim_number}}
    At-Fault: {{at_fault_name}}
    BI Carrier: {{bi_carrier}}
    BI Limits: {{bi_limits}}

Dear UIM Carrier:

We represent {{client_name}} regarding injuries from
an accident on {{accident_date}}.

The at-fault party carries liability coverage of {{bi_limits}}
with {{bi_carrier}}.

We anticipate settling the BI claim at or near policy limits.
Pursuant to Coots v. Allstate, we are providing you notice
and the opportunity to:

1. Consent to settlement
2. Pay the BI limits and preserve subrogation rights
3. Object to settlement

Please respond within 30 days.

{{attorney_signature_block}}
```

---

## Key Dates to Track

| Field | Purpose |
|-------|---------|
| `date_coots_letter_sent` | When COOTS notice mailed |
| `date_coots_letter_acknowledged` | When carrier responded |
| `date_demand_sent` | When UIM demand sent |
| `date_demand_acknowledged` | When UIM demand acknowledged |

---

## Common Mistakes to Avoid

1. **Settling BI without COOTS** - May lose UIM claim
2. **Not waiting 30 days** - Allow response time
3. **Wrong coverage** - Verify UIM vs UM
4. **Missing dec page** - Always get client's dec page early

