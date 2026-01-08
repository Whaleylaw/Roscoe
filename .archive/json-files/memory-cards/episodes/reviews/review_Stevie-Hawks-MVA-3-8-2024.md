# Relationship Review: Stevie-Hawks-MVA-3-8-2024

**Total Episodes:** 208

**Total Proposed Relationships:** 319


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (6)
- AirEvac LifeTeam
- Commonwealth Health Corporation
- Med Center Health
- Radiology Alliance PC (radiology)
- The Medical Center at Bowling Green (hospital)
- TriStar Skyline Medical Center (hospital)

### Insurance Claims (1)
- **PIPClaim**: State Farm Insurance Company
  - Adjuster: Brad Murray

### Liens (2)
- Medicare
- Rawlings Company ($19,953.34)

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (1 consolidated)
- [ ] Brad Murray — *✓ MATCHES: Brad Murray*

### Attorney (6 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Aries — *✓ MATCHES: Aries Penaflor (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Aries Paul Penaflor — *✓ MATCHES: Aries Penaflor (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessica — *✓ MATCHES: Jessica Bottorff (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessica Bottorff — *✓ MATCHES: Jessica Bottorff (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*

### BIClaim (1 consolidated)
- [ ] Bodily Injury (BI) coverage — *IGNORED - coverage description*

### Client (3 consolidated)
- [ ] Aries Penaflor — *✓ MATCHES: Aries Penaflor (WHALEY STAFF → should be CaseManager, not Client)*
- [ ] Stevie Hawks — *✓ MATCHES: Stevie Hawks*
- [ ] Stevie Martin Hawks — *✓ MATCHES: Stevie Hawks*

### Insurer (1 consolidated)
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*

### LawFirm (1 consolidated)
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### Lien (3 consolidated)
- [ ] Medicaid/Wellcare lien — *IGNORED - generic lien description*
- [ ] Medicare — *✓ MATCHES: Medicare*
- [ ] Rawlings Company — *✓ MATCHES: Rawlings Company*

### MedicalProvider (6 consolidated)
- [ ] AirEvac LifeTeam — *✓ MATCHES: AirEvac LifeTeam*
- [ ] Commonwealth Health Corporation — *✓ MATCHES: Commonwealth Health Corporation*
- [ ] Med Center Health — *✓ MATCHES: Med Center Health*
- [ ] Radiology Alliance PC — *✓ MATCHES: Radiology Alliance PC*
- [ ] The Medical Center at Bowling Green — *✓ MATCHES: The Medical Center at Bowling Green*
- [ ] TriStar Skyline Medical Center — *✓ MATCHES: TriStar Skyline Medical Center*

### Organization (3 consolidated)
- [ ] Aries — *✓ MATCHES: Aries Penaflor (WHALEY STAFF → should be CaseManager, not Organization)*
- [ ] City Clerk Open Records (bgky.org) — *IGNORED - government office*
- [ ] Organization — *IGNORED - too generic*

### PIPClaim (2 consolidated)
- [ ] PIPClaim: State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*
- [ ] State Farm Insurance Company (PIP) — *✓ MATCHES: State Farm Insurance Company*

### UMClaim (3 consolidated)
- [ ] UM rejection / Uninsured Motorist documentation — *IGNORED - claim description*
- [ ] Underinsured Motorist (UM) coverage — *IGNORED - coverage description*
- [ ] Underinsured/Uninsured Motorist (UM/UIM) — *IGNORED - coverage description*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships