# Relationship Review: Brooklyn-Ballard-MVA-02-28-2024

**Total Episodes:** 81

**Total Proposed Relationships:** 183


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (4)
- Bellevue-Dayton Fire/EMS (emergency medical services)
- Cincinnati Children's Hospital (hospital)
- MEBS Counseling
- St. Elizabeth Physicians - Crittenden

### Insurance Claims (3)
- **BIClaim**: Berkshire Risk Services
  - Adjuster: Scott Frayer
- **PIPClaim**: State Farm Insurance Company
  - Adjuster: Thomas Nie
- **UMClaim**: State Farm Insurance Company
  - Adjuster: Stephanie Thomas

### Liens (1)
- None

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (2 consolidated)
- [ ] Greg Gant — *IGNORED - not relevant*
- [ ] Stephanie Thomas — *✓ MATCHES: Stephanie Thomas*

### Attorney (6 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY)*
- [ ] Aries Paul Peñaflor — *✓ MATCHES: Aries Penaflor (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessa Galosmo — *✓ MATCHES: Jessa Galosmo (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessica Bottorff — *✓ MATCHES: Jessica Bottorff (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Whaley — *✓ CONSOLIDATED → Aaron G. Whaley*

### BIClaim (1 consolidated)
- [ ] Berkshire Risk Services — *✓ MATCHES: Berkshire Risk Services*

### Client (4 consolidated)
- [ ] Brooklyn (minor child) — *✓ CONSOLIDATED → Brooklyn Ballard*
- [ ] Deena Gilliam — *IGNORED - not client*
- [ ] Elizabeth Ballard — *IGNORED - not client*
- [ ] Ms. Brooklyn Ballard — *✓ MATCHES: Brooklyn Ballard*

### Insurer (1 consolidated)
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*

### LawFirm (1 consolidated)
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### Lien (2 consolidated)
- [ ] Brooklyn Ballard-Lien Request — *IGNORED - document reference, not lien*
- [ ] Health lien — *IGNORED - generic reference*

### MedicalProvider (4 consolidated)
- [ ] Bellevue-Dayton Fire/EMS — *✓ MATCHES: Bellevue-Dayton Fire/EMS*
- [ ] Cincinnati Children's Hospital — *✓ MATCHES: Cincinnati Children's Hospital*
- [ ] MEBS Counseling — *✓ MATCHES: MEBS Counseling*
- [ ] St. Elizabeth Physicians - Crittenden — *✓ MATCHES: St. Elizabeth Physicians - Crittenden*

### Organization (2 consolidated)
- [ ] Carelon — *✓ MATCHES: Carelon Subrogation (from directory)*
- [ ] Health Information Management (Cincinnati Children's Hospital) — *✓ MATCHES: Cincinnati Children's Hospital (department reference)*

### PIPClaim (1 consolidated)
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*

### UMClaim (1 consolidated)
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships
