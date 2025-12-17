---
template_id: complaint_mva_uim
template_type: complaint
case_type: MVA
counts_included:
  - Negligence
  - Underinsured Motorist (UIM)
context_type: litigation
auto_fill:
  - plaintiff.name
  - plaintiff.county
  - defendant.name
  - defendant.address
  - insurance.company
  - insurance.registered_agent
  - accident.date
  - firm.*
agent_fill:
  - Facts of accident
  - Specific negligent acts
  - Injuries sustained
  - UIM coverage confirmation
---

# MVA Complaint with Underinsured Motorist Coverage

## AGENT INSTRUCTIONS

This template is for an MVA complaint where the at-fault driver's insurance is insufficient to cover damages. Use when:
- At-fault driver is insured but underinsured
- Plaintiff has UIM coverage
- Damages exceed at-fault driver's policy limits

**Required Information:**
- At-fault driver's policy limits
- Plaintiff's UIM carrier and policy information
- UIM policy limits

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

*Service Address:*
[defendant.address]

**and**

**[insurance.company]**

*Service via Registered Agent:*
[insurance.registered_agent]
[insurance.agent_address]

DEFENDANTS

---

## COMPLAINT

---

Comes now the Plaintiff, [plaintiff.name], by counsel, and for Complaint against Defendants, [defendant.name] and [insurance.company], states as follows:

### JURISDICTION AND VENUE

1. That Plaintiff, [plaintiff.name], is a resident of [plaintiff.county], Kentucky.

2. That Defendant, [defendant.name], is a resident of [defendant.county], Kentucky.

3. That Defendant, [insurance.company], is an insurance company authorized to write insurance policies within the Commonwealth of Kentucky and has written a policy of underinsured motorist coverage for the Plaintiff.

4. The motor vehicle collision giving rise to this action occurred on or about [accident.date] in [accident.county], Kentucky.

5. That the acts and omissions that form the basis of Plaintiff's complaint occurred in [accident.county], Kentucky.

6. That Plaintiff's claims against Defendants exceed the jurisdictional minimum of this Court.

### FACTS

7. On or about [accident.date], Plaintiff was [operating/occupying] a motor vehicle in [accident.county], Kentucky.

8. At the same time and place, Defendant, [defendant.name], was operating a motor vehicle.

9. [AGENT: Describe how the accident occurred]

10. At the time of the collision, Defendant, [defendant.name], was underinsured, maintaining an insurance policy that does not provide sufficient coverage to compensate Plaintiff for damages sustained.

### COUNT I: NEGLIGENCE

11. Plaintiff re-alleges and incorporates paragraphs 1 through 10 as if fully set forth herein.

12. Defendant, [defendant.name], owed a duty of care to Plaintiff to operate the motor vehicle in a safe and prudent manner.

13. Defendant, [defendant.name], breached that duty by one or more of the following negligent acts or omissions:

<!-- AGENT: Check all that apply -->
    a. Failing to maintain a proper lookout;
    
    b. Failing to keep the vehicle under proper control;
    
    c. Operating the vehicle at an excessive rate of speed;
    
    d. Following too closely;
    
    e. Failing to yield the right of way;
    
    f. Failing to obey traffic control devices;
    
    g. [AGENT: Add other specific negligent acts]

14. The negligent acts and omissions of Defendant, [defendant.name], were a substantial factor in causing the collision and Plaintiff's resulting injuries.

15. As a direct and proximate result of Defendant's negligence, Plaintiff has suffered one or more of the following damages:

    a. Temporary and permanent bodily injuries;
    
    b. Physical pain and mental suffering, past and future;
    
    c. Past medical expenses and future medical expenses;
    
    d. Lost wages and impairment of ability to labor and earn money;
    
    e. Loss of enjoyment of life;
    
    f. Increased risk of future harm.

### COUNT II: UNDERINSURED MOTORIST COVERAGE

16. Plaintiff re-alleges and incorporates all preceding paragraphs as if fully set forth herein.

17. At the time of the collision, Plaintiff maintained a policy of insurance with Defendant, [insurance.company], which included underinsured motorist coverage.

18. Defendant, [defendant.name], was underinsured at the time of the collision, and [insurance.company] is liable for underinsured motorist coverage benefits.

19. Plaintiff has complied with all conditions precedent to recovery under the UIM policy.

20. [insurance.company] is obligated to pay underinsured motorist coverage to Plaintiff for all damages caused by Defendant, [defendant.name]'s negligence that exceed [defendant.name]'s available liability coverage.

21. [insurance.company] is liable to Plaintiff for medical expenses, pain and suffering, temporary and permanent impairment, loss of ability to labor and earn money, increased risk of future harm, and all other damages suffered in the collision.

---

## WHEREFORE

WHEREFORE, Plaintiff demands judgment against Defendants as follows:

**Against Defendant [defendant.name]:**

1. Compensatory damages in an amount in excess of the jurisdictional limits of this Court, including:

    a) Past and future medical expenses;
    
    b) Past and future lost wages;
    
    c) Permanent impairment and loss of ability to labor and earn money;
    
    d) Past and future pain, suffering, and mental anguish;
    
    e) Pre-judgment and post-judgment interest;
    
    f) Loss of enjoyment of life and increased risk of future harm;

**Against Defendant [insurance.company]:**

2. Underinsured motorist coverage benefits in an amount in excess of the jurisdictional limits of this Court;

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

