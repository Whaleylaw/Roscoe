# Graph Action Plan: Abby Sitgraves Case

**Case:** Abby-Sitgraves-MVA-7-13-2024
**Generated:** January 2, 2026

---

## Current State

### ✅ Entities Already in Graph (13)

**Connected to Case:**
1. Client: Abby Sitgraves (HAS_CLIENT)
2. PIPClaim: Abby-Sitgraves-MVA-7-13-2024-Personal Injury Protection (PIP)-633859-N (HAS_CLAIM)
3. Adjuster: Jordan Bahr (via PIPClaim → ASSIGNED_ADJUSTER)
4. Insurer: National Indemnity Company (via PIPClaim → INSURED_BY)
5. MedicalProvider: Foundation Radiology (TREATING_AT)
6. MedicalProvider: Jewish Hospital (TREATING_AT)
7. MedicalProvider: UofL Physicians - Orthopedics (TREATING_AT)
8. MedicalProvider: Saint Mary and Elizabeth Hospital (TREATING_AT)
9. Lien: Abby-Sitgraves-MVA-7-13-2024-Key Benefit Administrators (HAS_LIEN)
10. LienHolder: Key Benefit Administrators (via Lien → HAS_LIEN_FROM)
11. Phase: onboarding (IN_PHASE)
12. LandmarkStatus: 82 landmarks (HAS_STATUS)

**In Graph But NOT Connected:**
1. Attorney: Aaron G. Whaley
2. Attorney: Bryce Koon
3. Attorney: Bryce Cotton
4. CaseManager: Sarena Tuttle
5. CaseManager: Jessa Galosmo
6. LawFirm: The Whaley Law Firm
7. Insurer: State Farm Insurance Company
8. Insurer: Kentucky Farm Bureau
9. Defendant: CAALWINC (close match to "CAAL WORLDWIDE, INC.")
10. Court: Jefferson County Circuit Court

---

## Entities in Merged Episodes But NOT in Graph (18)

### Attorneys (8 opposing counsel)
1. Amy Scott
2. Bruce Anderson
3. Bryan Davenport
4. Derek Anthony Harvey
5. John Doyle
6. Marshall Rowland
7. Samuel Robert Leffert
8. Seth Gladstein

### Law Firms (3 opposing firms)
1. Blackburn Domene & Burchett, PLLC
2. Carlisle Law
3. Law Office of Bryan B. Davenport, P.C.

### Defendants (1)
1. Unknown Driver

### Clients (1)
1. Nayram Adadevoh (likely another client mentioned in correspondence)

### Courts (1)
1. Jefferson County Circuit Court, Division II (division not in graph)

### Organizations (1)
1. Kentucky Court Of Justice

### Medical Providers (1)
1. Saint Mary and Elizabeth Hospital - ✅ **Actually EXISTS** (verified above)

---

## Proposed Actions

### Phase 1: Connect Existing Whaley Entities (Priority)

These entities exist in graph but aren't connected to the case:

```cypher
// 1. Connect Whaley attorneys (if REPRESENTS_CLIENT relationship exists)
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (a:Attorney {name: "Aaron G. Whaley"})
MERGE (a)-[:REPRESENTS_CLIENT]->(c)

MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (a:Attorney {name: "Bryce Koon"})
MERGE (a)-[:REPRESENTS_CLIENT]->(c)

// 2. Connect Whaley law firm
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (lf:LawFirm {name: "The Whaley Law Firm"})
MERGE (lf)-[:REPRESENTS_CLIENT]->(c)

// 3. Connect case managers (if MANAGES_CASE relationship exists)
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (cm:CaseManager {name: "Sarena Tuttle"})
MERGE (cm)-[:MANAGES_CASE]->(c)

// 4. Connect State Farm and KFB insurers
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (i:Insurer {name: "State Farm Insurance Company"})
MERGE (c)-[:HAS_INSURER]->(i)

MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (i:Insurer {name: "Kentucky Farm Bureau"})
MERGE (c)-[:HAS_INSURER]->(i)

// 5. Fix CAALWINC name and connect as defendant
MATCH (d:Defendant {name: "CAALWINC"})
SET d.name = "CAAL WORLDWIDE, INC."

MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (d:Defendant {name: "CAAL WORLDWIDE, INC."})
MERGE (c)-[:HAS_DEFENDANT]->(d)
```

**Result:** 8 new relationships, 0 new entities, 1 entity name update

### Phase 2: Create Missing Core Entities (Optional)

Only create entities that are essential for the case:

```cypher
// Create Unknown Driver defendant
CREATE (d:Defendant {
  name: "Unknown Driver",
  group_id: "roscoe_graph",
  created_at: datetime()
})

MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (d:Defendant {name: "Unknown Driver"})
CREATE (c)-[:HAS_DEFENDANT]->(d)
```

**Result:** 1 new entity, 1 new relationship

### Phase 3: Episode Ingestion (After All Reviews Complete)

Create Episode nodes and ABOUT relationships:

```cypher
// For each of the 93 episodes:
CREATE (ep:Episodic {
  uuid: "<uuid>",
  name: "Justin Chumbley - 2024-07-18",
  content: "Abby Sitgraves is the client...",
  natural_language: "...",
  valid_at: datetime("2024-07-18T00:00:00"),
  author: "Justin Chumbley",
  group_id: "roscoe_graph",
  created_at: datetime()
})

// Create ABOUT relationships
MATCH (ep:Episodic {uuid: "<uuid>"})
MATCH (client:Client {name: "Abby Sitgraves"})
CREATE (ep)-[:ABOUT]->(client)
```

**Result:** 93 Episode nodes, ~320 ABOUT relationships

---

## Decision Matrix

| Approach | New Entities | New Relationships | Effort | Timing |
|----------|--------------|-------------------|--------|--------|
| **Phase 1 Only** | 0 | 8 | Low | Now |
| **Phase 1 + 2** | 1 | 9 | Low | Now |
| **Phase 1 + 2 + 3** | 94 | ~329 | High | After all 138 reviews |
| **Wait for Bulk** | 0 | 0 | None | After all 138 reviews |

---

## Recommended Approach

### ✅ Phase 1 (Do Now)

Connect existing Whaley entities to the case:
- 2 Attorneys (Aaron G. Whaley, Bryce Koon)
- 1 Law Firm (The Whaley Law Firm)
- 1 CaseManager (Sarena Tuttle)
- 2 Insurers (State Farm, Kentucky Farm Bureau)
- 1 Defendant (fix CAALWINC → CAAL WORLDWIDE, INC.)

**Why?** Tests that relationship types work correctly before bulk ingestion.

### ⏸️ Phase 2 & 3 (Wait)

**Opposing counsel entities** (8 attorneys, 3 law firms):
- Not essential for case operations
- Mentioned in episode narratives only
- Create during bulk Phase 3 ingestion

**Episode nodes** (93 episodes):
- Wait until all 138 cases reviewed and merged
- Bulk ingestion script for efficiency

---

## Next Step

**Check if relationship types exist in schema:**

Run these queries to verify:
1. `MATCH ()-[r:REPRESENTS_CLIENT]->() RETURN count(r)` - Attorney represents case?
2. `MATCH ()-[r:MANAGES_CASE]->() RETURN count(r)` - CaseManager manages case?
3. `MATCH ()-[r:HAS_DEFENDANT]->() RETURN count(r)` - Case has defendant?
4. `MATCH ()-[r:HAS_INSURER]->() RETURN count(r)` - Case has insurer?

If these don't exist, we need to check what the correct relationship types are from the current schema.
