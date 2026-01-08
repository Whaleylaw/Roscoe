# Medical Chronology Support - Added to Schema ✅

**Date:** January 4, 2026
**Purpose:** Support date-by-date medical visit tracking with related/unrelated flagging for lien negotiations

---

## What Was Added

### 1. MedicalVisit Entity (NEW)

**Location:** `graphiti_client.py` line 599

**Purpose:** Track individual medical visits by date for chronology and lien negotiation

**Key Fields:**
```python
class MedicalVisit(BaseModel):
    visit_date: date  # REQUIRED - for chronology ordering

    # CRITICAL for lien negotiations
    related_to_injury: bool = True  # Flag for lien negotiations
    unrelated_reason: Optional[str]  # "cold", "routine checkup", etc.

    # Visit details
    diagnosis: Optional[str]
    treatment_type: Optional[str]
    visit_number: Optional[int]

    # For queries
    provider_name: Optional[str]
    doctor_name: Optional[str]

    # Metadata
    notes: Optional[str]
    duration_minutes: Optional[int]
    source: Optional[str]
    validation_state: Optional[str]
```

---

### 2. Updated Bill Relationships

**Added to EDGE_TYPE_MAP:**
```python
("Bill", "Location"): ["BilledBy"],   # NEW - bill from specific location
("Bill", "Facility"): ["BilledBy"],   # NEW - bill from facility
```

**Replaces:**
```python
("Bill", "MedicalProvider"): ["BilledBy"],  # DEPRECATED
```

---

### 3. New MedicalVisit Relationships

**Added complete section to EDGE_TYPE_MAP (line 1334):**
```python
("Case", "MedicalVisit"): ["HasVisit"],
("MedicalVisit", "Location"): ["AtLocation"],
("MedicalVisit", "Facility"): ["AtLocation"],
("MedicalVisit", "Bill"): ["HasBill"],
("MedicalVisit", "Document"): ["HasDocument"],
("MedicalVisit", "Doctor"): ["SeenBy"],
("Client", "MedicalVisit"): ["Had"],
```

---

### 4. Lien Payment Tracking

**Added:**
```python
("Lien", "Bill"): ["PaidBill"],  # Track what lien holder paid
```

**Enables:** Queries showing which bills were paid by lien holders

---

## How This Supports Your Workflow

### Workflow: Separate Each Visit Date into PDF

**For each date in medical records:**

1. **Create MedicalVisit entity**
```cypher
CREATE (visit:MedicalVisit {
  name: "Abby Sitgraves - Norton Ortho - 2024-03-15",
  visit_date: "2024-03-15",
  related_to_injury: true,  // ✅ or false if cold/unrelated
  diagnosis: "Knee injury follow-up",
  treatment_type: "orthopedic consultation",
  visit_number: 3
})
```

2. **Link to Location**
```cypher
MATCH (visit:MedicalVisit {name: "..."})
MATCH (loc:Location {name: "Norton Orthopedic Institute - Downtown"})
CREATE (visit)-[:AT_LOCATION]->(loc)
```

3. **Link to Bill**
```cypher
MATCH (visit:MedicalVisit {visit_date: "2024-03-15"})
CREATE (bill:Bill {
  name: "Norton Ortho - 2024-03-15",
  amount: 5000.00,
  bill_date: "2024-03-15"
})
CREATE (visit)-[:HAS_BILL]->(bill)
CREATE (bill)-[:BILLED_BY]->(loc:Location {name: "Norton Orthopedic Institute - Downtown"})
```

4. **Link to PDF Document**
```cypher
MATCH (visit:MedicalVisit {visit_date: "2024-03-15"})
CREATE (doc:Document {
  name: "norton_ortho_2024_03_15.pdf",
  document_type: "medical_visit",
  page_count: 15
})
CREATE (visit)-[:HAS_DOCUMENT]->(doc)
```

5. **Mark unrelated visits**
```cypher
// Cold visit at Norton ER
CREATE (visit:MedicalVisit {
  name: "Abby Sitgraves - Norton ER - 2024-04-20",
  visit_date: "2024-04-20",
  related_to_injury: false,  // ❌ NOT related
  unrelated_reason: "upper respiratory infection",
  diagnosis: "URI",
  treatment_type: "ER"
})
```

---

## Query Examples

### Q1: Total Medical Bills (Related Only)

```cypher
MATCH (case:Case {name: $case_name})
      -[:HAS_VISIT]->(visit:MedicalVisit {related_to_injury: true})
      -[:HAS_BILL]->(bill:Bill)

RETURN
  sum(bill.amount) as total_related_bills,
  count(visit) as related_visits
```

**Result:** $67,500 from 28 related visits (excludes 2 unrelated visits = $1,200)

---

### Q2: Show Unrelated Bills to Lien Holder

