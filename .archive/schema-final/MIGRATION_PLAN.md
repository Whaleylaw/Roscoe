# Graph Migration Plan - What Stays vs What Gets Replaced

**Date:** January 4, 2026
**Current Graph:** 33,852 nodes, 21,758 relationships

---

## Current Graph State

### Total Counts

**Nodes:** 33,852
**Relationships:** 21,758
**Entity Types:** 45 labels

### Top 20 Entity Types (by count)

| Rank | Entity Type | Count | Status |
|------|-------------|-------|--------|
| 1 | Doctor | 20,708 | ✅ KEEP |
| 2 | LandmarkStatus | 8,991 | ✅ KEEP |
| 3 | **MedicalProvider** | **1,998** | ❌ **REPLACE** |
| 4 | Entity | 196 | ✅ KEEP |
| 5 | Pleading | 168 | ✅ KEEP |
| 6 | Adjuster | 148 | ✅ KEEP |
| 7 | CourtClerk | 121 | ✅ KEEP |
| 8 | PIPClaim | 120 | ✅ KEEP |
| 9 | BIClaim | 119 | ✅ KEEP |
| 10 | Court | 118 | ✅ KEEP |
| 11 | Case | 111 | ✅ KEEP |
| 12 | Client | 110 | ✅ KEEP |
| 13 | MasterCommissioner | 108 | ✅ KEEP |
| 14 | Lien | 103 | ✅ KEEP |
| 15 | CircuitJudge | 101 | ✅ KEEP |
| 16 | Insurer | 99 | ✅ KEEP |
| 17 | DistrictDivision | 94 | ✅ KEEP |
| 18 | DistrictJudge | 94 | ✅ KEEP |
| 19 | CircuitDivision | 86 | ✅ KEEP |
| 20 | Landmark | 82 | ✅ KEEP |

---

## What Will Be REMOVED ❌

### MedicalProvider Nodes (1,998 total)

**Breakdown:**
- **895 with PART_OF → HealthSystem** (from health system rosters)
- **1,103 independent** (no health system connection)

**Relationships to be deleted:**
- 899 PART_OF → HealthSystem
- 329 TREATING_AT ← Case
- 317 TREATED_BY ← Client
- **Total:** ~1,545 relationships

**Why remove:**
- Old flat structure
- Being replaced by Facility/Location 3-tier hierarchy
- Can't coexist with new structure (name collisions)

**Impact:**
- Cases will lose provider connections temporarily
- Clients will lose provider connections temporarily
- Will be rebuilt from medical records/episodes

---

## What Will Be KEPT ✅

### All Case Data (100%)

**Keep unchanged:**
- **Cases** (111) - All case entities
- **Clients** (110) - All client entities
- **Defendants** (7) - All defendants
- **Liens** (103) - All lien entities
- **LienHolders** (50) - All lien holders

**Relationships preserved:**
- Case ← Client (HAS_CLIENT)
- Case → Claim (HAS_CLAIM)
- Case → Lien (HAS_LIEN)
- Case → Phase (IN_PHASE)
- Case → LandmarkStatus (HAS_STATUS)
- Case → Defendant (relationships if they exist)

**No case data lost!** ✅

---

### All Insurance Data (100%)

**Keep unchanged:**
- **Insurers** (99)
- **Adjusters** (148)
- **PIPClaim** (120)
- **BIClaim** (119)
- **UMClaim** (14)
- **UIMClaim** (2)
- **WCClaim** (5)

**Relationships preserved:**
- Claim → Insurer (INSURED_BY)
- Claim → Adjuster (ASSIGNED_ADJUSTER)
- Case → Claim (HAS_CLAIM)
- All claim-to-case connections intact

**No insurance data lost!** ✅

---

### All Court Data (100%)

**Keep unchanged:**
- **Courts** (118)
- **CircuitDivision** (86)
- **DistrictDivision** (94)
- **CircuitJudge** (101)
- **DistrictJudge** (94)
- **AppellateJudge** (15)
- **SupremeCourtJustice** (8)
- **CourtClerk** (121)
- **MasterCommissioner** (108)
- **CourtAdministrator** (7)

**Relationships preserved:**
- Division → Court (PART_OF)
- Judge → Division (PRESIDES_OVER)
- All court hierarchy intact

**No court data lost!** ✅

---

### All Legal Data (100%)

**Keep unchanged:**
- **Attorneys** (35)
- **LawFirms** (28)
- **CaseManagers** (6)
- **Pleadings** (168)

