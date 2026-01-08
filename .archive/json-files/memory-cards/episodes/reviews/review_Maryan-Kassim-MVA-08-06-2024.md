# Relationship Review: Maryan-Kassim-MVA-08-06-2024

**Total Episodes:** 108

**Total Proposed Relationships:** 251


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (5)
- Diagnostic X-Ray Physicians PSC
- Louisville Metro EMS (emergency medical services)
- Norton Norton Audubon Hospital (hospital)
- Starlite Chiropractic (chiropractic)
- University of Louisville School of Dentistry

### Insurance Claims (2)
- **BIClaim**: Progressive Insurance Company
  - Adjuster: Brandi Chappell-Haggard
- **PIPClaim**: Progressive Insurance Company
  - Adjuster: Keri Hall

### Liens (1)
- Conduent ($3,830.39)

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (4 consolidated)
- [ ] Brandi L. Chappell-Haggard — *✓ MATCHES: Brandi Chappell-Haggard*
- [ ] Emma Hartell — *✓ MATCHES: Emma Hartell*
- [ ] Jessa Galosmo — *✓ MATCHES: Jessa Galosmo (WHALEY STAFF → should be CaseManager, not Adjuster)*
- [ ] Keri A Hall — *✓ MATCHES: Keri Hall*

### Attorney (6 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Jessa Galosmo — *✓ MATCHES: Jessa Galosmo (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessica Bottorff — *✓ MATCHES: Jessica Bottorff (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessica Whaley — *IGNORED - staff name only*
- [ ] Justin — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*

### BIClaim (2 consolidated)
- [ ] Progressive Claim #24-711062492 — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*

### Client (3 consolidated)
- [ ] Abdullahi — *IGNORED - first name only*
- [ ] Abdullahi Kassim — *IGNORED - family member*
- [ ] Maryan Kassim — *✓ MATCHES: Maryan Kassim*

### Insurer (1 consolidated)
- [ ] Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*

### LawFirm (1 consolidated)
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### Lien (1 consolidated)
- [ ] Conduent: $3830.39 — *✓ MATCHES: Conduent*

### MedicalProvider (5 consolidated)
- [ ] Diagnostic X-Ray Physicians PSC — *✓ MATCHES: Diagnostic X-Ray Physicians PSC*
- [ ] Louisville Metro EMS — *✓ MATCHES: Louisville Metro EMS*
- [ ] Norton Norton Audubon Hospital — *✓ MATCHES: Norton Norton Audubon Hospital*
- [ ] Starlite Chiropractic — *✓ MATCHES: Starlite Chiropractic*
- [ ] University of Louisville School of Dentistry — *✓ MATCHES: University of Louisville School of Dentistry*

### PIPClaim (4 consolidated)
- [ ] PIPClaim - CLM# 24711062492 (Progressive) — *IGNORED - claim number only*
- [ ] PIPClaim: Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Claim #24-711062492 — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Insurance Company (Adjuster: Keri Hall) — *✓ MATCHES: Progressive Insurance Company*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships