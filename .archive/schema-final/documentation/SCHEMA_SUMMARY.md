# Complete Knowledge Graph Schema - Final Summary

**Date:** January 4, 2026
**Status:** Ready for fresh graph ingestion

---

## Overview

**Total Schema:**
- **Entity Types:** 65 total (58 existing + 7 new)
- **Relationship Patterns:** ~110 total (60 existing + 50 new)
- **Entity Data Files:** 3,495 entities ready for ingestion

---

## New Structure Summary

### 1. Three-Tier Medical Provider Hierarchy ⭐

**Old (incorrect):**
```
MedicalProvider (generic, flat)
```

**New (correct):**
```
HealthSystem (6)
  ↓ PART_OF
Facility (1,164)
  ↓ PART_OF
Location (2,325)
```

**Benefits:**
- Multi-role support (provider/defendant/vendor/expert)
- Progressive detail (vague → specific)
- Records request infrastructure

---

### 2. Medical Chronology Support ⭐

**New Entity:** MedicalVisit

**Purpose:** Date-by-date visit tracking with related/unrelated flagging

**Key Feature:** `related_to_injury` field enables lien negotiation queries

**Example:**
```cypher
(MedicalVisit {
  visit_date: "2024-03-15",
  related_to_injury: true
})-[:HAS_BILL]->(Bill: "$5,000")

(MedicalVisit {
  visit_date: "2024-04-20",
  related_to_injury: false,  // Cold visit
  unrelated_reason: "URI"
})-[:HAS_BILL]->(Bill: "$1,200")  // Don't owe this back to lien!
```

---

### 3. Insurance Policy & Payment Tracking ⭐

**New Entities:** InsurancePolicy, InsurancePayment

**Purpose:** Separate policies from claims, track payment history

**Structure:**
```
Client
  ↓ HAS_POLICY
InsurancePolicy
  ↓ WITH_INSURER
Insurer
  ↓ HAS_CLAIM
PIPClaim
  ↓ MADE_PAYMENT
InsurancePayment ($2K, $3K, $5K advances)
```

---

### 4. Litigation Calendar & Events ⭐

**New Entity:** CourtEvent

**Purpose:** Track hearings, trials, mediations

**Structure:**
```
Case
  ↓ HAS_EVENT
CourtEvent (hearing, trial, mediation)
  ↓ IN
CircuitDivision
```

---

### 5. Multi-Office Law Firms ⭐

**New Entity:** LawFirmOffice

**Purpose:** Multi-office firm support (like medical Facility/Location)

**Structure:**
```
LawFirm: "Bryan Cave"
  ↓ PART_OF
LawFirmOffice: "Louisville Office"
  ↓ WORKS_AT
Attorney: "John Smith"
```

---

## Complete Entity List (65 total)

### Core Case (2)
- Case
- Client

### Insurance (10 - 2 NEW)
- Insurer
- Adjuster
- **InsurancePolicy** ⭐ NEW
- **InsurancePayment** ⭐ NEW
- PIPClaim, BIClaim, UMClaim, UIMClaim, WCClaim, MedPayClaim

### Medical (8 - 3 NEW)
- HealthSystem
- **Facility** ⭐ NEW
- **Location** ⭐ NEW
- MedicalProvider (DEPRECATED)
- Doctor
- **MedicalVisit** ⭐ NEW
- Lien, LienHolder

### Legal (17 - 2 NEW)
- LawFirm
- **LawFirmOffice** ⭐ NEW
- Attorney, CaseManager
- Court, CircuitDivision, DistrictDivision, AppellateDistrict, SupremeCourtDistrict
- CircuitJudge, DistrictJudge, AppellateJudge, SupremeCourtJustice
- CourtClerk, MasterCommissioner, CourtAdministrator
- Pleading
- **CourtEvent** ⭐ NEW

### Other (9)
- Defendant
- Organization
- Expert, Mediator, Witness, Vendor
- Document types (6)
- Bill, Expense, Negotiation, Settlement

### Workflow (8)
- Phase, SubPhase, Landmark, LandmarkStatus
- WorkflowDef, WorkflowStep, WorkflowChecklist, WorkflowTemplate

### Episodic (1)
- Episode (timeline narrative)

---

## Data Files Ready for Ingestion

**Location:** `schema-final/entities/`

### Medical Providers

**1. health_systems.json**
- 6 HealthSystem entities
- All with records_request fields

**2. facilities.json**
- 1,164 Facility entities
- 548 health system + 616 independent

**3. locations.json**
- 2,325 Location entities
- 1,709 health system + 616 independent

**4. hierarchy_relationships.json**
- 2,873 relationship mappings
- Location → Facility (2,325)
- Facility → HealthSystem (548)

### Other Entities (Already in Graph)

**Courts & Legal:**
- 118 Courts
- 192 Divisions
- 218 Judges
- 236 Court Personnel
- ~35 Attorneys
- ~28 Law Firms

