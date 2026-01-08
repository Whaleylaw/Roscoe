# Prompt Updates Summary

**Date:** January 4, 2026
**File:** `src/roscoe/agents/paralegal/prompts.py`

---

## What Changed

### ❌ Removed (Outdated)

**Old schema references:**
- "MedicalProvider" as entity type (replaced by Facility/Location)
- Old relationship examples (TREATING_AT to MedicalProvider)
- Generic provider structure

### ✅ Added (New Schema)

**1. Three-Tier Medical Provider Hierarchy**
- HealthSystem → Facility → Location structure explained
- When to use Facility vs Location
- Progressive detail workflow
- Hierarchy query examples

**2. Multi-Role Entity Support**
- Same entity can be provider/defendant/vendor/expert
- Relationship type determines role
- Norton Hospital example (provider AND defendant)

**3. New Entity Types**
- Facility, Location (medical hierarchy)
- InsurancePolicy, InsurancePayment (insurance tracking)
- MedicalVisit (chronology)
- CourtEvent (calendar)
- LawFirmOffice (multi-office firms)

**4. Medical Chronology Workflow**
- MedicalVisit entity for date-by-date tracking
- related_to_injury flag for lien negotiation
- Bill-to-visit linking
- Unrelated visit flagging

**5. Semantic Episode Search**
- 10,976 episodes with embeddings
- Semantic search capabilities
- Timeline queries

**6. Records Request Infrastructure**
- Fields at all three levels (HealthSystem, Facility, Location)
- Inheritance pattern (query up hierarchy)
- Workflow explanation

**7. Updated Entity Counts**
- Facility: 1,163
- Location: 1,969
- Episode: 10,976
- Doctor: 20,708
- Complete graph stats

---

## Major Concept Changes

### From → To

**Medical Providers:**
- **Old:** Flat MedicalProvider (1,998 generic nodes)
- **New:** HealthSystem (6) → Facility (1,163) → Location (1,969)

**Entity Roles:**
- **Old:** Single-role only (entity is one thing)
- **New:** Multi-role (entity can be provider, defendant, vendor, expert)

**Detail Level:**
- **Old:** Must know exact provider upfront
- **New:** Progressive (link to Facility, add Location later)

**Data Access:**
- **Old:** Graphiti library for unstructured data
- **New:** Pure Cypher queries, direct FalkorDB access

**Search:**
- **Old:** Keyword search only
- **New:** Semantic search via episode embeddings (10,976 episodes)

---

## Files

**Original:** `prompts.py` (208 lines)
**Updated:** `prompts_UPDATED.py` (244 lines)

**Ready to replace original when approved.**

---

## Next: Tools Update

After prompts, need to update:
- `tools.py` - Tool descriptions and parameters
- Agent tool functions if any reference old MedicalProvider
- Middleware if it references old schema

**Should I proceed with replacing prompts.py and updating tools?**
