---
module_id: count_um
module_type: count
legal_theory: Uninsured Motorist Coverage
statutes:
  - KRS 304.39-320
---

# Count Module: Uninsured Motorist (UM) Coverage

## Usage

Add this count when:
- At-fault driver has no insurance
- At-fault driver is unknown (hit-and-run)
- At-fault driver fled the scene
- Plaintiff has UM coverage through their own policy

## Prerequisites

- Must include negligence count against at-fault driver (or John Doe if unknown)
- Must have UM carrier named as defendant
- For unknown drivers, include description of vehicle if available

## Template

```markdown
### COUNT [N]: UNINSURED MOTORIST COVERAGE

[Paragraph Number]. Plaintiff re-alleges and incorporates all preceding paragraphs as if fully set forth herein.

[Paragraph Number]. At the time of the collision, Plaintiff maintained a policy of insurance with Defendant, [insurance.company], Policy No. [policy.number], which included uninsured motorist coverage.

<!-- Option A: Known uninsured driver -->
[Paragraph Number]. Defendant, [at_fault_driver.name], was uninsured at the time of the collision, having no liability insurance policy in effect.

<!-- Option B: Unknown driver -->
[Paragraph Number]. Defendant, John Doe, was an unknown driver who [fled the scene / caused the collision and left before identification could be made]. Despite reasonable efforts, the identity of the driver remains unknown.

[Paragraph Number]. Plaintiff has complied with all conditions precedent to recovery under the uninsured motorist coverage of the policy, including providing timely notice to [insurance.company].

[Paragraph Number]. Pursuant to KRS 304.39-320, [insurance.company] is obligated to pay uninsured motorist benefits to Plaintiff for all damages caused by the uninsured motorist's negligence.

[Paragraph Number]. [insurance.company] is liable to Plaintiff for medical expenses, pain and suffering, temporary and permanent impairment, loss of ability to labor and earn money, increased risk of future harm, and all other damages suffered in the collision.
```

---

## Defendant Naming for Unknown Drivers

```markdown
**JOHN DOE, Unknown Driver of [vehicle description if known]**

*Service via Warning Order Attorney*
```

If any identifying information is available:
- Vehicle color, make, model
- Partial license plate
- Physical description of driver
- Direction of travel

---

## Kentucky Legal Standards

**KRS 304.39-320:** Requires insurers to include UM coverage unless rejected in writing.

**"Uninsured Motor Vehicle" Includes:**
- Vehicle with no liability insurance
- Vehicle with insurance company that becomes insolvent
- Hit-and-run vehicle where identity is unknown
- Stolen vehicle (owner's insurance may not apply)

**Phantom Vehicle Rule:** For hit-and-run claims, Kentucky generally requires physical contact with the unidentified vehicle OR independent corroborating evidence.

---

## Service on Unknown Defendant

Unknown defendants must be served via Warning Order Attorney:

1. File motion for Warning Order
2. Court appoints Warning Order Attorney
3. Attorney conducts due diligence search
4. Attorney files report
5. Service is complete upon expiration of warning order period

---

## Prayer for Relief Addition

Add to Wherefore clause:

```markdown
**Against Defendant [insurance.company]:**

[N]. Uninsured motorist coverage benefits in an amount in excess of the jurisdictional limits of this Court, including:

    a) Past and future medical expenses;
    
    b) Past and future lost wages;
    
    c) Past and future pain, suffering, and mental anguish;
    
    d) All other compensable damages under the policy;
```

