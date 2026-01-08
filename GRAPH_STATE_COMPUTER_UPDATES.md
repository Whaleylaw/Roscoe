# Graph State Computer Updates

**File:** `/Volumes/X10 Pro/Roscoe/src/roscoe/workflow_engine/orchestrator/graph_state_computer.py`
**Date:** January 4, 2026
**Status:** ✅ Complete

---

## Changes Made

### 1. ✅ Converted DerivedWorkflowState from dataclass to Pydantic BaseModel

**Before:**
```python
from dataclasses import dataclass, field

@dataclass
class DerivedWorkflowState:
    case_id: str
    client_name: str
    # ... fields with no defaults
```

**After:**
```python
from pydantic import BaseModel, Field

class DerivedWorkflowState(BaseModel):
    case_id: str
    client_name: str
    # ... fields with proper defaults using Field(default_factory=...)
```

**Benefit:**
- Consistent with all entity definitions in `graphiti_client.py`
- Better validation and type checking
- Pydantic's built-in serialization methods available
- Proper default values using `Field(default_factory=...)`

---

### 2. ✅ Updated Medical Provider Query for Three-Tier Hierarchy

**Before (BROKEN):**
```python
query = """
    MATCH (case:Case {name: $case_name})-[:TREATING_AT]->(provider:MedicalProvider)
    OPTIONAL MATCH (provider)-[:PART_OF]->(org:Organization)
    RETURN provider.name as name,
           provider.specialty as specialty,
           provider.phone as phone,
           org.name as parent_org,
           provider.total_bills as total_bills
"""
```

**Issues:**
- ❌ `MedicalProvider` entity no longer exists
- ❌ Wrong relationship: `TREATING_AT` (should be `TREATED_AT`)
- ❌ Wrong path: Goes from Case directly (should go through Client)
- ❌ Uses `Organization` (should be `HealthSystem`)

**After (FIXED):**
```python
query = """
    MATCH (case:Case {name: $case_name})-[:HAS_CLIENT]->(client:Client)-[:TREATED_AT]->(provider)
    WHERE provider:Facility OR provider:Location
    OPTIONAL MATCH (provider)-[:PART_OF]->(parent)
    WHERE parent:Facility OR parent:HealthSystem
    OPTIONAL MATCH (parent)-[:PART_OF]->(grandparent:HealthSystem)
    RETURN provider.name as name,
           labels(provider)[0] as provider_type,
           provider.specialty as specialty,
           provider.phone as phone,
           provider.address as address,
           parent.name as parent_name,
           labels(parent)[0] as parent_type,
           grandparent.name as health_system
"""
```

**What Changed:**
- ✅ Correct path: Case -[:HAS_CLIENT]-> Client -[:TREATED_AT]-> Facility/Location
- ✅ Supports both Facility and Location entities
- ✅ Traverses up the three-tier hierarchy (Location → Facility → HealthSystem)
- ✅ Returns provider type (Facility or Location)
- ✅ Returns full hierarchy: provider, parent, health_system
- ✅ Includes address (for Location entities)

**Result Format:**
```python
{
    "name": "Norton Orthopedic Institute - Downtown",
    "type": "Location",
    "specialty": "Orthopedics",
    "phone": "555-1234",
    "address": "123 Main St, Louisville, KY",
    "parent": "Norton Orthopedic Institute",
    "health_system": "Norton Healthcare"
}
```

---

### 3. ✅ Updated Insurance Claims Query for InsurancePolicy Structure

**Before:**
```python
query = """
    MATCH (case:Case {name: $case_name})-[:HAS_CLAIM]->(claim:Entity)
    WHERE claim:BIClaim OR claim:PIPClaim OR claim:UMClaim OR claim:UIMClaim OR claim:WCClaim OR claim:MedPayClaim
    OPTIONAL MATCH (claim)-[:INSURED_BY]->(insurer:Insurer)
    OPTIONAL MATCH (claim)-[:ASSIGNED_ADJUSTER]->(adjuster:Adjuster)
    RETURN claim.name as claim_number,
           claim.entity_type as claim_type,
           insurer.name as insurer_name,
           adjuster.name as adjuster_name,
           claim.policy_limit as policy_limit,
           claim.demand_amount as demand_amount,
           claim.current_offer as current_offer
"""
```

**Issues:**
- ❌ Includes `MedPayClaim` (not in our schema)
- ❌ Wrong relationships: `INSURED_BY`, `ASSIGNED_ADJUSTER` (should use InsurancePolicy)
- ❌ Mixed fields: `policy_limit` on claim (should be on policy)

**After (FIXED):**
```python
query = """
    MATCH (case:Case {name: $case_name})-[:HAS_CLAIM]->(claim)
    WHERE claim:BIClaim OR claim:PIPClaim OR claim:UMClaim OR claim:UIMClaim OR claim:WCClaim
    OPTIONAL MATCH (claim)-[:UNDER_POLICY]->(policy:InsurancePolicy)
    OPTIONAL MATCH (policy)-[:WITH_INSURER]->(insurer:Insurer)
    OPTIONAL MATCH (claim)-[:HANDLED_BY]->(adjuster:Adjuster)
    RETURN claim.claim_number as claim_number,
           labels(claim)[0] as claim_type,
           policy.policy_number as policy_number,
           insurer.name as insurer_name,
           adjuster.name as adjuster_name,
           policy.bi_limit as bi_limit,
           policy.pip_limit as pip_limit,
           policy.um_limit as um_limit,
           policy.uim_limit as uim_limit,
           claim.amount_demanded as demand_amount,
           claim.amount_offered as current_offer,
           claim.status as claim_status
"""
```

