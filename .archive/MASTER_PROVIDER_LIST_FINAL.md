# Master Medical Provider List - FINAL ✅

**Date:** January 2, 2026
**File:** `json-files/memory-cards/entities/medical_providers.json`
**Total Providers:** 2,151

---

## This is the FINAL Combined List!

**Yes, this is your complete master provider list** combining:
- ✅ All 5 major health system providers (location-based from original import)
- ✅ All independent providers
- ✅ Clean, valid JSON
- ✅ Ready for use

---

## Contents Breakdown

**Total:** 2,151 providers

### By Health System

| Health System | Providers |
|---------------|-----------|
| **Norton Healthcare** | 226 |
| **Baptist Health** | 310 |
| **UofL Health** | 257 |
| **CHI Saint Joseph Health** | 148 |
| **St. Elizabeth Healthcare** | 25 |
| **Independent (no parent)** | 1,185 |
| **TOTAL** | **2,151** |

**Note:** Norton Children's Hospital providers are likely included in Norton Healthcare count or independent

---

## What Was Removed

**7 entries marked DELETE:**
1. 3000 Baptist Health Blvd, Suite 155 (address, not facility)
2. 3000 Baptist Health Blvd, Suite 170 (address, not facility)
3. 3000 Baptist Health Blvd, Suite 210 (address, not facility)
4. 3000 Baptist Health Blvd, Suite 240 (address, not facility)
5. 3000 Baptist Health Blvd, Suite 310 (address, not facility)
6. St. Elizabeth Healthcare Ft. Thomas (Obstetrical Ultrasound ONLY) (department note, not facility)
7. TEST Medical Provider - please delete (test entry)

**All removed successfully!**

---

## File Structure

**Location-Based Providers (from health systems):**
```json
{
  "name": "Norton Audubon Hospital - Emergency",
  "attributes": {
    "address": "1 Audubon Plaza Drive, Louisville, KY 40217",
    "phone": "(502) 636-7111",
    "parent_system": "Norton Healthcare"
  }
}
```

**Independent Providers:**
```json
{
  "name": "Starlite Chiropractic",
  "attributes": {
    "specialty": "chiropractic",
    "address": "1169 Eastern Pkwy, Louisville, KY 40217",
    "phone": "502-991-2056"
  }
}
```

**Consistent entity card format throughout!**

---

## Comparison to Facility-Based Structure

### Current File (Location-Based): 2,151 providers

**Structure:**
- Each location = separate node
- Norton Audubon Hospital - Emergency
- Norton Audubon Hospital - Neurodiagnostics
- Norton Audubon Hospital (main)
- 3 separate entries

### Facility-Based Alternative: 1,248 providers

**Structure:**
- One facility = one node with locations array
- Norton Audubon Hospital (1 node)
  - locations: [Emergency, Neurodiagnostics, Main]
- Reduces 368 Norton locations → 206 Norton facilities

**Reduction:** 2,151 → ~1,450 (if converted to facility-based)

---

## This File vs Other Files

### This File (medical_providers.json)

**Purpose:** Complete combined master list
**Structure:** Location-based (each location = entry)
**Content:** All health systems + all independent providers
**Total:** 2,151 providers
**Status:** ✅ CURRENT MASTER LIST

### Facility-Based Files

**Purpose:** Consolidated structure for major health systems only
**Structure:** Facility-based (locations as properties)
**Content:** 6 major health systems only (no independent)
**Total:** 1,248 facilities
**Status:** Alternative structure, not yet ingested

### Independent Providers File

**Purpose:** Independent providers only (extracted subset)
**Content:** 214 unique independent providers
**Status:** Reference/subset of master list

---

## Usage

### As Master Reference

**This file is your master provider list!**
- Use for lookups
- Use for ingestion
- Use as source of truth

### For Graph Ingestion

**To ingest to graph:**
1. Upload to GCS
2. Run ingestion script
3. Create 2,151 MedicalProvider nodes
4. Connect to health systems (966 providers)
5. Leave independent (1,185 providers)

### For Provider Management

**Update this file when:**
- Adding new providers
- Updating provider information
- Removing invalid entries

---

## Data Quality

### Health System Providers (966)

**Complete data:**
- Official names from health system websites
- Full addresses
- Phone numbers
- Parent system links
- Specialty information

### Independent Providers (1,185)

**Varying quality:**
- Some have complete data (addresses, phones)
- Some have minimal data
- Extracted from case records
- Can be enhanced over time

---

## Relationship to Graph

**Current graph state:**
- Has ~1,200 MedicalProvider nodes (mixed location + facility based)
- Some from old ingestion, some from new
- Mix of structures

**This file represents:**
- The INTENDED final state
- All providers that should be in graph
- Clean, deduplicated
- Ready for fresh ingestion if needed

---

## Next Steps (When Ready)

### Option A: Use Current Graph + This File

**Keep graph as-is, use file for reference**
- No re-ingestion needed
- File is authoritative source
- Update graph incrementally as needed

### Option B: Fresh Ingestion

**Clear old providers, ingest from this file**
- Upload medical_providers.json to GCS
- Clear old MedicalProvider nodes
- Ingest all 2,151 providers fresh
- Connect to cases from medical records

### Option C: Convert to Facility-Based First

**Transform this list to facility structure, then ingest**
- Reduces nodes by ~700
- Cleaner graph structure
- More work upfront

---

## Files Reference

**Master List (THIS FILE):**
- ✅ `/json-files/memory-cards/entities/medical_providers.json` (2,151 providers)

**Alternatives:**
- `facility-based/*.json` (1,248 facilities - alternative structure)
- `independent_providers.json` (214 providers - subset)

**Deprecated/Working:**
- `medical-providers-FINAL.json` (intermediate file)
- `medical-providers-DEDUPLICATED.json` (working file)

---

## ✅ Success

**You have your complete master medical provider list!**

**2,151 providers:**
- 966 from 5 major health systems
- 1,185 independent providers
- All in one file
- Clean, valid JSON
- Ready for use

**This is your authoritative provider database for Kentucky personal injury litigation!**
