# Provider Count Verification - Discrepancies Found ⚠️

**Date:** January 2, 2026
**Master List:** `medical_providers.json` (2,152 providers)

---

## Comparison Results

### ✅ Good Matches

| System | Source File | Master List | Difference | Status |
|--------|-------------|-------------|------------|--------|
| **St. Elizabeth Healthcare** | 419 | 419 | 0 (0%) | ✅ Perfect |
| **CHI Saint Joseph Health** | 152 | 148 | -4 (-3%) | ✅ Close |

**St. Elizabeth and CHI match well!**

---

### ⚠️ Significant Discrepancies

| System | Source File | Master List | Missing | % Missing |
|--------|-------------|-------------|---------|-----------|
| **Norton Healthcare** | 368 | 226 | -142 | -39% ⚠️ |
| **UofL Health** | 345 | 257 | -88 | -26% ⚠️ |
| **Baptist Health** | 467 | 310 | -157 | -34% ⚠️ |
| **Norton Children's** | 140 | 0* | -140 | -100% ⚠️ |

**\*Note:** Norton Children's has 17 entries with "Norton Children's" in the name, but parent_system is blank or set to something else

---

## Why The Discrepancies?

### 1. Master List Built from Graph, Not Source Files

**The current master list contains:**
- Providers that were already in the graph
- Some additions from source files
- But NOT a complete ingestion of all source files

### 2. Norton Healthcare (226 vs 368 source)

**Missing:** ~142 Norton locations

**Likely reason:**
- We deleted old Norton providers
- We created a few new ones during replacements
- But never ingested all 368 Norton locations from the source file

**What's in master:**
- Mix of old providers that weren't deleted
- Few new providers from replacements
- Not the complete 368-location roster

### 3. UofL Health (257 vs 345 source)

**Missing:** ~88 UofL locations

**Likely reason:**
- We deleted old UofL providers
- Fixed St. Elizabeth added some UofL (Mary & Elizabeth)
- But never ingested all 345 UofL locations

### 4. Baptist Health (310 vs 467 source)

**Missing:** ~157 Baptist locations

**Likely reason:**
- We deleted old Baptist providers
- Never ingested all 467 Baptist locations from source

### 5. Norton Children's (0 vs 140 source)

**Missing:** All 140 locations (but 17 exist by name)

**Likely reason:**
- 17 Norton Children's entries exist but don't have parent_system set
- OR parent_system is set to blank/Norton Healthcare
- The 140 scraped locations were ingested to graph but not added to this master JSON file

---

## What This Means

**The master list is NOT a complete ingestion of the source files.**

**It's a hybrid:**
- ✅ St. Elizabeth: Complete (all 419 from source)
- ✅ CHI: Nearly complete (148 of 152)
- ⚠️ Norton: Partial (226 of 368 - 62%)
- ⚠️ UofL: Partial (257 of 345 - 74%)
- ⚠️ Baptist: Partial (310 of 467 - 66%)
- ⚠️ Norton Children's: Not linked (0 of 140 with parent_system)
- ✅ Independent: 792 providers

---

## Options to Fix

### Option A: Add Missing Providers from Source Files

**For each system with discrepancies:**
1. Load source file (e.g., norton_healthcare_locations.json)
2. Load master list
3. Find locations in source NOT in master (by name)
4. Add missing ones to master
5. Result: Complete 1,891-location roster

**Would increase master list to ~2,600 providers**

### Option B: Use Facility-Based Structure Instead

**Better approach (your original plan):**
1. Use facility-based JSON files (1,248 facilities vs 1,891 locations)
2. Consolidates locations into facilities
3. Cleaner structure
4. Reduces nodes by 643

**Files ready:**
- norton_healthcare_facilities.json (206)
- uofl_health_facilities.json (169)
- baptist_health_facilities.json (251)
- chi_saint_joseph_health_facilities.json (139)
- st._elizabeth_healthcare_facilities.json (409)
- norton_childrens_hospital_facilities.json (74)

### Option C: Accept Current State

**Keep master list as-is:**
- Has most important providers
- Independent providers complete
- Can add more later as needed

---

## Issues Found

### 1. Empty Parent System (19 entries)

**19 providers have empty parent_system attribute:**
```
"parent_system": ""
```

**Should these be "Independent" or set to specific system?**

### 2. Norton Children's Not Linked

**17 "Norton Children's" providers exist but:**
- parent_system is blank or incorrect
- Should be "Norton Children's Hospital"

### 3. Missing Locations

**Norton:** Missing ~142 locations
**UofL:** Missing ~88 locations
**Baptist:** Missing ~157 locations

---

## Recommended Action

**I recommend Option B - Facility-Based Structure:**

**Advantages:**
1. Already created and ready (1,248 facilities)
2. Consolidates duplicate locations
3. Cleaner structure
4. All source data included
5. 643 fewer nodes

**This master list can be kept as backup/reference, but use facility-based for graph ingestion.**

---

## Quick Fixes Needed

### Fix 1: Norton Children's Parent System

**Set parent_system for 17 Norton Children's entries:**
```python
for p in master:
    if 'norton children' in p['name'].lower():
        p['attributes']['parent_system'] = 'Norton Children\'s Hospital'
```

### Fix 2: Add Missing Locations (if keeping location-based)

**For each system:**
- Load source file
- Find missing entries
- Add to master

**Would require:**
- ~400 additions to reach 2,550 total
- Match source files exactly

---

## Current State Summary

**Master list (2,152):**
- ✅ St. Elizabeth: 419 (100% of source)
- ✅ CHI: 148 (97% of source)
- ⚠️ Norton: 226 (61% of source)
- ⚠️ UofL: 257 (75% of source)
- ⚠️ Baptist: 310 (66% of source)
- ⚠️ Norton Children's: 0 properly linked (0% of source)
- ✅ Independent: 792

**Roughly 70% complete for health systems (excluding St. Elizabeth which is 100%)**

---

## Decision Needed

**What would you like to do?**

A. Add all missing locations from source files (complete the master list to ~2,550)
B. Use facility-based structure instead (cleaner, already prepared)
C. Fix Norton Children's parent_system links (quick fix for 17 entries)
D. Keep as-is and note the discrepancies

Let me know and I'll proceed accordingly!