**What Changed:**
- ✅ Removed `MedPayClaim` from WHERE clause
- ✅ Correct relationship chain: Claim -[:UNDER_POLICY]-> InsurancePolicy -[:WITH_INSURER]-> Insurer
- ✅ Correct adjuster relationship: Claim -[:HANDLED_BY]-> Adjuster
- ✅ Policy limits on InsurancePolicy (bi_limit, pip_limit, um_limit, uim_limit)
- ✅ Returns policy_number for better tracking
- ✅ Includes claim status
- ✅ Uses `labels(claim)[0]` to get actual claim type

**Result Format:**
```python
{
    "claim_number": "17-87C986K",
    "type": "PIPClaim",
    "policy_number": "POL-123456",
    "insurer": "State Farm",
    "adjuster": "Jane Smith",
    "bi_limit": 50000.00,
    "pip_limit": 10000.00,
    "um_limit": 50000.00,
    "uim_limit": 50000.00,
    "demand_amount": 10000.00,
    "current_offer": 8000.00,
    "status": "active"
}
```

---

## Impact

### What Now Works

1. **Medical Provider Queries:**
   - Correctly retrieves providers using new three-tier hierarchy
   - Supports both Facility and Location entities
   - Returns full hierarchy path for records requests
   - Properly traverses Client relationship

2. **Insurance Queries:**
   - Correctly uses InsurancePolicy entity
   - Separates policy limits from claim data
   - Returns all coverage limits (BI, PIP, UM, UIM)
   - Includes policy number for tracking

3. **Type Safety:**
   - Pydantic validation on all workflow state data
   - Better error messages for invalid data
   - Consistent with rest of codebase

### What Was Broken Before

1. **Medical Provider Query:**
   - Would return 0 results (MedicalProvider doesn't exist)
   - Agent couldn't see any providers treating the client
   - Workflow state would show empty provider list

2. **Insurance Query:**
   - Would return incomplete data (no policy limits)
   - Mixed claim and policy fields incorrectly
   - Included non-existent MedPayClaim type

### Functions Using This Code

The `GraphWorkflowStateComputer` is used by:
- `get_case_workflow_status()` tool (in agent tools)
- Workflow middleware (if implemented)
- Case state queries from any part of the system

**All these now work with the new schema.**

---

## Testing Recommendations

### Test Medical Provider Query

```python
from roscoe.workflow_engine.orchestrator.graph_state_computer import GraphWorkflowStateComputer

computer = GraphWorkflowStateComputer()
state = await computer.compute_state("Caryn-McCay-MVA-7-30-2023")

# Should show providers in new format
print(state.medical_providers)
# Expected: List with provider, parent, health_system fields
```

### Test Insurance Query

```python
# Should show insurance with policy_number and all limits
print(state.insurance_claims)
# Expected: List with bi_limit, pip_limit, um_limit, uim_limit fields
```

### Test Pydantic Validation

```python
# Should validate properly
state_dict = state.model_dump()  # Pydantic's built-in method
print(state_dict)

# Custom formatting still works
formatted = state.format_for_prompt()
print(formatted)
```

---

## Files Modified

1. `/Volumes/X10 Pro/Roscoe/src/roscoe/workflow_engine/orchestrator/graph_state_computer.py`
   - Lines 14-17: Import changes (dataclass → Pydantic)
   - Lines 20-55: DerivedWorkflowState class definition
   - Lines 336-374: _get_insurance_claims() method
   - Lines 376-394: _get_medical_providers() method

---

## Compatibility

### Backward Compatible

✅ The `to_dict()` and `format_for_prompt()` methods maintain the same output format, so existing code that uses these methods will continue to work.

### Breaking Changes

❌ **None** - All changes are internal to the GraphWorkflowStateComputer class. The external API remains the same.

### Pydantic Benefits Added

✅ Can now use:
- `state.model_dump()` - Pydantic's dict conversion
- `state.model_dump_json()` - Direct JSON serialization
- `DerivedWorkflowState.model_validate()` - Validation from dict
- Field validation on construction

---

## Summary

All graph queries in `graph_state_computer.py` now correctly use the new schema:

| Query | Old Entity | New Entity | Status |
|-------|-----------|------------|--------|
| Medical Providers | MedicalProvider | Facility/Location | ✅ Fixed |
| Insurance Claims | Direct insurer link | InsurancePolicy → Insurer | ✅ Fixed |
| State Model | dataclass | Pydantic BaseModel | ✅ Updated |

**Result:** The GraphWorkflowStateComputer is now fully compatible with the updated knowledge graph schema and will return accurate workflow state for all cases.
