---
template_id: complaint_premises_standard
template_type: complaint
case_type: Premises Liability
counts_included:
  - Negligence
context_type: litigation
auto_fill:
  - plaintiff.name
  - plaintiff.county
  - defendant.name
  - defendant.address
  - incident.date
  - incident.location
  - firm.*
agent_fill:
  - Description of dangerous condition
  - How injury occurred
  - Defendant's knowledge of condition
  - Injuries sustained
---

# Premises Liability Complaint - Standard

## AGENT INSTRUCTIONS

This template is for a standard premises liability complaint (slip/fall, dangerous condition). Use when:
- Injury occurred on defendant's property
- Caused by dangerous condition
- Defendant is private property owner/business
- NOT a government entity (use premises_government_entity.md)
- NOT an animal attack (use premises_dog_bite.md)

**Key Elements:**
1. Defendant owned/controlled premises
2. Dangerous condition existed
3. Defendant knew or should have known of condition
4. Defendant failed to warn or remedy
5. Condition caused plaintiff's injury

---

## CAPTION

**COMMONWEALTH OF KENTUCKY**
**[case.county] CIRCUIT COURT**

**CASE NO.:** [case.number]
**DIVISION:** [case.division]
**JUDGE:** [case.judge]

---

**[plaintiff.name]**
PLAINTIFF

**v.**

**[defendant.name]**

<!-- AGENT: For business entities, serve via registered agent -->
*Service via Registered Agent:*
[defendant.registered_agent]
[defendant.agent_address]

<!-- For individuals -->
*Service Address:*
[defendant.address]

DEFENDANT

---

## COMPLAINT

---

Comes now the Plaintiff, [plaintiff.name], by counsel, and for Complaint against Defendant, [defendant.name], states as follows:

### FACTUAL AND JURISDICTIONAL AVERMENTS

1. At the time of the injury on or about [incident.date], Plaintiff, [plaintiff.name], was a resident of [plaintiff.county], Kentucky.

2. At the time of the injury, Defendant, [defendant.name], owned, operated, managed, and/or controlled the premises located at [incident.location] in [incident.county], Kentucky.

3. The injury which is the subject of this Complaint occurred on the premises located at [incident.location] in [incident.county], Kentucky.

4. Plaintiff's damages exceed the jurisdictional minimum limit of this Court.

### FACTS

5. On or about [incident.date], Plaintiff was lawfully present on the premises located at [incident.location].

<!-- AGENT: Describe plaintiff's status -->
6. At the time of the incident, Plaintiff was [an invitee/a business invitee/a licensee] on Defendant's premises.

<!-- AGENT: Describe the dangerous condition -->
7. [AGENT: Describe the dangerous condition - e.g., "A hazardous accumulation of water/liquid on the floor," "A broken or uneven floor surface," "An unmarked step or elevation change," "Debris/obstruction in the walkway," etc.]

<!-- AGENT: Describe how injury occurred -->
8. [AGENT: Describe how the injury occurred - e.g., "Plaintiff slipped on the wet floor and fell," "Plaintiff tripped on the uneven surface and fell," etc.]

9. The dangerous condition that caused Plaintiff's injury was not open and obvious to Plaintiff.

### COUNT I: NEGLIGENCE

10. Plaintiff re-alleges and incorporates paragraphs 1 through 9 as if fully set forth herein.

11. Defendant, [defendant.name], had a duty to maintain its premises in a reasonably safe condition for persons lawfully present on the property.

12. Defendant, [defendant.name], had a duty to warn of dangerous conditions that were not open and obvious.

13. Defendant, [defendant.name], knew or should have known of the dangerous condition described herein.

<!-- AGENT: Select applicable allegations -->
14. Defendant, [defendant.name], breached its duty of care by one or more of the following negligent acts or omissions:

    a. Failing to maintain the premises in a reasonably safe condition;
    
    b. Failing to inspect the premises for dangerous conditions;
    
    c. Failing to remedy the dangerous condition within a reasonable time;
    
    d. Failing to warn of the dangerous condition;
    
    e. Allowing the dangerous condition to exist when Defendant knew or should have known of the hazard;
    
    f. Failing to have adequate policies and procedures for maintenance and inspection;
    
    g. [AGENT: Add other specific negligent acts]

15. Defendant had exclusive control and management of the premises and the condition that caused Plaintiff's injury.

16. Defendant's negligent acts and omissions were a substantial factor in causing Plaintiff's injuries.

17. As a direct and proximate result of Defendant's negligence, Plaintiff, [plaintiff.name], has suffered one or more of the following damages:

    a. Temporary and permanent bodily injuries;
    
    b. Physical pain and mental suffering, past and future;
    
    c. Past medical expenses and future medical expenses;
    
    d. Lost wages and impairment of ability to labor and earn money;
    
    e. Loss of enjoyment of life;
    
    f. Increased risk of future harm.

---

## WHEREFORE

WHEREFORE, Plaintiff, [plaintiff.name], prays for judgment against Defendant as follows:

A. Compensatory damages for past and future physical and mental suffering in an amount in excess of the jurisdictional limits of this Court;

B. Past, present, and future medical expenses necessitated by the injuries suffered;

C. Past, present, and future lost wages and impairment of ability to labor and earn money;

D. Damages for loss of enjoyment of life and increased risk of future injury;

E. Costs of this action;

F. Trial by jury on all issues so triable; and

G. All other just and proper relief to which Plaintiff may be entitled.

---

Respectfully submitted,

**[firm.name]**

_____________________________
[firm.attorney]
[firm.address]
[firm.city], Kentucky [firm.zip]
Phone: [firm.phone]
Fax: [firm.fax]
Email: [firm.email]

*Counsel for Plaintiff*

