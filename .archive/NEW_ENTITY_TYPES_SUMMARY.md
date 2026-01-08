# New Entity Types and Relationships

## Overview

Added 3 new entity types following the Attorney → LawFirm pattern for professional service providers.

## New Entity Types

### 1. Doctor
**Purpose:** Individual physicians (separate from medical provider organizations)

**Attributes:**
- `specialty`: Medical specialty (orthopedic, neurology, pain management, etc.)
- `credentials`: MD, DO, DC, PT, etc.
- `phone`: Phone number
- `email`: Email address
- `npi`: National Provider Identifier

**Relationships:**
- `Doctor -[WORKS_AT]-> MedicalProvider` (e.g., Dr. Wallace Huff -[WORKS_AT]-> Bluegrass Orthopaedics)
- `Doctor -[TREATED_BY]-> Client`
- `Doctor -[TREATED_BY]-> Case`
- `Episode -[ABOUT]-> Doctor`

**Example:**
```json
{
  "card_type": "entity",
  "entity_type": "Doctor",
  "name": "Dr. Wallace Huff",
  "attributes": {
    "specialty": "orthopedic",
    "credentials": "MD",
    "phone": "",
    "email": ""
  }
}
```

Then create relationship:
```cypher
MATCH (d:Doctor {name: "Dr. Wallace Huff"}), (p:MedicalProvider {name: "Bluegrass Orthopaedics"})
CREATE (d)-[:WORKS_AT]->(p)
```

---

### 2. Expert
**Purpose:** Expert witnesses (vocational, medical, life care planners, accident reconstruction, economists, etc.)

**Attributes:**
- `expert_type`: vocational, medical, accident_reconstruction, life_care_planner, economist, engineering, biomechanics, other
- `credentials`: Professional credentials
- `phone`: Phone number
- `email`: Email address
- `firm_name`: Expert firm/organization if applicable
- `hourly_rate`: Rate for services

**Relationships:**
- `Expert -[WORKS_AT]-> Organization` (e.g., Expert -[WORKS_AT]-> "Vocational Economics")
- `Expert -[RETAINED_FOR]-> Case`
- `Case -[RETAINED_EXPERT]-> Expert`
- `Episode -[ABOUT]-> Expert`

**Examples from Amy Mills review:**
- "Vocational Economics" (vocational expert firm)
- "PMR Life Care Plans, LLC" (life care planning)
- "BioKinetics" (biomechanical expert)
- "Commonwealth IME" (independent medical examination)

---

### 3. Mediator
**Purpose:** Mediators and arbitrators for case resolution

**Attributes:**
- `credentials`: Retired Judge, Esq., etc.
- `phone`: Phone number
- `email`: Email address
- `firm_name`: Mediation service organization if applicable
- `hourly_rate`: Rate for mediation services

**Relationships:**
- `Mediator -[WORKS_AT]-> Organization` (e.g., Hon. Thomas Knopf -[WORKS_AT]-> "Thomas J. Knopf Mediation Services")
- `Mediator -[RETAINED_FOR]-> Case`
- `Case -[RETAINED_MEDIATOR]-> Mediator`
- `Episode -[ABOUT]-> Mediator`

**Examples from Amy Mills review:**
- "Hon. Thomas J. Knopf (Ret.)" → Mediator entity
- "Thomas J. Knopf Mediation Services" → Organization
- "National Academy of Distinguished Neutrals (NADN)" → Organization

---

## Updated MedicalProvider

**MedicalProvider** now represents **organizations/facilities only**, not individual doctors:

**Added attribute:**
- `provider_type`: hospital, clinic, imaging_center, therapy_center, etc.

**Examples:**
- Baptist Health - Corbin (hospital)
- Bluegrass Orthopaedics (orthopedic clinic)
- Corbin Imaging And Diagnostic Center (imaging_center)
- PT Pros Physical Therapy (therapy_center)

---

## Relationship Pattern (Same as Attorney/LawFirm)

