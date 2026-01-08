# Relationship Review: Antonio-Lopez-MVA-11-14-2025

**Total Episodes:** 2

**Total Proposed Relationships:** 11

**⚠️ MULTI-CLIENT ACCIDENT:** All 4 clients (Antonio Lopez, A'zaire Lopez, Michae Guyton, Mi'ayla Lopez) were in the same accident. Cases need RELATED_ACCIDENT relationships.

---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Attorney (1 consolidated)
- [ ] Justin — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*

### Client (4 consolidated)
**NOTE:** All 4 clients from same accident - verify all exist in clients.json, then create RELATED_ACCIDENT relationships between cases
- [ ] Antonio Lopez — *CHECK clients.json - same accident group*
- [ ] A'zaire Lopez — *CHECK clients.json - same accident group*
- [ ] Michae Guyton — *CHECK clients.json - same accident group*
- [ ] Mi'ayla Lopez — *CHECK clients.json - same accident group*

### Insurer (1 consolidated)
- [ ] Progressive — *✓ MATCHES: Progressive Insurance Company*

### LawFirm (1 consolidated)
- [ ] Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### MedicalProvider (2 consolidated)
- [ ] UofL Health – Brown Cancer Center – Medical Oncology – UofL Hospital — *❌ WRONG MATCH - should be UofL Health – Brown Cancer Center – Medical Oncology facility, NOT ARH McDowell*
- [ ] Norton Cancer Institute Resource Center – Downtown — *❌ WRONG MATCH - should be UofL Health – Brown Cancer Center – Medical Oncology facility, NOT Norton Hospital*

### Organization (3 ignored)
- [ ] Kentucky PLLC — *IGNORED - generic/not relevant*
- [ ] University of Louisville — *IGNORED - too generic*
- [ ] UofL Health – Brown Cancer Center – Medical Oncology Inc. — *IGNORED - parent org reference*

### Other (1 consolidated)
- [ ] New Albany Police Department — *✓ MATCHES: New Albany Police Department (from directory)*

### UIMClaim (1 consolidated)
- [ ] Underinsured motorist coverage... — *IGNORED - generic claim reference*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships
