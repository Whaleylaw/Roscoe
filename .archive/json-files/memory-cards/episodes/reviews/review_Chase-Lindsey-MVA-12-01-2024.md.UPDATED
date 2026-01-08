# Relationship Review: Chase-Lindsey-MVA-12-01-2024

**Total Episodes:** 31

**Total Proposed Relationships:** 105

**⚠️ MULTI-CLIENT ACCIDENT:** All 4 Lindsey family members (Chase, Elizabeth, Jeremy, Owen) involved in same accident. Need RELATED_ACCIDENT relationships.

---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (2)
- Cincinnati Children's Hospital (hospital)
- Florence Fire/EMS (emergency medical services)

### Insurance Claims (3)
- **BIClaim**: Progressive Insurance Company
  - Adjuster: Jennifer Howard
- **PIPClaim**: None
- **PIPClaim**: Auto Owners Insurance

### Liens (1)
- Rawlings Company ($17,734.84)

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (1 consolidated)
- [ ] Chandler Wolfe — *✓ ADDED to adjusters.json*

### Attorney (4 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY)*
- [ ] Jessa Galosmo — *✓ MATCHES: Jessa Galosmo (WHALEY STAFF → should be CaseManager)*
- [ ] Jessica Bottorff — *✓ MATCHES: Jessica Bottorff (WHALEY STAFF → should be CaseManager)*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager)*

### Client (4 consolidated)
**NOTE:** All 4 clients from same accident - need RELATED_ACCIDENT relationships between their cases
- [ ] Chase Lindsey — *✓ ADDED to clients.json (linked to Elizabeth/Jeremy/Owen Lindsey)*
- [ ] Elizabeth Lindsey — *✓ MATCHES: Elizabeth Lindsey (RELATED_ACCIDENT link needed)*
- [ ] Jeremy Lindsey — *✓ MATCHES: Jeremy Lindsey (RELATED_ACCIDENT link needed)*
- [ ] Owen Lindsey — *✓ ADDED to clients.json (linked to other Lindseys)*

### Insurer (2 consolidated)
- [ ] Auto Owners Insurance — *✓ MATCHES: Auto Owners Insurance*
- [ ] Auto-Owners Insurance Company — *✓ CONSOLIDATED → Auto Owners Insurance*

### LawFirm (1 consolidated)
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### Lien (1 consolidated)
- [ ] Rawlings Company — *✓ MATCHES: Rawlings Company*

### MedicalProvider (2 consolidated)
- [ ] Cincinnati Children's Hospital — *✓ MATCHES: Cincinnati Children's Hospital*
- [ ] Florence Fire/EMS — *✓ MATCHES: Florence Fire/EMS*

### Organization (2 consolidated)
- [ ] EvenUP — *IGNORED - already exists as vendor, not organization*
- [ ] Louisville Accident Lawyer / Filevine — *IGNORED - generic reference/software*

### PIPClaim (1 consolidated)
- [ ] Auto Owners Insurance — *✓ MATCHES: Auto Owners Insurance*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships
