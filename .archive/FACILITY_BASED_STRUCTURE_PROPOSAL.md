# Facility-Based Provider Structure - Proposal

**Date:** January 2, 2026
**Impact:** Reduce provider nodes by 34% (1,891 → 1,248 = -643 nodes)

---

## The New Structure

### OLD Approach: Location-Level Nodes

**Each location = separate node:**
- UofL Health - Frazier Rehab - Downtown
- UofL Health - Frazier Rehab - Brownsboro
- UofL Health - Frazier Rehab - St. Matthews
- UofL Health - Frazier Rehab - Elizabethtown

**Result:** 4 separate nodes

### NEW Approach: Facility-Level Nodes

**One facility = one node with locations array:**

```json
{
  "name": "UofL Health – Frazier Rehabilitation Institute – Kleinert Kutz Hand Therapy",
  "attributes": {
    "parent_system": "UofL Health",
    "location_count": 4,
    "locations": [
      {
        "location": "Chamberlain",
        "address": "4642 Chamberlain Lane, Suite 203, Louisville, KY 40241",
        "phone": "502-562-0344"
      },
      {
        "location": "East",
        "address": "4010 Dupont Circle, Suite 308A, Louisville, KY 40207",
        "phone": "502-562-0334"
      },
      {
        "location": "Outpatient Care",
        "address": "225 Abraham Flexner Way, Suite 760, Louisville, KY 40202",
        "phone": "502-561-4295"
      },
      {
        "location": "New Albany",
        "address": "3605 Northgate Court, Suite 103, New Albany, IN 47150",
        "phone": "812-981-4735"
      }
    ]
  }
}
```

**Result:** 1 node with complete location details

---

## Consolidation Impact

### By Health System

| System | Old (Locations) | New (Facilities) | Reduction |
|--------|-----------------|------------------|-----------|
| **Baptist Health** | 467 | 251 | -216 (46%) |
| **UofL Health** | 345 | 169 | -176 (51%) |
| **Norton Healthcare** | 368 | 206 | -162 (44%) |
| **Norton Children's** | 140 | 74 | -66 (47%) |
| **CHI Saint Joseph** | 152 | 139 | -13 (9%) |
| **St. Elizabeth** | 419 | 409 | -10 (2%) |
| **TOTAL** | **1,891** | **1,248** | **-643 (34%)** |

**Overall reduction:** 643 fewer nodes while preserving all location detail!

---

## Examples

### Example 1: Norton Diagnostic Center (7 locations → 1 node)

**OLD Structure (7 nodes):**
1. Norton Diagnostic Center - St. Matthews
2. Norton Diagnostic Center - Elizabethtown
3. Norton Diagnostic Center - Jeffersonville Commons
4. Norton Diagnostic Center - Brownsboro
5. Norton Diagnostic Center - Dixie
6. Norton Diagnostic Center - Dupont
7. Norton Diagnostic Center - Fern Creek

**NEW Structure (1 node):**
- **Name:** Norton Diagnostic Center
- **Locations property:** Array of 7 locations with addresses/phones

### Example 2: Single Location Facility (No Change in Data)

**OLD Structure:**
- Norton Hospital (1 node)

**NEW Structure:**
- **Name:** Norton Hospital
- **Locations property:** [{location: "Main", address: "...", phone: "..."}]

Same data, just formatted consistently

---

## Benefits

### 1. Significant Node Reduction

**Current graph:** 33,908 nodes
**After conversion:** ~33,265 nodes (-643, -1.9%)

**More manageable:**
- Fewer nodes to traverse
- Cleaner query results
- Easier to understand provider structure

### 2. Preserves All Detail

**No information lost:**
- All addresses preserved
- All phone numbers preserved
- All location names preserved
- Just stored as properties instead of separate nodes

### 3. Better Semantic Queries

**Query for a facility (not specific location):**

```cypher
// OLD: Had to match multiple location nodes
MATCH (c:Case)-[:TREATING_AT]->(p:MedicalProvider)
WHERE p.name CONTAINS "Norton Diagnostic Center"
RETURN p.name

// Returns 7 different nodes

// NEW: Match one facility node
MATCH (c:Case)-[:TREATING_AT]->(p:MedicalProvider {name: "Norton Diagnostic Center"})
RETURN p.name, p.locations

// Returns 1 node with all 7 locations in properties
```

### 4. Easier Maintenance

**Adding a new location:**

OLD: Create entire new node
NEW: Add to locations array property

**Updating facility info:**

OLD: Update all location nodes
NEW: Update one facility node

---

## How Queries Change

### Finding Cases Treated at a Facility

**OLD Query:**
```cypher
// Find cases at any Norton Diagnostic Center location
MATCH (c:Case)-[:TREATING_AT]->(p:MedicalProvider)
WHERE p.name CONTAINS "Norton Diagnostic Center"
RETURN c.name, p.name
```

