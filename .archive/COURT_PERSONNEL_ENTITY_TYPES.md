# Court Personnel Entity Types

## Overview

Added 7 new entity types for Kentucky court personnel, imported from official KY court directory (993 entries → 819 active entities).

## New Entity Types

### Judges (Individual People)

#### 1. CircuitJudge (101 entities)
**Purpose:** Circuit court judges presiding over felony criminal and civil cases

**Attributes:**
- `county`: County or multi-county area (e.g., "Barren & Metcalfe")
- `circuit`: Circuit and division (e.g., "Cir. 43, Div. 01")
- `division`: Division number
- `phone`: Chambers phone
- `email`: Email address
- `address`: Chambers address

**Relationships:**
- `CircuitJudge -[PRESIDES_OVER]-> Court`
- `Case -[ASSIGNED_TO]-> CircuitJudge`
- `Episode -[ABOUT]-> CircuitJudge`

**Example:**
```json
{
  "entity_type": "CircuitJudge",
  "name": "John T. Alexander",
  "attributes": {
    "county": "Barren & Metcalfe",
    "circuit": "Cir. 43, Div. 01",
    "phone": "(270) 651-2744",
    "fax": "(270) 651-7051",
    "address": "Chief Circuit Judge, Barren County Courthouse, 300 Courthouse Square, Glasgow, KY 42141"
  }
}
```

#### 2. DistrictJudge (94 entities)
**Purpose:** District court judges handling misdemeanors, traffic, small claims

**Attributes:**
- `county`: County or multi-county area
- `district`: District and division (e.g., "Dist. 18, Div. 01")
- `division`: Division number
- `phone`: Chambers phone
- `email`: Email address
- `address`: Chambers address

**Relationships:**
- `DistrictJudge -[PRESIDES_OVER]-> Court`
- `Case -[ASSIGNED_TO]-> DistrictJudge`
- `Episode -[ABOUT]-> DistrictJudge`

#### 3. AppellateJudge (15 entities)
**Purpose:** Kentucky Court of Appeals judges

**Attributes:**
- `phone`: Phone number
- `email`: Email address
- `address`: Chambers address

**Relationships:**
- `AppellateJudge -[PRESIDES_OVER]-> Court` (Court of Appeals)
- `Episode -[ABOUT]-> AppellateJudge`

#### 4. SupremeCourtJustice (8 entities)
**Purpose:** Kentucky Supreme Court justices

**Attributes:**
- `phone`: Phone number
- `email`: Email address
- `address`: Chambers address

**Relationships:**
- `SupremeCourtJustice -[PRESIDES_OVER]-> Court` (Supreme Court)
- `Episode -[ABOUT]-> SupremeCourtJustice`

---

### Court Staff (Individual People)

#### 5. CourtClerk (120 entities)
**Purpose:** Circuit and district court clerks

**Attributes:**
- `clerk_type`: "circuit" or "district"
- `county`: County served
- `phone`: Office phone
- `email`: Email address
- `address`: Office address

**Relationships:**
- `CourtClerk -[WORKS_AT]-> Court`
- `Episode -[ABOUT]-> CourtClerk`

**Example:**
```json
{
  "entity_type": "CourtClerk",
  "name": "Gary W. Barton",
  "attributes": {
    "clerk_type": "circuit",
    "county": "Whitley",
    "phone": "(606) 549-2973 ; (606) 549-5162",
    "fax": "(606) 549-3393",
    "address": "Whitley County Circuit Court Clerk, Whitley County Judicial Center, 100 Main St., P.O. Box 329, Williamsburg, KY 40769-0329"
  }
}
```

#### 6. MasterCommissioner (114 entities)
**Purpose:** Court-appointed commissioners for property sales, discovery, etc.

**Attributes:**
- `county`: County served
- `phone`: Phone number
- `email`: Email address
- `address`: Office address

**Relationships:**
- `MasterCommissioner -[APPOINTED_BY]-> Court`
- `Episode -[ABOUT]-> MasterCommissioner`

#### 7. CourtAdministrator (7 entities)
**Purpose:** Court administrative staff

**Attributes:**
- `role`: Specific role or title
- `phone`: Phone number
- `email`: Email address
- `address`: Office address

**Relationships:**
- `CourtAdministrator -[WORKS_AT]-> Court`
- `Episode -[ABOUT]-> CourtAdministrator`

---

### Court Offices/Departments (Organizations - 360 entities)

