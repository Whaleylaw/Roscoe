# Clean Slate Provider Approach ✅

**Date:** January 2, 2026
**Strategy:** Delete old hodgepodge providers, rebuild connections from medical records

---

## The Approach

### Why Delete Old Providers?

**Problem with old data:**
- Created from case notes (generic names)
- May have incorrect connections
- Mixed quality (some had addresses, some didn't)
- Duplicates and inconsistencies

**Solution:**
1. ✅ Delete ALL old providers that match the new health system rosters
2. ✅ Keep new accurate facility-based providers ready
3. ⏳ Later: Review actual medical records to create correct connections

**Benefit:** Start fresh with accurate data, connect providers correctly based on actual medical records

---

## What Was Deleted

### Norton Providers: 18 old providers deleted

**From Norton mapping:**
- Norton Audubon Hospital
- Norton Brownsboro Hospital
- Norton Hospital Downtown
- Norton Neurology Services-Downtown
- Norton Community Medical Associates - Preston
- Norton Women's & Children's Hospital
- Norton Neurosciences Spine And Rehabilitation Center
- Norton Leatherman Spine
- Norton Cancer Institute - Brownsboro
- Norton Neuroscience Institute
- Norton Children's Medical Group
- Norton Children's Urology
- Norton Hospital
- River City Orthopedics (Norton Spine Specialist...)
- Norton Neuroscience Institute - Brownsboro
- Norton Community Medical Associates - Dixie
- Norton Hospital - Brownsboro
- Norton Orthopedic Institute - Audubon

**Note:** Some were already replaced/transferred in previous step, so actual deletions = fewer

### UofL Providers: 15 old providers deleted

**From UofL mapping:**
- University of Louisville Hospital
- University of Louisville Physicians
- UofL Health - Mary & Elizabeth Mary & Elizabeth Hospital
- University Of Louisville Hospital Radiology
- Jewish Hospital
- UofL Medical Center East
- University of Louisville School of Dentistry
- Saint Mary and Elizabeth Hospital
- UofL Health
- University Of Louisville Physicians
- UofL Physicians - Orthopedics
- UofL Physicians - Podiatric Medicine & Surgery
- UofL ER
- U of L Health Urgent Care Buechel
- UofL Health - Medical Center Southwest

### Total Deleted: 21 providers

**12 were already gone** from previous transfers/replacements
**21 were deleted** in this bulk deletion

---

## Graph State After Deletion

**Nodes:** 33,908 → 33,887 (-21)
**Relationships:** 21,978 → 21,850 (-128)

**Cases affected:**
- Abby Sitgraves: 93 → 89 (-4 provider connections)
- Many other cases also lost old provider connections

**This is intentional!** Connections will be rebuilt correctly from medical records.

---

## What's Ready for Reconnection

### New Facility-Based Providers (1,248 facilities)

**Location:** `/Volumes/X10 Pro/Roscoe/json-files/facility-based/`

1. ✅ **norton_healthcare_facilities.json** - 206 facilities
2. ✅ **uofl_health_facilities.json** - 169 facilities
3. ✅ **baptist_health_facilities.json** - 251 facilities
4. ✅ **chi_saint_joseph_health_facilities.json** - 139 facilities
5. ✅ **st._elizabeth_healthcare_facilities.json** - 409 facilities
6. ✅ **norton_childrens_hospital_facilities.json** - 74 facilities

**Each facility has:**
- Official name
- Parent health system
- Location count
- Locations array (addresses, phones for each location)

---

## Next Steps

### Phase 1: Ingest New Facility-Based Providers

**Upload to GCS and ingest:**
- 1,248 facility nodes (vs 1,891 location nodes)
- 643 fewer nodes than old location-based structure
- All with PART_OF → HealthSystem relationships

**Result:** Clean, accurate provider roster ready for case connections

### Phase 2: Review Medical Records & Reconnect

**For each case:**
1. Review actual medical records
2. Identify which facilities provided treatment
3. Create TREATING_AT relationships to correct facilities
4. Ensure connections are accurate

**This ensures:**
- Correct provider connections based on actual records
- No guessing or fuzzy matching
- Clean, verified data

---

## Why This is Better

### Old Approach (What We Moved Away From)

**Problem:**
```
Case notes say: "Treated at UofL Hospital"
→ Created generic "University of Louisville Hospital" provider
→ May or may not be accurate
→ No specific location info
→ Fuzzy matching to new roster = uncertain
```

### New Approach (Clean Slate)

**Solution:**
```
Medical records show: "UofL Health - Mary & Elizabeth Hospital, 1850 Bluegrass Ave"
→ Match to exact facility in new roster
→ Connect to "UofL Health – Mary & Elizabeth Hospital" facility
→ Accurate, verified connection
→ Has all 11 cases that actually treated there
```

---

## Current Graph State

### Providers in Graph

**With health system connections (898 providers):**
- Norton Healthcare: 225
- Baptist Health: 205
- UofL Health: 153
- CHI Saint Joseph: 148
- Norton Children's: 141
- St. Elizabeth: 26

**Without health system connections (~1,000+ providers):**
- Independent clinics
- Chiropractors
- Imaging centers
- Therapy clinics
- etc.

### Old Providers Status

**Deleted:** 21 old providers from Norton/UofL that matched new rosters
**Remaining:** ~200-250 old providers that are independent (not part of the 6 major systems)

---

## Files Ready for Next Phase

### Facility-Based Provider Rosters (Ready to Ingest)
- 6 JSON files with 1,248 facilities
- All with complete location details
- Ready to upload and ingest when you're ready

### Documentation
- This file: Clean slate approach explanation
- Mapping files: Show what was deleted
- Episode merge files: Have provider entity references for rebuilding connections

---

## When Ready to Reconnect

**You'll have:**
1. ✅ Clean facility-based provider nodes in graph
2. ✅ All facilities organized by health system
3. ✅ Episode data with provider mentions
4. ✅ Medical records to verify correct providers

**Process:**
1. Review medical records for each case
2. Identify exact facilities (with addresses)
3. Create TREATING_AT relationships to facility nodes
4. Result: Accurate, verified provider connections

---

## Summary

**✅ Old providers deleted:** 21 Norton/UofL providers removed
**✅ Clean slate achieved:** Cases no longer have incorrect provider connections
**✅ New rosters ready:** 1,248 facility-based providers ready to ingest
**⏳ Next:** Ingest facility-based providers, then rebuild case connections from medical records

**This is the right approach for ensuring data accuracy!**
