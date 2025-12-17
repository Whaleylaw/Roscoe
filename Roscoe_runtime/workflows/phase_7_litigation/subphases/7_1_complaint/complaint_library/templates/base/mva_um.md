---
template_id: complaint_mva_um
template_type: complaint
case_type: MVA
counts_included:
  - Negligence
  - Uninsured Motorist (UM)
context_type: litigation
auto_fill:
  - plaintiff.name
  - plaintiff.county
  - insurance.company
  - insurance.registered_agent
  - accident.date
  - firm.*
agent_fill:
  - Facts of accident
  - Description of at-fault driver (if known)
  - Injuries sustained
---

# MVA Complaint with Uninsured Motorist Coverage

## AGENT INSTRUCTIONS

This template is for an MVA complaint where the at-fault driver is uninsured or unknown (hit-and-run). Use when:
- At-fault driver has no insurance
- At-fault driver is unknown (hit-and-run)
- At-fault driver fled the scene
- Plaintiff has UM coverage

**Note:** If at-fault driver is unknown, include description of vehicle if available and serve via Warning Order Attorney.

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

<!-- AGENT: Use ONE of the following defendant formats -->

<!-- Option A: Known but uninsured driver -->
**[defendant.name]**

*Service Address:*
[defendant.address]

**and**

<!-- Option B: Unknown driver (hit-and-run) -->
**JOHN DOE, Unknown Driver**

*Service via Warning Order Attorney*

**and**

**[insurance.company]**

*Service via Registered Agent:*
[insurance.registered_agent]
[insurance.agent_address]

DEFENDANTS

---

## COMPLAINT

---

Comes now the Plaintiff, [plaintiff.name], by counsel, and for Complaint against Defendants states as follows:

### JURISDICTION AND VENUE

1. That Plaintiff, [plaintiff.name], is a resident of [plaintiff.county], Kentucky.

<!-- AGENT: Use appropriate paragraph based on known/unknown driver -->

<!-- For known driver: -->
2. That Defendant, [defendant.name], is believed to be a resident of [defendant.county], Kentucky, and was uninsured at the time of the collision.

<!-- For unknown driver: -->
2. That Defendant, John Doe, is an unknown driver who [fled the scene / caused the collision and left before identification could be made].

3. That Defendant, [insurance.company], is an insurance company authorized to write insurance policies within the Commonwealth of Kentucky and has written a policy of uninsured motorist coverage for the Plaintiff.

4. The motor vehicle collision giving rise to this action occurred on or about [accident.date] in [accident.county], Kentucky.

5. That the acts and omissions that form the basis of Plaintiff's complaint occurred in [accident.county], Kentucky.

6. That Plaintiff's claims against Defendants exceed the jurisdictional minimum of this Court.

### FACTS

7. On or about [accident.date], at approximately [accident.time], Plaintiff was [operating/occupying] a motor vehicle on [accident.location] in [accident.county], Kentucky.

8. At the same time and place, Defendant [defendant.name / John Doe] was operating a motor vehicle.

<!-- AGENT: For unknown driver, include any identifying information -->
9. [AGENT: Describe the accident and any known details about the at-fault vehicle/driver]

10. [AGENT: For unknown driver, describe efforts to identify the driver]

11. At the time of the collision, Defendant [defendant.name / John Doe] was uninsured, having no liability insurance policy in effect.

### COUNT I: NEGLIGENCE

12. Plaintiff re-alleges and incorporates paragraphs 1 through 11 as if fully set forth herein.

13. Defendant [defendant.name / John Doe] owed a duty of care to Plaintiff to operate the motor vehicle in a safe and prudent manner.

14. Defendant breached that duty by one or more of the following negligent acts or omissions:

<!-- AGENT: Check all that apply -->
    a. Failing to maintain a proper lookout;
    
    b. Failing to keep the vehicle under proper control;
    
    c. Operating the vehicle at an excessive rate of speed;
    
    d. Failing to yield the right of way;
    
    e. Failing to obey traffic control devices;
    
    f. Fleeing the scene of an accident;
    
    g. [AGENT: Add other specific negligent acts]

15. The negligent acts and omissions of Defendant were a substantial factor in causing the collision and Plaintiff's resulting injuries.

16. As a direct and proximate result of Defendant's negligence, Plaintiff has suffered one or more of the following damages:

    a. Temporary and permanent bodily injuries;
    
    b. Physical pain and mental suffering, past and future;
    
    c. Past medical expenses and future medical expenses;
    
    d. Lost wages and impairment of ability to labor and earn money;
    
    e. Loss of enjoyment of life;
    
    f. Increased risk of future harm.

### COUNT II: UNINSURED MOTORIST COVERAGE

17. Plaintiff re-alleges and incorporates all preceding paragraphs as if fully set forth herein.

18. At the time of the collision, Plaintiff maintained a policy of insurance with Defendant, [insurance.company], which included uninsured motorist coverage.

19. Defendant [defendant.name / John Doe] was uninsured at the time of the collision, and [insurance.company] is liable for uninsured motorist coverage benefits.

20. Plaintiff has complied with all conditions precedent to recovery under the UM policy.

21. [insurance.company] is obligated to pay uninsured motorist coverage to Plaintiff for all damages caused by the uninsured motorist's negligence.

22. [insurance.company] is liable to Plaintiff for medical expenses, pain and suffering, temporary and permanent impairment, loss of ability to labor and earn money, increased risk of future harm, and all other damages suffered in the collision.

---

## WHEREFORE

WHEREFORE, Plaintiff demands judgment against Defendants as follows:

**Against Defendant [defendant.name / John Doe]:**

1. Compensatory damages in an amount in excess of the jurisdictional limits of this Court;

**Against Defendant [insurance.company]:**

2. Uninsured motorist coverage benefits in an amount in excess of the jurisdictional limits of this Court, including:

    a) Past and future medical expenses;
    
    b) Past and future lost wages;
    
    c) Permanent impairment and loss of ability to labor and earn money;
    
    d) Past and future pain, suffering, and mental anguish;
    
    e) Pre-judgment and post-judgment interest;
    
    f) Loss of enjoyment of life and increased risk of future harm;

**Against All Defendants:**

3. Costs of this action;

4. Trial by jury on all issues so triable; and

5. All other relief to which Plaintiff may be entitled, including the right to amend this Complaint.

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

