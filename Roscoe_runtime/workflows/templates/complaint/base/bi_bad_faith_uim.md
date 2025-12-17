---
template_id: complaint_bi_bad_faith_uim
template_type: complaint
case_type: MVA - Bad Faith + UIM
counts_included:
  - Negligence
  - Underinsured Motorist (UIM)
  - Insurance Bad Faith (UCSPA)
context_type: litigation
auto_fill:
  - plaintiff.name
  - plaintiff.county
  - defendant.driver.name
  - defendant.driver.address
  - defendant.liability_carrier.name
  - defendant.uim_carrier.name
  - insurance.registered_agent
  - accident.date
  - firm.*
agent_fill:
  - Facts of accident
  - Specific negligent acts
  - Bad faith conduct by carrier(s)
  - UIM coverage details
---

# MVA Complaint with Bad Faith and UIM Coverage

## AGENT INSTRUCTIONS

This template combines three claims:
1. **Negligence** against the at-fault driver
2. **UIM Coverage** against plaintiff's UIM carrier
3. **Bad Faith** against one or both carriers

Use when:
- At-fault driver is underinsured
- Plaintiff has UIM coverage
- One or both carriers acting in bad faith
- Clear liability being disputed or unreasonable delay

**Note:** Bad faith can be alleged against:
- At-fault driver's liability carrier
- Plaintiff's UIM carrier
- Both carriers

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

*Service via [County] Sheriff:*
[defendant.driver.address]

**and**

**[defendant.liability_carrier.name]**

*Service via Registered Agent:*
[defendant.liability_carrier.registered_agent]
[defendant.liability_carrier.agent_address]

**and**

**[defendant.uim_carrier.name]**

*Service via Registered Agent:*
[defendant.uim_carrier.registered_agent]
[defendant.uim_carrier.agent_address]

DEFENDANTS

---

## COMPLAINT

---

Comes now the Plaintiff, [plaintiff.name], by counsel, and for Complaint against all Defendants states as follows:

### JURISDICTION AND VENUE

1. That Plaintiff, [plaintiff.name], is a resident of [plaintiff.county], Kentucky.

2. That Defendant, [defendant.driver.name], is a resident of [defendant.driver.county], Kentucky.

3. That Defendant, [defendant.liability_carrier.name], is an insurance company licensed to write insurance policies in the Commonwealth of Kentucky.

4. That Defendant, [defendant.uim_carrier.name], is an insurance company licensed to write insurance policies in the Commonwealth of Kentucky and is the underinsured motorist carrier for Plaintiff.

5. The motor vehicle collision giving rise to this action occurred on or about [accident.date] in [accident.county], Kentucky.

6. That the acts and omissions that form the basis of Plaintiff's complaint occurred in [accident.county], Kentucky.

7. That Plaintiff's claims against Defendants exceed the jurisdictional minimum of this Court.

### FACTS

8. On or about [accident.date], Plaintiff was [operating/occupying] a motor vehicle in [accident.county], Kentucky.

9. At the same time and place, Defendant, [defendant.driver.name], was operating a motor vehicle insured by Defendant, [defendant.liability_carrier.name].

10. [AGENT: Describe how the accident occurred]

11. At the time of the collision, Defendant, [defendant.driver.name], was underinsured, maintaining liability insurance with limits insufficient to compensate Plaintiff for damages sustained.

12. At the time of the collision, Plaintiff maintained underinsured motorist coverage with Defendant, [defendant.uim_carrier.name].

<!-- AGENT: Describe the bad faith conduct -->
13. [AGENT: Describe bad faith conduct - which carrier(s), what they did/failed to do]

### COUNT I: NEGLIGENCE - [defendant.driver.name]

14. Plaintiff re-alleges and incorporates paragraphs 1 through 13 as if fully set forth herein.

15. Defendant, [defendant.driver.name], owed a duty of care to Plaintiff to operate the motor vehicle in a safe and prudent manner.

16. Defendant, [defendant.driver.name], breached that duty by one or more of the following negligent acts or omissions:

    a. Failing to maintain a proper lookout;
    
    b. Failing to keep the vehicle under proper control;
    
    c. Operating the vehicle at an excessive rate of speed;
    
    d. Following too closely;
    
    e. Failing to yield the right of way;
    
    f. [AGENT: Add other specific negligent acts]

17. The negligent acts and omissions of Defendant were a substantial factor in causing the collision and Plaintiff's resulting injuries.

18. As a direct and proximate result of Defendant's negligence, Plaintiff has suffered one or more of the following damages:

    a. Temporary and permanent bodily injuries;
    
    b. Physical pain and mental suffering, past and future;
    
    c. Past medical expenses and future medical expenses;
    
    d. Lost wages and impairment of ability to labor and earn money;
    
    e. Loss of enjoyment of life;
    
    f. Increased risk of future harm.

