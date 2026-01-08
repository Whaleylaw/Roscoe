# Schema Corrections - Implementation Plan

Based on user feedback in Graph-Schema-comments.md

---

## 1. Entity Corrections

### **Remove:**
- ❌ `Note` entity - Superseded by Episode

### **Update Properties:**

**Episode:**
- ❌ Remove `raw_content` property - Not needed after initial ingestion
- ✅ Keep all other properties

**MedicalProvider:**
- ➕ Add `medical_records_endpoint` (str) - Can override parent HealthSystem
- ➕ Add `billing_endpoint` (str) - Can override parent HealthSystem

**Lien:**
- ✅ Update `lien_type` options: medical, ERISA, Medicare, Medicaid, child_support, **case_funding**, **other**
- ✅ Clarify: Only LienHolders hold liens, NOT MedicalProviders

**LienHolder:**
- ✅ Update lien_type to include case_funding

### **Rename:**
- ✅ `Settlement` → `Negotiation`

### **Add New Bill Entity:**
```python
class Bill(BaseModel):
    """Medical bill or other bill (different from lien)."""
    bill_type: str  # medical, legal_fee, expert_fee, filing_fee
    amount: float
    bill_date: date
    due_date: Optional[date]
    paid_date: Optional[date]
    paid_amount: Optional[float]
    provider_name: str  # Who billed
```

Relationships:
- (Bill)-[FROM]->(MedicalProvider/Vendor/etc.)
- (Lien)-[FOR_BILL]->(Bill) - Lien is for a specific bill

---

## 2. Workflow Entity Corrections

### **Phase Names (Correct from GCS):**
```python
Phase entities (9):
- phase_0_onboarding → "Onboarding"
- phase_1_file_setup → "File Setup"
- phase_2_treatment → "Treatment"
- phase_3_demand → "Demand"
- phase_4_negotiation → "Negotiation"
- phase_5_settlement → "Settlement"
- phase_6_lien → "Lien Resolution"
- phase_7_litigation → "Litigation"
- phase_8_closed → "Closed"
```

### **SubPhase Names (Litigation only):**
```python
SubPhase entities (5):
- 7_1_complaint → "Complaint"
- 7_2_discovery → "Discovery"
- 7_3_mediation → "Mediation"
- 7_4_trial_prep → "Trial Preparation"
- 7_5_trial → "Trial"
```

### **WorkflowDef Properties (from GCS structure):**
```python
class WorkflowDef(BaseModel):
    """Workflow definition."""
    workflow_id: str  # e.g., "1.1_create_project_structure"
    name: str  # Display name
    phase: str  # Parent phase
    description: str
    trigger: str  # What triggers this workflow
    when_to_use: str  # When agent should use this
    required_inputs: list[str]
    expected_outputs: list[str]
```

**WorkflowStep, WorkflowChecklist, WorkflowSkill, WorkflowTemplate, WorkflowTool:**
Download from GCS and extract actual structure

---

## 3. Relationship Corrections

### **Fix Directions:**

**Current (Wrong):**
```
(MedicalProvider)-[TREATED_BY]->(Client)  # Provider was treated BY client? No!
```

**Corrected:**
```
(Doctor/MedicalProvider)-[HAS_TREATED]->(Client)
(Client)-[TREATED_BY]->(Doctor/MedicalProvider)
```

Use both directions for flexibility.

### **Remove:**
- ❌ (Lien)-[HELD_BY]->(LienHolder)
- ❌ (LienHolder)-[HOLDS]->(Lien)

### **Add:**

**Bill Relationships:**
```
(Bill)-[BILLED_BY]->(MedicalProvider/Vendor/Attorney)
(Lien)-[FOR_BILL]->(Bill)
(Case)-[HAS_BILL]->(Bill)
```

**Client-Insurance:**
```
(Client)-[HAS_INSURANCE]->(Insurer)
(Claim)-[COVERS]->(Client)
(Client)-[FILED_CLAIM]->(Claim)
```

**Negotiation-Claim:**
```
(Negotiation)-[FOR_CLAIM]->(PIPClaim/BIClaim/etc.)
(Case)-[HAS_NEGOTIATION]->(Negotiation)
```

**Document-Entity Links:**
```
(Document)-[REGARDING]->(Case/Client/Claim/Provider/etc.)
(MedicalRecords)-[RECEIVED_FROM]->(MedicalProvider)
(MedicalRecordsRequest)-[SENT_TO]->(MedicalProvider)
(LetterOfRep)-[SENT_TO]->(Insurer/MedicalProvider)
```

---

