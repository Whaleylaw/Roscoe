# Roscoe Knowledge Graph Schema

**Current as of:** January 4, 2026
**Graph Database:** FalkorDB
**Total Nodes:** 45,962
**Total Relationships:** 47,252
**Entity Types:** 52
**Relationship Types:** ~30+

---

## Overview

The Roscoe knowledge graph is a comprehensive representation of personal injury case data, built on FalkorDB. It uses a graph structure to represent cases, people, organizations, events, and their relationships.

**Key Features:**
- Three-tier medical provider hierarchy (HealthSystem → Facility → Location)
- Multi-role entity support (same entity can be provider, defendant, vendor)
- Semantic episode search (10,976 episodes with 384-dim embeddings)
- Progressive detail workflow (vague → specific as information arrives)
- Deterministic workflow state management

---

## Core Entity Types

### Case Management

| Entity | Description | Example |
|--------|-------------|---------|
| **Case** | Personal injury case | "Christopher-Lanier-MVA-6-28-2025" |
| **Client** | Individual represented | "Christopher Lanier" |
| **Defendant** | Party being sued | "John Doe" (at-fault driver) |
| **Episode** | Timeline event with semantic embedding | "Adjuster call on 2025-12-15" |

**Episode Details:**
- Total: 10,976 episodes
- All have semantic embeddings (384-dim using sentence-transformers)
- Enable semantic search, timeline queries, entity linkage

---

## Medical Provider Hierarchy

### Three-Tier Structure

```
HealthSystem (6 total)
  ↓ [:PART_OF]
Facility (1,163 total)
  ↓ [:PART_OF]
Location (1,969 total)
```

| Entity | Count | Description | Example |
|--------|-------|-------------|---------|
| **HealthSystem** | 6 | Top-level health systems | Norton Healthcare, UofL Health, Baptist Health, CHI Saint Joseph, St. Elizabeth, Norton Children's |
| **Facility** | 1,163 | Treatment facilities/programs | Norton Orthopedic Institute, Starlight Chiropractic |
| **Location** | 1,969 | Physical locations with addresses | Norton Orthopedic Institute - Downtown |
| **Doctor** | 20,708 | Individual KY-licensed physicians | Dr. John Smith |

**Relationships:**
- Location -[:PART_OF]-> Facility
- Facility -[:PART_OF]-> HealthSystem
- Doctor -[:WORKS_AT]-> Location (or Facility)
- Client -[:TREATED_AT]-> Location (or Facility if location unknown)

**Multi-Role Capability:**
Same entity can play different roles:
- Provider: Client -[:TREATED_AT]-> Location
- Defendant: Case -[:DEFENDANT]-> Location (premise liability)
- Vendor: Case -[:VENDOR_FOR]-> Location (medical chronology service)
- Expert Source: Doctor -[:WORKS_AT]-> Location

---

## Medical Documentation

| Entity | Description | Key Fields |
|--------|-------------|------------|
| **MedicalVisit** | Individual visit by date | visit_date, related_to_injury (for lien negotiation), diagnosis, unrelated_reason |
| **Bill** | Medical bill | amount, provider, date_of_service |
| **Expense** | Case expense | amount, category, date |

**Relationships:**
- MedicalVisit -[:AT_LOCATION]-> Location
- MedicalVisit -[:HAS_BILL]-> Bill
- Bill -[:FROM_PROVIDER]-> Facility/Location

**Use Case: Lien Negotiation**
- Query MedicalVisit where related_to_injury = true
- Exclude unrelated visits from lien repayment calculations

---

## Document System

### Document Entity

| Entity | Description | Key Fields |
|--------|-------------|------------|
| **Document** | Any file in the case file system | path, document_type, file_type, description |

**Document Properties:**
- **name**: The filename (set explicitly, not auto-generated)
- **path**: Path relative to case folder (e.g., "Medical Records/Norton_MRI_2024.pdf")
- **document_type**: Category - one of: letter_of_rep, demand_package, medical_records, medical_bills, records_request, hipaa, retainer, pleading, discovery, correspondence, evidence
- **file_type**: File extension (pdf, docx, jpg, png, etc.)
- **description**: Brief description of document contents

### Specialized Document Subtypes