### Attorney Pattern (Existing):
```
Attorney: "Bryce Cotton"
   |
   | [WORKS_AT]
   ↓
LawFirm: "Blackburn Domene & Burchett, PLLC"
```

### Doctor Pattern (NEW):
```
Doctor: "Dr. Wallace Huff"
   |
   | [WORKS_AT]
   ↓
MedicalProvider: "Bluegrass Orthopaedics"
```

### Expert Pattern (NEW):
```
Expert: "Linda Jones"  (vocational expert)
   |
   | [WORKS_AT]
   ↓
Organization: "Vocational Economics"
```

### Mediator Pattern (NEW):
```
Mediator: "Hon. Thomas J. Knopf (Ret.)"
   |
   | [WORKS_AT]
   ↓
Organization: "Thomas J. Knopf Mediation Services"
```

---

## Graph Query Examples

### Find all doctors treating a case:
```cypher
MATCH (c:Case {name: $case_name})-[:TREATING_AT]->(d:Doctor)
RETURN d.name, d.specialty
```

### Find which medical provider a doctor works at:
```cypher
MATCH (d:Doctor {name: "Dr. Wallace Huff"})-[:WORKS_AT]->(p:MedicalProvider)
RETURN p.name, p.provider_type
```

### Find all experts retained for a case:
```cypher
MATCH (c:Case {name: $case_name})-[:RETAINED_EXPERT]->(e:Expert)
OPTIONAL MATCH (e)-[:WORKS_AT]->(o:Organization)
RETURN e.name, e.expert_type, o.name AS firm
```

### Find all episodes mentioning a doctor:
```cypher
MATCH (ep:Episode)-[:ABOUT]->(d:Doctor {name: "Dr. Wallace Huff"})
RETURN ep.content, ep.valid_at
ORDER BY ep.valid_at DESC
```

---

## Files Updated

1. **`src/roscoe/core/graphiti_client.py`**
   - Added `Doctor` Pydantic model (line 211-218)
   - Added `Expert` Pydantic model (line 298-305)
   - Added `Mediator` Pydantic model (line 308-314)
   - Updated `ENTITY_TYPES` list to include new types (lines 516, 528-529)
   - Updated `EDGE_TYPE_MAP` with new relationships (lines 899-904, 957-965, 1037, 1054-1055)

2. **`src/roscoe/scripts/process_episodes_for_case.py`**
   - Updated `valid_types` list to include Doctor, Expert, Mediator, CaseManager (lines 156-161)

3. **Entity JSON files created:**
   - `json-files/memory-cards/entities/doctors.json`
   - `json-files/memory-cards/entities/experts.json`
   - `json-files/memory-cards/entities/mediators.json`

---

## Next Steps

1. **Identify doctor mentions in reviews** and reclassify from MedicalProvider to Doctor
   - Example: "Dr. Wallace Huff" → Doctor entity
   - "Bluegrass Orthopaedics" → MedicalProvider entity
   - Create WORKS_AT relationship between them

2. **Identify expert mentions** and create Expert entities
   - Example: "Vocational Economics" (currently Organization) → keep as Organization
   - Create individual expert: "Linda Jones" → Expert entity with WORKS_AT → "Vocational Economics"

3. **Identify mediator mentions** and create Mediator entities
   - Example: "Hon. Thomas J. Knopf (Ret.)" → Mediator entity
   - "Thomas J. Knopf Mediation Services" → Organization entity
   - Create WORKS_AT relationship

4. **Update review generation** to recognize these entity types and suggest proper classifications

---

## Why This Matters

**Before:** All mixed together
- "Dr. Wallace Huff" classified as MedicalProvider
- No way to query "which doctors treated this client?"
- No way to see "which providers does Dr. Huff work for?"

**After:** Clean separation
- Doctors are people (can change employers)
- Medical Providers are organizations (hospitals, clinics)
- One-hop graph traversal: Doctor -[WORKS_AT]-> MedicalProvider
- Same pattern as Attorney -[WORKS_AT]-> LawFirm