### COUNT II: UNDERINSURED MOTORIST COVERAGE - [defendant.uim_carrier.name]

19. Plaintiff re-alleges and incorporates all preceding paragraphs as if fully set forth herein.

20. At the time of the collision, Plaintiff maintained a policy of insurance with Defendant, [defendant.uim_carrier.name], which included underinsured motorist coverage.

21. Defendant, [defendant.driver.name], was underinsured at the time of the collision, having liability limits of [AGENT: insert policy limits if known].

22. Plaintiff has complied with all conditions precedent to recovery under the UIM policy.

23. [defendant.uim_carrier.name] is obligated to pay underinsured motorist coverage to Plaintiff for all damages caused by [defendant.driver.name]'s negligence that exceed [defendant.driver.name]'s available liability coverage.

24. [defendant.uim_carrier.name] is liable to Plaintiff for medical expenses, pain and suffering, temporary and permanent impairment, loss of ability to labor and earn money, increased risk of future harm, and all other damages suffered in the collision.

### COUNT III: BAD FAITH - [defendant.liability_carrier.name]

25. Plaintiff re-alleges and incorporates all preceding paragraphs as if fully set forth herein.

26. Defendant, [defendant.liability_carrier.name], provided liability insurance coverage for Defendant, [defendant.driver.name].

27. Defendant, [defendant.liability_carrier.name], had a duty to deal with Plaintiff in good faith and to comply with the Unfair Claims Settlement Practices Act, KRS 304.12-230.

28. Defendant, [defendant.liability_carrier.name], violated KRS 304.12-230 by one or more of the following acts:

<!-- AGENT: Check applicable violations for liability carrier -->
    a. Not attempting in good faith to effectuate prompt, fair, and equitable settlements of claims in which liability has become reasonably clear;
    
    b. Compelling insureds to institute litigation to recover amounts due under an insurance policy;
    
    c. Failing to promptly provide a reasonable explanation for denial or delay;
    
    d. [AGENT: Add other specific violations]

29. [defendant.liability_carrier.name]'s conduct was willful, wanton, and in reckless disregard of Plaintiff's rights.

### COUNT IV: BAD FAITH - [defendant.uim_carrier.name]

30. Plaintiff re-alleges and incorporates all preceding paragraphs as if fully set forth herein.

31. Defendant, [defendant.uim_carrier.name], provided underinsured motorist coverage for Plaintiff.

32. Defendant, [defendant.uim_carrier.name], had a duty to deal with its insured, Plaintiff, in good faith and to comply with the Unfair Claims Settlement Practices Act, KRS 304.12-230.

33. Defendant, [defendant.uim_carrier.name], violated KRS 304.12-230 by one or more of the following acts:

<!-- AGENT: Check applicable violations for UIM carrier -->
    a. Failing to acknowledge and act reasonably and promptly upon Plaintiff's UIM claim;
    
    b. Refusing to pay the UIM claim without conducting a reasonable investigation;
    
    c. Not attempting in good faith to effectuate prompt, fair, and equitable settlement;
    
    d. Attempting to settle the claim for less than the amount to which a reasonable person would be entitled;
    
    e. Failing to provide a reasonable explanation for denial or delay;
    
    f. [AGENT: Add other specific violations]

34. [defendant.uim_carrier.name]'s conduct was willful, wanton, and in reckless disregard of Plaintiff's rights.

35. As a direct and proximate result of Defendants' bad faith, Plaintiff has suffered:

    a. Delay in receiving compensation for injuries;
    
    b. Additional costs in pursuing claims;
    
    c. Emotional distress and mental anguish;
    
    d. Attorney's fees and litigation costs.

---

## WHEREFORE

WHEREFORE, Plaintiff demands judgment against Defendants as follows:

**Against Defendant [defendant.driver.name]:**

1. Compensatory damages in an amount in excess of the jurisdictional limits of this Court;

**Against Defendant [defendant.uim_carrier.name]:**

2. Underinsured motorist coverage benefits in an amount in excess of the jurisdictional limits of this Court;

**Against Defendants [defendant.liability_carrier.name] and [defendant.uim_carrier.name]:**

3. Compensatory damages for bad faith;

4. Punitive damages for willful, wanton, and malicious conduct;

5. Attorney's fees and costs as authorized by law;

**Against All Defendants:**

6. Costs of this action;

7. Trial by jury on all issues so triable; and

8. All other relief to which Plaintiff may be entitled, including the right to amend this Complaint.

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

