# Remaining Medical Providers - Summary

**Date:** January 2, 2026
**New File:** `medical-providers-REMAINING.json`

---

## Summary

Created a cleaned version of medical-providers.json with all deleted Norton/UofL providers removed.

**Original:** 574 provider entries
**Deleted:** 116 entries (33 unique provider names)
**Remaining:** 458 entries

---

## What Was Removed

### 33 Unique Provider Names Deleted

**Norton Providers (18):**
- Norton Audubon Hospital
- Norton Brownsboro Hospital
- Norton Cancer Institute - Brownsboro
- Norton Children's Medical Group
- Norton Children's Urology
- Norton Community Medical Associates - Dixie
- Norton Community Medical Associates - Preston
- Norton Hospital
- Norton Hospital - Brownsboro
- Norton Hospital Downtown
- Norton Leatherman Spine
- Norton Neurology Services-Downtown
- Norton Neuroscience Institute
- Norton Neuroscience Institute - Brownsboro
- Norton Neurosciences Spine And Rehabilitation Center
- Norton Orthopedic Institute - Audubon
- Norton Women's & Children's Hospital
- River City Orthopedics (Norton Spine Specialist-Rouben & Casnellie)

**UofL Providers (15):**
- Jewish Hospital
- Saint Mary and Elizabeth Hospital
- U of L Health Urgent Care Buechel
- University Of Louisville Hospital Radiology
- University Of Louisville Physicians
- University of Louisville Hospital
- University of Louisville Physicians (variant)
- University of Louisville School of Dentistry
- UofL ER
- UofL Health
- UofL Health - Mary & Elizabeth Mary & Elizabeth Hospital
- UofL Health - Medical Center Southwest
- UofL Medical Center East
- UofL Physicians - Orthopedics
- UofL Physicians - Podiatric Medicine & Surgery

### Why 116 Entries Removed (not 33)?

**Multiple entries per provider:**
- Some providers treated patients in multiple cases
- Each case created a separate entry in the file
- Example: "University of Louisville Hospital" had 32 entries (32 different cases)

**Breakdown:**
- 33 unique provider names
- 116 total entries across all cases
- Average: ~3.5 entries per provider name

---

## What Remains (458 entries)

### By Health System

| Category | Entries | Notes |
|----------|---------|-------|
| **Independent Providers** | 414 | Chiropractors, imaging centers, independent clinics |
| **Baptist Health** | 40 | Not yet mapped/deleted (mapping pending) |
| **Norton (remaining)** | 4 | Norton affiliates not in mapping |
| **UofL** | 0 | All UofL providers deleted ✅ |
| **TOTAL** | **458** | |

### Remaining Norton Providers (4)

These are Norton-related providers that weren't in the mapping (likely Norton affiliates or independent):

**Count:** 4 entries (need to verify what these are)

### Remaining Baptist Providers (40)

**Baptist Health providers NOT yet mapped/deleted:**
- Awaiting Baptist mapping file review
- Will be processed in next phase

### Independent Providers (414)

**Examples:**
- Starlite Chiropractic
- 100% Chiropractic
- 1st Diagnostics (if not Baptist)
- Various imaging centers
- Physical therapy clinics
- Independent orthopedic practices
- Etc.

**These are NOT part of the 6 major health systems** and should remain in the file.

---

## File Details

### New File Created

**Location:** `/Volumes/X10 Pro/Roscoe/json-files/medical-providers-REMAINING.json`

**Contents:**
- 458 provider entries
- Same format as original
- All Norton/UofL entries removed
- Baptist entries still present (pending mapping)

### Original File (Preserved)

**Location:** `/Volumes/X10 Pro/Roscoe/json-files/medical-providers.json`

**Contents:**
- 574 provider entries (unchanged)
- Backup of original data

---

## Next Steps

### Phase 1: Process Baptist Providers (When Ready)

1. Review `provider-mappings/BAPTIST_MAPPING.md`
2. Mark Baptist providers for deletion
3. Re-run script to remove Baptist entries
4. Result: Further reduced file with only independent providers

### Phase 2: Same for CHI and St. Elizabeth

After Baptist, process:
- CHI Saint Joseph Health (7 providers)
- St. Elizabeth Healthcare (6 providers)

**Final result:** medical-providers.json with ONLY independent providers (~400 entries)

---

## Statistics

**Provider Entry Removal:**
- Norton: 42 entries → 4 entries (38 removed)
- UofL: 78 entries → 0 entries (78 removed, all deleted ✅)
- Baptist: 40 entries → 40 entries (pending)
- Independent: 414 entries → 414 entries (kept)

**Total removed so far:** 116 entries (20% of original)

---

## Verification

**Original file preserved:** ✅ medical-providers.json (574 entries)
**New cleaned file:** ✅ medical-providers-REMAINING.json (458 entries)

**Can compare:**
```bash
wc -l json-files/medical-providers.json
wc -l json-files/medical-providers-REMAINING.json
```

---

## Purpose

**This cleaned file represents:**
- Providers still in old case data format
- NOT covered by the 6 major health system rosters
- Mostly independent clinics and specialists
- Will be kept as-is (not part of facility-based conversion)

**The 6 major health systems (Norton, UofL, Baptist, CHI, St. Elizabeth, Norton Children's) are now managed via the facility-based JSON files instead.**

---

## ✅ Complete

**Created:** `medical-providers-REMAINING.json` with 458 provider entries

**Removed:** 116 Norton/UofL provider entries that were deleted from graph

**Remaining:** Baptist (40), CHI (7), St. Elizabeth (6), and independent providers (414)
