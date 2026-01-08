# HealthSystem Entity Structure

## Overview

Created hierarchical medical provider structure with parent HealthSystem organizations and child MedicalProvider locations, following the same pattern as Court → Division.

**Total Entities:**
- 5 HealthSystem parent organizations
- 2,159 MedicalProvider locations (1,386 added, 773 existing)

---

## Graph Structure

### **Hierarchy Pattern:**

```
(HealthSystem {name: "Norton Healthcare"})
  ↑ [PART_OF]
(MedicalProvider {name: "Norton Hospital Downtown"})
  ↑ [WORKS_AT]
(Doctor {name: "Dr. Smith"})

(Client)-[:TREATING_AT]->(MedicalProvider)-[:PART_OF]->(HealthSystem)
```

### **Complete Chain:**

```
Client
  ↓ [TREATING_AT]
MedicalProvider (specific location: "Norton Hospital Downtown")
  ↓ [PART_OF]
HealthSystem (parent org: "Norton Healthcare")
```

---

## Five Health Systems

### **1. Norton Healthcare**
- **Locations:** 368 total (226 new + existing)
- **Specialties:** Hospitals, cancer institutes, orthopedic institutes, community clinics, immediate care
- **Medical Records:** Central Norton Healthcare Medical Records
- **Coverage:** Louisville metro, Southern Indiana, outlying KY counties

**Example Locations:**
- Norton Hospital (Downtown)
- Norton Audubon Hospital
- Norton Brownsboro Hospital
- Norton Women's and Children's Hospital
- Norton Orthopedic Institute - multiple locations
- Norton Cancer Institute - multiple locations
- Norton Community Medical Associates - 30+ locations
- Norton Immediate Care Centers - 20+ locations

### **2. UofL Health**
- **Locations:** 345 total (257 new + existing)
- **Specialties:** Academic medical center, specialty clinics, cancer center, outpatient centers
- **Medical Records:** UofL Health Medical Records - Central
- **Coverage:** Louisville, statewide KY

**Example Locations:**
- UofL Hospital
- UofL Health – Brown Cancer Center
- UofL Health – Abraham Flexner Outpatient Center
- UofL Physicians - multiple specialties
- Carroll County Memorial Hospital – A Partner of UofL Health

### **3. Baptist Health**
- **Locations:** 467 total (317 new + existing)
- **Specialties:** Hospitals, medical groups, imaging centers, urgent care
- **Medical Records:** Baptist Health Medical Records
- **Coverage:** Louisville, Lexington, statewide KY

**Example Locations:**
- Baptist Health Louisville
- Baptist Health Lexington
- Baptist Health Corbin
- Baptist Health Medical Group - multiple locations
- Baptist Health Urgent Care - multiple locations

### **4. CHI Saint Joseph Health**
- **Locations:** 152 total (148 new + existing)
- **Specialties:** Hospitals, medical groups, specialty clinics
- **Medical Records:** CHI Saint Joseph Medical Records
- **Coverage:** Lexington, Eastern KY

**Example Locations:**
- CHI Saint Joseph Hospital
- CHI Saint Joseph Medical Group - multiple locations
- CHI Saint Joseph East

### **5. St. Elizabeth Healthcare**
- **Locations:** 419 total (26 new + existing)
- **Specialties:** Hospitals, physician groups, specialty clinics
- **Medical Records:** St. Elizabeth Medical Records
- **Coverage:** Northern KY (Covington, Florence, Ft. Thomas area)

**Example Locations:**
- St. Elizabeth Medical Center
- St. Elizabeth Physicians - multiple locations
- St. Elizabeth Urgent Care - multiple locations

---

## Use Cases

### **1. Medical Records Requests**

**Query parent system for records endpoint:**
```cypher
MATCH (c:Client {name: "Amy Mills"})-[:TREATING_AT]->(loc:MedicalProvider)
      -[:PART_OF]->(system:HealthSystem)
RETURN DISTINCT system.name, system.medical_records_endpoint
```

**Result:**
```
Norton Healthcare → Norton Healthcare Medical Records
UofL Health → UofL Health Medical Records - Central
```

**Benefit:** One query tells you where to send ALL medical records requests for this client

### **2. Find All Locations in a System**

```cypher
MATCH (loc:MedicalProvider)-[:PART_OF]->(system:HealthSystem {name: "Norton Healthcare"})
WHERE loc.name CONTAINS "Orthopedic"
RETURN loc.name, loc.address
```

### **3. Track Treatment Across System**

```cypher
// Client treated at multiple Norton locations
MATCH (c:Client {name: "Amy Mills"})-[:TREATING_AT]->(loc:MedicalProvider)
      -[:PART_OF]->(system:HealthSystem {name: "Norton Healthcare"})
RETURN loc.name, loc.specialty
```

### **4. Billing Aggregation**

