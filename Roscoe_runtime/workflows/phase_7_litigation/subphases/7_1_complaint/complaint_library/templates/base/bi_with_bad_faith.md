---
template_id: complaint_bi_with_bad_faith
template_type: complaint
case_type: MVA - Bad Faith
counts_included:
  - Negligence
  - Insurance Bad Faith (UCSPA)
context_type: litigation
auto_fill:
  - plaintiff.name
  - plaintiff.county
  - defendant.driver.name
  - defendant.driver.address
  - insurance.company
  - insurance.registered_agent
  - accident.date
  - firm.*
agent_fill:
  - Facts of accident
  - Specific negligent acts
  - Bad faith conduct by carrier
  - Timeline of carrier conduct
---

# MVA Complaint with Insurance Bad Faith

## AGENT INSTRUCTIONS

This template is for an MVA complaint where the at-fault driver's insurance carrier has acted in bad faith. Use when:
- Clear liability on at-fault driver
- Carrier denied liability without reasonable basis
- Unreasonable delay in settlement
- Failure to make good faith settlement offer
- Unfair claims practices

**Legal Basis:**
- KRS 304.12-230 - Unfair Claims Settlement Practices Act (UCSPA)

**Bad Faith Elements:**
1. Insurer's obligation to pay (covered claim)
2. Insurer lacked reasonable basis to refuse payment
3. Insurer knew or recklessly disregarded lack of reasonable basis

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

**[insurance.company]**

*Service via Registered Agent:*
[insurance.registered_agent]
[insurance.agent_address]

DEFENDANTS

---

## COMPLAINT

---

Comes now the Plaintiff, [plaintiff.name], by counsel, and for Complaint against Defendants, [defendant.driver.name] and [insurance.company], states as follows:

### JURISDICTION AND VENUE

1. That Plaintiff, [plaintiff.name], is a resident of [plaintiff.county], Kentucky.

2. That Defendant, [defendant.driver.name], is a resident of [defendant.driver.county], Kentucky.

3. That Defendant, [insurance.company], is an insurance company licensed to write insurance policies in the Commonwealth of Kentucky and writing policies and conducting business therein.

4. The motor vehicle collision giving rise to this action occurred on or about [accident.date] in [accident.county], Kentucky.

5. That the acts and omissions that form the basis of Plaintiff's complaint occurred in [accident.county], Kentucky.

6. That Plaintiff's claims against Defendants exceed the jurisdictional minimum of this Court.

### FACTS

7. On or about [accident.date], Plaintiff was [operating/occupying] a motor vehicle in [accident.county], Kentucky.

8. At the same time and place, Defendant, [defendant.driver.name], was operating a motor vehicle insured by Defendant, [insurance.company].

9. [AGENT: Describe how the accident occurred]

10. Liability for this collision is clear and indisputable against Defendant, [defendant.driver.name].

