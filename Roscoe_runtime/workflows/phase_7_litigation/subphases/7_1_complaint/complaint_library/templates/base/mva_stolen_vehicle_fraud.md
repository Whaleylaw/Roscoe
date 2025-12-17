---
template_id: complaint_mva_stolen_vehicle_fraud
template_type: complaint
case_type: MVA
counts_included:
  - Negligence
  - Fraud
  - Negligent Entrustment
context_type: litigation
auto_fill:
  - plaintiff.name
  - plaintiff.county
  - defendant.driver.name
  - defendant.owner.name
  - defendant.owner.address
  - insurance.company
  - accident.date
  - firm.*
agent_fill:
  - Facts of accident
  - Facts showing false stolen vehicle report
  - Relationship between owner and driver
  - Evidence of fraud
---

# MVA Complaint - Owner Reported Vehicle Stolen (Fraud)

## AGENT INSTRUCTIONS

This template is for an MVA complaint where the vehicle owner falsely reported the vehicle stolen to avoid liability. Use when:
- Driver fled the scene
- Owner filed false stolen vehicle report after accident
- Evidence suggests owner knew driver
- Owner attempting to avoid insurance liability

**Counts Included:**
1. Negligence (against driver)
2. Fraud (against owner for false report)
3. Negligent Entrustment (against owner)

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

**[defendant.driver.name]**

*Service via Jefferson County Sheriff:*
[defendant.driver.address]

**and**

**[defendant.owner.name]**

*Service via [Certified Mail / Jefferson County Sheriff]:*
[defendant.owner.address]

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

2. That Defendant, [defendant.driver.name], is believed to be a resident of [defendant.driver.county], Kentucky, and was operating a vehicle that struck the vehicle in which Plaintiff was [operating/occupying].

3. That Defendant, [defendant.owner.name], is a resident of [defendant.owner.county], Kentucky, and is the registered owner of the vehicle involved in the collision.

4. That Defendant, [insurance.company], had an insurance policy with coverage in effect covering the vehicle owned by [defendant.owner.name].

5. The motor vehicle collision giving rise to this action occurred on or about [accident.date] in [accident.county], Kentucky.

6. That the acts and omissions that form the basis of Plaintiff's complaint occurred in [accident.county], Kentucky.

7. That Plaintiff's claims against Defendants exceed the jurisdictional minimum of this Court.

### FACTS

8. On or about [accident.date], Plaintiff was [operating/occupying] a motor vehicle in [accident.county], Kentucky.

9. At the same time and place, Defendant, [defendant.driver.name], was operating a vehicle owned by and registered to Defendant, [defendant.owner.name], and insured by Defendant, [insurance.company].

10. [AGENT: Describe how the accident occurred]

11. Following the collision, Defendant, [defendant.driver.name], fled the scene.

12. Defendant, [defendant.owner.name], subsequently filed a false stolen vehicle report with law enforcement, claiming the vehicle had been stolen.

<!-- AGENT: Include facts from police report or investigation showing fraud -->
13. [AGENT: Describe evidence showing the stolen vehicle report was false - e.g., "The vehicle was a push-start vehicle that could not start without a key. Owner initially claimed to have only one set of keys, then changed story when confronted. No damage to ignition. Owner spoke to driver before filing report."]

### COUNT I: NEGLIGENCE - [defendant.driver.name]

14. Plaintiff re-alleges and incorporates paragraphs 1 through 13 as if fully set forth herein.

15. Defendant, [defendant.driver.name], owed a duty of care to Plaintiff to operate the motor vehicle in a safe and prudent manner.

16. Defendant, [defendant.driver.name], breached that duty by one or more of the following negligent acts or omissions:

    a. Failing to maintain a proper lookout;
    
    b. Failing to keep the vehicle under proper control;
    
    c. Operating the vehicle at an excessive rate of speed;
    
    d. Failing to yield the right of way;
    
    e. Fleeing the scene of an accident;
    
    f. [AGENT: Add other specific negligent acts]

17. The negligent acts and omissions of Defendant were a substantial factor in causing the collision and Plaintiff's resulting injuries.

18. As a direct and proximate result of Defendant's negligence, Plaintiff has suffered damages including temporary and permanent bodily injuries, physical pain and mental suffering, medical expenses, lost wages, and impairment of ability to labor and earn money.

19. Pursuant to KRS 304.39-060(2)(b), threshold requirements have been met by Plaintiff in that Plaintiff has incurred medical expenses exceeding $1,000.00 and/or sustained permanent injury.

### COUNT II: FRAUD - [defendant.owner.name]

20. Plaintiff re-alleges and incorporates all preceding paragraphs as if fully set forth herein.

21. Defendant, [defendant.owner.name], engaged in fraud in an attempt to avoid insurance liability to Plaintiff.

22. Defendant, [defendant.owner.name], knowingly provided false material representations regarding the whereabouts and driver of the vehicle involved in the collision.

23. Said false material representations were made with intent to deceive Plaintiff and [insurance.company].

24. Said false material representations led [insurance.company] to wrongly deny or delay coverage to Plaintiff.

25. Plaintiff reasonably relied on the false information provided to law enforcement and insurance in pursuing the claim.

26. As a result of Defendant, [defendant.owner.name]'s fraud, Plaintiff has suffered consequent and proximate injury, including delay in receiving compensation and additional costs in pursuing the claim.

27. Defendant, [defendant.owner.name]'s conduct was willful, wanton, and reckless, entitling Plaintiff to punitive damages above and beyond the special damages.

### COUNT III: NEGLIGENT ENTRUSTMENT - [defendant.owner.name]

28. Plaintiff re-alleges and incorporates all preceding paragraphs as if fully set forth herein.

29. At all relevant times, Defendant, [defendant.owner.name], was the owner of the vehicle involved in the collision.

30. Defendant, [defendant.owner.name], negligently and carelessly entrusted the vehicle to Defendant, [defendant.driver.name], whom [defendant.owner.name] knew or should have known would operate the vehicle in a careless manner.

31. [AGENT: Describe relationship between owner and driver and why owner knew or should have known of unfitness]

32. Defendant, [defendant.owner.name]'s negligent entrustment of the vehicle was a substantial factor in causing Plaintiff's injuries.

---

## WHEREFORE

WHEREFORE, Plaintiff demands judgment against Defendants as follows:

1. Judgment against Defendants, [defendant.driver.name], [defendant.owner.name], and [insurance.company], jointly and severally, in an amount in excess of the jurisdictional limits of this Court, including:

    a) Past and future medical expenses;
    
    b) Past and future lost wages;
    
    c) Permanent impairment and loss of ability to labor and earn money;
    
    d) Past and future pain, suffering, and mental anguish;
    
    e) Pre-judgment and post-judgment interest;

2. Punitive damages against Defendant, [defendant.owner.name], for fraud and willful misconduct;

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