**Relationships preserved:**
- Attorney → LawFirm (WORKS_AT)
- Attorney → Case (if exist)
- All legal connections intact

**No legal data lost!** ✅

---

### All Doctor Data (100%)

**Keep unchanged:**
- **Doctors** (20,708)

**Note:** Doctor WORKS_AT relationships may be affected
- Some doctors linked to MedicalProvider nodes
- Those links will be lost when MedicalProvider deleted
- Can be recreated to link to new Location nodes

---

### All Workflow Data (100%)

**Keep unchanged:**
- **Phases** (9)
- **SubPhases** (5)
- **Landmarks** (82)
- **LandmarkStatus** (8,991)
- **WorkflowDef** (39)
- **WorkflowTemplate** (28)
- **WorkflowChecklist** (12)
- **WorkflowTool** (21)

**No workflow data lost!** ✅

---

### All Other Entities (100%)

**Keep unchanged:**
- **Organizations** (19)
- **Vendors** (39)
- **Experts** (2)
- **Mediators** (3)
- **Witnesses** (1)
- **Entity** (196 - generic Graphiti entities)

**No other data lost!** ✅

---

## What Will Be ADDED ✅

### New Medical Provider Structure (3,495 new nodes)

**Add:**
- **HealthSystem** (6) - Update existing 6 with new fields
- **Facility** (1,164) - Create new
- **Location** (2,325) - Create new

**New relationships:**
- 2,325 Location → Facility (PART_OF)
- 548 Facility → HealthSystem (PART_OF)
- **Total:** 2,873 new relationships

**Net change:**
- Nodes: +1,497 (3,495 new - 1,998 deleted)
- Relationships: +1,328 (2,873 new - 1,545 deleted)

---

## Migration Strategy: Clean Replacement

### Phase 1: Document Current State ✅ (Done)

**Analyzed:**
- 33,852 nodes in graph
- 1,998 MedicalProvider nodes to be replaced
- 1,545 relationships connected to MedicalProviders

---

### Phase 2: Delete MedicalProvider Nodes

**Command:**
```cypher
MATCH (p:MedicalProvider)
DETACH DELETE p
```

**Impact:**
- Removes 1,998 nodes
- Removes 1,545 relationships
- **Cases lose provider connections** (temporary)
- **Clients lose provider connections** (temporary)
- All other data untouched ✅

**New state after deletion:**
- Nodes: 31,854 (33,852 - 1,998)
- Relationships: 20,213 (21,758 - 1,545)

---

### Phase 3: Update HealthSystem Nodes (6 nodes)

**Action:** Update existing 6 HealthSystem nodes with new fields

**What changes:**
- Add records_request fields (method, address, fax, phone, URL, notes)
- Add billing_request fields
- Add source, validation_state metadata

**Impact:**
- 0 nodes added/removed (update only)
- Existing PART_OF relationships preserved
- No disruption

---

### Phase 4: Ingest New Facilities (1,164 nodes)

**Source:** `schema-final/entities/facilities.json`

**Action:** Create 1,164 Facility nodes

**Impact:**
- +1,164 nodes
- No relationships yet (added in Phase 5)

**New state:**
- Nodes: 33,018 (31,854 + 1,164)

---

### Phase 5: Ingest New Locations (2,325 nodes)

**Source:** `schema-final/entities/locations.json`

**Action:** Create 2,325 Location nodes

**Impact:**
- +2,325 nodes
- No relationships yet (added in Phase 6)

**New state:**
- Nodes: 35,343 (33,018 + 2,325)

---

### Phase 6: Create Hierarchy Relationships (2,873 relationships)

**Source:** `schema-final/entities/hierarchy_relationships.json`

**Action:**
- Create 2,325 Location → Facility (PART_OF)
- Create 548 Facility → HealthSystem (PART_OF)

**Impact:**
- +2,873 relationships
- Hierarchy complete

**New state:**
- Nodes: 35,343 (no change)
- Relationships: 23,086 (20,213 + 2,873)

---

### Phase 7: Rebuild Case/Client → Provider Links (Manual)

**Later, from medical records/episodes:**
- Review medical records for each case
- Create Client → Location/Facility (TREATED_AT)
- Create Case → Location/Facility (TREATING_AT if needed)

**This is NOT part of initial ingestion**
- Will be done case-by-case
- Based on actual medical records
- Ensures accuracy

---

## Final Projected State

### After Migration Complete

**Nodes:** 35,343 (vs 33,852 current = +1,491 net)
**Relationships:** 23,086+ (vs 21,758 current = +1,328 net minimum)

**Entity Types:** ~52 (45 current + 7 new)

