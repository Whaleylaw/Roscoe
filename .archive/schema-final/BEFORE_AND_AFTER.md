# Graph State: Before vs After Migration

**Date:** January 4, 2026

---

## BEFORE (Current Graph State)

### Total
- **Nodes:** 33,852
- **Relationships:** 21,758
- **Entity Types:** 45 labels

### Complete Entity Breakdown

| Entity Type | Count | Will Be... |
|-------------|-------|------------|
| Doctor | 20,708 | ✅ KEPT |
| LandmarkStatus | 8,991 | ✅ KEPT |
| **MedicalProvider** | **1,998** | ❌ **DELETED** |
| Entity | 196 | ✅ KEPT |
| Pleading | 168 | ✅ KEPT |
| Adjuster | 148 | ✅ KEPT |
| CourtClerk | 121 | ✅ KEPT |
| PIPClaim | 120 | ✅ KEPT |
| BIClaim | 119 | ✅ KEPT |
| Court | 118 | ✅ KEPT |
| Case | 111 | ✅ KEPT |
| Client | 110 | ✅ KEPT |
| MasterCommissioner | 108 | ✅ KEPT |
| Lien | 103 | ✅ KEPT |
| CircuitJudge | 101 | ✅ KEPT |
| Insurer | 99 | ✅ KEPT |
| DistrictDivision | 94 | ✅ KEPT |
| DistrictJudge | 94 | ✅ KEPT |
| CircuitDivision | 86 | ✅ KEPT |
| Landmark | 82 | ✅ KEPT |
| LienHolder | 50 | ✅ KEPT |
| Vendor | 39 | ✅ KEPT |
| WorkflowDef | 39 | ✅ KEPT |
| Attorney | 35 | ✅ KEPT |
| LawFirm | 28 | ✅ KEPT |
| WorkflowTemplate | 28 | ✅ KEPT |
| WorkflowTool | 21 | ✅ KEPT |
| Organization | 19 | ✅ KEPT |
| AppellateJudge | 15 | ✅ KEPT |
| UMClaim | 14 | ✅ KEPT |
| WorkflowChecklist | 12 | ✅ KEPT |
| Phase | 9 | ✅ KEPT |
| SupremeCourtJustice | 8 | ✅ KEPT |
| CourtAdministrator | 7 | ✅ KEPT |
| Defendant | 7 | ✅ KEPT |
| **HealthSystem** | **6** | ✅ **UPDATED** |
| CaseManager | 6 | ✅ KEPT |
| SupremeCourtDistrict | 7 | ✅ KEPT |
| AppellateDistrict | 5 | ✅ KEPT |
| SubPhase | 5 | ✅ KEPT |
| WCClaim | 5 | ✅ KEPT |
| Mediator | 3 | ✅ KEPT |
| UIMClaim | 2 | ✅ KEPT |
| Expert | 2 | ✅ KEPT |
| Witness | 1 | ✅ KEPT |

**Total entities to KEEP:** 31,854 (94%)
**Total entities to DELETE:** 1,998 (6%)

---

## AFTER (Projected Graph State)

### Total
- **Nodes:** 35,343 (+1,491 net)
- **Relationships:** 23,086+ (+1,328 net minimum)
- **Entity Types:** 52 labels (+7 new types)

### New Medical Provider Structure

| Entity Type | Count | Status |
|-------------|-------|--------|
| HealthSystem | 6 | ✅ Updated (0 net change) |
| **Facility** | **1,164** | ⭐ **NEW** |
| **Location** | **2,325** | ⭐ **NEW** |
| MedicalProvider | 0 | ❌ Deleted |

**Net change:** +1,491 nodes (3,489 new - 1,998 deleted)

### New Insurance Entities (0 initially)

| Entity Type | Count | Status |
|-------------|-------|--------|
| **InsurancePolicy** | 0 | ⭐ NEW (type exists, data created later) |
| **InsurancePayment** | 0 | ⭐ NEW (type exists, data created later) |

**Created later from case data**

### New Medical/Legal Entities (0 initially)

| Entity Type | Count | Status |
|-------------|-------|--------|
| **MedicalVisit** | 0 | ⭐ NEW (created during chronology) |
| **CourtEvent** | 0 | ⭐ NEW (created from calendar) |
| **LawFirmOffice** | 0 | ⭐ NEW (created as needed) |

**Created later from case work**

### All Other Entities (UNCHANGED)

**Exact same counts as before:**
- Doctor: 20,708
- LandmarkStatus: 8,991
- Entity: 196
- Pleading: 168
- ... (all others same)

---

## Relationships: Before vs After

### BEFORE (Current)

