# Abby Sitgraves: Graph Actions Required

**Case:** Abby-Sitgraves-MVA-7-13-2024
**Date:** January 2, 2026

---

## ANSWER: Yes, Schema Exists!

✅ **The full schema IS defined** in `/src/roscoe/core/graphiti_client.py`:
- 58 entity types (lines 50-760)
- 71 relationship types (lines 770-1350)
- Including: HasDefendant, RepresentsClient, FiledIn, and all others

❌ **But only 25 relationship types have been CREATED** in the actual graph
- This is expected - relationships only exist when data is ingested
- We can create new relationships anytime using the schema definitions

---

## Current Graph State for Abby Sitgraves

### ✅ Already Connected (11 entities, 10 relationships)

| Entity | Type | Relationship | Status |
|--------|------|--------------|--------|
| Abby Sitgraves | Client | Case→HAS_CLIENT→Client | ✅ Connected |
| Jewish Hospital | MedicalProvider | Case→TREATING_AT→Provider | ✅ Connected |
| Foundation Radiology | MedicalProvider | Case→TREATING_AT→Provider | ✅ Connected |
| UofL Physicians - Orthopedics | MedicalProvider | Case→TREATING_AT→Provider | ✅ Connected |
| Saint Mary and Elizabeth Hospital | MedicalProvider | Case→TREATING_AT→Provider | ✅ Connected |
| National Indemnity Company | Insurer | Case→HAS_CLAIM→PIPClaim→INSURED_BY→Insurer | ✅ Connected |
| Jordan Bahr | Adjuster | PIPClaim→ASSIGNED_ADJUSTER→Adjuster | ✅ Connected |
| Key Benefit Administrators | LienHolder | Case→HAS_LIEN→Lien→HELD_BY→LienHolder | ✅ Connected |
| Key Benefit Administrators | Lien | Case→HAS_LIEN→Lien | ✅ Connected |
| onboarding | Phase | Case→IN_PHASE→Phase | ✅ Connected |
| (82 landmarks) | LandmarkStatus | Case→HAS_STATUS→LandmarkStatus | ✅ Connected |

### ✅ Exists But Not Connected (8 entities)

| Entity | Type | Has WORKS_AT? | Needs Connection |
|--------|------|---------------|------------------|
| Aaron G. Whaley | Attorney | ✅ Yes → The Whaley Law Firm | RepresentsClient → Case |
| Bryce Koon | Attorney | ✅ Yes → The Whaley Law Firm | RepresentsClient → Case |
| Bryce Cotton | Attorney | ❓ Unknown | RepresentsClient → Case (?) |
| Sarena Tuttle | CaseManager | ✅ Yes → The Whaley Law Firm | (No direct case relationship in schema) |
| Jessa Galosmo | CaseManager | ✅ Yes → The Whaley Law Firm | (No direct case relationship in schema) |
| The Whaley Law Firm | LawFirm | N/A | (Connected via attorneys) |
| State Farm Insurance Company | Insurer | N/A | ? (May connect via future UM/BI claim) |
| Kentucky Farm Bureau | Insurer | N/A | ? (May connect via future UM/BI claim) |

### ⚠️ Needs Fix (1 entity)

| Entity | Current Name | Correct Name | Action |
|--------|--------------|--------------|--------|
| CAALWINC | "CAALWINC" | "CAAL WORLDWIDE, INC." | UPDATE name, then connect |

### ❌ Needs Creation (1 entity)

| Entity | Type | Action |
|--------|------|--------|
| Unknown Driver | Defendant | CREATE entity, then connect |

---

## Proposed Actions

### Phase 1: Fix & Connect Core Entities (Do Now)

**1. Fix CAALWINC Name:**
```cypher
MATCH (d:Defendant {name: "CAALWINC"})
SET d.name = "CAAL WORLDWIDE, INC."
RETURN d.name
```

**2. Create Unknown Driver:**
```cypher
CREATE (d:Defendant {
  name: "Unknown Driver",
  group_id: "roscoe_graph",
  created_at: datetime()
})
RETURN d.name
```

