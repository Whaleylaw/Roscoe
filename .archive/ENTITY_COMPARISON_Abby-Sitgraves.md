# Entity Comparison: Abby Sitgraves Case
## Graph vs Merged Episode Data

**Case:** Abby-Sitgraves-MVA-7-13-2024
**Date:** January 2, 2026

---

## Current Graph State

### ✅ Entities Connected to Case

| Entity Type | Entity Name | Relationship | In Graph |
|-------------|-------------|--------------|----------|
| **Client** | Abby Sitgraves | HAS_CLIENT | ✅ Yes |
| **PIPClaim** | Abby-Sitgraves-MVA-7-13-2024-Personal Injury Protection (PIP)-633859-N | HAS_CLAIM | ✅ Yes |
| **Adjuster** | Jordan Bahr | ASSIGNED_ADJUSTER (via PIPClaim) | ✅ Yes |
| **Insurer** | National Indemnity Company | INSURED_BY (via PIPClaim) | ✅ Yes |
| **MedicalProvider** | Foundation Radiology | TREATING_AT | ✅ Yes |
| **MedicalProvider** | Jewish Hospital | TREATING_AT | ✅ Yes |
| **MedicalProvider** | UofL Physicians - Orthopedics | TREATING_AT | ✅ Yes |
| **Lien** | Abby-Sitgraves-MVA-7-13-2024-Key Benefit Administrators | HAS_LIEN | ✅ Yes |
| **LienHolder** | Key Benefit Administrators | HAS_LIEN_FROM (via Lien) | ✅ Yes |
| **Phase** | onboarding | IN_PHASE | ✅ Yes |
| **LandmarkStatus** | (82 landmarks) | HAS_STATUS | ✅ Yes |

**Total entities connected:** 93 (82 landmark statuses + 11 core entities)

---

## Merged Episode Data (33 Unique Entities)