**Medical Provider relationships (1,545 total):**
- 899 MedicalProvider → HealthSystem (PART_OF)
- 329 Case → MedicalProvider (TREATING_AT)
- 317 Client → MedicalProvider (TREATED_BY)

**All other relationships (~20,213):**
- Insurance relationships
- Court hierarchy
- Case workflow
- Attorney relationships
- Etc.

### AFTER (Projected)

**New Hierarchy relationships (2,873 new):**
- 2,325 Location → Facility (PART_OF)
- 548 Facility → HealthSystem (PART_OF)

**Deleted relationships (-1,545):**
- All MedicalProvider relationships gone

**Unchanged relationships (~20,213):**
- All insurance relationships ✅
- All court hierarchy ✅
- All case workflow ✅
- All attorney relationships ✅

**Net:** 23,086 total (20,213 kept + 2,873 new)

---

## Critical Data Preservation

### 100% Preserved ✅

**These relationships NEVER get touched:**

1. **Case Relationships:**
   - Case → Client (HAS_CLIENT) - 111 relationships ✅
   - Case → Claim (HAS_CLAIM) - ~260 relationships ✅
   - Case → Lien (HAS_LIEN) - ~103 relationships ✅
   - Case → Phase (IN_PHASE) - ~111 relationships ✅
   - Case → LandmarkStatus (HAS_STATUS) - 8,991 relationships ✅

2. **Insurance Relationships:**
   - Claim → Insurer (INSURED_BY) - ~260 relationships ✅
   - Claim → Adjuster (ASSIGNED_ADJUSTER) - ~120 relationships ✅
   - Adjuster → Insurer (WORKS_AT) - ~50 relationships ✅

3. **Court Relationships:**
   - Division → Court (PART_OF) - 192 relationships ✅
   - Judge → Division (PRESIDES_OVER) - 63 relationships ✅
   - Clerk/Commissioner → Court (WORKS_AT/APPOINTED_BY) - ~50 relationships ✅

4. **Attorney Relationships:**
   - Attorney → LawFirm (WORKS_AT) - ~25 relationships ✅
   - CaseManager → LawFirm (WORKS_AT) - ~6 relationships ✅

5. **Workflow Relationships:**
   - Phase → Landmark (HAS_LANDMARK) - ~82 relationships ✅
   - Phase → WorkflowDef (HAS_WORKFLOW) - ~39 relationships ✅
   - LandmarkStatus → Landmark (FOR_LANDMARK) - 8,991 relationships ✅

**Total preserved:** ~20,213 relationships (93%)

### Temporarily Lost (Will Rebuild)

**These relationships get deleted:**
- Case → MedicalProvider (TREATING_AT) - 329 relationships ❌
- Client → MedicalProvider (TREATED_BY) - 317 relationships ❌
- MedicalProvider → HealthSystem (PART_OF) - 899 relationships ❌

**Total deleted:** ~1,545 relationships (7%)

**How to rebuild:**
- Review medical records for each case
- Create Client → Location/Facility (TREATED_AT)
- Based on actual records, not old fuzzy data

---

## Summary

### What Gets Deleted
- **MedicalProvider nodes:** 1,998 (6% of graph)
- **Related relationships:** 1,545 (7% of relationships)

### What Stays Untouched
- **All other nodes:** 31,854 (94% of graph) ✅
- **All other relationships:** 20,213 (93% of relationships) ✅

### What Gets Added
- **New nodes:** 3,489 (Facility + Location, HealthSystem updated in place)
- **New relationships:** 2,873 (hierarchy relationships)

### Net Result
- **Nodes:** 33,852 → 35,343 (+1,491)
- **Relationships:** 21,758 → 23,086 (+1,328)
- **Better structure:** 3-tier hierarchy vs flat
- **Multi-role ready:** Same entity can be provider/defendant/vendor
- **Progressive detail:** Can link to Facility or Location

---

## Risk Level: LOW ✅

**Why low risk:**
- 94% of graph untouched
- Only replacing one entity type (MedicalProvider)
- All critical data preserved (cases, insurance, courts)
- Backup available
- Can rebuild provider connections from records

**Only downside:**
- Temporary loss of case → provider connections
- Expected as part of "clean slate" approach
- Will be rebuilt accurately from medical records

---

## ✅ Ready to Proceed?

**Review:**
1. This BEFORE_AND_AFTER.md
2. MIGRATION_PLAN.md
3. Entity data files in entities/

**Once approved:**
- Backup graph
- Delete MedicalProvider nodes (1,998)
- Ingest new structure (3,489 entities)
- Verify data integrity
- Ready for episode ingestion!
