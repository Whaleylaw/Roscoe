# Graphiti Schema Update Summary

**Date:** December 21, 2025
**File Updated:** `src/roscoe/core/graphiti_client.py`

---

## Philosophy: Clean Graph Model

**Key Principle:** Store only immutable facts in entity fields. Derive everything else from graph relationships and queries.

---

## Major Changes

### 1. **Minimal Case Entity** (Stripped to Essentials)

**Before:**
```python
class Case(BaseModel):
    case_type: str
    accident_date: date
    phase: str                    # ❌ REMOVED - now a relationship
    sol_date: date
    total_medical_bills: float    # ❌ REMOVED - computed from graph
    # ... more computed fields
```

**After:**
```python
class Case(BaseModel):
    case_type: Optional[str]      # ✅ Static fact
    accident_date: Optional[date] # ✅ Static fact
    sol_date: Optional[date]      # ✅ Static fact
    # Everything else is relationships or computed
```

**Removed Fields:**
- ~~`phase`~~ → Relationship: `Case -[IN_PHASE]-> Phase`
- ~~`total_medical_bills`~~ → Computed via graph query
- ~~`total_expenses`~~ → Computed via graph query
- ~~`total_liens`~~ → Computed via graph query
- ~~`case_summary`~~ → Generated on-demand via `generate_case_summary()`
- ~~`current_status`~~ → Generated from phase + recent notes
- ~~`case_role`~~ → SQL artifact, deleted

---

### 2. **New Note Entity** (Replaces Text Blobs)

```python
class Note(BaseModel):
    """A timestamped note attached to any entity."""
    note_date: Optional[date]      # When event occurred
    content: Optional[str]          # Note content
    author: Optional[str]           # Staff name or "agent"
    category: Optional[str]         # insurance_note, medical_note, etc.
    project_name: Optional[str]     # Associated case
    source_file: Optional[str]      # Source document if imported
```

**Replaces:** All `insurance_notes`, `medical_notes` string fields

**Benefits:**
- ✅ Semantic search on individual notes
- ✅ Temporal filtering ("notes from last week")
- ✅ Author attribution
- ✅ Multi-entity note linking
- ✅ Scalable as notes grow

---

### 3. **Updated Claim Entities** (Structured Data Only)

**All claim types now have:**
- `coverage_confirmation` - Status: "Coverage Confirmed", "Coverage Pending", "Coverage Denied"
- `project_name` - Associated case name

**Negotiable claims (BI, UM, UIM, WC) have:**
- `is_active_negotiation` - Boolean flag
- `settlement_date` - When settled

**First-party claims (PIP, MedPay) have:**
- `exhausted` - Boolean flag (NOT on negotiable claims)

**Removed from ALL claims:**
- ~~`insurance_notes`~~ → Use Note entities instead

---

### 4. **Enhanced Supporting Entities**

| Entity | Fields Added |
|--------|-------------|
| **MedicalProvider** | `email` |
| **Insurer** | `email` |
| **Vendor** | `email`, expanded `vendor_type` options |
| **Organization** | `email`, expanded `org_type` options |
| **Lien** | `lienholder_name`, `project_name`, `date_notice_received`, `date_lien_paid`, `reduction_amount` |
| **Court** | `phone`, `email`, `address` |
| **Defendant** | `phone`, `project_name` |

---

### 5. **New Note Relationships**

```python
class HasNote(BaseModel):
    """Entity has an associated note."""
    added_at: Optional[datetime]

class NotedOn(BaseModel):
    """Note is about an entity."""
    relevance: Optional[str]
```

**All entities can have notes:**
- Case, Client, PIPClaim, BIClaim, UMClaim, UIMClaim, WCClaim, MedPayClaim
- MedicalProvider, Insurer, Adjuster, Lien, LienHolder
- Defendant, Court, Attorney, LawFirm, Vendor, Organization
- Pleading, Document

---

### 6. **New Helper Function: generate_case_summary()**

```python
async def generate_case_summary(case_name: str) -> dict:
    """
    Generate case summary on-demand from graph data.

    Returns:
        {
            "case_name": str,
            "case_type": str,
            "client": {name, phone, email},
            "current_phase": str,
            "phase_progress": "67% (4/6 landmarks complete)",
            "total_medical_bills": float,    # Computed from graph
            "total_liens": float,             # Computed from graph
            "total_expenses": float,          # Computed from graph
            "active_claims": [...],           # All claims with details
            "recent_activity": [...]          # Last 10 notes
        }
    """
```

**Replaces:** Static fields on Case entity

**Benefits:**
- Always fresh (never stale)
- No sync issues
- Temporal queries possible
- Single source of truth

---

## Migration Strategy

### For Existing Data (JSON files):

**Old insurance.json structure:**
```json
{
  "claim_number": "633859-N",
  "insurer_name": "National Indemnity",
  "insurance_notes": "7/15 DEC page in route\n7/29 Saved ack\n..."
}
```

**New graph structure:**
```
PIPClaim {
  claim_number: "633859-N",
  insurer_name: "National Indemnity",
  exhausted: False,
  coverage_confirmation: "Coverage Confirmed"
}
  |
  ├─[HAS_NOTE]─> Note {date: "2024-07-15", content: "DEC page in route", author: "Coleen"}
  └─[HAS_NOTE]─> Note {date: "2024-07-29", content: "Saved ack", author: "Coleen"}
```

**Migration script needed:** Parse `insurance_notes` into individual Note entities.

---

## Updated Entity Counts

Based on JSON files in `/json-files/memory-cards/entities/`:

| Entity Type | Count | Notes |
|-------------|-------|-------|
| Case | ~100 | Stripped to 3 fields |
| Client | 52 | No changes |
| MedicalProvider | ~2,800 | Added email |
| Insurer | 65 | Added email |
| Adjuster | 80 | No changes |
| Attorney | 28 | No changes |
| Vendor | 20 | Added email |
| PIPClaim | ~80 | Added fields, removed insurance_notes |
| BIClaim | ~100 | Added fields, removed insurance_notes |
| Lien | 50 | Added 5 new fields |
| LienHolder | 28 | No changes |
| Court | 18 | Added phone, email, address |
| Defendant | 7 | Added phone, project_name |
| Organization | 15 | Added email |
| **Note** | **TBD** | New entity type (will be populated from notes migration) |

---

## Next Steps

1. **Validate schema** - Test with sample episode to ensure Graphiti accepts new entity types
2. **Create migration script** - Parse `insurance_notes` → individual Note entities
3. **Update agent tools** - Add `add_note()` tool for creating Note entities
4. **Test generate_case_summary()** - Ensure queries work with current graph structure
5. **Update CLAUDE.md** - Document Note entity and generate_case_summary() function

---

## Benefits of New Schema

### Before (SQL-style):
- ❌ Computed fields get stale
- ❌ Notes are text blobs, no search
- ❌ Sync issues between tables
- ❌ Can't query "notes from last week"

### After (Graph-native):
- ✅ Always fresh (computed on-demand)
- ✅ Semantic search on notes
- ✅ Single source of truth
- ✅ Temporal queries ("notes since settlement offer")
- ✅ Multi-entity note linking
- ✅ Clean, minimal entity schemas

---

## Schema Version

**Version:** 2.0
**Status:** Updated in graphiti_client.py (not yet deployed to production)
**Compatibility:** Backward compatible - can coexist with old data during migration
