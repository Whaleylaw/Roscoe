# CLAUDE_GRAPH.md

This file provides guidance to Claude Code when working on the **Roscoe Knowledge Graph** - a comprehensive case management knowledge graph for personal injury litigation.

**Related:** See `/CLAUDE.md` for overall Roscoe system architecture.

---

## Graph Overview

**Roscoe Knowledge Graph** is a custom implementation using FalkorDB (graph database) with Pydantic-modeled entities and relationships. The graph represents the complete state of personal injury cases, including people, organizations, medical treatment, insurance claims, legal proceedings, and temporal case history.

**Backend:** FalkorDB (Redis-compatible graph database with Cypher query language)
**Schema:** 58 entity types, 71 relationship types (all Pydantic models)
**Scale:** ~45,900 entities across 138 cases
**Purpose:** Semantic search, relationship inference, case context, temporal queries

**Note:** We use Pydantic models from `graphiti_client.py` for schema definition but do NOT use Graphiti for automatic ingestion. All relationships are manually reviewed and approved before ingestion.

---

## Current Graph State

### **Entities Imported (45,900+ total):**

| Entity Type | Count | Source |
|-------------|-------|--------|
| **Doctors** | 20,732 | KY Medical Board directory |
| **MedicalProviders** | 2,159 | Healthcare systems import (was 773) |
| **Court Divisions** | 192 | Extracted from judge assignments |
| **Court Personnel** | 819 | KY Court directory (judges, clerks, commissioners) |
| **Organizations** | 384 | Directory + case data |
| **Courts** | 106 | KY Court system (with division info) |
| **Clients** | 105 | Case data |
| **Insurers** | 99 | Case data |
| **Vendors** | 40 | Directory + case data |
| **Attorneys** | 34 | Litigation contacts + case data |
| **Law Firms** | 36 | Directory + case data |
| **Defendants** | 11 | Case data |
| **HealthSystems** | 5 | Healthcare parent organizations |
| **Mediators** | 2 | Case data |
| **Witnesses** | 1 | Case data |
| **Court Clerks** | 121 | KY Court directory |

### **Relationships (NOT YET IN GRAPH):**

**Current Status:** Entities have been extracted and stored in JSON files. Relationships are proposed in review documents but **NOT yet ingested to graph**.

**Proposed Relationships:** ~40,000+ ABOUT relationships linking episodes to entities

**In Progress:** Manual review and approval of proposed relationships before graph ingestion

---

## Entity-Centric Knowledge Graph Architecture

### **Design Philosophy:**

The graph represents two layers:

1. **"What" Layer (Entities)** - Current state snapshot
   - Cases, Clients, Providers, Claims, Attorneys, Courts, etc.
   - These are the THINGS in the case

2. **"Why/How" Layer (Episodes)** - Narrative timeline
   - Episodes explain WHY things happened and HOW
   - Linked to entities via ABOUT relationships
   - Example: "Called State Farm adjuster John Smith about PIP claim approval" → ABOUT relationships to Adjuster, Insurer, PIPClaim

### **Episode-Centric Design:**

Episodes are the narrative glue:
```
Episode: "Filed complaint in Jefferson County Circuit Court Division II before Judge O'Connell"
  -[ABOUT]-> CircuitDivision {name: "Jefferson County Circuit Court, Division II"}
  -[ABOUT]-> CircuitJudge {name: "Annie O'Connell"}
  -[ABOUT]-> Pleading {type: "complaint"}
```

**Why Episodes?**
- Capture temporal context ("when did this happen?")
- Preserve narrative ("why did we do this?")
- Enable semantic search ("find all episodes about Dr. Smith")
- Link discrete facts into coherent story

---

## Entity Types (58 total)

### **Core Case Entities:**
- `Case` - Personal injury case
- `Client` - Injured party/plaintiff
- `Defendant` - At-fault party
- `Episode` - Timeline narrative events (replaces Note)
- `Community` - Groups of related entities (Graphiti-inspired)

### **Insurance:**
- `Insurer` - Insurance company
- `Adjuster` - Insurance adjuster (WORKS_AT → Insurer)
- `PIPClaim`, `BIClaim`, `UMClaim`, `UIMClaim`, `WCClaim`, `MedPayClaim` - Claim types

### **Medical:**
- `HealthSystem` - Parent healthcare organization (Norton, UofL, Baptist, CHI, St. Elizabeth)
- `MedicalProvider` - Specific location (PART_OF → HealthSystem)
- `Doctor` - Individual physician (WORKS_AT → MedicalProvider)
- `Lien` - Lien on case
- `LienHolder` - Entity holding lien
- `Bill` - Medical bills and other bills (separate from liens)

### **Legal/Litigation:**
- `LawFirm` - Law firm
- `Attorney` - Lawyer (WORKS_AT → LawFirm)
- `CaseManager` - Paralegal/case manager (WORKS_AT → LawFirm)
- `Court` - Court entity (parent of divisions)
- `CircuitDivision` - Specific circuit court division (PART_OF → Court)
- `DistrictDivision` - Specific district court division (PART_OF → Court)
- `AppellateDistrict` - Court of Appeals regional office
- `SupremeCourtDistrict` - Supreme Court district
- `CircuitJudge` - Judge (PRESIDES_OVER → CircuitDivision)
- `DistrictJudge` - Judge (PRESIDES_OVER → DistrictDivision)
- `AppellateJudge` - Appellate judge
- `SupremeCourtJustice` - Supreme Court justice
- `CourtClerk` - Court clerk (WORKS_AT → Court)
- `MasterCommissioner` - Court-appointed commissioner
- `CourtAdministrator` - Court staff
- `Pleading` - Court filing/document