**NEW Query:**
```cypher
// Find cases at Norton Diagnostic Center facility
MATCH (c:Case)-[:TREATING_AT]->(p:MedicalProvider {name: "Norton Diagnostic Center"})
RETURN c.name, p.name, p.locations
```

### Getting Specific Location Details

**Access locations array:**
```cypher
MATCH (p:MedicalProvider {name: "Norton Diagnostic Center"})
UNWIND p.locations as loc
WHERE loc.location = "Brownsboro"
RETURN loc.address, loc.phone
```

---

## Migration Plan

### Phase 1: Convert JSON Files ✅ DONE

- ✅ Converted all 6 health system rosters to facility-based structure
- ✅ Saved to `/json-files/facility-based/` directory
- ✅ 643 node reduction confirmed

### Phase 2: Clear Old Providers (Proposed)

**Remove existing provider nodes:**
```cypher
// Delete all providers that have PART_OF → HealthSystem
// (These are the ones we're replacing with facility structure)
MATCH (p:MedicalProvider)-[:PART_OF]->(h:HealthSystem)
DETACH DELETE p
```

**Impact:**
- Removes ~900 provider nodes
- Removes ~900 PART_OF relationships
- Removes TREATING_AT relationships (will be recreated)

**Safety:** Back up case data first, verify Abby Sitgraves canary

### Phase 3: Ingest New Facility Structure

**Create new facility-based providers:**
- 1,248 facility nodes (vs 1,891 location nodes)
- Each has locations array property
- Reconnect to cases (TREATING_AT)
- Reconnect to health systems (PART_OF)

**Result:**
- Cleaner graph structure
- All data preserved
- 643 fewer nodes

---

## Comparison Example: UofL Health

### Before (Location-Based): 345 Nodes

```
- UofL Physicians - Cardiology - Brownsboro
- UofL Physicians - Cardiology - Downtown
- UofL Physicians - Cardiology - St. Matthews
- UofL Physicians - Cardiology - Elizabethtown
- UofL Physicians - Cardiology - Shelbyville
... (5 separate nodes for one cardiology program)
```

### After (Facility-Based): 169 Nodes

```
- UofL Physicians - Cardiology
  locations: [
    {location: "Brownsboro", address: "...", phone: "..."},
    {location: "Downtown", address: "...", phone: "..."},
    {location: "St. Matthews", address: "...", phone: "..."},
    {location: "Elizabethtown", address: "...", phone: "..."},
    {location: "Shelbyville", address: "...", phone: "..."}
  ]
... (1 node with 5 locations as properties)
```

---

## Files Created

**Converted facility-based JSONs:**

**Location:** `/Volumes/X10 Pro/Roscoe/json-files/facility-based/`

1. ✅ `uofl_health_facilities.json` (169 facilities)
2. ✅ `baptist_health_facilities.json` (251 facilities)
3. ✅ `norton_healthcare_facilities.json` (206 facilities)
4. ✅ `chi_saint_joseph_health_facilities.json` (139 facilities)
5. ✅ `st._elizabeth_healthcare_facilities.json` (409 facilities)
6. ✅ `norton_childrens_hospital_facilities.json` (74 facilities)

---

## Risks & Considerations

### Pros

✅ **34% fewer nodes** (643 reduction)
✅ **Cleaner query results** (one facility vs many locations)
✅ **All data preserved** (in properties)
✅ **Better semantic meaning** (facility is the entity, locations are attributes)
✅ **Easier maintenance** (update one node vs many)

### Cons

⚠️ **Requires re-ingestion** (delete old, create new)
⚠️ **Case relationships need updating** (reconnect to facility nodes)
⚠️ **More complex properties** (JSON arrays instead of flat properties)

---

## Recommendation

### Option A: Proceed with Full Conversion (Recommended)

**Benefits:**
- Cleaner graph structure
- Significant node reduction
- Better matches user's mental model (facilities, not individual locations)

**Process:**
1. Backup current graph state
2. Delete existing provider nodes with PART_OF relationships
3. Ingest new facility-based providers
4. Reconnect cases to facilities
5. Verify no data loss

**Time:** ~30 minutes

### Option B: Keep Current Structure

**Benefits:**
- No re-ingestion needed
- Already working
- Can query by specific location

**Drawbacks:**
- 643 extra nodes
- More complex queries (multiple nodes for same facility)
- Harder to consolidate provider information

---

## Decision Needed

**Do you want to proceed with the facility-based structure?**

If yes, I'll:
1. Create backup/rollback plan
2. Delete old location-based providers
3. Ingest new facility-based providers (1,248 facilities)
4. Reconnect all case relationships
5. Verify data integrity

**This is a significant restructuring but will result in a much cleaner graph!**
