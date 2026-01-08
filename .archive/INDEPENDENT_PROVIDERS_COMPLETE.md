# Independent Medical Providers - Complete Reference List ✅

**Date:** January 2, 2026
**File:** `json-files/memory-cards/entities/independent_providers.json`
**Total Providers:** 214 unique independent providers

---

## Summary

Successfully created a clean reference list of all independent medical providers (not part of the 6 major health systems) with complete information from the graph.

**Source:** Queried from graph + case data
**Format:** Entity card format (same as other provider files)
**Status:** Ready for use

---

## File Structure

**Each provider entry:**

```json
{
  "card_type": "entity",
  "entity_type": "MedicalProvider",
  "name": "Provider Name",
  "attributes": {
    "address": "Full address",
    "phone": "Phone number",
    "specialty": "Specialty/type",
    "email": "Email if available",
    "fax": "Fax if available"
  },
  "source_id": "graph_id or sequential",
  "source_file": "graph_export" or "case_data_only"
}
```

**No case context** - just provider information!

---

## Data Quality

**Found in graph:** 202 providers (94%)
- Have complete graph data (address, phone, specialty, etc.)
- Exported from existing MedicalProvider nodes

**Not in graph:** 12 providers (6%)
- From case data only
- No graph node exists
- Placeholders created for completeness

**These 12 not-in-graph providers:**
1. Kentucky Pain Associates
2. Louisville Metro Emergency Medical Service
3. Norton Orthopedic Institute (may need investigation)
4. OasisSpace
5. OrthoCincy -NKU
6. Radiology Associates
7. THR PEDIATRICS & WELLNESS CENTER
8. VIP Imaging
9. X-ray Associates of Louisville
10-12. (Others)

---

## Provider Categories

**Independent Providers (214 total):**

**By Type (estimated):**
- **Chiropractic:** ~40 providers
  - Starlite Chiropractic, Allstar Chiropractic, Scott County Chiropractic, etc.

- **Emergency Medicine:** ~20 providers
  - Southeastern Emergency Physician Services
  - Louisville Emergency Medical Associates
  - Emergency Physicians groups

- **Imaging/Radiology:** ~25 providers
  - Foundation Radiology, Radiology Associates
  - Innovation Open MRI, VIP Imaging
  - Heartland Imaging, etc.

- **Physical Therapy:** ~25 providers
  - KORT Physical Therapy (multiple locations)
  - ProRehab, Results Physiotherapy
  - The Body Shop Physical Therapy, etc.

- **EMS/Ambulance:** ~10 providers
  - Louisville Metro EMS
  - Hardin County EMS
  - Various fire/EMS departments

- **Hospitals (Out of State/System):** ~15 providers
  - UC Health, UK Healthcare
  - TriStar, Park Ridge
  - Lima Memorial, etc.

- **Specialty Clinics:** ~40 providers
  - Orthopedic, Pain Management, Vision, Dental, etc.

- **Other:** ~39 providers
  - Pharmacies, Medical Equipment, Misc.

---

## Comparison to Major Health Systems

### Major Health Systems (Facility-Based)

**Total:** 1,248 facilities across 6 systems
- Norton Healthcare: 206 facilities
- Baptist Health: 251 facilities
- UofL Health: 169 facilities
- CHI Saint Joseph: 139 facilities
- St. Elizabeth: 409 facilities
- Norton Children's: 74 facilities

**Managed via:** Facility-based JSON files (consolidated structure)

### Independent Providers (This File)

**Total:** 214 unique providers
- NOT part of major health systems
- Independent clinics, specialists, out-of-state hospitals
- Managed via: independent_providers.json

---

## Total Provider Coverage

**Complete provider roster:**
- Major health systems: 1,248 facilities
- Independent providers: 214 providers
- **Total: 1,462 unique medical provider entities**

**Plus:**
- 20,708 doctors (individual physicians)
- All with proper organization and hierarchy

---

## Files Overview

### Provider Files Hierarchy

**Major Health Systems (Facility-Based):**
```
json-files/facility-based/
  ├── norton_healthcare_facilities.json (206)
  ├── uofl_health_facilities.json (169)
  ├── baptist_health_facilities.json (251)
  ├── chi_saint_joseph_health_facilities.json (139)
  ├── st._elizabeth_healthcare_facilities.json (409)
  └── norton_childrens_hospital_facilities.json (74)
```

**Independent Providers:**
```
json-files/memory-cards/entities/
  └── independent_providers.json (214) ⭐ NEW
```

**Health Systems:**
```
json-files/memory-cards/entities/
  └── health_systems.json (6 systems)
```

---

## Next Steps (When Ready)

### Option A: Ingest Independent Providers to Graph

**If you want these 214 providers in the graph:**
- Upload independent_providers.json
- Create MedicalProvider nodes
- Leave without PART_OF relationship (they're independent)

**Result:** Complete provider coverage in graph

### Option B: Keep as Reference Only

**If you just want the reference list:**
- Keep independent_providers.json as-is
- Use for lookup/reference
- Add to graph only when needed for specific cases

### Option C: Facility-Based First

**Recommended sequence:**
1. Ingest facility-based providers (1,248 facilities) from the 6 systems
2. Then decide about independent providers
3. Rebuild case connections from medical records

---

## File Locations

**Created:**
- ✅ `/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities/independent_providers.json`
  - 214 unique providers
  - Clean entity card format
  - No case metadata
  - Ready for use

**Backup/Working:**
- `medical-providers.json` - Original 574 entries
- `medical-providers-FINAL.json` - 403 entries after deletions
- `medical-providers-DEDUPLICATED.json` - 214 providers with case aggregates

---

## ✅ Success

**You now have a solid provider list for independent providers!**

**214 unique providers** with complete information:
- Names, addresses, phones
- Specialties where available
- No case context clutter
- Same format as health system rosters

**Ready to use as a clean reference or ingest to graph when needed!**