## 4. Document Entity Expansion

### **Create Document Subtypes:**

Instead of generic `Document`, create specific types:

```python
class MedicalRecords(BaseModel):
    """Received medical records."""
    document_subtype: str = "medical_records"
    received_date: date
    date_range_start: date  # Records cover this date range
    date_range_end: date
    pages: int
    format: str  # pdf, paper, cd

class MedicalBills(BaseModel):
    """Received medical bills."""
    document_subtype: str = "medical_bills"
    received_date: date
    total_billed: float

class MedicalRecordsRequest(BaseModel):
    """Outgoing medical records request."""
    document_subtype: str = "medical_records_request"
    sent_date: date
    request_number: int  # 1st, 2nd, 3rd request
    via: str  # email, fax, mail, chart_swap

class LetterOfRepresentation(BaseModel):
    """Letter of representation sent."""
    sent_date: date
    sent_to: str  # Insurer/Provider name
    acknowledged: bool
    acknowledged_date: Optional[date]

class InsuranceDocument(BaseModel):
    """Insurance-related document."""
    doc_subtype: str  # dec_page, eob, denial_letter, coverage_letter
    received_date: date
    insurer_name: str

class CorrespondenceDocument(BaseModel):
    """General correspondence."""
    correspondence_type: str  # email, letter, fax
    direction: str  # inbound, outbound
    from_entity: str
    to_entity: str
    sent_date: date
```

### **Document Relationships:**
```
(MedicalRecordsRequest)-[SENT_TO {date, via}]->(MedicalProvider)
(MedicalRecords)-[RECEIVED_FROM {date}]->(MedicalProvider)
(MedicalBills)-[FROM]->(MedicalProvider)
(Document)-[ATTACHED_TO]->(Case)
(Document)-[REGARDING]->(Client/Claim/Provider/etc.)
```

### **Enable Queries:**
```cypher
// Do we have medical records from this provider?
MATCH (c:Case {name: $case})-[:HAS_DOCUMENT]->(rec:MedicalRecords)
      -[:RECEIVED_FROM]->(p:MedicalProvider {name: "Norton Hospital Downtown"})
RETURN rec.received_date, rec.pages

// Did we get response after 2nd request?
MATCH (req:MedicalRecordsRequest {request_number: 2})-[:SENT_TO]->(p:MedicalProvider)
MATCH (p)<-[:RECEIVED_FROM]-(rec:MedicalRecords)
WHERE rec.received_date > req.sent_date
RETURN "YES" as received_after_2nd_request, rec.received_date
```

---

## 5. Community Entity (Graphiti-inspired)

### **Community Entity:**
```python
class Community(BaseModel):
    """Group of related entities (e.g., all providers treating herniated disc)."""
    name: str  # "Orthopedic Providers - Spine"
    community_type: str  # provider_group, attorney_network, related_cases
    description: str
    created_date: date
```

### **Relationships:**
```
(Community)-[HAS_MEMBER]->(Entity)
(Entity)-[MEMBER_OF]->(Community)
```

### **Use Cases:**
- Group all orthopedic providers who treat herniated discs
- Group all defense attorneys from Sturgill Turner
- Group related cases (same defendant, same injury type)
- Enable query: "All providers in the spine treatment community"

---

## 6. Research Tasks

### **Law Firm Attorney Rosters:**

**Process:**
1. Query directory.json for all law firms
2. For each law firm, research attorneys
3. Create Attorney entities linked to firms
4. Enables: "Which attorney from Ward Hocker Thornton handles our cases?"

**Target:** ~200-300 additional attorneys from law firm rosters

---

## Implementation Order

**Phase 1: Quick Fixes (1 hour)**
1. Fix Phase/SubPhase names
2. Add WorkflowDef properties
3. Fix TREATED_BY relationship direction
4. Add Client-Insurance relationships
5. Rename Settlement → Negotiation

**Phase 2: Document System (2-3 hours)**
1. Create document subtypes
2. Add document-entity relationships
3. Update Pydantic models
4. Test document tracking queries

**Phase 3: Bill vs Lien (1 hour)**
1. Create Bill entity
2. Remove HELD_BY/HOLDS
3. Add Bill relationships
4. Update lien_type options

**Phase 4: Communities (1 hour)**
1. Create Community entity
2. Add HAS_MEMBER relationships
3. Design community types

**Phase 5: Research (ongoing)**
1. Law firm attorney rosters
2. Create additional attorney entities

**Total Estimate:** 5-6 hours of schema updates + ongoing research

**Should I proceed with Phase 1 (Quick Fixes)?**