| Subtype | Description | Additional Fields |
|---------|-------------|-------------------|
| **MedicalRecords** | Clinical records from providers | provider_name, date_range_start, date_range_end, page_count |
| **MedicalBills** | Bills from providers | provider_name, total_amount, date_range_start, date_range_end |
| **MedicalRecordsRequest** | Request for records | provider_name, request_date, response_due, status |
| **LetterOfRepresentation** | LOR sent to parties | recipient, sent_date, delivery_method |
| **InsuranceDocument** | Insurance-related docs | insurer_name, policy_number, document_subtype |
| **CorrespondenceDocument** | Letters, emails, faxes | sender, recipient, sent_date, correspondence_type |

### Document Relationships

**Link documents to entities:**
```
Document -[:IN_CASE]-> Case
Document -[:FROM_PROVIDER]-> Facility/Location
Document -[:FROM_INSURER]-> Insurer
Document -[:REGARDING_CLAIM]-> Claim (BIClaim, PIPClaim, etc.)
Document -[:FILED_WITH]-> Court/CircuitDivision
Document -[:SENT_TO]-> Attorney/Adjuster/LienHolder
```

**Examples:**

**Medical Records:**
```cypher
CREATE (d:MedicalRecords {
  name: "Norton_Orthopedic_Records_2024.pdf",
  path: "Medical Records/Norton_Orthopedic_Records_2024.pdf",
  document_type: "medical_records",
  file_type: "pdf",
  provider_name: "Norton Orthopedic Institute",
  date_range_start: "2024-01-15",
  date_range_end: "2024-06-30",
  page_count: 47
})
MATCH (c:Case {name: "Wilson-MVA-2024"})
MATCH (f:Facility {name: "Norton Orthopedic Institute"})
CREATE (d)-[:IN_CASE]->(c)
CREATE (d)-[:FROM_PROVIDER]->(f)
```

**Insurance Document:**
```cypher
CREATE (d:InsuranceDocument {
  name: "Progressive_Dec_Page.pdf",
  path: "Insurance/Progressive_Dec_Page.pdf",
  document_type: "insurance",
  file_type: "pdf",
  insurer_name: "Progressive",
  policy_number: "12345678",
  document_subtype: "declarations_page"
})
MATCH (c:Case {name: "Wilson-MVA-2024"})
MATCH (i:Insurer {name: "Progressive"})
CREATE (d)-[:IN_CASE]->(c)
CREATE (d)-[:FROM_INSURER]->(i)
```

**Use Cases:**
- Track which documents have been received from providers
- Link medical bills to facilities for lien negotiation
- Associate pleadings with court filings
- Create document inventory per case
- Query: "Show all documents from Norton Healthcare"

---

## Insurance Entities

### Insurance Structure

| Entity | Description | Key Fields |
|--------|-------------|------------|
| **Insurer** | Insurance company | name, address, contact |
| **Adjuster** | Claims adjuster | name, phone, email, insurer |
| **InsurancePolicy** | Policy providing coverage | policy_number, pip_limit, bi_limit, coverage_limits |
| **InsurancePayment** | Individual payment | amount, date, payment_type, recipient |

### Claim Types

| Entity | Description |
|--------|-------------|
| **PIPClaim** | Personal Injury Protection claim |
| **BIClaim** | Bodily Injury claim |
| **UMClaim** | Uninsured Motorist claim |
| **UIMClaim** | Underinsured Motorist claim |
| **WCClaim** | Workers' Compensation claim |

**All Claims Include:**
- claim_number, insurer_name, adjuster_name
- date_filed, status, amount_demanded, amount_offered
- denial_date, denial_reason, appeal_filed, appeal_date, appeal_outcome

**Relationships:**
- Claim -[:UNDER_POLICY]-> InsurancePolicy
- InsurancePolicy -[:WITH_INSURER]-> Insurer
- Claim -[:HANDLED_BY]-> Adjuster
- Claim -[:MADE_PAYMENT]-> InsurancePayment

---

## Liens and Subrogation

| Entity | Description | Key Fields |
|--------|-------------|------------|
| **Lien** | Medical lien or subrogation claim | amount, lien_type, status, date_filed |
| **LienHolder** | Entity holding lien | name, lien_type (medical, ERISA, Medicare, Medicaid, hospital), contact |

