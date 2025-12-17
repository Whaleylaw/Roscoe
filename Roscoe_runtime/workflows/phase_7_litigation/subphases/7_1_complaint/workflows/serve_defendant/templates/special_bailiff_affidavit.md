---
template_id: special_bailiff_affidavit
template_type: motion
context_type: litigation
auto_fill:
  - case.number
  - case.county
  - plaintiff.name
  - defendant.name
  - firm.*
agent_fill:
  - Prior service attempts
  - Reasons for failure
  - Requested Special Bailiff name
---

# Affidavit of Good Cause for Appointment of Special Bailiff

## AGENT INSTRUCTIONS

This affidavit supports a motion to appoint a Special Bailiff when regular service methods have failed. Document:
- All prior service attempts
- Why each attempt failed
- Why Special Bailiff is necessary

**File with:**
- Motion for Appointment of Special Bailiff
- Proposed Order Appointing Special Bailiff

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
DEFENDANT

---

## AFFIDAVIT OF GOOD CAUSE FOR APPOINTMENT OF SPECIAL BAILIFF

---

Commonwealth of Kentucky
County of [affiant.county]

I, [firm.attorney], being first duly sworn, state as follows:

1. I am counsel of record for Plaintiff, [plaintiff.name], in the above-captioned matter.

2. On [filing.date], a Complaint and Summons were filed in this matter against Defendant, [defendant.name].

3. The following attempts have been made to serve Defendant, [defendant.name]:

<!-- AGENT: List all service attempts chronologically -->

**Attempt 1:**
- Date: [attempt1.date]
- Method: [Sheriff service / Certified mail / etc.]
- Address: [attempt1.address]
- Result: [attempt1.result - e.g., "Unable to locate at address," "Defendant not home," "Refused to accept," etc.]

**Attempt 2:**
- Date: [attempt2.date]
- Method: [Sheriff service / Certified mail / etc.]
- Address: [attempt2.address]
- Result: [attempt2.result]

**Attempt 3:**
- Date: [attempt3.date]
- Method: [Sheriff service / Certified mail / etc.]
- Address: [attempt3.address]
- Result: [attempt3.result]

<!-- Add additional attempts as needed -->

4. Despite diligent efforts, service has not been accomplished on Defendant due to [AGENT: explain why - e.g., "Defendant appears to be actively avoiding service," "Defendant's work schedule makes Sheriff service difficult," "Defendant's residence is in a gated community that Sheriff cannot access," etc.].

5. Good cause exists for appointment of a Special Bailiff to effectuate service because:

<!-- AGENT: Select and customize applicable reasons -->

    a. Multiple attempts at service by the Jefferson County Sheriff have been unsuccessful;
    
    b. Defendant appears to be actively avoiding service of process;
    
    c. The Sheriff's office has limited hours and resources that make service at defendant's known locations difficult;
    
    d. A private process server will have greater flexibility in timing and methods to effectuate service;
    
    e. [Additional reason as applicable].

6. Plaintiff requests that [special_bailiff.name], be appointed as Special Bailiff to serve process upon Defendant, [defendant.name].

7. [special_bailiff.name] is over the age of eighteen (18) years and is not a party to this action.

---

FURTHER AFFIANT SAYETH NAUGHT.

_____________________________
[firm.attorney]

**SUBSCRIBED AND SWORN** to before me this _____ day of _____________, 20___.

_____________________________
Notary Public, State at Large
My Commission Expires: ___________

---

## CERTIFICATE OF SERVICE

I hereby certify that on [service.date], a copy of the foregoing was served upon:

[defendant.name]
[defendant.address]

via [first class mail / certified mail].

_____________________________
[firm.attorney]