### **Professional Services:**
- `Expert` - Expert witness (WORKS_AT → Organization)
- `Mediator` - Mediator/arbitrator (WORKS_AT → Organization)
- `Witness` - Fact witness
- `Vendor` - Service provider

### **Documents:**
- `Document` - Generic document
- `MedicalRecords` - Received medical records
- `MedicalBills` - Received medical bills
- `MedicalRecordsRequest` - Outgoing records request
- `LetterOfRepresentation` - Letter of rep sent
- `InsuranceDocument` - Insurance docs (dec pages, EOBs)
- `CorrespondenceDocument` - General correspondence

### **Financial:**
- `Bill` - Medical bills and other bills (separate from liens)
- `Expense` - Case expense
- `Negotiation` - Active settlement negotiation process
- `Settlement` - Final settlement breakdown

### **Other:**
- `Organization` - Generic organization

### **Workflow Entities (Structural):**
- `Phase`, `SubPhase`, `Landmark`, `LandmarkStatus`
- `WorkflowDef`, `WorkflowStep`, `WorkflowChecklist`, `WorkflowSkill`, `WorkflowTemplate`, `WorkflowTool`

---

## Professional Relationship Pattern (WORKS_AT / PRESIDES_OVER)

All professional entities connect to their organizations following a consistent pattern:

| Person Entity | Organization Entity | Relationship |
|---------------|---------------------|--------------|
| Attorney | LawFirm | WORKS_AT |
| CaseManager | LawFirm | WORKS_AT |
| Doctor | MedicalProvider | WORKS_AT |
| Adjuster | Insurer | WORKS_AT |
| Expert | Organization | WORKS_AT |
| Mediator | Organization | WORKS_AT |
| CircuitJudge | CircuitDivision | PRESIDES_OVER |
| DistrictJudge | DistrictDivision | PRESIDES_OVER |
| AppellateJudge | AppellateDistrict | PRESIDES_OVER |
| SupremeCourtJustice | SupremeCourtDistrict | PRESIDES_OVER |
| CourtClerk | Court | WORKS_AT |
| MasterCommissioner | Court | APPOINTED_BY |
| CourtAdministrator | Court | WORKS_AT |

**Benefits:**
- One-hop query: "Which firm does this attorney work for?"
- Change tracking: Update WORKS_AT when attorney changes firms
- Analytics: "How many cases has this judge presided over?"

---

## Court Division Structure (Critical)

### **Why Divisions Matter:**

Kentucky courts have multiple divisions with assigned judges:
- **Jefferson County Circuit Court**: 13 divisions
- **Jefferson County District Court**: 16 divisions
- Each division has a specific judge assigned
- Judges change via elections

### **Graph Structure:**

```
(Court {name: "Jefferson County Circuit Court"})
  ↑ [PART_OF]
(CircuitDivision {name: "Jefferson County Circuit Court, Division II", number: "02"})
  ↑ [PRESIDES_OVER]
(CircuitJudge {name: "Annie O'Connell"})

(Case {name: "Abby-Sitgraves"})-[:FILED_IN]->(CircuitDivision)
(Episode)-[:ABOUT]->(CircuitDivision)
```

### **Division Entities Created:**

- 86 CircuitDivision entities (all KY circuit courts with divisions)
- 94 DistrictDivision entities (all KY district courts with divisions)
- 7 SupremeCourtDistrict entities (geographic regions)
- 5 AppellateDistrict entities (regional offices)

**Files:**
- `circuit_divisions.json`
- `district_divisions.json`
- `supreme_court_districts.json`
- `appellate_districts.json`
- `judge_division_mappings.json` (maps judges to divisions)

### **Division-Specific Attributes:**

```python
class CircuitDivision(BaseModel):
    division_number: str  # "01", "02", etc.
    court_name: str
    circuit_number: str
    local_rules: Optional[str]  # Division-specific rules
    scheduling_preferences: Optional[str]  # Judge preferences
    mediation_required: Optional[bool]
```

**Use Cases:**
- Track judge performance by division
- Store division-specific local rules
- Analyze settlement rates per judge
- Change judge assignment when elections happen

---

## Current Work: Manual Episode Relationship Review & Approval

### **Goal:**
Manually review and approve 40,605 proposed ABOUT relationships between 13,491 episodes and ~45,900 entities before graph ingestion.

### **Why Manual Review?**

We initially tried Graphiti for automatic relationship extraction, but:
- ❌ Created generic RELATES_TO relationships (not specific types like HAS_CLIENT)
- ❌ Entities without proper labels (:Entity instead of :Case, :Client)
- ❌ No control over entity extraction quality
- ❌ Progressive slowdown (10 min/episode)

**Solution:** Custom manual review process with human-in-the-loop before ingestion.

### **Process:**

**Phase 1: GPT-5 Entity Extraction (COMPLETED ✓)**
1. Process 138 cases with GPT-5 Mini/Nano
2. Convert structured notes → natural language (for readability)
3. GPT-5 Mini extracts entity mentions with few-shot examples
4. Generate 138 review documents showing proposed relationships
5. Result: 40,605 proposed ABOUT relationships ready for review

**Phase 2: Manual Review & Approval (IN PROGRESS - 3 of 138 approved)**

**The Review Files (`/json-files/memory-cards/episodes/reviews/`):**
- 138 review_*.md files (one per case)
- Each shows: existing entities vs proposed entity mentions
- Match status: ✓ MATCHES, ? NEW, consolidated variants
- User adds inline annotations for corrections

