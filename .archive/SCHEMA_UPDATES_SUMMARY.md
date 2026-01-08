# Schema Updates Summary - Based on User Feedback

## Changes Completed ✅

### **1. Episode Entity**
- ✅ Removed `raw_content` property (not needed after initial ingestion)
- Pydantic model updated in graphiti_client.py line 457

---

## Changes to Implement

### **2. Phase Names (Already Correct in Code)**

Phase entity is flexible - actual phase names from GCS bucket:
```
0. Onboarding (phase_0_onboarding)
1. File Setup (phase_1_file_setup)
2. Treatment (phase_2_treatment)
3. Demand (phase_3_demand)
4. Negotiation (phase_4_negotiation)
5. Settlement (phase_5_settlement)
6. Lien Resolution (phase_6_lien)
7. Litigation (phase_7_litigation)
8. Closed (phase_8_closed)
```

**Action:** Update documentation only - Pydantic model already flexible

### **3. SubPhase Names (Already Correct in Code)**

Litigation subphases from GCS:
```
7.1 Complaint (7_1_complaint)
7.2 Discovery (7_2_discovery)
7.3 Mediation (7_3_mediation)
7.4 Trial Preparation (7_4_trial_prep)
7.5 Trial (7_5_trial)
```

**Action:** Update documentation only - Pydantic model already flexible

### **4. Remove Note Entity**

Note has been superseded by Episode.

**Actions:**
- Remove `Note` from ENTITY_TYPES list (line ~613)
- Remove NotedOn relationship type
- Remove Note class definition (line 72)
- Update any references to Note → Episode

### **5. Create Bill Entity**

Bills are different from Liens.

```python
class Bill(BaseModel):
    """Medical bill or other bill (separate from lien). Name is auto-set."""
    bill_type: Optional[str] = Field(default=None, description="Type: medical, legal_fee, expert_fee, filing_fee, vendor")
    amount: Optional[float] = Field(default=None, description="Billed amount")
    bill_date: Optional[date] = Field(default=None, description="Date of bill")
    due_date: Optional[date] = Field(default=None, description="Payment due date")
    paid_date: Optional[date] = Field(default=None, description="Date paid")
    paid_amount: Optional[float] = Field(default=None, description="Amount actually paid")
    balance: Optional[float] = Field(default=None, description="Outstanding balance")
    provider_name: Optional[str] = Field(default=None, description="Who sent the bill")
```

**Relationships:**
- (Bill)-[BILLED_BY]->(MedicalProvider/Vendor/Attorney/etc.)
- (Lien)-[FOR_BILL]->(Bill) - Lien is against a specific bill
- (Case)-[HAS_BILL]->(Bill)

### **6. Update Lien Entity**

**Properties to add:**
```python
lien_type options: "medical", "ERISA", "Medicare", "Medicaid", "child_support", "case_funding", "other"
```

**Remove relationships:**
- ❌ HELD_BY (Lien → LienHolder)
- ❌ HOLDS (LienHolder → Lien)

**Add relationship:**
- ✅ (Lien)-[FOR_BILL]->(Bill)

### **7. Rename Settlement → Negotiation**

```python
class Negotiation(BaseModel):
    """Active settlement negotiation with insurer. Name is auto-set."""
    claim_type: str  # Which claim being negotiated (PIP, BI, UM, etc.)
    demand_amount: float
    demand_sent_date: date
    current_offer: Optional[float]
    offer_date: Optional[date]
    counter_offer: Optional[float]
    counter_date: Optional[date]
    is_active: bool
    final_amount: Optional[float]  # If settled
    settlement_date: Optional[date]
```

**Relationships:**
- (Negotiation)-[FOR_CLAIM]->(PIPClaim/BIClaim/etc.)
- (Case)-[HAS_NEGOTIATION]->(Negotiation)

### **8. Fix Medical Relationship Directions**

**Current (confusing):**
```
(MedicalProvider)-[TREATED_BY]->(Client)  # Provider treated BY client? Wrong!
```

**Corrected (bidirectional):**
```
(Doctor/MedicalProvider)-[HAS_TREATED]->(Client)  # Provider treated client
(Client)-[TREATED_BY]->(Doctor/MedicalProvider)  # Client treated by provider
```

