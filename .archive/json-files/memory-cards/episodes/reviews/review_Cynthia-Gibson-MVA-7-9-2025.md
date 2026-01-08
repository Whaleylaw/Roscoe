# Relationship Review: Cynthia-Gibson-MVA-7-9-2025

**Total Episodes:** 36

**Total Proposed Relationships:** 70


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (4)
- Baptist Health Breckenridge Imaging Occupational Medicine - Fern Valley
- Bullitt County EMS (emergency medical services)
- Starlite Chiropractic (chiropractic)
- Norton Audubon Hospital (hospital)

### Insurance Claims (3)
- **BIClaim**: Root Auto Insurance
  - Adjuster: Courtney Heinnickel
- **PIPClaim**: State Farm Insurance Company
  - Adjuster: Ryan Ricci
- **UMClaim**: State Farm Insurance Company
  - Adjuster: Gary Jones

### Liens (1)
- Conduent

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (2 consolidated)
- [ ] Gary Jones — *✓ MATCHES: Gary Jones*
- [ ] Ryan Ricci — *✓ MATCHES: Ryan Ricci*

### Attorney (1 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*

### BIClaim (1 consolidated)
- [ ] Root Auto Insurance — *✓ MATCHES: Root Auto Insurance*

### Client (1 consolidated)
- [ ] Cynthia Gibson — *✓ MATCHES: Cynthia Gibson*

### Insurer (1 consolidated)
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*

### LawFirm (1 consolidated)
- [ ] Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### MedicalProvider (3 consolidated)
- [ ] Baptist Health Breckenridge Imaging Occupational Medicine - Fern Valley — *✓ MATCHES: Baptist Health Breckenridge Imaging Occupational Medicine - Fern Valley*
- [ ] Bullitt County EMS — *✓ MATCHES: Bullitt County EMS*
- [ ] Norton Audubon Hospital — *✓ MATCHES: Norton Audubon Hospital*

### Organization (1 consolidated)
- [ ] Bullitt County Police Department — *✓ MATCHES: Bullitt County Police Department (from organizations)*

### PIPClaim (2 consolidated)
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*
- [ ] State Farm Insurance Company - PIP Claim #4720852C0317 — *✓ MATCHES: State Farm Insurance Company*

### UMClaim (2 consolidated)
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*
- [ ] UMClaim - State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships