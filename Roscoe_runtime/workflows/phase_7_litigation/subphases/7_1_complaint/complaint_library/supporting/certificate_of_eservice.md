---
template_id: certificate_of_eservice
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
  - Email addresses served
---

# Certificate of Electronic Service

## AGENT INSTRUCTIONS

This certificate is used when service is made electronically through the court's eFiling system or via email to parties enrolled in electronic service.

**Kentucky eFiling:** CourtNet 2.0 eFiling system automatically generates service notifications for enrolled parties.

**Use when:**
- All parties are enrolled in electronic filing
- Service via email is permitted by agreement or court order

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

## CERTIFICATE OF ELECTRONIC SERVICE

---

I hereby certify that on **[service.date]**, a true and correct copy of the foregoing **[document.name]** was served electronically via the Kentucky Court of Justice eFiling System (CourtNet 2.0) upon the following counsel of record who are registered users of the eFiling system:

<!-- AGENT: List each person served electronically -->

| Counsel | Firm | Email |
|---------|------|-------|
| [attorney1.name] | [attorney1.firm] | [attorney1.email] |
| [attorney2.name] | [attorney2.firm] | [attorney2.email] |

---

The Court's eFiling system will send automatic notification of this filing to all parties enrolled for electronic service.

---

_____________________________
[firm.attorney]
[firm.name]
[firm.address]
[firm.city], Kentucky [firm.zip]
Phone: [firm.phone]
[firm.bar_number]

*Counsel for Plaintiff*

---

## ALTERNATIVE: Email Service Certificate

If serving by email outside the eFiling system:

---

## CERTIFICATE OF SERVICE VIA EMAIL

---

I hereby certify that on **[service.date]**, a true and correct copy of the foregoing **[document.name]** was served via email upon the following:

| Counsel | Firm | Email Address |
|---------|------|---------------|
| [attorney1.name] | [attorney1.firm] | [attorney1.email] |
| [attorney2.name] | [attorney2.firm] | [attorney2.email] |

Service by email is authorized pursuant to [agreement of parties / Court Order dated ______].

---

_____________________________
[firm.attorney]

