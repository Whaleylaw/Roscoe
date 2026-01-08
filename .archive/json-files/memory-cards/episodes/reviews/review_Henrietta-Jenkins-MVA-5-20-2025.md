# Relationship Review: Henrietta-Jenkins-MVA-5-20-2025

**Total Episodes:** 48

**Total Proposed Relationships:** 96


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (2)
- Norton Norton Audubon Hospital (hospital)
- Synergy Injury Care & Rehab Diagnostics Injury Care & Rehab Diagnostics (physical therapy)

### Insurance Claims (2)
- **BIClaim**: Progressive Insurance Company
  - Adjuster: Colin Karsnitz
- **PIPClaim**: Root Auto Insurance
  - Adjuster: Aaron Ross

### Liens (1)
- Legal Funding Partners

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (2 consolidated)
- [ ] Colin Karsnitz — *✓ MATCHES: Colin Karsnitz*
- [ ] Salena Kelly — *✓ MATCHES: Selena Kelly (from adjusters)*

### Attorney (1 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*

### BIClaim (3 consolidated)
- [ ] BIClaim: Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Insurance Company (BI claim #25-391686743) — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Insurance Company (BIClaim) — *✓ MATCHES: Progressive Insurance Company*

### Client (1 consolidated)
- [ ] Henrietta Jenkins — *✓ MATCHES: Henrietta Jenkins*

### Insurer (2 consolidated)
- [ ] Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*
- [ ] Root Auto Insurance — *✓ MATCHES: Root Auto Insurance*

### MedicalProvider (2 consolidated)
- [ ] Norton Norton Audubon Hospital — *✓ MATCHES: Norton Norton Audubon Hospital*
- [ ] Synergy Injury Care & Rehab Diagnostics Injury Care & Rehab Diagnostics — *✓ MATCHES: Synergy Injury Care & Rehab Diagnostics Injury Care & Rehab Diagnostics*

### PIPClaim (2 consolidated)
- [ ] Root Auto Insurance — *✓ MATCHES: Root Auto Insurance*
- [ ] Root Auto Insurance (PIP claim #25-391686743) — *✓ MATCHES: Root Auto Insurance*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships