# Entity Mapping: Abby Sitgraves Case → Graph

**Case:** Abby-Sitgraves-MVA-7-13-2024
**Date:** January 2, 2026

---

## Merged File Entities vs Graph Entities

### ✅ CLIENT (2 in merged → 1 in graph)

| Entity Name | In Graph? | Connected to Case? | Action |
|-------------|-----------|-------------------|--------|
| **Abby Sitgraves** | ✅ Yes | ✅ Yes (HAS_CLIENT) | None needed |
| Nayram Adadevoh | ❌ No | N/A | **Decision:** Skip (likely mentioned as another attorney's client) |

---

### ✅ MEDICAL PROVIDERS (4 in merged → 4 in graph)

| Entity Name | In Graph? | Connected to Case? | Action |
|-------------|-----------|-------------------|--------|
| **Foundation Radiology** | ✅ Yes | ✅ Yes (TREATING_AT) | None needed |
| **Jewish Hospital** | ✅ Yes | ✅ Yes (TREATING_AT) | None needed |
| **UofL Physicians - Orthopedics** | ✅ Yes | ✅ Yes (TREATING_AT) | None needed |
| **Saint Mary and Elizabeth Hospital** | ✅ Yes | ✅ Yes (TREATING_AT) | None needed |

---

### ⚠️ INSURANCE (4 in merged → 3 in graph, 1 connected)

| Entity Name | In Graph? | Connected to Case? | Action |
|-------------|-----------|-------------------|--------|
| **National Indemnity Company** | ✅ Yes | ✅ Yes (via PIPClaim) | None needed |
| **Jordan Bahr** (Adjuster) | ✅ Yes | ✅ Yes (via PIPClaim) | None needed |
| **State Farm Insurance Company** | ✅ Yes | ❌ No | **ADD:** Case relationship |
| **Kentucky Farm Bureau** | ✅ Yes | ❌ No | **ADD:** Case relationship |

---

### ⚠️ CLAIMS (1 in merged → 1 in graph)

| Entity Name | In Graph? | Connected to Case? | Action |
|-------------|-----------|-------------------|--------|
| **National Indemnity Company** (PIPClaim) | ✅ Yes | ✅ Yes (HAS_CLAIM) | None needed |

**Note:** Merged file shows "National Indemnity Company" as the PIPClaim reference (consolidated from variants). The actual claim entity name in graph is the full claim ID.

---

### ⚠️ LIENS (1 in merged → 1 in graph)

| Entity Name | In Graph? | Connected to Case? | Action |
|-------------|-----------|-------------------|--------|
| **Key Benefit Administrators** | ✅ Yes | ✅ Yes (via Lien) | None needed |

---

### ⚠️ WHALEY LAW FIRM ENTITIES (4 in merged → 4 in graph, 0 connected)

| Entity Name | Type | In Graph? | Connected to Case? | Action |
|-------------|------|-----------|-------------------|--------|
| **Aaron G. Whaley** | Attorney | ✅ Yes | ❌ No | **ADD:** Case relationship |
| **Bryce Koon** | Attorney | ✅ Yes | ❌ No | **ADD:** Case relationship |
| **Sarena Tuttle** | CaseManager | ✅ Yes | ❌ No | **ADD:** Case relationship |
| **Jessa** (Jessa Galosmo) | CaseManager | ✅ Yes | ❌ No | **ADD:** Case relationship |
| **The Whaley Law Firm** | LawFirm | ✅ Yes | ❌ No | **ADD:** Case relationship |

---

### ❌ OPPOSING COUNSEL (11 in merged → 1 in graph)

| Entity Name | Type | In Graph? | Action |
|-------------|------|-----------|--------|
| Amy Scott | Attorney | ❌ No | **Skip** (episode reference only) |
| Bruce Anderson | Attorney | ❌ No | **Skip** (episode reference only) |
| Bryan Davenport | Attorney | ❌ No | **Skip** (episode reference only) |
| Bryce Cotton | Attorney | ✅ Yes | **Decision:** Connect or skip? |
| Derek Anthony Harvey | Attorney | ❌ No | **Skip** (episode reference only) |
| John Doyle | Attorney | ❌ No | **Skip** (episode reference only) |
| Marshall Rowland | Attorney | ❌ No | **Skip** (episode reference only) |
| Samuel Robert Leffert | Attorney | ❌ No | **Skip** (episode reference only) |
| Seth Gladstein | Attorney | ❌ No | **Skip** (episode reference only) |
| Blackburn Domene & Burchett, PLLC | LawFirm | ❌ No | **Skip** (episode reference only) |
| Carlisle Law | LawFirm | ❌ No | **Skip** (episode reference only) |
| Law Office of Bryan B. Davenport, P.C. | LawFirm | ❌ No | **Skip** (episode reference only) |

**Rationale:** These attorneys are mentioned in episode narratives (email correspondence, opposing counsel) but aren't essential for case structure. They'll be linked via Episode → ABOUT relationships when episodes are ingested.

---

### ❌ DEFENDANTS (2 in merged → 1 in graph as "CAALWINC")

| Entity Name | In Graph? | Connected to Case? | Action |
|-------------|-----------|-------------------|--------|
| **CAAL WORLDWIDE, INC.** | ⚠️ Partial (as "CAALWINC") | ❌ No | **UPDATE:** Rename CAALWINC → CAAL WORLDWIDE, INC., then connect |
| Unknown Driver | ❌ No | N/A | **CREATE:** New defendant entity, then connect |

---

### ❌ COURTS (1 in merged → 0 divisions in graph)

| Entity Name | In Graph? | Action |
|-------------|-----------|--------|
| **Jefferson County Circuit Court, Division II** | ❌ No (base court exists) | **Wait for Phase 3** (division entities not yet ingested) |

**Alternative:** Create division entity now for this case specifically.

---

### ❌ ORGANIZATIONS (1 in merged → probably exists)

| Entity Name | In Graph? | Action |
|-------------|-----------|--------|
| Kentucky Court Of Justice | ❓ Unknown | **Skip** (generic reference to court system) |

---

## Available Relationship Types (From Graph Schema)

Based on `CALL db.relationshipTypes()`:

| Relationship | Current Usage | Can Use For |
|--------------|---------------|-------------|
| **HAS_CLIENT** | Case → Client | ✅ Already used |
| **HAS_CLAIM** | Case → Claim | ✅ Already used |
| **PLAINTIFF_IN** | Case → Defendant | ✅ Use for defendants |
| **TREATING_AT** | Case → MedicalProvider | ✅ Already used |
| **HAS_LIEN** | Case → Lien | ✅ Already used |
| **HAS_LIEN_FROM** | Case → LienHolder | ✅ Already used |
| **WORKS_AT** | Person → Organization | ✅ Use for Attorney/CaseManager → LawFirm |
| **ASSIGNED_ADJUSTER** | Claim → Adjuster | ✅ Already used |
| **INSURED_BY** | Claim → Insurer | ✅ Already used |
| **RELATES_TO** | Generic | ⚠️ Avoid (too generic) |
| **MENTIONS** | Generic | ⚠️ Avoid (too generic) |

**Missing relationship types we need:**
- `REPRESENTS_CLIENT` (Attorney → Case) - **NOT in graph!**
- `MANAGES_CASE` (CaseManager → Case) - **NOT in graph!**
- `HAS_DEFENDANT` (Case → Defendant) - **NOT in graph!** (use PLAINTIFF_IN instead)
- `HAS_INSURER` (Case → Insurer) - **NOT in graph!**
- `FILED_IN` (Case → Court/Division) - **NOT in graph!**

---

## Proposed Actions (Phase 1)

### 1. Update CAALWINC Name

```cypher
MATCH (d:Defendant {name: "CAALWINC"})
SET d.name = "CAAL WORLDWIDE, INC."
RETURN d.name
```

### 2. Connect Defendants to Case

```cypher
// Connect CAAL WORLDWIDE
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (d:Defendant {name: "CAAL WORLDWIDE, INC."})
MERGE (c)-[:PLAINTIFF_IN]->(d)

// Create and connect Unknown Driver
CREATE (d:Defendant {
  name: "Unknown Driver",
  group_id: "roscoe_graph",
  created_at: datetime()
})
WITH d
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MERGE (c)-[:PLAINTIFF_IN]->(d)
```

### 3. Connect Attorneys to Law Firm

```cypher
// Aaron G. Whaley → The Whaley Law Firm
MATCH (a:Attorney {name: "Aaron G. Whaley"})
MATCH (lf:LawFirm {name: "The Whaley Law Firm"})
MERGE (a)-[:WORKS_AT]->(lf)

// Bryce Koon → The Whaley Law Firm
MATCH (a:Attorney {name: "Bryce Koon"})
MATCH (lf:LawFirm {name: "The Whaley Law Firm"})
MERGE (a)-[:WORKS_AT]->(lf)

// Sarena Tuttle → The Whaley Law Firm
MATCH (cm:CaseManager {name: "Sarena Tuttle"})
MATCH (lf:LawFirm {name: "The Whaley Law Firm"})
MERGE (cm)-[:WORKS_AT]->(lf)

// Jessa Galosmo → The Whaley Law Firm
MATCH (cm:CaseManager {name: "Jessa Galosmo"})
MATCH (lf:LawFirm {name: "The Whaley Law Firm"})
MERGE (cm)-[:WORKS_AT]->(lf)
```

### 4. Create Law Firm → Case Relationship

**Problem:** No relationship type exists for LawFirm → Case or Attorney → Case!

**Options:**
- **A.** Use RELATES_TO (generic, not ideal)
- **B.** Create new relationship type REPRESENTS_CLIENT
- **C.** Wait for schema update before connecting

### 5. Connect Additional Insurers (if relationship type exists)

State Farm and Kentucky Farm Bureau are mentioned in episodes but not connected to case.

**Problem:** No HAS_INSURER relationship type exists!

**Alternative:** These insurers may be connected to other claims (UM/UIM) that haven't been created yet.

---

## Summary

### ✅ Already Complete (9 entities connected)
- Client, 4 MedicalProviders, 1 PIPClaim, 1 Adjuster, 1 Insurer, 1 Lien, 1 LienHolder

### ⚠️ Can Connect Now (with existing relationship types)
- **2 Defendants** (1 rename + 1 create) → use PLAINTIFF_IN
- **4 Whaley staff** → use WORKS_AT to connect to LawFirm

### ❌ Blocked (missing relationship types)
- **Cannot connect attorneys to case** - No REPRESENTS_CLIENT relationship type
- **Cannot connect case managers to case** - No MANAGES_CASE relationship type
- **Cannot connect law firm to case** - No REPRESENTS_CLIENT relationship type
- **Cannot connect insurers to case directly** - No HAS_INSURER relationship type
- **Cannot connect court** - No FILED_IN relationship type, and division doesn't exist

### 📋 Decision Needed

**Option A: Add Missing Relationship Types to Schema**
- Create REPRESENTS_CLIENT, MANAGES_CASE, HAS_INSURER, FILED_IN
- Then connect all entities

**Option B: Use RELATES_TO for Everything**
- Generic relationship (not ideal for typed queries)
- Works but loses semantic meaning

**Option C: Wait for Full Schema Implementation**
- Complete manual review for all 138 cases
- Implement complete schema with all relationship types
- Bulk ingestion with proper relationships

---

## Recommendation

**Phase 1a (Do Now):**
1. Rename CAALWINC → CAAL WORLDWIDE, INC.
2. Create Unknown Driver defendant
3. Connect both defendants via PLAINTIFF_IN

**Phase 1b (After Schema Update):**
4. Add missing relationship types (REPRESENTS_CLIENT, MANAGES_CASE, HAS_INSURER, FILED_IN)
5. Connect Whaley attorneys/managers to case
6. Connect additional insurers

**Phase 2 (After All Reviews):**
7. Create Episode nodes
8. Create ABOUT relationships

**Phase 3 (Bulk):**
9. Ingest court divisions
10. Ingest opposing counsel entities (via episodes)

---

## Files Reference

- `ENTITY_COMPARISON_Abby-Sitgraves.md` - Detailed entity comparison
- `GRAPH_ACTION_PLAN_Abby-Sitgraves.md` - Proposed actions with Cypher queries
- `merged_Abby-Sitgraves-MVA-7-13-2024.json` - Source data (33 entities, 93 episodes)
- `merged_Abby-Sitgraves-MVA-7-13-2024.md` - Human-readable summary

**Next:** Decide whether to add missing relationship types now or wait for schema completion.