---

## What Gets Lost (Temporarily)

### Case → Provider Connections

**Current:**
- 329 Case → MedicalProvider (TREATING_AT)
- 317 Client → MedicalProvider (TREATED_BY)

**After migration:**
- These connections will be GONE
- **Must be rebuilt from medical records**
- Not automatic!

**Cases affected:** ~100-150 cases (estimated)

**This is intentional per your "clean slate" approach**

---

### Doctor → Provider Connections

**Current:**
- Unknown how many Doctor → MedicalProvider (WORKS_AT)

**After migration:**
- These will be LOST
- Can be recreated as Doctor → Location (WORKS_AT)
- Phase 3 work (after hierarchy established)

---

## What Never Gets Touched ✅

**These entities and ALL their relationships stay 100% intact:**

✅ **All case operational data:**
- Cases, Clients, Defendants
- Insurance claims and adjusters
- Liens and lien holders
- Case workflow states (Phases, Landmarks, LandmarkStatus)

✅ **All court system:**
- Courts, Divisions, Judges
- Court personnel
- Pleadings
- All court hierarchy

✅ **All legal professionals:**
- Attorneys, Law Firms, Case Managers
- All attorney-case connections

✅ **All doctors:**
- 20,708 Doctor entities
- (Their WORKS_AT → MedicalProvider links will break, but doctors themselves preserved)

✅ **All other entities:**
- Organizations, Vendors, Experts, Mediators, Witnesses
- Generic Entity nodes
- All workflow definitions

---

## Risk Assessment

### HIGH CONFIDENCE (Safe)

**Will NOT be affected:**
- ✅ Case data (111 cases)
- ✅ Insurance data (all claims, insurers, adjusters)
- ✅ Court data (all courts, judges, divisions)
- ✅ Workflow data (all phases, landmarks, statuses)
- ✅ Legal data (attorneys, law firms, pleadings)
- ✅ Lien data (all liens and lien holders)

### MEDIUM IMPACT (Fixable)

**Will be temporarily lost:**
- ⚠️ Case → Provider connections (646 relationships)
- ⚠️ Doctor → Provider connections (unknown count)

**How to fix:**
- Rebuild from medical records (manual)
- Create during episode ingestion
- Expected as part of "clean slate" approach

### NO RISK

**Data that doesn't exist yet (new entities):**
- InsurancePolicy, InsurancePayment, MedicalVisit, CourtEvent, LawFirmOffice
- These don't exist in current graph
- Pure additions when data is created

---

## Recommended Migration Steps

### Step 1: BACKUP (Critical!)

```bash
# Backup current graph before ANY changes
docker exec roscoe-graphdb redis-cli -p 6379 BGSAVE
# Or export full graph to JSON
```

**Why:** Safety net in case something goes wrong

---

### Step 2: DELETE MedicalProvider Nodes

```cypher
MATCH (p:MedicalProvider)
DETACH DELETE p
```

**Verification after:**
```cypher
MATCH (p:MedicalProvider) RETURN count(p)  // Should be 0
MATCH (n) RETURN count(n)  // Should be 31,854
```

---

### Step 3: UPDATE HealthSystem Nodes (6)

**For each HealthSystem, add new fields:**
```cypher
MATCH (h:HealthSystem {name: "Norton Healthcare"})
SET
  h.records_request_method = null,
  h.records_request_address = null,
  h.records_request_fax = null,
  h.records_request_phone = null,
  h.records_request_url = null,
  h.records_request_notes = null,
  h.billing_request_method = null,
  h.billing_request_address = null,
  h.billing_request_phone = null,
  h.source = "health_system_roster",
  h.validation_state = "unverified"
RETURN h.name
```

**Repeat for all 6 systems**

---

### Step 4: INGEST Facilities (1,164 new)

**From:** `facilities.json`

**Create nodes:**
```cypher
// For each facility in JSON
CREATE (f:Facility {
  name: $name,
  group_id: "roscoe_graph",
  ...all attributes
})
```

**Verification:**
```cypher
MATCH (f:Facility) RETURN count(f)  // Should be 1,164
```

---

### Step 5: INGEST Locations (2,325 new)

**From:** `locations.json`

**Create nodes:**
```cypher
// For each location in JSON
CREATE (l:Location {
  name: $name,
  group_id: "roscoe_graph",
  address: $address,  // REQUIRED
  ...all attributes
})
```

**Verification:**
```cypher
MATCH (l:Location) RETURN count(l)  // Should be 2,325
```

---

### Step 6: CREATE Hierarchy Relationships

