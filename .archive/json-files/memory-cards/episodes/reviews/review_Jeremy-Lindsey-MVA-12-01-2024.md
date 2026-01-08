# Relationship Review: Jeremy-Lindsey-MVA-12-01-2024

**Total Episodes:** 102

**Total Proposed Relationships:** 214


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (1)
- St. Elizabeth Physicians- Burlington

### Insurance Claims (3)
- **BIClaim**: Progressive Insurance Company
  - Adjuster: Jennifer Howard
- **PIPClaim**: Auto Owners Insurance
  - Adjuster: Emily Pernice
- **PIPClaim**: Auto Owners Insurance

### Liens (1)
- Rawlings Company

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (7 consolidated)
- [ ] Chandler Wolfe — *✓ MATCHES: Chandler Wolfe*
- [ ] Donna Zelenika — *✓ MATCHES: Donna Zelenika (from adjusters)*
- [ ] Emily Pernice — *✓ MATCHES: Emily Pernice*
- [ ] Jennifer Howard — *✓ MATCHES: Jennifer Howard*
- [ ] Jessa — *✓ MATCHES: Jessa Galosmo (WHALEY STAFF → should be CaseManager, not Adjuster)*
- [ ] Rob Weyhing — *✓ MATCHES: Rob Weyhing (from adjusters)*
- [ ] property-damage adjuster — *IGNORED - generic term*

### Attorney (4 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Jessa Galosmo — *✓ MATCHES: Jessa Galosmo (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessica Bottorff — *✓ MATCHES: Jessica Bottorff (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*

### BIClaim (4 consolidated)
- [ ] BIClaim: Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*
- [ ] BIClaim: Progressive Insurance Company (Adjuster: Jennifer Howard) — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Claim #24-902741838 — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Insurance Company (Claim #24-902741838) — *✓ MATCHES: Progressive Insurance Company*

### Client (4 consolidated)
- [ ] Chase Lindsey — *✓ MATCHES: Chase Lindsey*
- [ ] Elizabeth Lindsey — *✓ MATCHES: Elizabeth Lindsey*
- [ ] Jeremy Lindsey — *✓ MATCHES: Jeremy Lindsey*
- [ ] Owen Lindsey — *✓ MATCHES: Owen Lindsey*

### Insurer (3 consolidated)
- [ ] Auto Owners Insurance — *✓ MATCHES: Auto Owners Insurance*
- [ ] Progressive Direct Insurance Company — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Insurance — *✓ MATCHES: Progressive Insurance Company*

### LawFirm (1 consolidated)
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### Lien (1 consolidated)
- [ ] Rawlings Company — *✓ MATCHES: Rawlings Company*

### LienHolder (1 consolidated)
- [ ] Blue Cross and Blue Shield — *✓ MATCHES: Blue Cross Blue Shield (from lienholders)*

### MedicalProvider (1 consolidated)
- [ ] St. Elizabeth Physicians- Burlington — *✓ MATCHES: St. Elizabeth Physicians- Burlington*

### PIPClaim (3 consolidated)
- [ ] Auto Owners Insurance (Adjuster: None) — *✓ MATCHES: Auto Owners Insurance*
- [ ] Auto Owners Insurance (PIP) — *✓ MATCHES: Auto Owners Insurance*
- [ ] PIPClaim: Auto Owners Insurance (Adjuster: Emily Pernice) — *✓ MATCHES: Auto Owners Insurance*

### UIMClaim (1 consolidated)
- [ ] Auto Owners Insurance (UIM) — *✓ MATCHES: Auto Owners Insurance (from insurers)*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships