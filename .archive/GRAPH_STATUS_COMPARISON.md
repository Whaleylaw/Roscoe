# Knowledge Graph Status - Documentation vs Actual

**Date:** January 2, 2026
**FalkorDB Connection:** roscoe-graphdb (port 6380)

---

## Graph Metrics

| Metric | Actual | Documentation |
|--------|--------|---------------|
| **Total Nodes** | 11,166 | 11,166 ✓ |
| **Total Relationships** | 20,805 | 20,805 ✓ |
| **Node Labels** | 31 | 58 entity types defined |
| **Relationship Types** | 25 | 71 relationship types defined |

---

## What's IN the Graph (11,166 nodes)

### **Case Operations (Active Data)**

| Entity Type | Count | Status |
|-------------|-------|--------|
| **LandmarkStatus** | 8,991 | ✓ Workflow state tracking |
| **MedicalProvider** | 773 | ⚠️ Partial (should be 2,159) |
| **Pleading** | 168 | ✓ Court filings |
| **Adjuster** | 148 | ✓ Insurance adjusters |
| **PIPClaim** | 120 | ✓ Claim entities |
| **BIClaim** | 119 | ✓ Claim entities |
| **Case** | 111 | ✓ Case entities |
| **Client** | 110 | ✓ Client entities |
| **Lien** | 103 | ✓ Lien tracking |
| **Insurer** | 99 | ✓ Insurance companies |
| **LienHolder** | 50 | ✓ Lien holders |
| **Vendor** | 39 | ✓ Service providers |
| **Attorney** | 35 | ✓ Litigation counsel |
| **LawFirm** | 28 | ✓ Law firms |
| **Court** | 23 | ✓ Court entities |
| **Organization** | 19 | ✓ Generic orgs |
| **UMClaim** | 14 | ✓ Claim entities |
| **Defendant** | 7 | ✓ Defendants |
| **CaseManager** | 6 | ✓ Paralegals |
| **WCClaim** | 5 | ✓ Workers' comp |
| **UIMClaim** | 2 | ✓ Underinsured claims |

### **Workflow State Machine**

| Entity Type | Count | Status |
|-------------|-------|--------|
| **Landmark** | 82 | ✓ Workflow checkpoints |
| **WorkflowDef** | 39 | ✓ Workflow definitions |
| **WorkflowTemplate** | 28 | ✓ Document templates |
| **WorkflowTool** | 21 | ✓ Tool references |
| **WorkflowChecklist** | 12 | ✓ Checklist definitions |
| **Phase** | 9 | ✓ Case phases |
| **SubPhase** | 5 | ✓ Litigation sub-phases |

### **Generic Graphiti Entities**

| Entity Type | Count | Status |
|-------------|-------|--------|
| **Entity** | 196 | ✓ Generic entities with embeddings |
| **Community** | 0 | ⚠️ Index exists, no nodes |
| **Episodic** | 0 | ⚠️ Index exists, no nodes (13,491 episodes pending) |

---

## What's NOT in Graph (In JSON Files, Pending Ingestion)

### **People (In JSON files, not yet ingested)**

| Entity Type | JSON Count | Graph Count | Gap |
|-------------|-----------|-------------|-----|
| **Doctor** | 20,732 | 0 | ❌ 20,732 missing |
| **CircuitJudge** | 101 | 0 | ❌ 101 missing |
| **DistrictJudge** | 94 | 0 | ❌ 94 missing |
| **CourtClerk** | 121 | 0 | ❌ 121 missing |
| **Mediator** | 2 | 0 | ❌ 2 missing |
| **Witness** | 1 | 0 | ❌ 1 missing |
| **AppellateJudge** | ? | 0 | ❌ Missing |
| **SupremeCourtJustice** | ? | 0 | ❌ Missing |

### **Organizations (In JSON files, not yet ingested)**

| Entity Type | JSON Count | Graph Count | Gap |
|-------------|-----------|-------------|-----|
| **HealthSystem** | 5 | 0 | ❌ 5 missing |
| **CircuitDivision** | 86 | 0 | ❌ 86 missing |
| **DistrictDivision** | 94 | 0 | ❌ 94 missing |
| **AppellateDistrict** | 5 | 0 | ❌ 5 missing |
| **SupremeCourtDistrict** | 7 | 0 | ❌ 7 missing |

### **MedicalProvider Discrepancy**

| Source | Count | Notes |
|--------|-------|-------|
| **In Graph** | 773 | Original providers from case data |
| **In JSON** | 2,159 | After healthcare system imports |
| **Gap** | 1,386 | Missing provider locations |

---

## Episodes and Relationships

### **Episode Status**

