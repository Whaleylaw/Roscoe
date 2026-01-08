# Litigation & Court Schema Analysis

**Date:** January 4, 2026
**Purpose:** Review current legal/court/attorney schema for completeness

---

## Current Legal Entities (14)

### Law Firms & Attorneys

**1. LawFirm**
- Law firm entity
- Properties: phone, fax, address

**2. Attorney**
- Individual attorney
- Properties: role (plaintiff_counsel, defense_counsel, co_counsel, referring_attorney), bar_number, firm_name, phone, email

**3. CaseManager**
- Paralegal or case manager
- Properties: role (case_manager, paralegal, legal_assistant), firm_name, phone, email

### Courts & Divisions

**4. Court**
- Parent court entity
- Properties: county, state, case_number, division, phone, email, address

**5. CircuitDivision**
- Circuit court division (e.g., "Jefferson County Circuit Court, Division II")
- Properties: division_number, court_name, circuit_number, local_rules, scheduling_preferences, mediation_required

**6. DistrictDivision**
- District court division
- Properties: division_number, court_name, district_number

**7. AppellateDistrict**
- Court of Appeals district
- Properties: district_number, region, counties

**8. SupremeCourtDistrict**
- Kentucky Supreme Court district (7 districts)
- Properties: district_number, counties, region

### Judges & Personnel

**9. CircuitJudge**
- Circuit court judge
- Properties: county, circuit, division, phone, email, address

**10. DistrictJudge**
- District court judge
- Properties: county, district, division, phone, email, address

**11. AppellateJudge**
- Court of Appeals judge
- Properties: phone, email, address

**12. SupremeCourtJustice**
- Kentucky Supreme Court justice
- Properties: phone, email, address

**13. CourtClerk**
- Circuit/district court clerk
- Properties: clerk_type, county, phone, email, address

**14. MasterCommissioner**
- Court-appointed master commissioner
- Properties: county, phone, email, address

**15. CourtAdministrator**
- Court administrative staff
- Properties: role, phone, email, address

### Litigation Documents

**16. Pleading**
- Court filing/litigation document
- Properties: pleading_type (complaint, answer, motion, discovery, subpoena, order, judgment), filed_date, due_date, filed_by

---

## Current Relationships

### Case → Court/Attorney

```cypher
(Case)-[:FILED_IN]->(Court)
(Case)-[:FILED_IN]->(CircuitDivision)  // Or specific division
(Attorney)-[:REPRESENTS_CLIENT]->(Case)
(Case)-[:DEFENSE_COUNSEL]->(Attorney)
(Case)-[:REPRESENTED_BY]->(Attorney)
```

### Attorney → Law Firm

```cypher
(Attorney)-[:WORKS_AT]->(LawFirm)
(CaseManager)-[:WORKS_AT]->(LawFirm)
```

### Court Hierarchy

```cypher
(CircuitDivision)-[:PART_OF]->(Court)
(DistrictDivision)-[:PART_OF]->(Court)
(CircuitJudge)-[:PRESIDES_OVER]->(CircuitDivision)
(DistrictJudge)-[:PRESIDES_OVER]->(DistrictDivision)
(CourtClerk)-[:WORKS_AT]->(Court)
(MasterCommissioner)-[:APPOINTED_BY]->(Court)
```

### Pleadings

```cypher
(Pleading)-[:FILED_IN]->(Court)
(Case)-[:HAS_PLEADING]->(Pleading)  // Need to verify this exists
```

---

## Current Graph State (from earlier ingestion)

**From previous work:**
- Courts: 118 entities
- CircuitDivision: 86
- DistrictDivision: 94
- CircuitJudge: 101
- DistrictJudge: 94
- AppellateJudge: 15
- SupremeCourtJustice: 8
- CourtClerk: 121
- MasterCommissioner: 108
- CourtAdministrator: 7
- Attorneys: ~35
- LawFirms: ~28
- Pleadings: ~168

**Total legal entities:** ~983

---

## What's Good ✅

**1. Complete Court Hierarchy**
- Court → Division → Judge structure
- All Kentucky courts/divisions imported
- Proper hierarchy relationships (PART_OF, PRESIDES_OVER)

**2. Judge Tracking**
- All judge types covered (Circuit, District, Appellate, Supreme)
- Division assignments
- Contact information

**3. Court Personnel**
- Clerks, Master Commissioners, Administrators
- Linked to courts

**4. Attorney Organization**
- Attorney → LawFirm structure
- Role tracking (plaintiff vs defense)
- Bar numbers

**5. Pleading Tracking**
- Different pleading types
- Filed dates and due dates
- Filed by plaintiff vs defendant

---

## What Could Be Enhanced 🔧

### 1. Missing: Attorney Contact Details

**Current:** Basic phone/email
**Could add:**
- Office address (separate from law firm address)
- Direct dial vs main number
- Preferred contact method
- Practice areas
- Bar admission dates

### 2. Missing: Law Firm Multi-Office Support

