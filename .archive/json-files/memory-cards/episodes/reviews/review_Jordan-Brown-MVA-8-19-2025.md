# Relationship Review: Jordan-Brown-MVA-8-19-2025

**Total Episodes:** 10

**Total Proposed Relationships:** 34


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (3)
- Louisville Metro EMS (emergency medical services)
- Starlite Chiropractic (chiropractic)
- Norton Audubon Hospital (hospital)

### Insurance Claims (2)
- **BIClaim**: Progressive Insurance Company
  - Adjuster: Walter Kenny
- **PIPClaim**: Root Auto Insurance
  - Adjuster: Blake Pierce

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (3 consolidated)
- [ ] Blake Pierce — *✓ MATCHES: Blake Pierce*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Adjuster)*
- [ ] Walter Kenny — *✓ MATCHES: Walter Kenny*

### Attorney (2 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*

### BIClaim (1 consolidated)
- [ ] Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*

### Client (1 consolidated)
- [ ] Jordan Brown — *✓ MATCHES: Jordan Brown*

### Insurer (3 consolidated)
- [ ] Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*
- [ ] Root Auto Insurance — *✓ MATCHES: Root Auto Insurance*
- [ ] SafeCo Insurance Company — *✓ MATCHES: Falcon Insurance Company*

### LawFirm (1 consolidated)
- [ ] Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### MedicalProvider (3 consolidated)
- [ ] Louisville Metro EMS — *✓ MATCHES: Louisville Metro EMS*
- [ ] Starlite Chiropractic — *✓ MATCHES: Starlite Chiropractic*
- [ ] Norton Audubon Hospital — *✓ MATCHES: Norton Audubon Hospital*

### PIPClaim (1 consolidated)
- [ ] Root Auto Insurance — *✓ MATCHES: Root Auto Insurance*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships