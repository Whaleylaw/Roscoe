# Norton Children's Hospital - Separate Health System

**Date:** January 2, 2026
**Discovery:** Norton Children's is a separate organization from Norton Healthcare

---

## Key Finding

**Norton Children's Hospital** operates independently from **Norton Healthcare**, despite the similar names.

**Evidence:**
- Separate website: nortonchildrens.com (vs nortonhealthcare.com)
- Not included in Norton Healthcare's official location roster (368 locations)
- Has its own locations page: https://nortonchildrens.com/location/

---

## Old Providers Affected

From the case data, we have **2 Norton Children's providers**:

### 1. Norton Children's Medical Group
- **Cases:** 1 (Michael-Ditto-Jr-Med-Mal-04-11-2023)
- **Treatment dates:** Records received
- **Status:** NO MATCH in Norton Healthcare roster

### 2. Norton Children's Urology
- **Cases:** 1 (Michael-Ditto-Jr-Med-Mal-04-11-2023)
- **Treatment dates:** Records received
- **Status:** NO MATCH in Norton Healthcare roster

**Reason for no match:** These are Norton CHILDREN'S providers, not Norton HEALTHCARE providers.

---

## Recommendation

### Option A: Treat as 6th Health System

**Create Norton Children's as a separate HealthSystem:**

1. Add Norton Children's Hospital to health_systems.json
2. Scrape locations from https://nortonchildrens.com/location/
3. Create norton_childrens_locations.json
4. Ingest to graph as 6th health system
5. Connect existing Norton Children's providers via PART_OF relationship

**Benefits:**
- Complete coverage of Norton family of hospitals
- Proper hierarchy for pediatric providers
- Medical records workflows for children's hospital

### Option B: Keep as Independent Providers

**Leave the 2 Norton Children's providers as-is:**

- No PART_OF relationship (independent)
- Keep existing case connections
- Don't create separate health system (only 2 providers)

**Benefits:**
- Simpler (no additional scraping needed)
- Only 1 case affected
- Can add Norton Children's system later if more cases appear

### Option C: Manual Entry (Hybrid)

**Create Norton Children's health system but manually enter locations:**

- Add to health_systems.json
- Manually add the 2 known locations (Medical Group, Urology)
- Can expand roster later as needed

**Benefits:**
- Establishes the hierarchy
- Minimal effort
- Room to grow

---

## My Recommendation

**Option C - Manual Entry**

Reasons:
1. Only 2 Norton Children's providers in current case data
2. Only 1 case affected (Michael Ditto Jr)
3. Can establish the health system now for future growth
4. Avoids complex web scraping for minimal immediate benefit

---

## Implementation (Option C)

### Step 1: Add to health_systems.json

```json
{
  "card_type": "entity",
  "entity_type": "HealthSystem",
  "name": "Norton Children's Hospital",
  "attributes": {
    "medical_records_endpoint": "Norton Children's Medical Records",
    "billing_endpoint": "Norton Children's Patient Financial Services",
    "phone": "(502) 629-5437",
    "address": "231 East Chestnut Street, Louisville, KY 40202",
    "website": "nortonchildrens.com"
  },
  "source_id": "norton_childrens",
  "source_file": "norton_childrens_website"
}
```

### Step 2: Create norton_childrens_locations.json

```json
[
  {
    "card_type": "entity",
    "entity_type": "MedicalProvider",
    "name": "Norton Children's Medical Group",
    "attributes": {
      "parent_system": "Norton Children's Hospital",
      "specialty": "pediatrics"
    },
    "source_id": "case_data",
    "source_file": "medical-providers.json"
  },
  {
    "card_type": "entity",
    "entity_type": "MedicalProvider",
    "name": "Norton Children's Urology",
    "attributes": {
      "parent_system": "Norton Children's Hospital",
      "specialty": "pediatric_urology"
    },
    "source_id": "case_data",
    "source_file": "medical-providers.json"
  }
]
```

### Step 3: Ingest to Graph

1. Add Norton Children's Hospital as HealthSystem
2. Update the 2 existing Norton Children's providers to link via PART_OF
3. Total: 6 health systems in graph

---

## Alternative: Full Scraping (Option A)

If you want the complete Norton Children's roster, we can:

1. **Use Playwright with longer timeout** to scrape the dynamic page
2. **Manually compile** from the website (clicking through each location)
3. **Contact Norton Children's** for official location list
4. **Use their location API** if they have one

**Estimated locations:** 20-50 (based on typical children's hospital networks)

---

## Impact Analysis

### Current Situation
- 2 Norton Children's providers in old case data
- 1 case affected (Michael-Ditto-Jr-Med-Mal-04-11-2023)
- Both providers currently in graph but not linked to any health system

### If We Add Norton Children's System
- 1 new HealthSystem entity
- 2 PART_OF relationships (existing providers → new system)
- No case relationship updates needed
- Future: Can add more Norton Children's locations as cases appear

### If We Don't
- 2 providers remain independent
- No health system hierarchy for pediatric providers
- Works fine for now (only 1 case)

---

## Decision Needed

**Which option do you prefer?**

A. Full scraping - Add Norton Children's as 6th system with complete location roster
B. Keep independent - Leave the 2 providers as-is
C. Manual entry - Add system + 2 known locations, expand later

**My recommendation is Option C** - establishes the system now without the complexity of full web scraping, and we can add more locations as needed.

---

## Files to Update

**If proceeding with Option C:**

1. `/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities/health_systems.json`
   - Add Norton Children's Hospital (becomes 6 systems)

2. `/Volumes/X10 Pro/Roscoe/json-files/norton_childrens_locations.json` (create new)
   - Add 2 known Norton Children's providers

3. Upload to GCS and ingest to graph
   - 1 new HealthSystem
   - Update 2 existing providers with PART_OF relationships

**Total impact:** Minimal (1 HealthSystem + 2 relationship updates)
