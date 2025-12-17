# BI Claim Opening Checklist

## When to Use
Use this checklist when opening a bodily injury (BI) claim against the at-fault party's insurance company. This is typically done during the File Setup phase after the client is signed.

---

## Pre-Send: Gather Information

### From Accident Report
- [ ] **At-fault driver's name**
- [ ] **At-fault driver's insurance company**
- [ ] **Policy number** (if listed)
- [ ] **Claim number** (if already assigned)
- [ ] **Date of accident**
- [ ] **Location of accident**

### Add to Case File
- [ ] **Update `insurance.json`** with at-fault party's insurer info:
  ```json
  {
    "bi_claim": {
      "insurer": "{{INSURER_NAME}}",
      "policy_number": "{{POLICY_NUMBER}}",
      "claim_number": "",
      "adjuster_name": "",
      "adjuster_phone": "",
      "adjuster_email": "",
      "lor_sent_date": "",
      "acknowledgment_received": false,
      "acknowledgment_type": "",
      "acknowledgment_date": "",
      "policy_limits": "",
      "dec_page_requested": false,
      "dec_page_received": false
    }
  }
  ```

---

## Send Documents

### 1. Letter of Representation (LOR)
**Template:** `/forms/insurance/BI/lor_to_bi_adjuster_TEMPLATE.md`

**Required placeholders:**
- `{{CLIENT_NAME}}` - Client's full name
- `{{DATE_OF_ACCIDENT}}` - Date of the accident
- `{{INSURER_NAME}}` - Insurance company name
- `{{INSURED_NAME}}` - At-fault party's name (their insured)
- `{{CLAIM_NUMBER}}` - If known, otherwise "To Be Assigned"
- `{{DATE}}` - Today's date

**Send via:**
- [ ] Mail (certified recommended)
- [ ] Fax (if available)
- [ ] Email (if adjuster email known)

**Record:**
- [ ] Date sent: `______________`
- [ ] Method: `______________`

### 2. Request Declaration Page
**Template:** `/forms/insurance/BI/request_dec_page_TEMPLATE.md`

*Can be sent with LOR or separately after claim number assigned*

- [ ] Dec page request sent
- [ ] Date sent: `______________`

---

## Track Acknowledgment

### What Counts as Acknowledgment
- Letter from insurance company confirming representation
- Phone call with adjuster (document date, time, name)
- Email from adjuster
- Claim number assignment letter

### Update Case File When Received
```json
{
  "acknowledgment_received": true,
  "acknowledgment_type": "letter|phone|email",
  "acknowledgment_date": "YYYY-MM-DD",
  "adjuster_name": "{{ADJUSTER_NAME}}",
  "adjuster_phone": "{{PHONE}}",
  "adjuster_email": "{{EMAIL}}",
  "claim_number": "{{CLAIM_NUMBER}}"
}
```

- [ ] **Acknowledgment received**
- [ ] **Date received:** `______________`
- [ ] **Type:** Letter / Phone / Email
- [ ] **Case file updated**

---

## Follow-Up Schedule

| Day | Action |
|-----|--------|
| Day 0 | Send LOR |
| Day 14 | If no acknowledgment, follow up by phone |
| Day 21 | If still no response, send second LOR (certified mail) |
| Day 30 | If no response, consider formal complaint to insurance commissioner |

### Follow-Up Notes
- [ ] 14-day follow-up completed: `______________`
- [ ] 21-day follow-up completed: `______________`
- [ ] Resolution: `______________`

---

## Adjuster Changes

**Important:** When you receive a letter indicating a new adjuster has been assigned:

1. **Do NOT just file it away**
2. **Update the case file** with new adjuster information:
   - Name
   - Phone
   - Email
   - Date of change
3. **Note the change** in case notes

### Adjuster Change Log
| Date | Old Adjuster | New Adjuster | Reason |
|------|--------------|--------------|--------|
| | | | |

---

## Common Issues

### No Response After 30 Days
1. Verify correct address/fax for claims department
2. Try contacting insurer's main claims line
3. File complaint with KY Department of Insurance if persistent

### Claim Number Not Assigned
- Some insurers don't assign until medical bills submitted
- Continue tracking by date of loss and insured's name

### Coverage Dispute
- Request written denial of coverage
- Investigate other potential coverage (UM/UIM)

---

## Templates Referenced

| Purpose | Template Path |
|---------|---------------|
| Letter of Representation | `/forms/insurance/BI/lor_to_bi_adjuster_TEMPLATE.md` |
| Declaration Page Request | `/forms/insurance/BI/request_dec_page_TEMPLATE.md` |

