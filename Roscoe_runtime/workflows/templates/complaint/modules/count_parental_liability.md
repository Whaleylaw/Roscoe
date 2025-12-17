---
module_id: count_parental_liability
module_type: count
legal_theory: Parental Liability for Minor Driver
statutes:
  - KRS 186.590
---

# Count Module: Parental Liability (Minor Driver)

## Usage

Add this count when:
- At-fault driver is a minor (under 18)
- Parent signed minor's driver's license application
- Parent is owner of vehicle (additional theories may apply)

## Legal Basis

**KRS 186.590** - Parental Liability for Minor's Driving:

> Any negligence or wilful misconduct of a minor under the age of eighteen (18) years when driving a motor vehicle upon a highway shall be imputed to the person who has signed the application of such minor for an operator's license...

**Effect:** Parent who signed license application is jointly and severally liable for minor's negligence while driving.

## Prerequisites

- Must include negligence count against minor driver
- Must establish parent signed license application
- Minor must have been under 18 at time of accident

## Template

```markdown
### COUNT [N]: PARENTAL LIABILITY - [defendant.parent.name]

[Paragraph Number]. Plaintiff re-alleges and incorporates all preceding paragraphs as if fully set forth herein.

[Paragraph Number]. At the time of the collision, Defendant, [defendant.minor.name], was under the age of eighteen (18) years.

[Paragraph Number]. Defendant, [defendant.parent.name], signed the application for [defendant.minor.name]'s operator's license.

[Paragraph Number]. Pursuant to KRS 186.590, any negligence or willful misconduct of a minor under the age of eighteen when driving a motor vehicle upon a highway shall be imputed to the person who signed the application for such minor's operator's license.

[Paragraph Number]. Defendant, [defendant.parent.name], is therefore jointly and severally liable with [defendant.minor.name] for all damages caused by [defendant.minor.name]'s negligent operation of a motor vehicle.

[Paragraph Number]. As a direct and proximate result of [defendant.minor.name]'s negligence, for which [defendant.parent.name] is statutorily liable, Plaintiff has suffered the damages set forth herein.
```

---

## Additional Theories Against Parents

### Negligent Entrustment (If Parent is Owner)

If parent also owns the vehicle:

```markdown
[Paragraph Number]. In addition to statutory liability under KRS 186.590, Defendant, [defendant.parent.name], negligently entrusted the vehicle to [defendant.minor.name].

[Paragraph Number]. [defendant.parent.name] knew or should have known that [defendant.minor.name] was [inexperienced / had demonstrated reckless behavior / etc.].
```

### Negligent Supervision

If parent knew of prior dangerous behavior:

```markdown
[Paragraph Number]. Defendant, [defendant.parent.name], had a duty to reasonably supervise [defendant.minor.name]'s driving.

[Paragraph Number]. [defendant.parent.name] knew of [defendant.minor.name]'s propensity for [reckless driving / speeding / etc.] based on [prior incidents / warnings / etc.].

[Paragraph Number]. [defendant.parent.name] failed to take reasonable steps to prevent [defendant.minor.name] from driving in a dangerous manner.
```

---

## Defendant Naming

Name both minor and parent:

```markdown
**[defendant.minor.name], a minor**

*Service via [County] Sheriff:*
[defendant.minor.address]

**and**

**[defendant.parent.name], individually and as parent/guardian of [defendant.minor.name]**

*Service via [County] Sheriff:*
[defendant.parent.address]
```

---

## Prayer for Relief Addition

Add to Wherefore clause:

```markdown
[N]. Judgment against Defendants, [defendant.minor.name] and [defendant.parent.name], jointly and severally, for compensatory damages in an amount in excess of the jurisdictional limits of this Court;
```

---

## Evidence to Gather

- Minor's birth certificate (establish age)
- Driver's license application (who signed)
- Vehicle registration (establish ownership)
- Prior driving incidents
- School records (if relevant to supervision)
- Text messages/social media showing parent knowledge of dangerous driving