**Manual Review Workflow:**
1. User reviews batch of 5-10 files
2. Adds inline annotations:
   - "Ignore" → entity should be filtered
   - "Add as attorney" → create entity card
   - "This is Division III" → case-specific court division
   - "She's an attorney, not client" → type correction
3. Developer manually applies corrections (NO automated scripts)
4. Updates entity JSON files
5. Marks file as approved → adds to APPROVED_REVIEWS.txt
6. Regenerates non-approved files with new entity data

**Approved Files (protected from regeneration):**
- review_Abby-Sitgraves-MVA-7-13-2024.md ✓
- review_Abigail-Whaley-MVA-10-24-2024.md ✓
- review_Alma-Cristobal-MVA-2-15-2024.md ✓

**Phase 3: Custom Graph Ingestion (PENDING - after all 138 approved)**
1. Create custom ingestion script (NOT using Graphiti)
2. Ingest approved Episode nodes to FalkorDB
3. Create verified ABOUT relationships (Episode → Entity)
4. Create FOLLOWS relationships (Episode → Episode for temporal/topical links)
5. Create professional relationships (WORKS_AT, PRESIDES_OVER, PART_OF)
6. Add enriched embeddings for semantic search

**Key Difference from Graphiti:**
- **Graphiti:** Automatic entity extraction → immediate ingestion → generic relationships
- **Our Process:** GPT-5 extraction → manual review → approval → custom ingestion → specific relationships

---

## Review Document Structure

### **Example: review_Alma-Cristobal-MVA-2-15-2024.md**

```markdown
## 1. Existing Entities in Graph
*(These are already in the graph for this case)*

### Medical Providers (7)
- Aptiva Health
- University of Louisville Hospital
...

## 2. Proposed Entity Mentions (from LLM extraction)
*(Consolidated duplicates, showing matches to existing entities)*

### Attorney (11 consolidated)
- [ ] Aletha N. Thomas, Esq. — *✓ MATCHES: Aletha N. Thomas, Esq.*
- [ ] Kaleb J. Noblett — *✓ MATCHES: Kaleb J. Noblett*
...

### Court (2 consolidated)
- [ ] Jefferson County Circuit Court, Division III — *✓ MATCHES: Jefferson County Circuit Court, Division III (Judge: Mitch Perry)*
      ↳ _Jefferson 24-CI-004728_
      ↳ _Jefferson Circuit Court_
      ↳ _Jefferson County (24-CI-004728)_
      ... (7 variants consolidated)
```

### **Match Status Meanings:**

- `✓ MATCHES: Entity Name` - Entity exists, ready for relationship creation
- `✓ MATCHES: Entity (Judge: Name)` - Division entity with judge info
- `✓ MATCHES: Entity (WHALEY STAFF → should be CaseManager)` - Type correction needed
- `? NEW` - Entity doesn't exist yet, needs review
- Consolidated with variants shown as `↳ _variant_`

### **Manual Corrections Process:**

**User adds inline annotations:**
```
- [ ] District Court — *✓ MATCHES: Christian County District Court* Now, this is Jefferson County District Court.
```