**Insurance:**
- ~99 Insurers
- ~148 Adjusters
- ~260 Claims

**Doctors:**
- 20,708 Doctors

---

## Key Design Principles

### 1. Multi-Role Entities ✅

**Same entity, different roles:**
- Norton Hospital as provider: `(Client)-[:TREATED_AT]->(Location)`
- Norton Hospital as defendant: `(Case)-[:DEFENDANT]->(Location)`
- Norton Hospital as vendor: `(Case)-[:VENDOR_FOR]->(Location)`

### 2. Progressive Detail ✅

**Start vague, add specificity later:**
- Initial: `(Client)-[:TREATED_AT]->(Facility: "Norton Orthopedic")`
- Later: `(Client)-[:TREATED_AT]->(Location: "Norton Ortho - Downtown")`

### 3. Hierarchy Inheritance ✅

**Query up hierarchy for information:**
```cypher
// Find records request method
MATCH (loc:Location)-[:PART_OF]->(fac:Facility)-[:PART_OF]->(sys:HealthSystem)
WITH COALESCE(loc.records_request_method, fac.records_request_method, sys.records_request_method) as method
RETURN method
```

### 4. Separation of Concerns ✅

**Policies separate from claims:**
- InsurancePolicy (one per policy)
- Multiple claims under same policy

**Visits separate from bills:**
- MedicalVisit (one per date)
- Bills linked to visits

---

## Implementation Status

### ✅ Complete in Pydantic Models

**All new entities defined in:** `src/roscoe/core/graphiti_client.py`
- 7 new entity classes
- 8 enhanced entity classes
- 50+ new relationship patterns
- All in ENTITY_TYPES list
- All in EDGE_TYPE_MAP

### ✅ Complete in Data Files

**All medical provider data ready:**
- 6 HealthSystems
- 1,164 Facilities
- 2,325 Locations
- 2,873 hierarchy relationships

### ⏳ Pending

**Other entity data (already in graph, don't need new files):**
- Insurers, Adjusters, Claims (already exist)
- Courts, Judges, Divisions (already ingested)
- Attorneys, Law Firms (already exist)
- Doctors (already ingested - 20,708)

**New entity types don't have data yet (will be created from episodes/case work):**
- InsurancePolicy (extract from case data)
- InsurancePayment (extract from case data)
- MedicalVisit (create during chronology)
- CourtEvent (extract from calendar/case notes)
- LawFirmOffice (extract from attorney data)

---

## Next Steps

### 1. Review This Folder

**Check all files in `schema-final/`:**
- Entity data files (entities/)
- Documentation (documentation/)
- README.md (this summary)

### 2. Approve for Ingestion

**Once approved:**
- Upload entity files to GCS
- Run fresh graph ingestion
- Create all new entity types
- Establish hierarchy relationships

### 3. Episode Ingestion

**After graph structure ready:**
- Ingest 13,491 episodes
- Link to Facilities/Locations (not old MedicalProvider)
- Create MedicalVisit entities from chronology
- Link to InsurancePolicies
- Create CourtEvents from case notes

---

## Files in This Package

```
schema-final/
├── README.md
├── entities/
│   ├── health_systems.json (6 - 5.4KB)
│   ├── facilities.json (1,164 - 909KB)
│   ├── locations.json (2,325 - 1.9MB)
│   └── hierarchy_relationships.json (2,873 - 359KB)
├── documentation/
│   ├── NEW_ENTITIES.md (7 new types)
│   ├── NEW_RELATIONSHIPS.md (51 new patterns)
│   ├── ENHANCED_ENTITIES.md (8 enhanced types)
│   └── SCHEMA_SUMMARY.md (this file)
└── source/
    └── (will copy updated graphiti_client.py)
```

**Total package size:** ~3.2MB

---

## What This Enables

**Your complete knowledge graph will support:**

✅ **Medical Provider Management**
- 3-tier hierarchy (system → facility → location)
- Multi-role scenarios (provider who's also defendant)
- Progressive detail (vague → specific over time)
- Records request workflows

✅ **Medical Chronology**
- Date-by-date visit tracking
- Related/unrelated flagging
- Bill-to-visit linking
- Lien negotiation queries

✅ **Insurance Workflows**
- Policy tracking (separate from claims)
- Payment history (PIP advances)
- Denial/appeal tracking
- Defendant insurance linkage

✅ **Litigation Management**
- Multi-office law firms
- Court calendar and events
- Discovery tracking
- Pleading attribution

✅ **Real-World Accuracy**
- Entities can play multiple roles
- Hierarchies mirror real structures
- Progressive detail matches case development
- Query flexibility

---

## ✅ Everything You Need is in This Folder

**Review `schema-final/` to see:**
- All new entities
- All new relationships
- All entity data (3,495 entities)
- Complete documentation

**Ready for your approval and graph ingestion!**