### Client (2)
- ✅ **Abby Sitgraves** - EXISTS in graph
- ❌ **Nayram Adadevoh** - NOT in graph (likely attorney's client, mentioned in episode)

### Medical Providers (4)
- ✅ **Foundation Radiology** - EXISTS in graph
- ✅ **Jewish Hospital** - EXISTS in graph
- ✅ **UofL Physicians - Orthopedics** - EXISTS in graph
- ✅ **Saint Mary and Elizabeth Hospital** - EXISTS in graph (as "Saint Mary and Elizabeth Hospital")

### Insurance (4)
- ✅ **National Indemnity Company** - EXISTS in graph (connected via PIPClaim)
- ✅ **Kentucky Farm Bureau** - EXISTS in graph
- ✅ **State Farm Insurance Company** - EXISTS in graph
- ✅ **Jordan Bahr** (Adjuster) - EXISTS in graph (connected to PIPClaim)

### Claims (1)
- ✅ **National Indemnity Company** (PIPClaim) - EXISTS in graph

### Liens (1)
- ✅ **Key Benefit Administrators** - EXISTS in graph

### Legal - Whaley Law Firm (4)
- ✅ **Aaron G. Whaley** (Attorney) - EXISTS in graph
- ✅ **Bryce Koon** (Attorney) - EXISTS in graph
- ✅ **Sarena Tuttle** (CaseManager) - EXISTS in graph
- ❓ **Jessa** (Attorney in episodes, actually CaseManager "Jessa Galosmo") - EXISTS in graph as CaseManager

### Legal - Law Firms (4)
- ✅ **The Whaley Law Firm** - EXISTS in graph
- ❌ **Blackburn Domene & Burchett, PLLC** - NOT in graph
- ❌ **Carlisle Law** - NOT in graph
- ❌ **Law Office of Bryan B. Davenport, P.C.** - NOT in graph

### Legal - Other Attorneys (8)
- ❌ **Amy Scott** - NOT in graph
- ❌ **Bruce Anderson** - NOT in graph
- ❌ **Bryan Davenport** - NOT in graph
- ✅ **Bryce Cotton** - EXISTS in graph
- ❌ **Derek Anthony Harvey** - NOT in graph
- ❌ **John Doyle** - NOT in graph
- ❌ **Marshall Rowland** - NOT in graph
- ❌ **Samuel Robert Leffert** - NOT in graph
- ❌ **Seth Gladstein** - NOT in graph

### Defendants (2)
- ❓ **CAAL WORLDWIDE, INC.** - Graph has "CAALWINC" (close match, likely same entity)
- ❌ **Unknown Driver** - NOT in graph

### Courts (1)
- ❓ **Jefferson County Circuit Court, Division II** - Division not in graph (base court exists)

### Organizations (1)
- ❌ **Kentucky Court Of Justice** - NOT in graph

---

## Entity Status Summary

| Status | Count | Entities |
|--------|-------|----------|
| ✅ **Exact Match in Graph** | 13 | Client, 3 MedicalProviders, 3 Insurers, 1 Adjuster, 1 Lien, 2 Attorneys, 1 CaseManager, 1 LawFirm |
| ❓ **Close Match (Verify)** | 2 | CAALWINC vs CAAL WORLDWIDE, INC., Jessa vs Jessa Galosmo |
| ❌ **Not in Graph** | 18 | 8 Attorneys, 3 Law Firms, 1 Defendant, 1 Court Division, 1 Client, 1 Organization, 1 MedicalProvider |

---

## Analysis by Category

### ✅ Core Case Entities (ALL EXIST)
All essential case entities are already in the graph:
- Client: Abby Sitgraves ✓
- PIPClaim with National Indemnity ✓
- Adjuster: Jordan Bahr ✓
- Medical Providers: 3/4 treating providers ✓
- Lien: Key Benefit Administrators ✓

### ⚠️ Litigation Entities (PARTIAL)
- **In Graph:** Aaron G. Whaley, Bryce Koon (Whaley attorneys)
- **Missing:** 8 opposing counsel attorneys (Amy Scott, Bruce Anderson, etc.)
- **Missing:** 3 opposing law firms

**Why missing?** These are likely opposing counsel mentioned in episode narratives but not yet created as graph entities for this case.

### ⚠️ Structural Entities (MISSING)
- **Court Division:** Jefferson County Circuit Court, Division II not in graph
  - Base court "Jefferson County Circuit Court" exists
  - Division entities haven't been ingested yet (part of Phase 3)
- **Defendant:** CAAL WORLDWIDE, INC.
  - Graph has "CAALWINC" - likely same entity (abbreviation)
  - "Unknown Driver" not in graph

### ⚠️ Reference Entities (CONTEXTUAL)
- **Nayram Adadevoh** - Likely another attorney's client mentioned in correspondence
- **Kentucky Court Of Justice** - System/organization reference
- **Saint Mary and Elizabeth Hospital** - May already exist, need to verify exact name match

---

## Recommendations

### Option 1: Connect Existing Entities Only (Conservative)

Create relationships ONLY for entities that already exist in graph:

```cypher
// Connect Whaley attorneys
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (a:Attorney {name: "Aaron G. Whaley"})
CREATE (a)-[:REPRESENTS_CLIENT]->(c)

MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (a:Attorney {name: "Bryce Koon"})
CREATE (a)-[:REPRESENTS_CLIENT]->(c)

// Connect law firm
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (lf:LawFirm {name: "The Whaley Law Firm"})
CREATE (lf)-[:REPRESENTS_CLIENT]->(c)

// Connect case managers (if relationship type exists)
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (cm:CaseManager {name: "Sarena Tuttle"})
CREATE (cm)-[:MANAGES_CASE]->(c)

// Connect other insurers (mentioned in episodes)
MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (i:Insurer {name: "State Farm Insurance Company"})
CREATE (c)-[:HAS_INSURER]->(i)

MATCH (c:Case {name: "Abby-Sitgraves-MVA-7-13-2024"})
MATCH (i:Insurer {name: "Kentucky Farm Bureau"})
CREATE (c)-[:HAS_INSURER]->(i)
```

**Result:** ~8 new relationships, no new entities created

### Option 2: Create Missing Entities (Comprehensive)

Create all entities from merged file that don't exist:

**Create:**
1. 8 opposing attorneys (Amy Scott, Bruce Anderson, etc.)
2. 3 opposing law firms
3. 1 defendant (Unknown Driver)
4. 1 court division (Jefferson County Circuit Court, Division II)
5. 1 organization (Kentucky Court Of Justice)

Then create all ABOUT relationships from episodes.

**Result:** ~18 new entities + ~320 ABOUT relationships

### Option 3: Verify CAALWINC Match First

```cypher
// Check CAALWINC details
MATCH (d:Defendant {name: "CAALWINC"})
RETURN d
```

If it's an abbreviation of "CAAL WORLDWIDE, INC.":
- Update entity name to full version
- Connect to case with HAS_DEFENDANT relationship

---

## Questions to Resolve

1. **CAALWINC vs CAAL WORLDWIDE, INC.**
   - Same entity? (likely yes)
   - Update name or keep abbreviation?

2. **Opposing Counsel**
   - Create individual attorney entities for all 8?
   - Or just track via episodes (ABOUT relationships)?

3. **Court Division**
   - Wait for Phase 3 division ingestion?
   - Or create now for this case?

4. **Saint Mary and Elizabeth Hospital**
   - Verify it exists in MedicalProvider list
   - Check if exact name match

5. **Relationship Types**
   - REPRESENTS_CLIENT exists?
   - MANAGES_CASE exists?
   - HAS_DEFENDANT exists?
   - FILED_IN exists?

---

## Next Action

**Recommendation:** Start with Option 1 (connect existing entities) to verify the relationship types work, then decide if we need to create missing entities or wait for bulk Phase 3 ingestion.

Let me know which approach you prefer!