**Developer manually applies:**
1. Read annotation
2. Understand intent
3. Make correction
4. Update line: `- [ ] District Court — *✓ MATCHES: Jefferson County District Court*`
5. Remove annotation (it's been processed)
6. Add to APPROVED_REVIEWS.txt

**Never use automated scripts to parse annotations** - manual review ensures accuracy.

---

## Entity Files Location

All entity data stored as JSON files in:
`/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities/`

### **Major Files:**

**People:**
- `doctors.json` (20,732) - All KY licensed physicians
- `circuit_judges.json` (101) - Circuit court judges
- `district_judges.json` (94) - District court judges
- `attorneys.json` (34) - Attorneys on cases
- `clients.json` (105) - Case clients
- `adjusters.json` - Insurance adjusters
- `court_clerks.json` (121) - Court clerks
- `mediators.json` (2) - Mediators/arbitrators
- `witnesses.json` (1) - Fact witnesses

**Organizations:**
- `courts.json` (106) - All KY courts
- `circuit_divisions.json` (86) - Circuit court divisions
- `district_divisions.json` (94) - District court divisions
- `health_systems.json` (5) - Parent healthcare organizations
- `medical_providers.json` (2,159) - Hospitals, clinics, imaging centers (was 773)
- `lawfirms.json` (36) - Law firms
- `insurers.json` (99) - Insurance companies
- `organizations.json` (384) - Generic organizations
- `vendors.json` (40) - Service providers

**Claims:**
- `biclaim_claims.json`, `pipclaim_claims.json`, `umclaim_claims.json`, etc.

**Other:**
- `defendants.json` (11)
- `liens.json`, `lienholders.json`

### **Episode Data:**

**Location:** `/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/`

- `cleaned_episodes.json` - 13,491 episodes (filtered from 17,097 original)
- `by_case/*.json` - Episodes grouped by case (104 files)
- `processed_*.json` - 138 files with GPT-5 entity extraction
- `reviews/review_*.md` - 138 review documents for manual approval

---

## Pydantic Schema Definition

**Location:** `/Volumes/X10 Pro/Roscoe/src/roscoe/core/graphiti_client.py`

**Note:** This file is named "graphiti_client" for historical reasons, but we are NOT using Graphiti for episode ingestion. It contains our Pydantic schema definitions for the knowledge graph.

### **Key Sections:**

**Lines 50-500:** Entity type definitions (Pydantic BaseModel classes)
- Each entity type defines its properties
- Example: `class Doctor(BaseModel)` with specialty, credentials, license_number, etc.
- Names are set explicitly during entity creation (not auto-generated)
- Used for schema validation and type checking

**Lines 687-760:** `ENTITY_TYPES` list
- Master list of all 58 entity types
- Defines the complete entity schema
- Used to validate entity extraction during GPT-5 processing

**Lines 770-900:** Relationship type definitions (Pydantic models)
- Defines properties for each relationship type
- Example: `class WorksAt(BaseModel)` with start_date, end_date, role
- Most relationships have optional metadata (dates, amounts, etc.)

**Lines 1000-1350:** `EDGE_TYPE_MAP`
- Defines which relationships are valid between which entity types
- Example: `("Attorney", "LawFirm"): ["WorksAt"]`
- Prevents invalid relationships like `("Client", "Insurer"): ["WorksAt"]`
- Validation layer for relationship creation

### **How Entity Names Are Set:**

**We set names explicitly** during:
1. Entity import (doctors.json, courts.json, etc.) - from source data
2. Manual review approval - correcting GPT-5 extractions
3. Graph ingestion - using approved entity names from JSON files

**Examples:**
- Doctor: "Dr. Wallace L. Huff Jr." (from KY Medical Board data)
- Court Division: "Jefferson County Circuit Court, Division II" (manually determined per case)
- Episode: Generated from episode_name field in processed data

### **Adding New Entity Types:**

1. Create Pydantic model in graphiti_client.py (lines 50-500)
2. Add to ENTITY_TYPES list (line 687+)
3. Define valid relationships in EDGE_TYPE_MAP (line 1000+)
4. Add to GPT-5 extraction valid_types (process_episodes_for_case.py line 156)
5. Create entity JSON file in /entities/ directory
6. Update review matching logic if needed

---

## Episode Processing Pipeline

### **Overview:**

Convert 13,491 cleaned episodes → natural language → extract entities → propose relationships → manual review → graph ingestion

### **Scripts:**

**1. Clean Episodes** (`clean_episodes.py`)
- Filter vague/auto-generated episodes
- Input: 17,097 raw episodes
- Output: 13,491 cleaned episodes
- Removed: "New note added", "Phase changed", auto-generated Filevine entries

**2. Process Episodes for Case** (`process_episodes_for_case.py`)
- Convert one case's episodes to natural language
- Extract entity relationships using GPT-5
- Input: Case episodes from by_case/*.json
- Output: processed_{case_name}.json

**3. Process All Episodes** (`process_all_episodes_parallel.py`)
- Process all 138 cases in parallel (5 workers)
- Uses GPT-5 Nano for natural language conversion
- Uses GPT-5 Mini for entity extraction
- Output: 138 processed_*.json files (now downloaded from GCS)

**4. Generate Review Documents** (`generate_review_docs.py`)
- Create review_{case_name}.md for each case
- Shows existing entities vs proposed entities
- Consolidates duplicates
- Fuzzy matches against entity databases
- Output: 138 review documents

**5. Regenerate Reviews** (`regenerate_all_reviews.py`)
**Purpose:** Apply new entity data and consolidation logic to all non-approved review files

**How it works:**
1. Loads APPROVED_REVIEWS.txt and skips those files (protected)
2. Loads ALL entity databases:
   - 20,732 doctors
   - 2,159 medical providers
   - 106 courts
   - 192 court divisions
   - 34 attorneys
   - 2,211 directory entries
   - All other entity types
3. For each non-approved review:
   - Extracts proposed entities from existing review
   - Applies KNOWN_MAPPINGS (consolidations like "BK" → "Betsy R. Catron")
   - Filters IGNORE_ENTITIES (generic terms, software, etc.)
   - Fuzzy matches against all entity databases
   - Regenerates review file with updated matches
4. Reports: "Regenerated 135, Skipped 3 approved"

**When you add a new entity** (e.g., Unknown Driver to defendants.json), running this script makes that entity match in ALL remaining review files (but skips approved ones).

**Matching logic imported from:** `generate_review_docs.py`
- KNOWN_MAPPINGS, IGNORE_ENTITIES
- fuzzy_match_entity(), fuzzy_match_doctor()
- normalize_attorney_name(), check_whaley_staff()
- load_global_entities()

---

## Manual Review Process (Current Work)

### **Workflow:**

1. **Review batch of files** (e.g., Abby-Sitgraves through Alma-Cristobal)

2. **Add inline annotations** for each entity:
   - "Ignore" → Entity should be filtered
   - "Add as attorney" → Create entity card
   - "This is X" → Correct wrong match
   - "Works at Y" → Add firm information
   - "Division II" → Case-specific court division

3. **Developer manually processes annotations:**
   - Read each annotation
   - Understand intent
   - Make specific correction
   - Update entity JSON files
   - Update review file
   - Remove annotation (mark as processed)

4. **Mark as approved:**
   - Add filename to `APPROVED_REVIEWS.txt`
   - File is now protected from regeneration

5. **Apply patterns to remaining files:**
   - Add new entities to databases
   - Update KNOWN_MAPPINGS for consolidations
   - Update IGNORE_ENTITIES for filtering
   - Regenerate non-approved files (135 remaining)

6. **Repeat** until all 138 files approved

---

## Review Files - Status

### **Approved (3 files) - PROTECTED:**

1. **review_Abby-Sitgraves-MVA-7-13-2024.md** ✓
   - 93 episodes, 332 proposed relationships
   - Division II corrections applied
   - Unknown Driver added as defendant
   - Kentucky One Health removed (wrong match)

2. **review_Abigail-Whaley-MVA-10-24-2024.md** ✓
   - 21 episodes, 46 proposed relationships
   - Lynette Duncan added as adjuster

3. **review_Alma-Cristobal-MVA-2-15-2024.md** ✓
   - 235 episodes, 852 proposed relationships
   - Division III corrections applied
   - Aletha Thomas type correction
   - Alma Cristobal consolidated (3 variants)
   - Louisville Metro Police separated

### **Pending Review (135 files):**

Next batch to review:
- Amy-Mills-Premise-04-26-2019.md (676 episodes, 2,257 relationships)
- Anella-Noble-MVA-01-03-2021.md
- Antonio-Lopez-MVA-11-14-2025.md
- Ashlee-Williams-MVA-08-29-2023.md
- etc.

---

## Consolidation & Fuzzy Matching

### **Automatic Consolidation:**

**Script:** `generate_review_docs.py` (lines 509-585)

**Process:**
1. Collect all entity mentions from episodes
2. Apply manual mappings (KNOWN_MAPPINGS)
3. Filter ignored entities (IGNORE_ENTITIES)
4. Fuzzy match by entity type:
   - Attorneys: Remove middle names, handle last-name-first
   - Doctors: Strict first+last name matching (95%+ threshold)
   - Courts: Remove case numbers, normalize variants
   - Medical Providers: Remove prefixes, handle hospital name variations

**Example:**
```python
# Input: Multiple mentions
["Derek A. Harvey Jr.", "Derek Anthony Harvey"]

# Normalization: Both → "derek harvey"
# Output: Consolidated as one entity with variants
**Derek Anthony Harvey** — *✓ MATCHES*
  ↳ _Derek A. Harvey Jr._
```

### **Manual Mappings (KNOWN_MAPPINGS):**

Hard-coded consolidations for known variants:
```python
KNOWN_MAPPINGS = {
    "A. G. Whaley": "Aaron G. Whaley",
    "Greg Whaley": "Aaron G. Whaley",
    "BK": "Betsy R. Catron",
    "Dr. Huff": "Dr. Wallace Huff",
    "Knox County Circuit Court": "Knox Circuit Court",
    "WHT Law": "Whaley Harrison & Thorne, PLLC",
    ...
}
```

### **Whaley Staff Detection:**

Special handling for Whaley Law Firm staff (checked FIRST before any matching):
```python
WHALEY_STAFF = {
    "Aaron G. Whaley": ("Attorney", "plaintiff_counsel"),
    "Bryce Koon": ("Attorney", "plaintiff_counsel"),
    "Sarena Tuttle": ("CaseManager", "paralegal"),
    "Justin Chumbley": ("CaseManager", "case_manager"),
    ...
}
```

Prevents misclassification:
- "Justin Chumbley" extracted as Adjuster → Flagged as "WHALEY STAFF → should be CaseManager"

### **Ignore List (IGNORE_ENTITIES):**

Generic terms automatically filtered during consolidation:
- Legal: "Defense counsel", "DC", "Defendants", "court"
- Software: "Filevine", "Dropbox", "DocuSign", "Zoom"
- Claims: "BIClaim #", "PIP #", "UIM coverage"
- ~60 patterns total

---

## Relationship Types

### **Case Relationships:**
- `HasClient`, `HasDefendant`, `HasClaim`, `HasLien`, `FiledIn`, `HasDocument`, `HasExpense`, `SettledWith`

### **Medical:**
- `TreatingAt` (Client → Provider)
- `HasTreated` (Provider/Doctor → Client)
- `TreatedBy` (Client → Provider/Doctor, bidirectional)
- `WorksAt` (Doctor → MedicalProvider)
- `PartOf` (MedicalProvider → HealthSystem)

### **Insurance:**
- `InsuredBy` (Claim → Insurer)
- `HasClaim` (Insurer → Claim, bidirectional)
- `HasInsurance` (Client → Insurer)
- `FiledClaim` (Client → Claim)
- `Covers` (Claim → Client)
- `HandlesInsuranceClaim` (Adjuster → Claim)
- `AssignedAdjuster` (Claim → Adjuster, bidirectional)

### **Legal:**
- `RepresentsClient` (Attorney → Case)
- `WorksAt` (Attorney/CaseManager → LawFirm)
- `FiledIn` (Case → CircuitDivision/DistrictDivision)
- `PresidesOver` (Judge → Division)
- `PartOf` (Division → Court)

### **Professional Services:**
- `RetainedFor` (Expert/Mediator → Case)
- `WorksAt` (Expert/Mediator → Organization)

### **Bills and Negotiations:**
- `HasBill` (Case → Bill)
- `BilledBy` (Bill → MedicalProvider/Vendor/Attorney)
- `ForBill` (Lien → Bill)
- `HasNegotiation` (Case → Negotiation)
- `ForClaim` (Negotiation → Claim)

### **Documents:**
- `HasDocument` (Case → Document/MedicalRecords/etc.)
- `ReceivedFrom` (MedicalRecords/Bills → MedicalProvider)
- `SentTo` (MedicalRecordsRequest/LetterOfRep → Provider/Insurer)
- `From` (InsuranceDocument → Insurer)
- `Regarding` (Document → Case/Client/Claim)

### **Community:**
- `HasMember` (Community → Entity)
- `MemberOf` (Entity → Community)

### **Episode Relationships:**
- `About` (Episode → any entity) - 40,605 proposed
- `Follows` (Episode → Episode, topical/sequential)
- `PartOfWorkflow` (Episode → WorkflowDef)
- `RelatesTo` (Episode → Case, always present)

---

## Workflow Engine Integration

**Location:** `/workspace/workflow_engine/schemas/`

The graph integrates with a deterministic workflow state machine for case lifecycle management.

### **Workflow Entities in Graph:**

**Structural (Definition):**
- `Phase` - Major case stage (Intake, Pre-Litigation, Litigation, Settlement, Closed)
- `SubPhase` - Litigation sub-phases (Discovery, Motions, Trial)
- `Landmark` - Checkpoints (Retainer Signed, MMI Reached, Complaint Filed)
- `WorkflowDef` - Workflow definitions
- `WorkflowStep` - Individual workflow steps

**State (Case-Specific):**
- `LandmarkStatus` - Tracks landmark completion per case
  - Each case has ~82 LandmarkStatus nodes (one per landmark)
  - Properties: status (complete/incomplete), completed_at, notes

### **Workflow State Computer:**

**Location:** `src/roscoe/core/workflow_state_computer.py`

Computes current case state from graph data:
- Queries case entities (overview.json, notes.json, etc.)
- Applies deterministic rules
- Outputs: Current phase, completed landmarks, next actions, blockers

**Example Query:**
```python
get_case_workflow_status(case_name="Alma-Cristobal")
# Returns:
# - Phase: Pre-Litigation
# - Progress: 45%
# - Next: Obtain final medical bill from University Hospital
# - Blockers: MMI not yet reached
```

### **Graph Queries for Workflow:**

```cypher
// Get case phase
MATCH (c:Case {name: $case_name})-[:IN_PHASE]->(p:Phase)
RETURN p.name

// Get completed landmarks
MATCH (c:Case {name: $case_name})-[:LANDMARK_STATUS]->(ls:LandmarkStatus)
WHERE ls.status = 'complete'
RETURN ls.landmark_id, ls.completed_at

// Advance to next phase
MATCH (c:Case {name: $case_name})-[:IN_PHASE]->(current:Phase)
MATCH (current)-[:NEXT_PHASE]->(next:Phase)
MATCH (c)-[r:IN_PHASE]->(current)
DELETE r
CREATE (c)-[:IN_PHASE]->(next)
```

---

## Important Note: Graphiti vs Our Custom Process

### **File Naming:**
- `graphiti_client.py` - Historical name, but contains OUR Pydantic schema definitions
- We are NOT using Graphiti's automatic ingestion features
- The file defines entity types, relationship types, and validation rules

### **What We Use from Graphiti:**
- ✓ Pydantic BaseModel pattern for entities
- ✓ EDGE_TYPE_MAP concept for relationship validation
- ✓ Entity typing system

### **What We Don't Use from Graphiti:**
- ❌ Automatic entity extraction (we use GPT-5 with manual review)
- ❌ Automatic relationship creation (we manually approve all relationships)
- ❌ Auto-generated entity names (we set names explicitly)
- ❌ Graphiti's add_episode function (we'll write custom ingestion)

## Key Design Decisions

### **1. Why Not Pure Graphiti?**

We initially tried Graphiti for automatic episode ingestion, but encountered:
- ❌ Generic RELATES_TO relationships (not specific types like HAS_CLIENT, TREATING_AT)
- ❌ Entities without proper labels (:Entity instead of :Case, :Client)
- ❌ No control over entity extraction quality
- ❌ Progressive slowdown (10 min/episode after 3,000 episodes)
- ❌ Couldn't handle case-specific context (Division II vs Division III requires manual determination)

**Our Solution:** Manual review workflow with custom ingestion
- ✓ GPT-5 Mini extracts entities with few-shot examples
- ✓ Human reviews and approves ALL relationships before ingestion
- ✓ Specific relationship types defined in EDGE_TYPE_MAP
- ✓ Proper entity labels for all entity types
- ✓ Case-specific corrections (court divisions, type corrections, consolidations)
- ✓ Custom ingestion script using approved data

### **2. Two-Phase Ingestion**

**Phase 1: Structured Entities (Direct Cypher) - 65%**
- Cases, Clients, Claims, Providers, Liens
- Workflow state (Phase, Landmarks)
- Deterministic relationships
- Module: `graph_manager.py`

**Phase 2: Episode Layer (Custom) - 35%**
- Episodes with ABOUT relationships
- Semantic search via embeddings
- Module: `graphiti_client.py` (Pydantic models only)

### **3. Episode = "Why/How", Graph Entities = "What"**

**Graph Entities:** Current state snapshot
- Case has PIPClaim from National Indemnity
- Client treating at Jewish Hospital
- Filed in Division II

**Episodes:** Narrative explaining how we got here
- "Called adjuster Jordan Bahr on 8/15/24 to discuss PIP exhaustion"
- "Client reported knee pain, scheduled follow-up at Jewish Hospital ER"
- "Filed complaint in Division II before Judge O'Connell on 9/20/24"

### **4. Division Entities for Judge Tracking**

**Why:** Judge performance analytics requires division-level granularity
- Each division has assigned judge
- Judges change via elections
- Division-specific local rules
- Query: "All settlements with Judge O'Connell in Division II since 2020"

**Structure:** Division as first-class entity (not property)
- CircuitDivision, DistrictDivision nodes
- Judge -[PRESIDES_OVER]→ Division
- Case -[FILED_IN]→ Division -[PART_OF]→ Court

---

## Common Patterns

### **Find all entities related to a case:**
```cypher
MATCH (c:Case {name: $case_name})-[r]->(entity)
RETURN labels(entity), entity.name, type(r)
```

### **Find episodes about an entity:**
```cypher
MATCH (ep:Episode)-[:ABOUT]->(e {name: $entity_name})
RETURN ep.content, ep.valid_at
ORDER BY ep.valid_at DESC
```

### **Find doctor's employer:**
```cypher
MATCH (d:Doctor {name: "Dr. Wallace Huff"})-[:WORKS_AT]->(p:MedicalProvider)
RETURN p.name, p.specialty
```

### **Find cases in a division:**
```cypher
MATCH (c:Case)-[:FILED_IN]->(div:CircuitDivision {name: "Jefferson County Circuit Court, Division II"})
RETURN c.name, c.filing_date
```

### **Find judge presiding over case:**
```cypher
MATCH (c:Case {name: $case_name})-[:FILED_IN]->(div:CircuitDivision)
      <-[:PRESIDES_OVER]-(j:CircuitJudge)
RETURN j.name, div.name
```

---

## Tools & Agent Integration

### **Agent Tools for Graph Operations:**

**Location:** `src/roscoe/agents/paralegal/tools.py`

```python
# Record case updates to knowledge graph
update_case_data(
    case_name="Wilson-MVA-2024",
    data={"provider": "Dr. Smith", "diagnosis": "L4-L5 herniation"},
    source_type="medical_record"
)

# Search knowledge graph
query_case_graph(
    case_name="Wilson-MVA-2024",
    query="What medical providers treated the patient?"
)

# Direct Cypher queries
graph_query(
    query_name="cases_by_provider",
    params={"provider_name": "Dr. Smith"}
)
```

### **Middleware Integration:**

**CaseContextMiddleware** loads case entities from graph when client mentioned:
```python
# User: "Tell me about Caryn McCay's case"
# Middleware detects "Caryn McCay"
# Loads from graph:
#   - Case overview
#   - Medical providers
#   - Insurance claims
#   - Liens
#   - Attorneys
# Injects into system prompt
```

---

## Database Configuration

**FalkorDB Connection:**
```python
import os
from falkordb import FalkorDB

db = FalkorDB(
    host=os.getenv("FALKORDB_HOST", "roscoe-graphdb"),
    port=int(os.getenv("FALKORDB_PORT", "6379"))
)
graph = db.select_graph("roscoe_graph")
```

**Persistence (CRITICAL):**
```yaml
# docker-compose.yml
falkordb:
  environment:
    - FALKORDB_ARGS=--save 60 1 --dir /data --dbfilename dump.rdb --appendonly yes --appendfsync everysec
  deploy:
    resources:
      limits:
        memory: 8G
        cpus: '4.0'
```

**Note:** FalkorDB had no persistence initially (data lost on restart). Now uses RDB snapshots + AOF.

---

## Embeddings

**Model:** sentence-transformers (all-MiniLM-L6-v2)
**Format:** vecf32() in FalkorDB

**Enriched Episode Embeddings:**
- Episode content + first-hop entity context
- Example: "Called Dr. Smith" → embed with "Dr. Smith (orthopedic surgeon at UK Hospital)"
- Enables semantic search: "Find episodes about orthopedic treatment"

**Entity Embeddings:**
```python
# Case embedding
f"{case.name} - {case.case_type} - Client: {client.name}"

# Provider embedding
f"{provider.name} ({specialty}) - Treating {case_count} cases: {case_list}"

# Claim embedding
f"{claim_type} - {insurer} - Adjuster: {adjuster}"
```

---

## Next Steps

### **Immediate:**

1. **Continue Manual Review**
   - Review next batch of 5-10 files
   - Apply annotations
   - Mark as approved
   - Repeat until all 138 approved

2. **Create Division Mappings**
   - Build KNOWN_MAPPINGS for division consolidations
   - Handle case-specific division assignments
   - Ensure Division II/III only applies to correct cases

3. **Add Missing Entities**
   - Doctors from Amy Mills case (Dr. Alsorogi, Dr. Barefoot, etc.)
   - Attorneys from annotations
   - Organizations from directory matches

### **After All Reviews Approved:**

1. **Create Graph Ingestion Script**
   - Ingest all Episodes as nodes
   - Create ABOUT relationships (Episode → Entity)
   - Create FOLLOWS relationships (Episode → Episode)
   - Create WORKS_AT/PRESIDES_OVER relationships

2. **Build Division Relationships**
   - Link all CircuitDivision → Court (PART_OF)
   - Link all CircuitJudge → CircuitDivision (PRESIDES_OVER)
   - Link all Cases → Divisions (FILED_IN)

3. **Add Enriched Embeddings**
   - Generate embeddings for all episodes
   - Include entity context for richer semantic search

4. **Verify Graph Integrity**
   - Query all relationship types
   - Verify no orphan nodes
   - Test semantic search
   - Validate workflow queries

---

## Files Overview

### **Core Schema:**
- `src/roscoe/core/graphiti_client.py` - Pydantic models, entity/relationship definitions

### **Processing Scripts:**
- `src/roscoe/scripts/clean_episodes.py` - Filter vague episodes
- `src/roscoe/scripts/process_episodes_for_case.py` - Single case processing
- `src/roscoe/scripts/process_all_episodes_parallel.py` - Batch processing
- `src/roscoe/scripts/generate_review_docs.py` - Create review documents
- `src/roscoe/scripts/regenerate_all_reviews.py` - Update reviews (with approval protection)

### **Import Scripts:**
- `src/roscoe/scripts/import_ky_doctors.py` - Import 20,732 doctors from KY Medical Board
- `src/roscoe/scripts/import_ky_court_personnel.py` - Import 819 court personnel
- `src/roscoe/scripts/extract_courts_from_directory.py` - Extract 106 courts with divisions
- `src/roscoe/scripts/create_court_divisions.py` - Create 180 division entities
- `src/roscoe/scripts/create_appellate_districts.py` - Create appellate/supreme districts
- `src/roscoe/scripts/import_healthcare_locations.py` - Import 1,369 provider locations (5 health systems)
- `src/roscoe/scripts/flag_better_provider_matches.py` - Flag more specific provider matches in reviews

### **Entity Data:**
- `/json-files/memory-cards/entities/*.json` - ~45,900 entities (updated this session)
- `/json-files/memory-cards/episodes/processed_*.json` - 138 processed episode files
- `/json-files/memory-cards/episodes/reviews/review_*.md` - 138 review documents
- `/json-files/memory-cards/episodes/reviews/APPROVED_REVIEWS.txt` - 3 approved files (protected)

### **Documentation:**
- `CLAUDE_GRAPH.md` - This file (primary developer guide for graph work)
- `GRAPH_SCHEMA.md` - Complete schema from Pydantic models (102 entities, 63 relationships)
- `GRAPH_SCHEMA_ACTUAL.md` - Current FalkorDB state (31 labels, 26 relationships, 11,166 nodes)
- `GRAPH_SCHEMA_COMPLETE.md` - Target state when fully ingested (~57,000 nodes)
- `GRAPH_PROCESS_CLARIFICATION.md` - Clarifies we don't use Graphiti for ingestion
- `DIVISION_ENTITY_STRUCTURE.md` - Division structure and query examples
- `HEALTH_SYSTEM_STRUCTURE.md` - Healthcare hierarchy (5 systems, 2,159 locations)
- `COURT_PERSONNEL_ENTITY_TYPES.md` - Court personnel types (819 personnel)
- `NEW_ENTITY_TYPES_SUMMARY.md` - Doctor, Expert, Mediator, Witness types
- `APPROVED_REVIEWS_PROTECTION.md` - How approval system works
- `SCHEMA_UPDATES_COMPLETE.md` - All schema changes made this session
- `SESSION_SUMMARY_GRAPH_WORK.md` - Complete session summary

---

## Key Principles

1. **Pydantic Models for Everything**
   - All entities defined as Pydantic models
   - All relationships defined as Pydantic models
   - EDGE_TYPE_MAP validates relationship constraints

2. **Manual Review Before Ingestion**
   - Never blindly ingest LLM-extracted entities
   - Human review ensures quality
   - Iterative approval process

3. **Case-Specific Context**
   - Court divisions are case-specific (Division II vs III)
   - Can't be automated - requires case number research
   - Protect approved files from regeneration

4. **Professional Relationship Pattern**
   - Person entities → Organization entities (WORKS_AT/PRESIDES_OVER)
   - Enables one-hop queries
   - Trackable over time (judge elections, attorney job changes)

5. **Division Granularity**
   - Divisions are entities, not properties
   - Enables judge-specific queries and analytics
   - Supports division-specific rules and preferences

---

## Troubleshooting

### **FalkorDB Connection:**
```python
# Test connection
from falkordb import FalkorDB
import os

db = FalkorDB(host=os.getenv("FALKORDB_HOST", "roscoe-graphdb"), port=6379)
graph = db.select_graph("roscoe_graph")
result = graph.query("MATCH (n) RETURN count(n) as total")
print(f"Total nodes: {result.result_set[0][0]}")
```

### **Check Persistence:**
```bash
docker exec roscoe-falkordb redis-cli -p 6379 CONFIG GET save
docker exec roscoe-falkordb redis-cli -p 6379 CONFIG GET appendonly
```

Should show: `save 60 1` and `appendonly yes`

### **Query Performance:**
- Use labels in MATCH clauses: `MATCH (c:Case)` not `MATCH (c)`
- Index frequently-queried properties
- Limit result sets with LIMIT
- Use EXPLAIN for query plan analysis

---

## Current Metrics

**Entities in JSON Files:** ~45,900 across 138 cases
**Episodes:** 13,491 cleaned, ready for ingestion
**Proposed Relationships:** 40,605 ABOUT relationships pending approval
**Review Progress:** 3 of 138 files approved (2%)
**Entity Types:** 58 Pydantic models (was 50)
**Relationship Types:** 71 Pydantic models (was 51)

**Nodes in FalkorDB:** 11,166 (mostly workflow state - episodes not yet ingested)
**Relationships in FalkorDB:** 20,805

**Status:** Manual review phase - building approved relationship set before custom graph ingestion (NOT using Graphiti).

---

## Recent Updates (This Session)

### **Schema Enhancements:**
- ✅ Added 8 new entity types (Bill, Negotiation, 6 document subtypes, Community)
- ✅ Removed deprecated Note entity
- ✅ Added 20+ new relationship types (Client-Insurance, Bills, Documents, Community)
- ✅ Fixed TREATED_BY relationship direction
- ✅ Updated MedicalProvider with endpoints (medical_records_endpoint, billing_endpoint)

### **Major Imports:**
- ✅ 20,732 Doctors (KY Medical Board)
- ✅ 1,386 Medical Provider locations (5 healthcare systems)
- ✅ 5 HealthSystem parent entities
- ✅ 192 Court Divisions with judge assignments
- ✅ 819 Court Personnel
- ✅ 106 Courts with division information

### **Review Process:**
- ✅ 3 files manually corrected and approved
- ✅ Approved file protection mechanism (APPROVED_REVIEWS.txt)
- ✅ 47 files flagged with better medical provider matches
- ✅ Clear workflow: annotate → manually apply → approve → protect

### **Documentation:**
- ✅ 12 comprehensive documentation files created
- ✅ Clarified Graphiti vs custom process
- ✅ Schema fully documented with examples

**Next:** Continue manual review of remaining 135 files, then custom episode ingestion.