**Relationships:**
- Lien -[:HELD_BY]-> LienHolder
- Lien -[:AGAINST_CASE]-> Case
- Lien -[:FOR_PROVIDER]-> Facility/Location

---

## Court System

### Court Structure

```
Court (118 total)
  ↓ [:HAS_DIVISION]
CircuitDivision or DistrictDivision (192 total)
  ↓ [:PRESIDES_OVER]
CircuitJudge or DistrictJudge (218 total)
```

| Entity | Count | Description |
|--------|-------|-------------|
| **Court** | 118 | Kentucky courts |
| **CircuitDivision** | ~96 | Circuit court divisions |
| **DistrictDivision** | ~96 | District court divisions |
| **CircuitJudge** | ~109 | Circuit judges |
| **DistrictJudge** | ~109 | District judges |

**Court Personnel:**
- **CourtClerk** - Court clerks
- **MasterCommissioner** - Master commissioners
- **CourtAdministrator** - Court administrators
- Total personnel: 236

**Relationships:**
- CircuitDivision -[:PART_OF]-> Court
- DistrictDivision -[:PART_OF]-> Court
- CircuitJudge -[:PRESIDES_OVER]-> CircuitDivision
- DistrictJudge -[:PRESIDES_OVER]-> DistrictDivision
- Case -[:FILED_IN]-> CircuitDivision (or DistrictDivision)

---

## Litigation Entities

| Entity | Description | Key Fields |
|--------|-------------|------------|
| **Pleading** | Court filing | pleading_type, file_date, status |
| **CourtEvent** | Hearing/trial/mediation | event_type, event_date, location, outcome |
| **Discovery** | Discovery request/response | discovery_type, due_date, completion_date |

**Pleading Fields:**
- pleading_type, file_date, docket_number
- status, filed_by
- discovery_request_date, discovery_response_due, discovery_completed
- interrogatories_served, requests_for_production_served

**Relationships:**
- Pleading -[:FILED_IN]-> CircuitDivision
- CourtEvent -[:FOR_CASE]-> Case
- CourtEvent -[:AT_COURT]-> Court
- Pleading -[:RELATED_TO]-> Case

---

## Legal Professionals

| Entity | Description | Key Fields |
|--------|-------------|------------|
| **Attorney** | Lawyer | name, bar_number, practice_areas, specialization, years_experience |
| **LawFirm** | Law firm | name, address, phone |
| **LawFirmOffice** | Specific office location | office_name, address, city, state |
| **CaseManager** | Case manager/paralegal | name, role, contact |

**Relationships:**
- Attorney -[:WORKS_AT]-> LawFirm
- Attorney -[:WORKS_AT]-> LawFirmOffice
- LawFirmOffice -[:PART_OF]-> LawFirm
- Attorney -[:REPRESENTS]-> Client
- Attorney -[:OPPOSING_COUNSEL_FOR]-> Case

---

## Workflow and State Management

### Phase System

| Entity | Description |
|--------|-------------|
| **Phase** | Case phase | file_setup, treatment, demand_in_progress, negotiation, litigation, closed |
| **LandmarkStatus** | Checkpoint status | landmark_id, status (complete/incomplete/in_progress/not_applicable), completion_date |

**Phases (in order):**
1. file_setup - Initial setup, retainer, insurance identification
2. treatment - Active medical treatment
3. demand_in_progress - Preparing demand package
4. negotiation - Settlement negotiations
5. litigation - Case filed in court
6. closed - Case resolved

**Landmark Examples:**
- retainer_signed (hard blocker for file_setup)
- full_intake_complete
- insurance_claims_setup
- treatment_complete
- demand_sent (hard blocker for demand_in_progress)
- settlement_reached

**Relationships:**
- Case -[:IN_PHASE]-> Phase
- Case -[:HAS_STATUS]-> LandmarkStatus (count: 8,991)
- LandmarkStatus -[:FOR_LANDMARK]-> Landmark

---

## Episode System

### Episodes and Semantic Search

| Entity | Count | Description |
|--------|-------|-------------|
| **Episode** | 10,976 | Timeline events with semantic embeddings |

**Episode Properties:**
- uuid (unique identifier)
- name (episode name)
- content (natural language description)
- valid_at (timestamp)
- author (who created it)
- case_name (associated case)
- episode_type (imported, user_note, etc.)
- group_id (always "roscoe_graph")
- embedding (384-dim vector for semantic search)
- created_at (timestamp)

**Relationships:**
- Episode -[:RELATES_TO]-> Case (count: ~10,883)
- Episode -[:ABOUT]-> Any Entity (count: ~13,863)

**Use Cases:**
- Semantic search: "Find episodes about settlement negotiations"
- Timeline queries: "What happened last week?"
- Entity tracking: "All episodes mentioning Dr. Smith"

---

## Key Relationship Patterns

### Medical Hierarchy
- Location -[:PART_OF]-> Facility (count: ~1,969)
- Facility -[:PART_OF]-> HealthSystem (count: ~1,163)
- Total hierarchy relationships: 2,517

### Treatment
- Client -[:TREATED_AT]-> Facility (when location unknown)
- Client -[:TREATED_AT]-> Location (when address known)

### Multi-Role Examples
- Client -[:TREATED_AT]-> Location (provider role)
- Case -[:DEFENDANT]-> Location (defendant role - premise liability)
- Case -[:VENDOR_FOR]-> Location (vendor role - services)
- Doctor -[:WORKS_AT]-> Location (employment)

### Episode Linkage
- Episode -[:RELATES_TO]-> Case (timeline for case)
- Episode -[:ABOUT]-> Facility/Location/Attorney/Adjuster/etc. (entity mentions)

### Insurance
- Claim -[:UNDER_POLICY]-> InsurancePolicy
- InsurancePolicy -[:WITH_INSURER]-> Insurer
- Claim -[:MADE_PAYMENT]-> InsurancePayment

### Workflow State
- Case -[:IN_PHASE]-> Phase
- Case -[:HAS_STATUS]-> LandmarkStatus (count: 8,991)

### Court System
- CircuitDivision -[:PART_OF]-> Court
- CircuitJudge -[:PRESIDES_OVER]-> CircuitDivision
- Case -[:FILED_IN]-> CircuitDivision

---

## Progressive Detail Workflow

The graph supports progressive refinement as information becomes available:

**Initial (vague information):**
```
"Client treated at Norton Orthopedic"
→ Client -[:TREATED_AT]-> Facility: "Norton Orthopedic Institute"
```

**Later (specific location from records):**
```
"Records show Norton Orthopedic Institute - Downtown"
→ Client -[:TREATED_AT]-> Location: "Norton Orthopedic Institute - Downtown"
```

**Records Request (query up hierarchy):**
```
Location: "Norton Ortho - Downtown"
  → parent_facility: "Norton Orthopedic Institute"
  → parent_system: "Norton Healthcare"
    → records_request_address: "Norton Healthcare Medical Records, PO Box..."
```

**Fields for Records Requests:**
Available at all three levels (Location, Facility, HealthSystem):
- records_request_method (mail, fax, portal, online)
- records_request_address
- records_request_url
- records_request_phone
- billing_request_address
- billing_request_phone
- billing_request_email

**Inheritance:** If not set at Location, check Facility, then HealthSystem

---

## Summary Statistics

### Node Counts (Total: 45,962)

| Entity Type | Count | Percentage |
|-------------|-------|------------|
| Doctor | 20,708 | 45.0% |
| Episode | 10,976 | 23.9% |
| LandmarkStatus | 8,991 | 19.6% |
| Location | 1,969 | 4.3% |
| Facility | 1,163 | 2.5% |
| Pleading | 168 | 0.4% |
| Other entities | ~2,000 | 4.3% |

### Relationship Counts (Total: 47,252)

| Relationship Type | Count (est.) | Percentage |
|-------------------|--------------|------------|
| Episode -[:ABOUT]-> Entity | 13,863 | 29.3% |
| Episode -[:RELATES_TO]-> Case | 10,883 | 23.0% |
| Case -[:HAS_STATUS]-> LandmarkStatus | 8,991 | 19.0% |
| Location/Facility -[:PART_OF]-> Parent | 2,517 | 5.3% |
| Other relationships | 11,000 | 23.3% |

### Entity Type Count: 52 Labels

**New Entity Types (added in Jan 2026 migration):**
- Facility
- Location
- InsurancePolicy
- InsurancePayment
- MedicalVisit
- CourtEvent
- LawFirmOffice