These are imported as **Organization** entities with specific `organization_type`:

1. **Pretrial Services** (120 locations)
   - `organization_type`: "pretrial_services"
   - County-specific pretrial services offices

2. **Drug Courts** (120 locations)
   - `organization_type`: "drug_court"
   - Specialized treatment courts

3. **Court Designated Worker Program** (120 locations)
   - `organization_type`: "court_designated_worker_program"
   - Court social services

---

## Complete WORKS_AT / Professional Relationship Pattern

All professional entities now follow this pattern:

| Person Entity | Organization Entity | Relationship |
|---------------|---------------------|--------------|
| Attorney | LawFirm | WORKS_AT |
| CaseManager | LawFirm | WORKS_AT |
| Doctor | MedicalProvider | WORKS_AT |
| Adjuster | Insurer | WORKS_AT |
| Expert | Organization | WORKS_AT |
| Mediator | Organization | WORKS_AT |
| CircuitJudge | Court | PRESIDES_OVER |
| DistrictJudge | Court | PRESIDES_OVER |
| AppellateJudge | Court | PRESIDES_OVER |
| SupremeCourtJustice | Court | PRESIDES_OVER |
| CourtClerk | Court | WORKS_AT |
| MasterCommissioner | Court | APPOINTED_BY |
| CourtAdministrator | Court | WORKS_AT |

---

## Graph Query Examples

### Find judge assigned to a case:
```cypher
MATCH (c:Case {name: $case_name})-[:ASSIGNED_TO]->(j:CircuitJudge)
RETURN j.name, j.circuit, j.county
```

### Find which court a judge presides over:
```cypher
MATCH (j:CircuitJudge {name: "John T. Alexander"})-[:PRESIDES_OVER]->(c:Court)
RETURN c.name, c.county
```

### Find all judges in Jefferson County:
```cypher
MATCH (j:CircuitJudge)
WHERE j.county CONTAINS "Jefferson"
RETURN j.name, j.circuit
```

### Find court clerk for a specific court:
```cypher
MATCH (clerk:CourtClerk)-[:WORKS_AT]->(c:Court {name: "Jefferson County Circuit Court"})
RETURN clerk.name, clerk.phone, clerk.email
```

---

## Files Created

1. **Entity Type Definitions** (`graphiti_client.py`)
   - CircuitJudge (line 288-295)
   - DistrictJudge (line 298-305)
   - AppellateJudge (line 308-312)
   - SupremeCourtJustice (line 315-319)
   - CourtClerk (line 322-328)
   - MasterCommissioner (line 331-336)
   - CourtAdministrator (line 339-344)

2. **Entity JSON Files** (`json-files/memory-cards/entities/`)
   - `circuit_judges.json` (101 judges)
   - `district_judges.json` (94 judges)
   - `appellate_judges.json` (15 judges)
   - `supreme_court_justices.json` (8 justices)
   - `court_clerks.json` (120 clerks)
   - `master_commissioners.json` (114 commissioners)
   - `court_administrators.json` (7 administrators)
   - `organizations.json` (+360 court offices)

3. **Relationship Mappings** (EDGE_TYPE_MAP lines 1033-1044)
   - PRESIDES_OVER (judges → courts)
   - WORKS_AT (clerks/administrators → courts)
   - APPOINTED_BY (commissioners → courts)
   - ASSIGNED_TO (cases → judges)

---

## Total Entity Count: 819 Court Personnel

- **Judges**: 218 (101 Circuit + 94 District + 15 Appellate + 8 Supreme)
- **Court Staff**: 241 (120 Clerks + 114 Master Commissioners + 7 Administrators)
- **Court Offices**: 360 (Organizations for pretrial services, drug courts, etc.)

Skipped: 174 vacant positions or entries without category

---

## Usage in Episodes

When processing episodes, the LLM can now extract mentions of court personnel:

```
Episode: "Case assigned to Judge John T. Alexander in Barren Circuit Court."

Proposed relationships:
{
  "about": [
    {"entity_type": "CircuitJudge", "entity_name": "John T. Alexander"},
    {"entity_type": "Court", "entity_name": "Barren County Circuit Court"}
  ]
}
```

The graph will then have:
- Episode -[ABOUT]-> CircuitJudge "John T. Alexander"
- Episode -[ABOUT]-> Court "Barren County Circuit Court"
- CircuitJudge "John T. Alexander" -[PRESIDES_OVER]-> Court "Barren County Circuit Court"
