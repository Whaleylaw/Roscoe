# Schema Ingestion Plan: Pydantic → FalkorDB

**Goal:** Make FalkorDB graph match the Pydantic schema in `graphiti_client.py`

**Date:** January 2, 2026

---

## Two Types of "Schema Ingestion"

### Option A: Schema Preparation (Metadata Only)

**What:** Prepare FalkorDB to receive entity types
**How:** Create indices, constraints, or placeholder nodes
**Impact:** Zero impact on existing data
**Time:** ~5 minutes
**Result:** Graph "knows about" all 58 entity types

**Note:** In FalkorDB, schemas are dynamic - you don't need to pre-declare entity types. They're created automatically when you insert nodes.

### Option B: Data Ingestion (Actual Entities)

**What:** Ingest the 45,900 entities from JSON files
**How:** Read JSON files, create nodes and relationships
**Impact:** Adds ~45,900 nodes + ~21,500 relationships
**Time:** ~30-60 minutes
**Result:** Graph has all reference data (doctors, judges, divisions, etc.)

---

## What Needs to Be Ingested (JSON → Graph)

### Ready to Ingest (In JSON Files)

| Entity Type | Count | Source File | Relationships |
|-------------|-------|-------------|---------------|
| **Doctor** | 20,732 | doctors.json | WORKS_AT → MedicalProvider |
| **MedicalProvider** | +1,386 | medical_providers.json | PART_OF → HealthSystem |
| **HealthSystem** | 5 | health_systems.json | (top-level) |
| **CircuitDivision** | 86 | circuit_divisions.json | PART_OF → Court |
| **DistrictDivision** | 94 | district_divisions.json | PART_OF → Court |
| **AppellateDistrict** | 5 | appellate_districts.json | PART_OF → Court |
| **SupremeCourtDistrict** | 7 | supreme_court_districts.json | PART_OF → Court |
| **CircuitJudge** | 101 | circuit_judges.json | PRESIDES_OVER → CircuitDivision |
| **DistrictJudge** | 94 | district_judges.json | PRESIDES_OVER → DistrictDivision |
| **CourtClerk** | 121 | court_clerks.json | WORKS_AT → Court |
| **MasterCommissioner** | 114 | (in court personnel) | APPOINTED_BY → Court |
| **CourtAdministrator** | 7 | (in court personnel) | WORKS_AT → Court |
| **Court** | +83 | courts.json | (add missing) |
| **Episode** | 13,491 | merged_*.json | RELATES_TO → Case, ABOUT → Entities |

**Total to Ingest:** ~37,325 new entities + ~21,500+ relationships

### Pending Manual Review (Not Ready)

| Entity Type | Count | Status |
|-------------|-------|--------|
| **Episode ABOUT relationships** | 40,605 | 3 of 138 cases approved |
| **Opposing Attorneys** | ~200 | In episode narratives |
| **Opposing Law Firms** | ~50 | In episode narratives |
| **Bills, Expenses, Settlements** | TBD | Not yet extracted |

---

## Ingestion Impact Analysis

### ✅ Safe to Ingest (No Conflicts)

These don't overlap with existing data:
- **Doctors** (0 in graph → 20,732)
- **Court Divisions** (0 in graph → 192)
- **Judges** (0 in graph → 316)
- **Health Systems** (0 in graph → 5)

### ⚠️ Merge Required

These need to be merged with existing:
- **MedicalProvider** (773 in graph → +1,386 new = 2,159 total)
  - Must NOT duplicate existing 773
  - Add only the 1,386 new providers
- **Courts** (23 in graph → +83 new = 106 total)
  - Add missing courts
  - Don't duplicate existing

### ⏸️ Wait for Review

These depend on approved episode reviews:
- **Episodes** (0 in graph → 13,491)
  - Wait until all 138 cases reviewed and merged
  - Then bulk ingest with ABOUT relationships

---

## Recommended Approach

### Phase 1: Ingest Reference Data (Safe - No Dependencies)

**Do NOW** - These are completely independent:

1. ✅ **Health Systems** (5 entities)
   - No parent, no conflicts
   - Fastest to ingest

