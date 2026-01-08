# New Entity Types - Complete List

**Date:** January 4, 2026
**Total New Entities:** 7 types

---

## 1. Facility (Medical)

**Purpose:** Medical facility or program - conceptual unit

**File:** graphiti_client.py line 228

**When to use:** Norton Orthopedic Institute, Baptist Medical Group, Starlite Chiropractic

**Key Fields:**
- `parent_system` - HealthSystem name or null (independent)
- `location_count` - Number of locations
- `facility_type` - hospital, clinic, imaging_center, urgent_care, chiropractic
- `specialty` - orthopedics, cardiology, primary_care
- `records_request_method` - mail, fax, portal, online
- `records_request_address` - Where to request records
- `billing_request_method` - How to request bills

**Relationships:**
- Facility -[:PART_OF]-> HealthSystem
- Location -[:PART_OF]-> Facility
- Client -[:TREATED_AT]-> Facility (when location unknown)
- Case -[:DEFENDANT]-> Facility (multi-role)
- Case -[:VENDOR_FOR]-> Facility (multi-role)

**Example:**
```json
{
  "name": "Norton Orthopedic Institute",
  "parent_system": "Norton Healthcare",
  "location_count": 19,
  "facility_type": "specialty_clinic",
  "specialty": "orthopedics"
}
```

---

## 2. Location (Medical)

**Purpose:** Specific physical location with street address

**File:** graphiti_client.py line 261

**When to use:** Norton Orthopedic Institute - Downtown (210 E Gray St)

**Key Fields:**
- `address` - Street address (REQUIRED)
- `city`, `state`, `zip` - Parsed address
- `phone`, `fax`, `email` - Contact info
- `parent_facility` - Facility name
- `parent_system` - HealthSystem name (reference)
- `location_type` - main_campus, satellite, department
- `records_request_method` - Rarely set (defers to parent)

**Relationships:**
- Location -[:PART_OF]-> Facility
- Client -[:TREATED_AT]-> Location (specific location known)
- Case -[:DEFENDANT]-> Location (multi-role)
- Doctor -[:WORKS_AT]-> Location
- MedicalVisit -[:AT_LOCATION]-> Location
- Document -[:FROM]-> Location

**Example:**
```json
{
  "name": "Norton Orthopedic Institute - Downtown",
  "address": "210 East Gray Street, Suite 604",
  "city": "Louisville",
  "state": "KY",
  "zip": "40202",
  "phone": "(502) 629-5633",
  "parent_facility": "Norton Orthopedic Institute",
  "parent_system": "Norton Healthcare"
}
```

---

## 3. InsurancePolicy

**Purpose:** Insurance policy providing coverage (separate from claims)

**File:** graphiti_client.py line 106

**When to use:** Client's State Farm auto policy, Defendant's Geico policy

**Key Fields:**
- `policy_number` - Policy ID (REQUIRED)
- `insurer_name` - Insurance company (REQUIRED)
- `policyholder_name` - Who owns policy (REQUIRED)
- `pip_limit`, `bi_limit`, `um_limit`, `uim_limit`, `medpay_limit` - Coverage limits
- `effective_date`, `expiration_date` - Policy dates
- `policy_type` - auto, health, workers_comp, homeowners, umbrella

**Relationships:**
- Client -[:HAS_POLICY]-> InsurancePolicy
- Defendant -[:HAS_POLICY]-> InsurancePolicy
- InsurancePolicy -[:WITH_INSURER]-> Insurer
- All claim types -[:UNDER_POLICY]-> InsurancePolicy

**Example:**
```json
{
  "policy_number": "12-345-6789",
  "insurer_name": "State Farm",
  "policyholder_name": "Amy Mills",
  "pip_limit": 10000.00,
  "bi_limit": 25000.00,
  "um_limit": 25000.00,
  "policy_type": "auto",
  "effective_date": "2024-01-01"
}
```

**Benefits:**
- One policy → multiple claim types (PIP + UM + UIM all from same policy)
- Track policy limits centrally
- Know when policies expire

---

## 4. InsurancePayment

**Purpose:** Track individual payments from insurers (PIP advances, BI settlements)

**File:** graphiti_client.py line 132

**When to use:** PIP advance, BI settlement check, MedPay payment

**Key Fields:**
- `payment_date` - Date received (REQUIRED)
- `amount` - Payment amount (REQUIRED)
- `payment_type` - partial, final, advance, medpay, pip, bi_settlement
- `check_number` - Check or transaction reference
- `for_medical_bills`, `for_settlement`, `for_lost_wages` - What payment is for