| Item | Count | Status |
|------|-------|--------|
| **Raw Episodes** | 17,097 | Original from Filevine |
| **Cleaned Episodes** | 13,491 | Filtered (vague/auto-generated removed) |
| **Episodic Nodes (Graph)** | 0 | ❌ Not yet ingested |
| **Proposed Relationships** | 40,605 | ABOUT relationships (pending approval) |
| **Review Files** | 138 | Generated for manual approval |
| **Approved Reviews** | 3 | Abby Sitgraves, Abigail Whaley, Alma Cristobal |
| **Pending Reviews** | 135 | Awaiting manual review |

---

## Graph Indices (For Search)

| Index | Label Type | Properties | Status |
|-------|-----------|------------|--------|
| **Entity** | NODE | uuid, group_id, name, created_at, summary | ✓ 196 docs |
| **Episodic** | NODE | uuid, group_id, created_at, valid_at, content, source | ✓ Ready (0 docs) |
| **Community** | NODE | uuid, name, group_id | ✓ Ready (0 docs) |
| **RELATES_TO** | RELATIONSHIP | uuid, group_id, name, created_at, fact | ✓ Ready (0 docs) |
| **MENTIONS** | RELATIONSHIP | uuid, group_id | ✓ Ready (0 docs) |
| **HAS_MEMBER** | RELATIONSHIP | uuid | ✓ Ready (0 docs) |

---

## Relationship Types in Graph (25)

Current relationships (all structural/workflow):
- NEXT_PHASE, HAS_WORKFLOW, HAS_LANDMARK, USES_TEMPLATE, HAS_SUB_LANDMARK, HAS_SUBPHASE
- HAS_CLIENT, ASSIGNED_ADJUSTER, HANDLES_CLAIM, HAS_CLAIM, HAS_LIEN, HAS_LIEN_FROM, HELD_BY, HOLDS
- INSURED_BY, PLAINTIFF_IN, TREATED_BY, TREATING_AT, WORKS_AT
- IN_PHASE, HAS_STATUS, FOR_LANDMARK
- RELATES_TO, MENTIONS, HAS_MEMBER

**Missing from graph** (defined in Pydantic models but not yet created):
- Professional: PRESIDES_OVER, PART_OF, RETAINED_FOR
- Medical: HAS_TREATED, FOR_BILL
- Legal: REPRESENTS_CLIENT, FILED_IN
- Documents: HAS_DOCUMENT, RECEIVED_FROM, SENT_TO, REGARDING
- Episodes: ABOUT (40,605 proposed), FOLLOWS
- ~46 other relationship types from schema

---

## Schema Alignment

### **Defined in Pydantic Models** (`graphiti_client.py`)
- 58 entity types
- 71 relationship types
- EDGE_TYPE_MAP validation rules
- Full property definitions

### **Actually in FalkorDB**
- 31 node labels (mostly case operations + workflow)
- 25 relationship types (mostly structural)
- Focus on operational data and workflow state

### **Gap Explanation**

The documentation says:
> **Entities Imported (45,900+ total):** ... Doctors 20,732, MedicalProviders 2,159, etc.

But this means "imported to **JSON files**" not "imported to **graph**".

**Current Phase:** Phase 2 - Manual Review (3 of 138 approved)
**Next Phase:** Phase 3 - Custom Graph Ingestion (after all 138 approved)

The large entity imports (doctors, judges, divisions, health systems) are **staged in JSON files** awaiting the completion of manual review before custom graph ingestion.

---

## Conclusion

### ✅ **What's Working**
1. FalkorDB running healthy with persistence enabled
2. Workflow state machine fully operational (8,991 landmark statuses)
3. Case operational data complete (111 cases, 110 clients, claims, liens)
4. Indices ready for episode ingestion
5. Metrics match documentation (11,166 nodes, 20,805 relationships)

### ⚠️ **What's Pending**
1. **~45,900 entities** staged in JSON files, not yet in graph
2. **13,491 episodes** cleaned and processed, awaiting ingestion
3. **40,605 ABOUT relationships** proposed, pending manual approval
4. **135 review files** awaiting manual review and approval
5. **1,386 medical providers** from healthcare imports not yet in graph

### 🎯 **Next Steps**
1. Continue manual review (135 files remaining)
2. Apply corrections to entity JSON files
3. Complete all 138 approvals
4. Create custom graph ingestion script (NOT using Graphiti)
5. Ingest approved episodes + ABOUT relationships
6. Ingest 45,900+ entities from JSON files
7. Add enriched embeddings for semantic search

---

**Status:** Schema documentation is **aspirational** (what will be in graph after ingestion).
**Reality:** Graph currently has **operational data + workflow state** only.
**Timeline:** Large entity ingestion happens in Phase 3, after Phase 2 (manual review) completes.

This is **by design** - manual review ensures quality before bulk ingestion.
