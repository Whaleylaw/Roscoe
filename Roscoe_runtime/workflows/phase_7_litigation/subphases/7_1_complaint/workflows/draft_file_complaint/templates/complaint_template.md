---
template_id: complaint_mva
template_version: "1.0"
output_format: docx_and_pdf
auto_fields:
  - client.name
  - defendant.name
  - incidentDate
  - firm.attorney
  - firm.barNumber
  - firm.signature
  - firm.name
  - firm.address
  - firm.phone
agent_fields:
  - county
  - division
  - facts
  - venue_reason
  - negligent_acts
  - injuries
  - damages
---

# Complaint Template

## Instructions

<!-- 
Agent Instructions:
1. Copy this template to: /{project}/Litigation/Complaint.md
2. Fill in ALL bracketed fields below
3. Auto-fill fields ({{placeholder}}) will be replaced automatically
4. Save the file
5. Run: python generate_document.py "{path_to_saved_file}"
-->

Fill in bracketed fields with case-specific information. Auto-fill fields use {{placeholder}} syntax.

---

```
COMMONWEALTH OF KENTUCKY
[COUNTY] CIRCUIT COURT
DIVISION [DIVISION NUMBER]

CIVIL ACTION NO. ____________

{{client.name}},
                    PLAINTIFF,

v.

{{defendant.name}},
                    DEFENDANT.

* * * * * * * * * * * * * * * * * *

                COMPLAINT

* * * * * * * * * * * * * * * * * *

    Comes now the Plaintiff, {{client.name}}, by counsel, and for 
their Complaint against the Defendant states as follows:

                    JURISDICTION AND VENUE

    1. This Court has jurisdiction over this matter pursuant to 
KRS 23A.010.

    2. Venue is proper in [COUNTY] County pursuant to KRS 452.400 
because [SELECT: the cause of action arose in this county / the 
Defendant resides in this county / the Plaintiff resides in this 
county and Defendant is a non-resident].

                    PARTIES

    3. Plaintiff, {{client.name}}, is an adult individual residing 
at [CLIENT ADDRESS], in [CITY], [COUNTY] County, Kentucky.

    4. Defendant, {{defendant.name}}, is [SELECT: an adult individual 
residing at [DEFENDANT ADDRESS] / a [STATE] corporation authorized to do 
business in Kentucky with a registered agent at [DEFENDANT ADDRESS]].

                    FACTS

    5. On or about {{incidentDate}}, Plaintiff was [LOCATION/
ACTIVITY - e.g., "traveling westbound on Main Street in Louisville, 
Kentucky"].

    6. At that time, Defendant [DESCRIBE DEFENDANT'S CONDUCT - e.g., 
"was operating a motor vehicle traveling eastbound on Main Street"].

    7. [DESCRIBE HOW INCIDENT OCCURRED - e.g., "Defendant failed to 
yield the right of way and struck Plaintiff's vehicle"].

    8. [ADDITIONAL FACTS AS NECESSARY]

                    COUNT I
                    NEGLIGENCE

    9. Plaintiff incorporates by reference all preceding paragraphs 
as if fully set forth herein.

    10. At all times relevant hereto, Defendant owed a duty to 
Plaintiff to [DESCRIBE DUTY - e.g., "operate their motor vehicle in 
a safe and prudent manner in compliance with Kentucky traffic laws"].

    11. Defendant breached this duty by:
        a. [SPECIFIC NEGLIGENT ACT];
        b. [SPECIFIC NEGLIGENT ACT];
        c. [ADDITIONAL ACTS AS APPLICABLE].

    12. As a direct and proximate result of Defendant's negligence, 
Plaintiff suffered the following injuries and damages:
        a. Physical injuries including [LIST INJURIES];
        b. Pain and suffering, past and future;
        c. Medical expenses, past and future;
        d. Lost wages and earning capacity;
        e. [ADDITIONAL DAMAGES].

    13. Defendant's conduct was negligent under Kentucky law.

                    DAMAGES

    14. As a direct and proximate result of Defendant's negligence, 
Plaintiff has incurred and will continue to incur:
        a. Medical expenses in an amount to be proven at trial;
        b. Lost wages in an amount to be proven at trial;
        c. Pain and suffering in an amount to be proven at trial;
        d. [ADDITIONAL DAMAGES].

                    PRAYER FOR RELIEF

    WHEREFORE, Plaintiff respectfully prays that this Court:

    1. Enter judgment in favor of Plaintiff and against Defendant;
    2. Award Plaintiff compensatory damages in an amount to be 
       determined at trial;
    3. Award Plaintiff pre-judgment and post-judgment interest;
    4. Award Plaintiff costs of this action; and
    5. Grant all other relief to which Plaintiff may be entitled.

                    JURY DEMAND

    Plaintiff demands a trial by jury on all issues triable of right 
by a jury.

                    Respectfully submitted,

                    _________________________
                    {{firm.attorney}}
                    Kentucky Bar No. {{firm.barNumber}}
                    {{firm.name}}
                    {{firm.address}}
                    {{firm.city_state_zip}}
                    {{firm.phone}}
                    
                    Counsel for Plaintiff
```

---

## Field Reference

| Field | Type | Source |
|-------|------|--------|
| `{{client.name}}` | Auto | `overview.json` → client_name |
| `{{defendant.name}}` | Auto | `contacts.json` → liable party |
| `{{incidentDate}}` | Auto | `overview.json` → accident_date |
| `{{firm.attorney}}` | Auto | Firm config |
| `{{firm.barNumber}}` | Auto | Firm config |
| `{{firm.name}}` | Auto | Firm config |
| `{{firm.address}}` | Auto | Firm config |
| `{{firm.phone}}` | Auto | Firm config |
| `[COUNTY]` | Agent | Case venue decision |
| `[FACTS]` | Agent | Agent writes based on case |
| `[INJURIES]` | Agent | Medical chronology |
| `[NEGLIGENT ACTS]` | Agent | Agent analyzes |

## Usage

1. Agent copies this template to `/{project}/Litigation/Complaint.md`
2. Agent fills in all `[BRACKETED]` fields
3. Agent saves the file
4. Agent runs: `python generate_document.py "{path}"`
5. Tool auto-fills `{{placeholder}}` fields from case data
6. Tool generates `Complaint.docx` and `Complaint.pdf`

