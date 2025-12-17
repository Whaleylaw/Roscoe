# Red Flag Identification

## What Are Red Flags?

Red flags are issues in medical records that may affect case value, credibility, or liability. Document all red flags in chronology comments.

## Categories of Red Flags

### Treatment Gaps

| Gap Duration | Severity | Comment |
|--------------|----------|---------|
| 14-30 days | Minor | Note if unexpected |
| 30-60 days | Moderate | Document in comments |
| 60+ days | Significant | Flag for attorney review |

**Comment Format**:
```json
{
  "type": "red_flag",
  "category": "treatment_gap",
  "text": "Gap in treatment from 5/1/24 to 7/15/24 (75 days). No documented reason for gap."
}
```

### Inconsistent Histories

Watch for discrepancies in:
- Mechanism of injury (how accident happened)
- Symptoms reported
- Prior medical history
- Prior accidents/injuries

**Comment Format**:
```json
{
  "type": "red_flag",
  "category": "inconsistent_history",
  "text": "ER note states client 'rear-ended at stoplight' vs. PCP note stating 'T-bone collision at intersection.'"
}
```

### Pre-Existing Conditions

Document when records mention:
- Prior treatment for same body part
- Degenerative findings on imaging
- Previous accidents or injuries
- Chronic conditions affecting same area

**Comment Format**:
```json
{
  "type": "red_flag",
  "category": "preexisting",
  "text": "MRI shows 'moderate degenerative disc disease at L4-L5, may pre-date accident.'"
}
```

### Causation Issues

Flag when provider statements suggest:
- Injuries unrelated to accident
- Symptoms disproportionate to mechanism
- Malingering or exaggeration concerns
- Alternative causes for condition

**Comment Format**:
```json
{
  "type": "red_flag",
  "category": "causation",
  "text": "Dr. Smith notes 'findings may be consistent with age-related changes rather than acute injury.'"
}
```

### Compliance Issues

Document when records show:
- Missed appointments
- Non-compliance with treatment
- Failure to follow recommendations
- Early discharge against advice

**Comment Format**:
```json
{
  "type": "red_flag",
  "category": "compliance",
  "text": "Patient no-showed for 3 consecutive PT appointments (6/1, 6/8, 6/15)."
}
```

### Conflicting Diagnoses

Note when different providers reach different conclusions:
- Different diagnoses for same symptoms
- Disagreement on treatment necessity
- Conflicting imaging interpretations

**Comment Format**:
```json
{
  "type": "red_flag",
  "category": "conflicting_diagnosis",
  "text": "Orthopedist diagnoses 'cervical disc herniation' while neurologist states 'cervical strain only.'"
}
```

## Positive Indicators (Also Flag)

### Causation Statements

When providers positively link injuries to accident:

```json
{
  "type": "causation",
  "category": "positive",
  "text": "Dr. Jones: 'Patient's injuries are consistent with and causally related to the motor vehicle accident of 4/26/24.'"
}
```

### Treatment Necessity Statements

When providers document why treatment is needed:

```json
{
  "type": "causation",
  "category": "necessity",
  "text": "Dr. Smith: 'Surgery recommended due to failure of 6 months conservative care.'"
}
```

## Severity Ratings

| Rating | Definition | Action |
|--------|------------|--------|
| **Minor** | Explainable, may not affect case | Document only |
| **Moderate** | Needs explanation, may affect value | Flag for discussion |
| **Significant** | Seriously affects case | Immediate attorney attention |

## Documentation Template

For each red flag:

```json
{
  "type": "red_flag",
  "category": "[category]",
  "severity": "minor|moderate|significant",
  "text": "[Description of the issue]",
  "source_date": "MM/DD/YYYY",
  "source_provider": "Provider name",
  "page_number": "Reference"
}
```

