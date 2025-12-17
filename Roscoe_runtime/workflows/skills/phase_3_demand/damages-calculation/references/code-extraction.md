# CPT/ICD Code Extraction Guide

## Overview

Medical bills contain CPT (procedure) and ICD (diagnosis) codes that document what was done and why. These codes strengthen the demand by showing specific medical interventions.

## Common Personal Injury CPT Codes

### Evaluation & Management (E/M)

| Code | Description | Typical Use |
|------|-------------|-------------|
| 99201-99205 | New patient office | Initial specialist visit |
| 99211-99215 | Established patient | Follow-up visits |
| 99281-99285 | Emergency room | ER visits (99284-85 = significant) |
| 99241-99245 | Consultation | Specialist consults |

### Physical Therapy

| Code | Description | Typical Use |
|------|-------------|-------------|
| 97110 | Therapeutic exercises | Strengthening, stretching |
| 97140 | Manual therapy | Hands-on treatment |
| 97530 | Therapeutic activities | Functional activities |
| 97112 | Neuromuscular reeducation | Balance, coordination |
| 97035 | Ultrasound | Soft tissue treatment |
| 97010 | Hot/cold packs | Adjunctive treatment |

### Injections

| Code | Description | Typical Use |
|------|-------------|-------------|
| 62322-62323 | Lumbar epidural | Low back injection |
| 62320-62321 | Cervical epidural | Neck injection |
| 64490-64495 | Facet joint | Spine facet blocks |
| 20610 | Large joint injection | Knee, shoulder |
| 20552-20553 | Trigger point | Muscle injections |

### Imaging

| Code | Description | Typical Use |
|------|-------------|-------------|
| 72141-72142 | MRI cervical spine | Neck MRI |
| 72146-72147 | MRI thoracic spine | Mid-back MRI |
| 72148-72149 | MRI lumbar spine | Low back MRI |
| 72100-72114 | Spine X-rays | Initial imaging |
| 70553 | MRI brain | TBI evaluation |
| 73721-73723 | MRI lower extremity | Knee, hip |

### Chiropractic

| Code | Description | Typical Use |
|------|-------------|-------------|
| 98940 | CMT 1-2 regions | Adjustment |
| 98941 | CMT 3-4 regions | Adjustment |
| 98942 | CMT 5 regions | Full spine |

---

## Common ICD-10 Codes

### Cervical Spine

| Code | Description |
|------|-------------|
| S13.4XXA | Cervical sprain (initial) |
| M54.2 | Cervicalgia (neck pain) |
| M50.1XX | Cervical disc disorder with radiculopathy |
| M54.12 | Cervical radiculopathy |

### Lumbar Spine

| Code | Description |
|------|-------------|
| S33.5XXA | Lumbar sprain (initial) |
| M54.5 | Low back pain |
| M51.16 | Lumbar disc disorder with radiculopathy |
| M54.16 | Lumbar radiculopathy |

### Thoracic Spine

| Code | Description |
|------|-------------|
| S23.3XXA | Thoracic sprain |
| M54.6 | Thoracic pain |
| M51.14 | Thoracic disc disorder |

### Head/Concussion

| Code | Description |
|------|-------------|
| S06.0XXA | Concussion (initial) |
| S06.0XXD | Concussion (subsequent) |
| G43.909 | Migraine, unspecified |
| R51 | Headache |

### Extremities

| Code | Description |
|------|-------------|
| S83.509A | Knee sprain |
| S93.409A | Ankle sprain |
| S43.409A | Shoulder sprain |
| M25.511-M25.579 | Joint pain by location |

---

## Extracting Codes from Bills

### Where to Find Codes

| Bill Type | Code Location |
|-----------|---------------|
| Hospital (UB-04) | Revenue codes, CPT in line items |
| Physician (CMS-1500) | Box 24D (CPT), Box 21 (ICD) |
| Itemized statement | Usually listed per service |

### If Codes Missing

1. Request itemized bill specifically
2. Request "superbill" or "encounter form"
3. Ask for UB-04 (hospital) or CMS-1500 (physician)

---

## Table Format for Demand

```
MEDICAL EXPENSES WITH PROCEDURE CODES

Provider         | Service              | CPT    | ICD        | Amount
-----------------|----------------------|--------|------------|--------
Norton ER        | ER Visit Level 4     | 99284  | S13.4XXA  | $1,200
Norton ER        | CT Cervical Spine    | 72125  | S13.4XXA  | $1,500
Dr. Smith Ortho  | New Patient Consult  | 99204  | M54.2     | $450
Dr. Smith Ortho  | Follow-up            | 99213  | M50.12    | $175
Louisville MRI   | MRI Cervical w/o     | 72141  | M50.12    | $1,800
Pain Management  | Cervical ESI         | 62321  | M50.12    | $2,500
ABC PT           | PT Evaluation        | 97161  | M54.2     | $200
ABC PT           | Therapeutic Ex (12u) | 97110  | M54.2     | $600
```

