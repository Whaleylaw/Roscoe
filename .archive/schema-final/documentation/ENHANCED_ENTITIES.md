# Enhanced Existing Entities - New Fields Added

**Date:** January 4, 2026
**Entities Enhanced:** 8 existing entity types

---

## 1. HealthSystem (Enhanced)

**Added 12 new fields for records/billing requests:**

```python
# Records request fields (centralized for all facilities/locations)
records_request_method: Optional[str]   # mail | fax | portal | online
records_request_url: Optional[str]      # Online request URL
records_request_address: Optional[str]  # Mailing address
records_request_fax: Optional[str]      # Fax number
records_request_phone: Optional[str]    # Phone number
records_request_notes: Optional[str]    # Special instructions

# Billing request fields
billing_request_method: Optional[str]   # mail | fax | portal | online
billing_request_address: Optional[str]  # Billing dept address
billing_request_phone: Optional[str]    # Billing dept phone

# Metadata
source: Optional[str]                   # official_website | csv | manual
validation_state: Optional[str]         # verified | unverified | needs_review
last_verified: Optional[datetime]       # Verification timestamp
```

**Why:** Enable medical records request workflows at system-wide level

**Example:**
```json
{
  "name": "Norton Healthcare",
  "records_request_method": "mail",
  "records_request_address": "Norton Healthcare Medical Records, PO Box...",
  "records_request_notes": "Centralized for all 368 Norton locations"
}
```

---

## 2. PIPClaim (Enhanced)

**Added 5 denial/appeal fields:**

```python
denial_reason: Optional[str]     # Reason for denial
denial_date: Optional[date]      # When denied
appeal_filed: Optional[bool]     # Whether appeal filed
appeal_date: Optional[date]      # When appeal filed
appeal_outcome: Optional[str]    # granted | denied | pending
```

**Why:** Track coverage disputes and appeals

---

## 3. BIClaim (Enhanced)

**Added 5 denial/appeal fields** (same as PIPClaim)

---

## 4. UMClaim (Enhanced)

**Added 5 denial/appeal fields** (same as PIPClaim)

---

## 5. UIMClaim (Enhanced)

**Added 5 denial/appeal fields** (same as PIPClaim)

---

## 6. WCClaim (Enhanced)

**Added 5 denial/appeal fields** (same as PIPClaim)

---

## 7. Pleading (Enhanced)

**Added 5 discovery-specific fields:**

```python
# Discovery fields (when pleading_type is discovery)
discovery_type: Optional[str]      # interrogatories | rfp | rfa | deposition_notice | subpoena
propounded_to: Optional[str]       # plaintiff | defendant | third_party
response_due: Optional[date]       # When response is due
response_received: Optional[bool]  # Whether response received
response_date: Optional[date]      # Date response received
```

**Why:** Enhanced discovery tracking and deadline monitoring

**Example:**
```json
{
  "name": "First Set of Interrogatories",
  "pleading_type": "discovery_request",
  "discovery_type": "interrogatories",
  "propounded_to": "defendant",
  "response_due": "2024-09-01",
  "response_received": false  // Overdue!
}
```

---

## 8. Attorney (Enhanced)

**Added 6 professional detail fields:**

```python
practice_areas: Optional[str]      # Practice areas (comma-separated)
bar_admission_date: Optional[date] # Date admitted to bar
bar_states: Optional[str]          # States licensed (comma-separated)
office_address: Optional[str]      # Attorney's office address
direct_phone: Optional[str]        # Direct dial number
preferred_contact: Optional[str]   # email | phone | text | fax
```

**Why:** More complete attorney profiles and contact information

**Example:**
```json
{
  "name": "Bryce Koon",
  "practice_areas": "Personal Injury, Medical Malpractice",
  "bar_admission_date": "2015-05-20",
  "bar_states": "KY, IN",
  "direct_phone": "(502) 555-1234",
  "preferred_contact": "email"
}
```

---

## 9. LawFirm (Enhanced)

**Added 1 field:**

```python
website: Optional[str]  # Firm website
```

---

## 10. LienHolder (Enhanced)

**Updated lien_type description to include "workers_comp":**

```python
lien_type: Optional[str]  # "medical, ERISA, Medicare, Medicaid, child_support, case_funding, workers_comp, collection, other"
```

**Why:** Support WC subrogation liens

---

## Summary

**8 existing entity types enhanced with 35 new fields:**

| Entity | New Fields | Purpose |
|--------|------------|---------|
| HealthSystem | 12 | Records/billing request infrastructure |
| PIPClaim | 5 | Denial/appeal tracking |
| BIClaim | 5 | Denial/appeal tracking |
| UMClaim | 5 | Denial/appeal tracking |
| UIMClaim | 5 | Denial/appeal tracking |
| WCClaim | 5 | Denial/appeal tracking |
| Pleading | 5 | Discovery tracking |
| Attorney | 6 | Professional details |
| LawFirm | 1 | Website |
| LienHolder | 0 | Updated description only |

**Total:** 49 new fields across existing entities

---

## Impact

**These enhancements enable:**

✅ **Medical records workflows**
- Request records at HealthSystem, Facility, or Location level
- Inheritance up hierarchy if not set at child level

✅ **Insurance dispute tracking**
- Coverage denials and reasons
- Appeal filing and outcomes
- Timeline of disputes

✅ **Discovery management**
- Track discovery requests and responses
- Deadline monitoring
- Overdue discovery alerts

✅ **Attorney contact management**
- Direct dial numbers
- Preferred contact methods
- Practice area tracking

✅ **Workers comp subrogation**
- Proper lien_type for WC
- Integrated with existing Lien structure

---

## All Changes In

**File:** `src/roscoe/core/graphiti_client.py`

**Lines:**
- HealthSystem: ~199-225
- Insurance Claims: ~149-260
- Pleading: ~608-621
- Attorney: ~515-530
- LawFirm: ~483-488
- LienHolder: ~408-414
