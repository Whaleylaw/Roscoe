---
template_id: complaint_mva_standard
template_type: complaint
case_type: MVA
counts_included:
  - Negligence
context_type: litigation
auto_fill:
  - plaintiff.name
  - plaintiff.county
  - defendant.name
  - defendant.address
  - accident.date
  - accident.location
  - firm.*
agent_fill:
  - Facts of accident
  - Specific negligent acts
  - Injuries sustained
---

# Standard MVA Complaint - Negligence

## AGENT INSTRUCTIONS

This template is for a basic motor vehicle accident negligence complaint. Use when:
- Single at-fault driver
- Driver is adequately insured
- No vicarious liability or entrustment issues
- No bad faith by carrier

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
DEFENDANT

*Service Address:*
[defendant.address]

---

## COMPLAINT

---

Comes now the Plaintiff, [plaintiff.name], by counsel, and for Complaint against the Defendant, [defendant.name], states as follows:

### JURISDICTION AND VENUE

1. That Plaintiff, [plaintiff.name], is a resident of [plaintiff.county], Kentucky.

2. That Defendant, [defendant.name], is a resident of [defendant.county], Kentucky.

3. That the motor vehicle collision giving rise to this action occurred on or about [accident.date] in [accident.county], Kentucky.

4. That the acts and omissions that form the basis of Plaintiff's complaint occurred in [accident.county], Kentucky.

5. That Plaintiff's claims against Defendant exceed the jurisdictional minimum of this Court.

### FACTS

<!-- AGENT: Describe the accident facts here. Include:
- Time and location of accident
- What vehicles were involved
- How the accident occurred
- Weather/road conditions if relevant
-->

6. On or about [accident.date], at approximately [accident.time], Plaintiff was [operating/occupying] a motor vehicle on [accident.location] in [accident.county], Kentucky.

7. At the same time and place, Defendant, [defendant.name], was operating a motor vehicle.

8. [AGENT: Describe how the accident occurred - e.g., "Defendant failed to stop at a red light and struck Plaintiff's vehicle in the intersection" or "Defendant was following too closely and rear-ended Plaintiff's vehicle"]

### COUNT I: NEGLIGENCE

9. Plaintiff re-alleges and incorporates paragraphs 1 through 8 as if fully set forth herein.

10. Defendant, [defendant.name], owed a duty of care to Plaintiff to operate the motor vehicle in a safe and prudent manner.

11. Defendant breached that duty by one or more of the following negligent acts or omissions:

<!-- AGENT: Check all that apply and add specific facts -->
    a. Failing to maintain a proper lookout;
    
    b. Failing to keep the vehicle under proper control;
    
    c. Operating the vehicle at an excessive rate of speed;
    
    d. Following too closely;
    
    e. Failing to yield the right of way;
    
    f. Failing to obey traffic control devices;
    
    g. Driving while distracted;
    
    h. [AGENT: Add other specific negligent acts as applicable]

12. The negligent acts and omissions of Defendant were a substantial factor in causing the collision and Plaintiff's resulting injuries.

13. As a direct and proximate result of Defendant's negligence, Plaintiff has suffered one or more of the following damages:

    a. Temporary and permanent bodily injuries;
    
    b. Physical pain and mental suffering, past and future;
    
    c. Past medical expenses and future medical expenses;
    
    d. Lost wages and impairment of ability to labor and earn money;
    
    e. Loss of enjoyment of life;
    
    f. Increased risk of future harm.

14. Pursuant to KRS 304.39-060(2)(b), the threshold requirements have been met by Plaintiff in that Plaintiff has incurred medical expenses exceeding $1,000.00 and/or sustained permanent injury.

---

## WHEREFORE

WHEREFORE, Plaintiff demands judgment against Defendant as follows:

1. Compensatory damages in an amount in excess of the jurisdictional limits of this Court, to be determined by the evidence, including:

    a) Past and future medical expenses;
    
    b) Past and future lost wages;
    
    c) Permanent impairment and loss of ability to labor and earn money;
    
    d) Past and future pain, suffering, and mental anguish;
    
    e) Loss of enjoyment of life;
    
    f) Pre-judgment and post-judgment interest;

2. Costs of this action;

3. Trial by jury on all issues so triable; and

4. All other relief to which Plaintiff may be entitled, including the right to amend this Complaint.

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

