---
template_id: certificate_of_service
template_type: certificate
context_type: litigation
auto_fill:
  - case.number
  - case.county
  - plaintiff.name
  - defendant.name
  - firm.*
agent_fill:
  - Documents served
  - Service method
  - Persons served
---

# Certificate of Service

## AGENT INSTRUCTIONS

This certificate is attached to filed documents to certify that copies have been served on all parties. 

**Use for:**
- Motions
- Discovery requests/responses
- Briefs
- Any filed document after initial complaint

**Service Methods:**
- First-class U.S. Mail
- Certified Mail
- Hand Delivery
- Electronic Service (if enrolled in electronic filing)

---

## DOCUMENT

**COMMONWEALTH OF KENTUCKY**
**[case.county] CIRCUIT COURT**

**CASE NO.:** [case.number]

---

**[plaintiff.name]**
PLAINTIFF

**v.**

**[defendant.name]**
DEFENDANT(S)

---

## CERTIFICATE OF SERVICE

---

I hereby certify that on **[service.date]**, a true and correct copy of the foregoing **[document.name]** was served upon the following by the method indicated:

<!-- AGENT: List each person served and method -->

**[recipient.name]**
[recipient.firm] (if applicable)
[recipient.address]
[recipient.city], [recipient.state] [recipient.zip]

[ ] First Class U.S. Mail, postage prepaid
[ ] Certified Mail, Return Receipt Requested
[ ] Hand Delivery
[ ] Facsimile to [fax.number]
[ ] Electronic Service via [eFiling system / email to [email.address]]

---

<!-- Additional recipients as needed -->

**[recipient2.name]**
[recipient2.firm] (if applicable)
[recipient2.address]
[recipient2.city], [recipient2.state] [recipient2.zip]

[ ] First Class U.S. Mail, postage prepaid
[ ] Certified Mail, Return Receipt Requested
[ ] Hand Delivery
[ ] Facsimile to [fax.number]
[ ] Electronic Service via [eFiling system / email to [email.address]]

---

_____________________________
[firm.attorney]
[firm.name]
[firm.address]
[firm.city], Kentucky [firm.zip]
Phone: [firm.phone]
[firm.bar_number]

*Counsel for Plaintiff*