```cypher
MATCH (case:Case {name: $case_name})
      -[:HAS_VISIT]->(visit:MedicalVisit {related_to_injury: false})
      -[:HAS_BILL]->(bill:Bill)
      -[:BILLED_BY]->(provider)

OPTIONAL MATCH (provider)-[:PART_OF*]->(sys:HealthSystem)

RETURN
  visit.visit_date as date,
  provider.name as location,
  sys.name as health_system,
  visit.diagnosis as diagnosis,
  visit.unrelated_reason as reason,
  bill.amount as amount,
  'DO NOT REPAY LIEN FOR THIS' as status
ORDER BY visit.visit_date
```

**Use:** Show health plan these visits are unrelated, don't owe reimbursement

---

### Q3: Medical Chronology with Bills

```cypher
MATCH (case:Case {name: $case_name})
      -[:HAS_VISIT]->(visit:MedicalVisit)

OPTIONAL MATCH (visit)-[:AT_LOCATION]->(provider)
OPTIONAL MATCH (visit)-[:HAS_BILL]->(bill:Bill)
OPTIONAL MATCH (visit)-[:SEEN_BY]->(doctor:Doctor)
OPTIONAL MATCH (visit)-[:HAS_DOCUMENT]->(doc:Document)

RETURN
  visit.visit_date as date,
  provider.name as location,
  doctor.name as physician,
  visit.diagnosis as diagnosis,
  visit.related_to_injury as related,
  bill.amount as billed,
  doc.name as pdf_file
ORDER BY visit.visit_date
```

**Result:** Complete chronology showing every visit with bills and relatedness

---

### Q4: Bills Paid by Lien vs What We Owe Back

```cypher
MATCH (case:Case {name: $case_name})
      -[:HAS_LIEN]->(lien:Lien)

// Find what lien holder paid
MATCH (lien)-[:PAID_BILL]->(bill:Bill)

// Get the visit for this bill
MATCH (visit:MedicalVisit)-[:HAS_BILL]->(bill)

RETURN
  sum(bill.amount) as total_lien_paid,
  sum(CASE WHEN visit.related_to_injury THEN bill.amount ELSE 0 END) as amount_we_owe_back,
  sum(CASE WHEN NOT visit.related_to_injury THEN bill.amount ELSE 0 END) as unrelated_amount_to_exclude
```

**Example Result:**
- Total lien paid: $69,700
- Amount we owe back: $68,500
- Unrelated to exclude: $1,200 (cold visits)

---

## Lien Negotiation Report

**Query for negotiation:**
```cypher
MATCH (case:Case {name: $case_name})-[:HAS_LIEN]->(lien:Lien {name: $lien_name})
MATCH (lien)-[:PAID_BILL]->(bill:Bill)
MATCH (visit:MedicalVisit)-[:HAS_BILL]->(bill)
MATCH (visit)-[:AT_LOCATION]->(provider)
OPTIONAL MATCH (provider)-[:PART_OF*]->(sys:HealthSystem)

RETURN
  visit.visit_date,
  provider.name,
  sys.name as system,
  visit.diagnosis,
  visit.related_to_injury,
  visit.unrelated_reason,
  bill.amount,
  CASE
    WHEN visit.related_to_injury THEN bill.amount
    ELSE 0
  END as amount_to_repay
ORDER BY visit.visit_date
```

**Export to spreadsheet for lien negotiation!**

---

## Changes Made to graphiti_client.py

### Added:
1. ✅ `class MedicalVisit` (line 599)
2. ✅ `MedicalVisit` to ENTITY_TYPES list (line 856)
3. ✅ `("Bill", "Location"): ["BilledBy"]`
4. ✅ `("Bill", "Facility"): ["BilledBy"]`
5. ✅ 7 MedicalVisit relationships
6. ✅ `("Lien", "Bill"): ["PaidBill"]`

### Total Changes:
- 1 new entity type
- 9 new relationship patterns
- Full support for date-by-date medical chronology with lien negotiation

---

## Benefits

**Your workflow is now fully supported:**

✅ **Separate PDF per visit date**
- Each date = MedicalVisit entity
- Link to Document (PDF)

✅ **Mark unrelated visits**
- `related_to_injury: false`
- `unrelated_reason: "cold"`

✅ **Link bills to visits**
- MedicalVisit -[:HAS_BILL]-> Bill
- Bill -[:BILLED_BY]-> Location

✅ **Lien negotiations**
- Query related vs unrelated
- Show what lien paid vs what you owe back
- Exclude unrelated bills from reimbursement

✅ **Multi-role support**
- Provider who bills can also be defendant
- Same Location entity, different relationships

---

## ✅ Schema Complete for Medical Chronology

Your medical chronology workflow is now fully supported in the Pydantic schema!

**Ready for:**
- Creating MedicalVisit entities (one per date)
- Flagging related/unrelated
- Linking bills to visits
- Linking PDFs to visits
- Running lien negotiation queries
- Multi-role provider scenarios

**All additions complete!**