**Relationships:**
- All claim types -[:MADE_PAYMENT]-> InsurancePayment
- InsurancePayment -[:FROM]-> Insurer
- InsurancePayment -[:PAID_BILL]-> Bill

**Example:**
```json
{
  "payment_date": "2024-04-15",
  "amount": 2000.00,
  "payment_type": "advance",
  "check_number": "CHK-12345",
  "for_medical_bills": true
}
```

**Benefits:**
- Track PIP payment history (advance 1, 2, 3, final)
- Link payments to specific bills
- Payment reconciliation

---

## 5. MedicalVisit

**Purpose:** Individual medical visit/appointment by date for medical chronology

**File:** graphiti_client.py line 599

**When to use:** Each visit date in treatment timeline

**Key Fields:**
- `visit_date` - Date of visit (REQUIRED)
- `related_to_injury` - true/false (CRITICAL for lien negotiations)
- `unrelated_reason` - "cold", "routine checkup" (if unrelated)
- `diagnosis` - Chief complaint
- `treatment_type` - ER, surgery, follow-up, imaging, therapy
- `visit_number` - Sequential number

**Relationships:**
- Case -[:HAS_VISIT]-> MedicalVisit
- MedicalVisit -[:AT_LOCATION]-> Location/Facility
- MedicalVisit -[:HAS_BILL]-> Bill
- MedicalVisit -[:HAS_DOCUMENT]-> Document (PDF of records)
- MedicalVisit -[:SEEN_BY]-> Doctor

**Example:**
```json
{
  "visit_date": "2024-03-15",
  "related_to_injury": true,
  "diagnosis": "Knee injury follow-up",
  "treatment_type": "orthopedic consultation",
  "visit_number": 3
}
```

**Benefits:**
- Separate each visit date into own entity
- Flag unrelated visits for lien negotiations
- Link bills to specific visits
- Medical chronology organization

---

## 6. CourtEvent

**Purpose:** Track court hearings, trials, mediations, conferences

**File:** graphiti_client.py line 623

**When to use:** Any scheduled court event

**Key Fields:**
- `event_type` - hearing, trial, mediation, status_conference, pretrial, motion_hearing
- `event_date` - Date of event (REQUIRED)
- `event_time` - Time (e.g., "9:00 AM")
- `location` - Courtroom or location
- `virtual` - Whether remote
- `outcome` - continued, heard, settled, granted, denied
- `continued_to` - New date if continued

**Relationships:**
- Case -[:HAS_EVENT]-> CourtEvent
- CourtEvent -[:IN]-> Court/Division

**Example:**
```json
{
  "event_type": "motion_hearing",
  "event_date": "2025-06-15",
  "event_time": "9:00 AM",
  "location": "Courtroom 5A",
  "purpose": "Defendant's MSJ",
  "outcome": "denied"
}
```

**Benefits:**
- Calendar integration
- Track hearing outcomes
- Continuance tracking

---

## 7. LawFirmOffice

**Purpose:** Specific office/branch of multi-office law firm

**File:** graphiti_client.py line 491

**When to use:** Bryan Cave Louisville Office, Bryan Cave Lexington Office

**Key Fields:**
- `office_name` - Office identifier (REQUIRED)
- `parent_firm` - Law firm name (REQUIRED)
- `address` - Office address (REQUIRED)
- `city`, `state`, `zip` - Parsed address
- `phone`, `fax`, `email` - Office contact
- `office_type` - main, branch, satellite

**Relationships:**
- LawFirmOffice -[:PART_OF]-> LawFirm
- Attorney -[:WORKS_AT]-> LawFirmOffice
- CaseManager -[:WORKS_AT]-> LawFirmOffice

**Example:**
```json
{
  "office_name": "Louisville Office",
  "parent_firm": "Bryan Cave Leighton Paisner",
  "address": "500 W Jefferson St, Louisville, KY 40202",
  "office_type": "branch"
}
```

**Benefits:**
- Multi-office firm support
- Mirrors medical Facility/Location pattern
- Office-specific contact info

---

## Summary

**7 new entity types enable:**
- ✅ Three-tier medical provider hierarchy
- ✅ Multi-role entities (provider/defendant/vendor/expert)
- ✅ Progressive detail workflows
- ✅ Medical chronology with lien negotiation
- ✅ Insurance policy and payment tracking
- ✅ Court calendar and event tracking
- ✅ Multi-office law firm support

**All definitions in:** `src/roscoe/core/graphiti_client.py`

**All data ready in:** `schema-final/entities/` folder