**3. Connect Defendants to Case:**
```cypher
// Connect CAAL WORLDWIDE
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (d:Defendant {name: "CAAL WORLDWIDE, INC."})
MERGE (c)-[:HAS_DEFENDANT]->(d)

// Connect Unknown Driver
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (d:Defendant {name: "Unknown Driver"})
MERGE (c)-[:HAS_DEFENDANT]->(d)
```

**4. Connect Whaley Attorneys to Case:**
```cypher
MATCH (a:Attorney {name: "Aaron G. Whaley"})
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MERGE (a)-[:REPRESENTS_CLIENT]->(c)

MATCH (a:Attorney {name: "Bryce Koon"})
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MERGE (a)-[:REPRESENTS_CLIENT]->(c)
```

**Result:**
- 1 entity renamed
- 1 entity created
- 4 new relationships created (2 HAS_DEFENDANT, 2 REPRESENTS_CLIENT)

### Phase 2: Test Episode Ingestion (Optional - For Validation)

Ingest first 10 episodes from `merged_Abby-Sitgraves-MVA-7-13-2024.json`:

**Benefits:**
- Validates merged file format
- Tests Episode → ABOUT → Entity relationships
- Tests RELATES_TO (Episode → Case)
- Provides prototype for bulk ingestion script

**Script Needed:** `test_episode_ingestion.py`

### Phase 3: Wait for Other Items

**Don't create now (wait for Phase 3 bulk ingestion):**
- ❌ Court division (entity doesn't exist, part of 192 divisions import)
- ❌ Opposing counsel attorneys (18 entities, mentioned in episodes only)
- ❌ Opposing law firms (3 entities, mentioned in episodes only)
- ❌ State Farm/KFB insurer connections (may need UM/BI claims first)

---

## Verification Queries

After creating relationships, verify:

```cypher
// 1. Check case now has defendants
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})-[:HAS_DEFENDANT]->(d:Defendant)
RETURN d.name
// Expected: ["CAAL WORLDWIDE, INC.", "Unknown Driver"]

// 2. Check attorneys represent case
MATCH (a:Attorney)-[:REPRESENTS_CLIENT]->(c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
RETURN a.name
// Expected: ["Aaron G. Whaley", "Bryce Koon"]

// 3. Check attorneys work at law firm
MATCH (a:Attorney)-[:WORKS_AT]->(lf:LawFirm)
WHERE a.name IN ["Aaron G. Whaley", "Bryce Koon"]
RETURN a.name, lf.name
// Expected: Both → "The Whaley Law Firm"

// 4. Count total relationships for case
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})-[r]-()
RETURN count(r) as total_relationships
// Expected: ~95 (was ~91, should be +4)
```

---

## Summary

**Q: Does the schema exist in the graph?**

**A: YES, the schema is fully defined in Pydantic models.**

**Relationship types you need:**
- ✅ HasDefendant - graphiti_client.py line 801
- ✅ RepresentsClient - graphiti_client.py line 806
- ✅ FiledIn - graphiti_client.py line 812
- ✅ WorksAt - Already in use
- ✅ About (Episode → Entity) - graphiti_client.py line ~850
- ✅ All 71 relationship types defined

**They just haven't been CREATED yet because:**
1. Manual review still in progress (3 of 138 cases approved)
2. Waiting for bulk ingestion
3. Reference data (divisions, judges, doctors) staged in JSON files

**You can create these relationships NOW** for Abby Sitgraves as a test case!

---

## Files Created

1. ✅ `SCHEMA_REALITY_CHECK.md` - Full schema comparison
2. ✅ `ENTITY_MAPPING_Abby-Sitgraves.md` - Entity mapping analysis
3. ✅ `ABBY_SITGRAVES_GRAPH_ACTIONS.md` - This file (action plan)

**Next:** Want me to create the Cypher script to add these 4 relationships to the graph?