Add both directions for query flexibility.

### **9. Add Client-Insurance Relationships**

Currently missing link between Client and their insurance!

**Add:**
```
(Client)-[HAS_INSURANCE]->(Insurer)  # Client has insurance with
(Client)-[FILED_CLAIM]->(Claim)  # Client filed this claim
(Claim)-[COVERS]->(Client)  # Claim covers client
```

### **10. Create Document Subtypes**

Replace generic `Document` with specific types:

```python
class MedicalRecords(BaseModel):
    """Received medical records from provider."""
    received_date: date
    date_range_start: Optional[date]  # Records cover this period
    date_range_end: Optional[date]
    pages: Optional[int]
    format: str  # pdf, paper, cd, electronic

class MedicalBills(BaseModel):
    """Received medical bills from provider."""
    received_date: date
    total_billed: float
    line_items: Optional[str]  # JSON of bill details

class MedicalRecordsRequest(BaseModel):
    """Outgoing medical records request."""
    sent_date: date
    request_number: int  # 1st, 2nd, 3rd request
    via: str  # email, fax, mail, chartswap
    response_deadline: Optional[date]

class LetterOfRepresentation(BaseModel):
    """Letter of rep sent to insurer/provider."""
    sent_date: date
    sent_to_name: str  # Entity name
    acknowledged: bool
    acknowledged_date: Optional[date]

class InsuranceDocument(BaseModel):
    """Insurance document."""
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

**Document Relationships:**
```
(MedicalRecordsRequest)-[SENT_TO {date, via}]->(MedicalProvider)
(MedicalRecords)-[RECEIVED_FROM {date}]->(MedicalProvider)
(MedicalBills)-[FROM]->(MedicalProvider)
(LetterOfRep)-[SENT_TO]->(Insurer/MedicalProvider)
(Document)-[REGARDING]->(Case/Client/Claim/etc.)
```

### **11. Community Entity (Graphiti-inspired)**

```python
class Community(BaseModel):
    """Group of related entities for collective queries."""
    name: str  # "Orthopedic Spine Specialists", "Sturgill Turner Attorneys"
    community_type: str  # provider_group, attorney_network, related_cases, injury_type
    description: str
    created_date: date
```

**Relationships:**
```
(Community)-[HAS_MEMBER]->(Entity)
(Entity)-[MEMBER_OF]->(Community)
```

**Use Cases:**
- All orthopedic providers treating herniated discs
- All defense attorneys from specific firm
- All cases with same defendant
- All providers in a health network

---

## Updated Entity Count

**After Changes:**
- Remove: 1 (Note)
- Add: 8 (Bill + 7 document subtypes)
- Rename: 1 (Settlement → Negotiation)
- **Net Change:** +7 entity types

**Total Entity Types:** 57 (was 50)

---

## Updated Relationship Count

**Remove:** 3 (HELD_BY, HOLDS, NotedOn)
**Add:** ~12 (document relationships, Client-Insurance, Bill relationships, HAS_TREATED)

**Total Relationship Types:** 60 (was 51)

---

## Priority for Implementation

**High Priority (Core Functionality):**
1. ✅ Remove raw_content from Episode
2. Fix TREATED_BY → HAS_TREATED (bidirectional)
3. Add Client-Insurance relationships
4. Create Bill entity (separate from Lien)
5. Remove HELD_BY/HOLDS relationships

**Medium Priority (Enhanced Tracking):**
6. Create Document subtypes (MedicalRecords, MedicalRecordsRequest, etc.)
7. Add document-entity relationships
8. Rename Settlement → Negotiation
9. Update Lien.lien_type options

**Low Priority (Nice to Have):**
10. Community entity for grouping
11. Research law firm attorney rosters

---

## Next Steps

1. ✅ Episode raw_content removed
2. Update MedicalProvider with endpoints
3. Fix relationship directions in EDGE_TYPE_MAP
4. Create Bill, Document subtypes, Community entities
5. Update ENTITY_TYPES list
6. Update EDGE_TYPE_MAP with new relationships
7. Update GRAPH_SCHEMA_COMPLETE.md with corrections
8. Test that schema still validates

**Estimated remaining time:** 2-3 hours for all changes