```cypher
// All providers client treated at, grouped by system
MATCH (c:Client {name: $client_name})-[:TREATING_AT]->(loc:MedicalProvider)
OPTIONAL MATCH (loc)-[:PART_OF]->(system:HealthSystem)
RETURN
  COALESCE(system.name, "Independent") as health_system,
  collect(loc.name) as locations,
  count(loc) as location_count
```

### **5. System-Wide Analytics**

```cypher
// How many cases treated at Norton vs UofL?
MATCH (c:Case)-[:TREATING_AT]->(loc:MedicalProvider)-[:PART_OF]->(system:HealthSystem)
RETURN system.name, count(DISTINCT c) as case_count
ORDER BY case_count DESC
```

---

## Entity Counts

| Type | Count | Description |
|------|-------|-------------|
| HealthSystem | 5 | Parent organizations |
| MedicalProvider | 2,159 | Specific locations (1,386 new + 773 existing) |
| └─ Norton Healthcare | 368 | All Norton locations |
| └─ UofL Health | 345 | All UofL locations |
| └─ Baptist Health | 467 | All Baptist locations |
| └─ CHI Saint Joseph | 152 | All CHI locations |
| └─ St. Elizabeth | 419 | All St. Elizabeth locations |

**Note:** 412 locations couldn't be mapped to a parent system (independent providers)

---

## Pydantic Models

### **HealthSystem:**
```python
class HealthSystem(BaseModel):
    """Parent healthcare organization."""
    medical_records_endpoint: Optional[str]
    billing_endpoint: Optional[str]
    phone: Optional[str]
    fax: Optional[str]
    email: Optional[str]
    address: Optional[str]
    website: Optional[str]
```

### **MedicalProvider (Updated):**
```python
class MedicalProvider(BaseModel):
    """Specific medical provider location."""
    specialty: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    fax: Optional[str]
    address: Optional[str]
    provider_type: Optional[str]
    parent_system: Optional[str]  # NEW - links to HealthSystem
```

---

## Relationships

### **PART_OF:**
```cypher
(MedicalProvider)-[:PART_OF]->(HealthSystem)
```

**Example:**
```cypher
CREATE (:MedicalProvider {name: "Norton Hospital Downtown"})
       -[:PART_OF]->
       (:HealthSystem {name: "Norton Healthcare"})
```

### **Full Treatment Chain:**

```
Doctor: "Dr. Smith"
  ↓ [WORKS_AT]
MedicalProvider: "Norton Orthopedic Institute - Downtown"
  ↓ [PART_OF]
HealthSystem: "Norton Healthcare"

Client: "Amy Mills"
  ↓ [TREATING_AT]
MedicalProvider: "Norton Orthopedic Institute - Downtown"
```

---

## Comparison to Court/Division Pattern

| Medical | Court | Relationship |
|---------|-------|--------------|
| HealthSystem | Court | Parent entity |
| MedicalProvider (location) | Division | Specific entity |
| Client → Location | Case → Division | Where treatment/filing happens |
| Location → System | Division → Court | Hierarchy |

**Same Pattern:**
- HealthSystem has system-wide attributes (records endpoint)
- MedicalProvider has location-specific attributes (address, phone, specialty)
- Client treats at specific location, records requested from system
- Division has division-specific attributes (local rules)
- Case filed in specific division, part of parent court

---

## Import Results

**Before:**
- 773 medical providers (mix of systems and independent)

**After:**
- 5 HealthSystem entities
- 2,159 MedicalProvider locations
  - 365 matched existing (kept original)
  - 1,386 added new
  - 773 - 365 = 408 existing that didn't match (independent providers)

**Files Created:**
- `health_systems.json` (5 entities)
- `medical_providers.json` (updated from 773 → 2,159)

---

## Query Examples

### **Where to request records for a client:**
```cypher
MATCH (c:Client {name: "Amy Mills"})-[:TREATING_AT]->(loc:MedicalProvider)
OPTIONAL MATCH (loc)-[:PART_OF]->(system:HealthSystem)
RETURN
  loc.name as location,
  system.name as health_system,
  system.medical_records_endpoint as records_contact
```

### **All Norton locations client treated at:**
```cypher
MATCH (c:Client {name: "Amy Mills"})-[:TREATING_AT]->(loc:MedicalProvider)
      -[:PART_OF]->(system:HealthSystem {name: "Norton Healthcare"})
RETURN loc.name, loc.address
```

### **Find specific location within system:**
```cypher
MATCH (loc:MedicalProvider {name: "Norton Orthopedic Institute - Downtown"})
      -[:PART_OF]->(system:HealthSystem)
RETURN system.name, system.medical_records_endpoint
```

---

## Total Entity Count: ~45,900

| Category | Count |
|----------|-------|
| Doctors | 20,732 |
| MedicalProvider | 2,159 |
| Organizations | 384 |
| Court Divisions | 192 |
| Courts | 106 |
| ... | ... |
| **HealthSystem** | **5** |

**All with proper hierarchical relationships for practical case management!**