**Enhanced Entities (major field additions):**
- HealthSystem (12 new fields)
- PIPClaim, BIClaim, UMClaim, UIMClaim, WCClaim (5 denial/appeal fields each)
- Pleading (5 discovery fields)
- Attorney (6 professional detail fields)

---

## Schema Definition Location

**Primary Schema File:**
`/Volumes/X10 Pro/Roscoe/src/roscoe/core/graphiti_client.py`

**Contents:**
- 67 Pydantic entity class definitions
- 110+ relationship type mappings (EDGE_TYPE_MAP)
- Pure Pydantic models + Cypher helpers
- No Graphiti library dependencies (cleaned in Jan 2026)
- 2,776 lines

**Schema Package (reference data):**
`/Volumes/X10 Pro/Roscoe/schema-final/`
- entities/facilities.json (1,164 entities)
- entities/locations.json (2,325 entities)
- entities/health_systems.json (6 entities)
- entities/hierarchy_relationships.json (2,873 mappings)
- documentation/ (guides)

---

## Design Principles

### 1. Graph-First Data Model
All case data stored in graph, not JSON files. Graph tools (query_case_graph, update_case_data) are the interface.

### 2. Multi-Role Entity Support
Same entity can have different roles via different relationship types.

### 3. Progressive Detail
Support linking to Facility when location unknown, adding Location when address available.

### 4. Semantic Search
All Episodes have embeddings for meaning-based search, not just keywords.

### 5. Deterministic Workflow State
Phase and landmark status computed from graph relationships, not stored in separate files.

### 6. Temporal Awareness
Episodes track when information was known (valid_at), enabling "What changed since X?" queries.

### 7. Hierarchical Inheritance
Medical provider metadata (records request info) inherits up hierarchy: Location → Facility → HealthSystem.

---

## Query Examples

### Find All Cases for a Provider
```cypher
MATCH (c:Client)-[:TREATED_AT]->(f:Facility {name: "Norton Orthopedic Institute"})
MATCH (case:Case)-[:HAS_CLIENT]->(c)
RETURN case.name, c.name
```

### Get Medical Provider Hierarchy
```cypher
MATCH (l:Location)-[:PART_OF]->(f:Facility)-[:PART_OF]->(h:HealthSystem)
WHERE l.name = "Norton Orthopedic Institute - Downtown"
RETURN h.name, f.name, l.name, l.address
```

### Semantic Episode Search (via embeddings)
```
Use query_case_graph() tool with natural language:
"Find episodes about settlement negotiations"
System computes similarity between query embedding and episode embeddings
```

### Get Case Workflow Status
```cypher
MATCH (case:Case {name: "Christopher-Lanier-MVA-6-28-2025"})-[:IN_PHASE]->(p:Phase)
MATCH (case)-[:HAS_STATUS]->(ls:LandmarkStatus)
RETURN p.name, ls.landmark_id, ls.status
```

### Multi-Role Entity Query
```cypher
MATCH (norton:Location {name: "Norton Hospital"})
OPTIONAL MATCH (c1:Client)-[:TREATED_AT]->(norton)
OPTIONAL MATCH (case:Case)-[:DEFENDANT]->(norton)
OPTIONAL MATCH (case2:Case)-[:VENDOR_FOR]->(norton)
RETURN norton.name, count(c1) as patients, count(case) as defendant_cases, count(case2) as vendor_cases
```

---

## Migration Notes

**Last Major Migration:** January 4, 2026

**Changes:**
- Replaced flat MedicalProvider (1,998 nodes) with three-tier hierarchy (3,138 nodes)
- Added 10,976 Episodes with semantic embeddings
- Ingested reference data: 118 courts, 192 divisions, 218 judges, 20,708 doctors
- Created 2,517 hierarchy relationships
- Updated 111 case reviews with corrected entity names
- Cleaned schema: removed Graphiti library dependencies

**Data Integrity:**
- 94% of existing graph untouched during migration
- All episodes linked to new Facility/Location structure
- Provider name mappings created (259 verified pairs)
- No data loss

---

**Document Version:** 1.0
**Last Updated:** January 4, 2026
**Maintained By:** Schema changes should update this document
