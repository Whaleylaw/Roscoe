---
template_id: notice_to_bi_adjuster
template_type: notice
context_type: litigation
auto_fill:
  - client.name
  - firm.*
  - insurance.company
  - insurance.adjuster.name
  - insurance.adjuster.address
  - insurance.claim_number
  - case.number
  - case.county
agent_fill:
  - None (fully auto-filled)
---

# Notice of Lawsuit to Bodily Injury Adjuster

## AGENT INSTRUCTIONS

This notice must be sent to the BI adjuster when a lawsuit is filed. It serves to:
1. Inform the carrier of pending litigation
2. Provide case information
3. Request policy limits disclosure (if not already known)

Send via certified mail and retain proof of mailing.

---

## DOCUMENT

**[firm.name]**
[firm.address]
[firm.city], Kentucky [firm.zip]
Phone: [firm.phone] | Fax: [firm.fax]

---

**[date]**

**VIA CERTIFIED MAIL**

[insurance.adjuster.name]
[insurance.company]
[insurance.adjuster.address]

**RE:** Claimant: [client.name]
      Insured: [defendant.name]
      Claim No.: [insurance.claim_number]
      Date of Loss: [accident.date]
      **NOTICE OF LAWSUIT**

---

Dear [insurance.adjuster.name]:

Please be advised that we have filed suit on behalf of our client, [client.name], in the [case.county] Circuit Court, Commonwealth of Kentucky.

**Case Information:**
- **Case Number:** [case.number]
- **Court:** [case.county] Circuit Court
- **Plaintiff:** [client.name]
- **Defendant(s):** [defendant.name]

Enclosed please find a copy of the Complaint and Summons filed in this matter.

Please forward these documents to your legal department and/or assigned defense counsel immediately. If defense counsel has been assigned, please provide their contact information to our office.

Additionally, if you have not already done so, please provide confirmation of the liability policy limits available for your insured.

We remain willing to discuss settlement at any time prior to trial. Please feel free to contact our office.

Thank you for your attention to this matter.

Sincerely,

**[firm.name]**

_____________________________
[firm.attorney]
[firm.bar_number]

**Enclosures:**
- Complaint
- Summons

cc: [client.name] (via email)
    File