<!-- AGENT: Describe the bad faith conduct -->
11. [AGENT: Describe the carrier's bad faith conduct - e.g., "Despite clear liability, [insurance.company] has denied the claim," "has unreasonably delayed settlement," "has refused to make a good faith settlement offer," etc.]

### COUNT I: NEGLIGENCE - [defendant.driver.name]

12. Plaintiff re-alleges and incorporates paragraphs 1 through 11 as if fully set forth herein.

13. Defendant, [defendant.driver.name], owed a duty of care to Plaintiff to operate the motor vehicle in a safe and prudent manner.

14. Defendant, [defendant.driver.name], breached that duty by one or more of the following negligent acts or omissions:

    a. Failing to maintain a proper lookout;
    
    b. Failing to keep the vehicle under proper control;
    
    c. Operating the vehicle at an excessive rate of speed;
    
    d. Following too closely;
    
    e. Failing to yield the right of way;
    
    f. [AGENT: Add other specific negligent acts]

15. The negligent acts and omissions of Defendant, [defendant.driver.name], were a substantial factor in causing the collision and Plaintiff's resulting injuries.

16. As a direct and proximate result of Defendant's negligence, Plaintiff has suffered one or more of the following damages:

    a. Temporary and permanent bodily injuries;
    
    b. Physical pain and mental suffering, past and future;
    
    c. Past medical expenses and future medical expenses;
    
    d. Lost wages and impairment of ability to labor and earn money;
    
    e. Loss of enjoyment of life;
    
    f. Increased risk of future harm.

### COUNT II: BAD FAITH - [insurance.company]

17. Plaintiff re-alleges and incorporates all preceding paragraphs as if fully set forth herein.

18. At the time of the collision, Defendant, [insurance.company], provided liability insurance coverage for Defendant, [defendant.driver.name].

19. Defendant, [insurance.company], is licensed to write motor vehicle insurance in the Commonwealth of Kentucky and is subject to KRS Chapter 304.

20. At all relevant times, [insurance.company] was subject to and required to comply with the Unfair Claims Settlement Practices Act, KRS 304.12-230.

21. Defendant, [insurance.company], had a duty to deal with Plaintiff in good faith and to comply with the Unfair Claims Settlement Practices Act.

22. Defendant, [insurance.company], violated KRS 304.12-230 by one or more of the following acts or omissions:

<!-- AGENT: Check all applicable violations -->
    a. Misrepresenting pertinent facts or insurance policy provisions relating to coverage at issue;
    
    b. Failing to acknowledge and act reasonably and promptly upon communications with respect to claims arising under insurance policies;
    
    c. Failing to adopt and implement reasonable standards for the prompt investigation of claims arising under insurance policies;
    
    d. Refusing to pay claims without conducting a reasonable investigation based upon all available information;
    
    e. Failing to affirm or deny coverage of claims within a reasonable time after proof of loss statements have been completed;
    
    f. Not attempting in good faith to effectuate prompt, fair, and equitable settlements of claims in which liability has become reasonably clear;
    
    g. Compelling insureds to institute litigation to recover amounts due under an insurance policy by offering substantially less than the amounts ultimately recovered in actions brought by such insureds;
    
    h. Attempting to settle a claim for less than the amount to which a reasonable person would have believed he was entitled;
    
    i. Failing to promptly provide a reasonable explanation of the basis in the insurance policy in relation to the facts or applicable law for denial of a claim or for the offer of a compromise settlement;
    
    j. [AGENT: Add other specific violations]

23. Defendant, [insurance.company]'s conduct was in reckless disregard of the rights of Plaintiff.

24. As a direct and proximate result of Defendant, [insurance.company]'s bad faith, Plaintiff has suffered consequent and proximate injury, including:

    a. Delay in receiving compensation for injuries;
    
    b. Additional costs in pursuing the claim;
    
    c. Emotional distress and mental anguish;
    
    d. Attorney's fees and litigation costs.

25. Defendant, [insurance.company]'s conduct was willful, wanton, and malicious, entitling Plaintiff to punitive damages.

---

## WHEREFORE

WHEREFORE, Plaintiff demands judgment against Defendants as follows:

**Against Defendant [defendant.driver.name]:**

1. Compensatory damages in an amount in excess of the jurisdictional limits of this Court, including:

    a) Past and future medical expenses;
    
    b) Past and future lost wages;
    
    c) Permanent impairment and loss of ability to labor and earn money;
    
    d) Past and future pain, suffering, and mental anguish;
    
    e) Pre-judgment and post-judgment interest;

**Against Defendant [insurance.company]:**

2. Compensatory damages for bad faith in an amount in excess of the jurisdictional limits of this Court;

3. Punitive damages for willful, wanton, and malicious conduct;

4. Attorney's fees and costs as authorized by law;

**Against All Defendants:**

5. Costs of this action;

6. Trial by jury on all issues so triable; and

7. All other relief to which Plaintiff may be entitled, including the right to amend this Complaint.

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