**From:** `hierarchy_relationships.json`

**Create Location → Facility:**
```cypher
// For each mapping
MATCH (l:Location {name: $location_name})
MATCH (f:Facility {name: $facility_name})
CREATE (l)-[:PART_OF]->(f)
```

**Create Facility → HealthSystem:**
```cypher
// For each mapping
MATCH (f:Facility {name: $facility_name})
MATCH (h:HealthSystem {name: $health_system_name})
CREATE (f)-[:PART_OF]->(h)
```

**Verification:**
```cypher
MATCH ()-[r:PART_OF]->() WHERE (startNode(r):Location OR startNode(r):Facility)
RETURN count(r)  // Should be 2,873
```

---

### Step 7: VERIFY Final State

**Expected final state:**
- Nodes: ~35,343
- Relationships: ~23,086
- HealthSystem: 6
- Facility: 1,164
- Location: 2,325
- MedicalProvider: 0 (deleted)

**Critical checks:**
```cypher
// All cases still exist
MATCH (c:Case) RETURN count(c)  // Should be 111

// All clients still exist
MATCH (c:Client) RETURN count(c)  // Should be 110

// All insurance still exists
MATCH (i:Insurer) RETURN count(i)  // Should be 99

// All doctors still exist
MATCH (d:Doctor) RETURN count(d)  // Should be 20,708

// Canary check - Abby Sitgraves case exists
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"}) RETURN c.name
```

---

## What Cases Will Lose

### Temporarily Lost Relationships

**Example: Abby Sitgraves Case**

**Before migration:**
```cypher
(Case: "Abby-Sitgraves")-[:TREATING_AT]->(MedicalProvider: "Jewish Hospital")
(Case: "Abby-Sitgraves")-[:TREATING_AT]->(MedicalProvider: "Foundation Radiology")
(Case: "Abby-Sitgraves")-[:TREATING_AT]->(MedicalProvider: "UofL Physicians - Orthopedics")
(Case: "Abby-Sitgraves")-[:TREATING_AT]->(MedicalProvider: "Norton Orthopedic")
```

**After migration:**
```cypher
(Case: "Abby-Sitgraves")  // No provider connections!
```

**How to rebuild:**
1. Review Abby's medical records
2. Identify providers with addresses
3. Match to Facility or Location in new structure
4. Create: `(Client: "Abby Sitgraves")-[:TREATED_AT]->(Location: "UofL Health – Jewish Hospital")`

**This is your "clean slate" approach - rebuild connections accurately from records**

---

## Canary Check Point

**Before ANY changes:**
```cypher
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})-[r]-()
RETURN count(r) as abby_relationships
```

**Current:** Should show 89 relationships (after earlier cleanup)

**After MedicalProvider deletion:**
- Will drop by ~4 (provider connections lost)
- Expected: ~85 relationships

**After full migration:**
- Should be ~85 (no provider connections until manual rebuild)

---

## Summary

### SAFE TO DELETE (1,998 nodes)
- MedicalProvider (all)
- Old flat structure
- Being replaced by Facility/Location

### NEVER TOUCH (31,854 nodes - 94% of graph!)
- All cases, clients, defendants
- All insurance (insurers, adjusters, claims)
- All courts, judges, divisions, personnel
- All attorneys, law firms, pleadings
- All doctors (20,708)
- All workflow states
- All liens
- All other entities

### WILL ADD (3,495 nodes)
- 6 HealthSystem (update existing)
- 1,164 Facility (new)
- 2,325 Location (new)

### NET RESULT
- Nodes: 33,852 → 35,343 (+1,491)
- Relationships: 21,758 → 23,086 (+1,328 minimum)
- Better structure: 3-tier hierarchy
- Multi-role support ready
- Clean slate for provider connections

---

## Recommendation

**Migration is LOW RISK with one major caveat:**

✅ **94% of graph untouched** (all case data, insurance, courts, etc.)
⚠️ **Provider connections will be lost** (646 relationships)
✅ **Can be rebuilt** from medical records/episodes

**Proceed with:**
1. Backup first (CRITICAL)
2. Delete MedicalProvider nodes
3. Ingest new Facility/Location structure
4. Verify all other data intact
5. Rebuild provider connections from records (manual/episodic)

**This matches your "clean slate" approach perfectly.**

---

## Files for Review

**All in:** `/Volumes/X10 Pro/Roscoe/schema-final/`

**Review before approving:**
1. This migration plan
2. Entity data files (entities/)
3. Schema documentation (documentation/)

**Ready to proceed when you approve!**