2. ✅ **Court Divisions** (192 entities)
   - Create CircuitDivision, DistrictDivision nodes
   - Add PART_OF → Court relationships

3. ✅ **Judges** (316 entities)
   - Create Judge nodes
   - Add PRESIDES_OVER → Division relationships

4. ✅ **Court Personnel** (242 entities)
   - CourtClerk, MasterCommissioner, CourtAdministrator
   - Add WORKS_AT/APPOINTED_BY → Court relationships

5. ✅ **New Medical Providers** (1,386 entities)
   - Filter out existing 773 (by exact name match)
   - Add new providers only
   - Add PART_OF → HealthSystem relationships

6. ✅ **Doctors** (20,732 entities)
   - Add Doctor nodes
   - **SKIP WORKS_AT relationships for now** (requires matching doctors to specific provider locations - complex)
   - Just create the nodes first

**Result:** +22,925 new entities, ~1,500 new relationships
**Time:** 30-60 minutes
**Risk:** LOW - No overlap with existing case data

### Phase 2: Connect Entities to Cases (After Phase 1)

**Do AFTER Phase 1:**

1. Connect doctors to providers (WORKS_AT)
2. Connect cases to court divisions (FILED_IN)
3. Connect cases to judges (ASSIGNED_TO)

**Risk:** MEDIUM - Requires matching logic

### Phase 3: Episode Ingestion (After All Reviews Complete)

**Do LAST:**

1. Wait for all 138 episode reviews to be approved
2. Ingest all episodes (13,491 nodes)
3. Create ABOUT relationships (40,605 links)
4. Create FOLLOWS relationships (temporal/topical)

**Risk:** LOW - Clean ingestion from approved merged files

---

## Schema Prep vs Data Ingestion

**Schema Prep (Option A):**
- FalkorDB doesn't need it - schemas are dynamic
- We CAN create empty indices or placeholder nodes
- But it's not required

**Data Ingestion (Option B):**
- Ingest the actual 45,900 entities from JSON files
- This makes the graph match the schema by HAVING the entities
- Recommended approach

---

## My Interpretation

When you said "make the FalkorDB match that", I believe you want **Option B - Data Ingestion**.

Specifically:
1. Ingest the reference data (doctors, judges, divisions, health systems)
2. WITHOUT breaking existing case relationships
3. So the graph has all the entity types defined in the schema

**Is this correct?**

If yes, I'll create ingestion scripts for:
- Phase 1a: Health Systems (5 entities) - Test ingestion
- Phase 1b: Court Divisions (192 entities) - If 1a works
- Phase 1c: Judges (316 entities) - If 1b works
- Phase 1d: Court Personnel (242 entities)
- Phase 1e: New Medical Providers (1,386 entities)
- Phase 1f: Doctors (20,732 entities)

**Or do you want something else?**

---

## Safety Guarantees

**How we avoid breaking existing relationships:**

1. **Read-Only Check First:**
   - Query existing entities before creating
   - Skip if already exists (by exact name match)

2. **Additive Only:**
   - CREATE new nodes
   - CREATE new relationships
   - NEVER DELETE or UPDATE existing (except CAALWINC rename)

3. **Transaction Safety:**
   - Use MERGE instead of CREATE where appropriate
   - Batch commits (100 nodes at a time)

4. **Verification:**
   - Count total nodes before/after
   - Verify no relationships lost
   - Check case data still intact

**Example Safe Pattern:**
```cypher
// Safe - only creates if doesn't exist
MERGE (d:Doctor {name: "Dr. Wallace L. Huff Jr.", group_id: "roscoe_graph"})
ON CREATE SET
  d.specialty = "orthopedic surgery",
  d.created_at = datetime()
```

---

## What I Need from You

**Clarify what you want:**

**Option 1:** Just prep the schema (create indices, verify readiness)
**Option 2:** Ingest Phase 1 reference data (22,925 entities from JSON files)
**Option 3:** Just create relationships for Abby Sitgraves case (test case)
**Option 4:** Something else

Let me know and I'll proceed accordingly!
