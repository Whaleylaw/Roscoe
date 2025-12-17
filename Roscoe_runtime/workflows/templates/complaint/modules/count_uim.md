---
module_id: count_uim
module_type: count
legal_theory: Underinsured Motorist Coverage
statutes:
  - KRS 304.39-320
---

# Count Module: Underinsured Motorist (UIM) Coverage

## Usage

Add this count when:
- At-fault driver's insurance limits are insufficient to cover damages
- Plaintiff has UIM coverage through their own policy
- Plaintiff has complied with conditions precedent

## Prerequisites

- Must include negligence count against at-fault driver
- Must have UIM carrier named as defendant
- Verify UIM coverage exists and limits

## Template

```markdown
### COUNT [N]: UNDERINSURED MOTORIST COVERAGE

[Paragraph Number]. Plaintiff re-alleges and incorporates all preceding paragraphs as if fully set forth herein.

[Paragraph Number]. At the time of the collision, Plaintiff maintained a policy of insurance with Defendant, [insurance.company], Policy No. [policy.number], which included underinsured motorist coverage.

[Paragraph Number]. Defendant, [at_fault_driver.name], was underinsured at the time of the collision, maintaining liability insurance with [at_fault_carrier.name] with policy limits of [limits] which are insufficient to compensate Plaintiff for damages sustained.

[Paragraph Number]. Plaintiff has complied with all conditions precedent to recovery under the underinsured motorist coverage of the policy, including providing timely notice to [insurance.company].

[Paragraph Number]. Pursuant to KRS 304.39-320, [insurance.company] is obligated to pay underinsured motorist benefits to Plaintiff for all damages caused by the underinsured motorist's negligence that exceed the underinsured motorist's available liability coverage.

[Paragraph Number]. [insurance.company] is liable to Plaintiff for medical expenses, pain and suffering, temporary and permanent impairment, loss of ability to labor and earn money, increased risk of future harm, and all other damages suffered in the collision, to the extent such damages exceed the available liability coverage of the underinsured motorist.
```

---

## Service of Process

UIM carriers must be served via their registered agent in Kentucky:

```markdown
**[insurance.company]**

*Service via Registered Agent:*
[insurance.registered_agent]
[insurance.agent_address]
```

---

## Kentucky Legal Standards

**KRS 304.39-320:** Requires insurers to offer UIM coverage up to the liability limits of the policy.

**Conditions Precedent:**
- Timely notice to UIM carrier
- Policy in effect at time of accident
- Damages exceed at-fault driver's limits

**Important:** UIM coverage is subject to the terms of the policy. Review policy for:
- Coverage limits
- Notice requirements
- Consent to settle provisions
- Offset provisions

---

## Prayer for Relief Addition

Add to Wherefore clause:

```markdown
**Against Defendant [insurance.company]:**

[N]. Underinsured motorist coverage benefits in an amount in excess of the jurisdictional limits of this Court, including:

    a) Past and future medical expenses;
    
    b) Past and future lost wages;
    
    c) Past and future pain, suffering, and mental anguish;
    
    d) All other compensable damages under the policy;
```

