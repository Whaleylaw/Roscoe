# Demand Letter Narrative Sections

## Section 1: Introduction

**Purpose**: Establish representation and claim

**Template**:
```
Dear [Adjuster Name]:

This firm represents [Client Name] for injuries sustained in a [collision type] 
that occurred on [Date of Accident] in [City, County, Kentucky].

Your insured, [At-Fault Party Name], was the driver of the [Year Make Model] 
that [description of collision]. Claim Number: [Claim Number].
```

**Data Sources**:
- `overview.json`: client name, accident date, location
- `contacts.json`: at-fault party info
- `insurance.json`: claim number, adjuster name

---

## Section 2: Facts of Accident

**Purpose**: Establish what happened and who is at fault

**Structure**:
1. Date, time, location
2. Vehicles involved
3. What client was doing (lawfully proceeding)
4. What defendant did wrong
5. Impact and immediate aftermath

**Negligence Language**:
- "Failed to maintain proper lookout"
- "Failed to yield right of way"
- "Followed too closely"
- "Operated vehicle at unsafe speed"
- "Was distracted by [device/activity]"
- "Violated KRS [statute]"

**Sample Narrative**:
```
On [Date], at approximately [Time], our client was [lawfully proceeding/stopped] 
at [location]. Your insured, traveling [direction], [negligent act - failed to stop, 
ran red light, etc.] and struck our client's vehicle [impact location - rear end, 
driver's side, etc.].

The collision was entirely caused by your insured's negligence in:
1. [Primary negligent act]
2. [Secondary negligent act]
```

---

## Section 3: Injuries

**Purpose**: Document injuries caused by accident

**Organization**: List injuries in order of severity

**Format for Each Injury**:
```
[Body Part] - [Diagnosis (ICD-10 if available)]
  - Symptoms experienced
  - Treatment required
  - Current status/prognosis
```

**Sample**:
```
As a direct and proximate result of the collision, [Client] sustained the 
following injuries:

CERVICAL SPINE
- Cervical strain (ICD-10: S13.4XXA)
- Limited range of motion and persistent pain
- Required physical therapy and pain management
- Ongoing intermittent symptoms

LUMBAR SPINE  
- Lumbar radiculopathy (ICD-10: M54.16)
- Radiating pain to lower extremities
- Required epidural steroid injections
- Permanent structural changes on MRI
```

---

## Section 4: Treatment Narrative

**Purpose**: Summarize medical care chronologically

**Structure**:
1. Initial treatment (ER, urgent care)
2. Primary care evaluation
3. Specialist consultations
4. Ongoing treatment
5. Procedures performed
6. Current status

**Sample**:
```
TREATMENT SUMMARY

Following the collision, [Client] was transported to [Hospital] Emergency 
Department where [he/she] was evaluated and treated for [primary complaints]. 
X-rays revealed [findings].

[Client] subsequently came under the care of Dr. [Name], [specialty], who 
diagnosed [diagnoses] and recommended [treatment plan].

Treatment included:
- [Number] physical therapy sessions at [Provider]
- [Number] chiropractic treatments at [Provider]  
- MRI imaging showing [findings]
- [Number] epidural steroid injections at [Provider]

Treatment concluded on [date] with [outcome - MMI, discharged, etc.].
```

---

## Section 5: Demand & Closing

**Purpose**: State demand amount and response deadline

**Structure**:
1. Restate liability
2. Summarize damages
3. State demand
4. Set deadline
5. Closing

**Sample**:
```
DEMAND

Given the clear liability of your insured and the significant injuries, pain, 
and suffering endured by our client, we demand the sum of [AMOUNT] to fully 
and finally settle all claims arising from this incident.

This demand will remain open for thirty (30) days from the date of this letter. 
If we do not receive a response within this timeframe, we will assume [Carrier] 
is unwilling to negotiate in good faith and will proceed accordingly.

Please contact our office to discuss resolution of this claim.

Sincerely,

[Attorney Name]
[Firm Name]

Enclosures: [List exhibits]
```

---

## Tone Guidelines

**DO**:
- Be professional and factual
- Use specific dates and facts
- Reference medical records
- Acknowledge what client was doing lawfully
- Use clear liability language

**DON'T**:
- Be inflammatory or personal
- Exaggerate injuries or facts
- Include unsupported claims
- Use emotional language
- Attack the defendant personally