**Current:** LawFirm is single entity
**Issue:** Firms like Bryan Cave have multiple offices

**Could add:**
```python
class LawFirmOffice(BaseModel):
    """Specific office/branch of a law firm."""
    office_name: str  # "Louisville Office", "Lexington Office"
    parent_firm: str  # "Bryan Cave Leighton Paisner"
    address: str
    phone: str
```

**Relationships:**
```cypher
(LawFirmOffice)-[:PART_OF]->(LawFirm)
(Attorney)-[:WORKS_AT]->(LawFirmOffice)
```

**Similar to your medical provider hierarchy!**

### 3. Missing: Case Assignment to Judge

**Current:** Can query Division → Judge
**Missing:** Direct Case → Judge relationship

**Could add:**
```cypher
(Case)-[:ASSIGNED_TO]->(CircuitJudge)
```

**Benefits:**
- Direct link for quick queries
- Track which judge has the case
- Judge reassignment tracking

### 4. Missing: Pleading → Attorney Link

**Current:** Pleading filed in Court, filed_by (plaintiff/defendant)
**Missing:** Who actually filed it

**Could add:**
```cypher
(Pleading)-[:FILED_BY]->(Attorney)
```

**Benefits:**
- Know which attorney filed which pleadings
- Track attorney work product
- Discovery organization

### 5. Missing: Court Deadlines/Events

**Current:** Pleading has due_date
**Missing:** Court events (hearings, trials, mediation)

**Could add:**
```python
class CourtEvent(BaseModel):
    """Court hearing, trial, mediation, or other event."""
    event_type: str  # hearing, trial, mediation, status_conference
    event_date: date
    event_time: Optional[str]
    location: Optional[str]  # Courtroom, virtual, etc.
    purpose: Optional[str]
    notes: Optional[str]
```

**Relationships:**
```cypher
(Case)-[:HAS_EVENT]->(CourtEvent)
(CourtEvent)-[:IN]->(Court)
```

### 6. Missing: Discovery Tracking

**Current:** Pleading type includes "discovery_request"/"discovery_response"
**Could enhance:**

```python
class DiscoveryRequest(BaseModel):
    """Discovery request (interrogatories, RFP, RFA, deposition notice)."""
    discovery_type: str  # interrogatories, rfp, rfa, deposition
    propounded_date: date
    response_due_date: date
    propounded_by: str  # plaintiff | defendant
    response_received: Optional[bool]
    response_date: Optional[date]
```

**Or keep as Pleading with better properties?**

### 7. Missing: Mediation/Settlement Conference

**Could add:**
```python
class Mediation(BaseModel):
    """Mediation or settlement conference."""
    mediation_date: date
    mediator_name: Optional[str]
    location: Optional[str]
    outcome: Optional[str]  # settled, partial_settlement, failed
    settlement_amount: Optional[float]
```

**Or track as CourtEvent?**

### 8. Missing: Attorney Multi-Role Support

**Issue:** Attorney can be plaintiff counsel on one case, defense on another

**Current structure supports this!**
- Same Attorney entity
- Different relationship types (RepresentsClient vs DefenseCounsel)
- Works like your medical provider multi-role

**Just need to document it clearly**

---

## What's Already Good (Keep As-Is) ✅

**1. Court Hierarchy Structure**
- Court → Division → Judge
- Mirrors your medical provider hierarchy!
- Progressive detail supported (can link to Court or Division)

**2. Multiple Judge Types**
- Circuit, District, Appellate, Supreme
- Appropriate for different court levels

**3. Separate Pleading Entity**
- Not just properties on Case
- Trackable documents
- Filed dates and deadlines

**4. Court Personnel**
- Clerks, Commissioners, Administrators
- Proper role distinction

---

## Recommended Enhancements

### HIGH PRIORITY

**1. Add Case → Judge Direct Link**
- Makes queries simpler
- Track case assignments

**2. Add Pleading → Attorney Link**
- Know who filed what
- Discovery organization

**3. Consider LawFirm Office Structure**
- Multi-office firms common
- Mirrors medical Facility/Location pattern

### MEDIUM PRIORITY

**4. Add CourtEvent Entity**
- Hearings, trials, conferences
- Calendar integration

**5. Enhanced Discovery Tracking**
- Separate from generic Pleading?
- Or enhance Pleading properties

### LOW PRIORITY

**6. Mediation as separate entity**
- Or part of CourtEvent?

**7. Enhanced Attorney fields**
- Practice areas, bar dates, etc.

---

## Questions for You

**Which enhancements do you want?**

1. **Court Event tracking** - Do you need separate CourtEvent entity for hearings/trials?
2. **Law Firm offices** - Do you track multi-office firms like medical providers?
3. **Pleading → Attorney links** - Important for discovery organization?
4. **Discovery as separate entity** - Or keep as Pleading type?
5. **Case → Judge direct link** - Useful or can query via Division?

**Let me know what's most important for your litigation workflow!**
