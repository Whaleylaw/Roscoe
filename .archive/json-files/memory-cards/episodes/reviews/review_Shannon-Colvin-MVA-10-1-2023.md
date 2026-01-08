# Relationship Review: Shannon-Colvin-MVA-10-1-2023

**Total Episodes:** 114

**Total Proposed Relationships:** 306


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (5)
- Baptist Health Breckenridge Imaging Hardin
- Elizabethtown Emergency Physicians
- Radiology Associates Inc (radiology)
- UL Health Primary Care
- Zip Clinic Urgent Care

### Insurance Claims (3)
- **BIClaim**: Kentucky Farm Bureau
  - Adjuster: Ben Taylor
- **PIPClaim**: State Farm Insurance Company
  - Adjuster: State Farm PIP Team
- **UIMClaim**: State Farm Insurance Company

### Liens (1)
- United Healthcare ($145.72)

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (3 consolidated)
- [ ] Anne Perez — *✓ MATCHES: Anne Perez*
- [ ] Ben Taylor — *✓ MATCHES: Ben Taylor*
- [ ] State Farm PIP Team — *✓ MATCHES: State Farm PIP Team*

### Attorney (7 consolidated)
- [ ] Aaron Gregory Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] B.L. Lally — *✓ MATCHES: Brandon Thomas Lally*
- [ ] Brandon Thomas Lally — *✓ MATCHES: Brandon Thomas Lally*
- [ ] Defense Counsel — *IGNORED - generic term*
- [ ] Jessa Galosmo — *✓ MATCHES: Jessa Galosmo (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Sarena — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] W. Bryce Koon, Esq. — *✓ MATCHES: Bryce Koon (WHALEY ATTORNEY, not Attorney)*

### BIClaim (3 consolidated)
- [ ] BIClaim (Kentucky Farm Bureau) — *✓ MATCHES: Kentucky Farm Bureau*
- [ ] KFB Claim #04908174 — *IGNORED - claim number*
- [ ] Kentucky Farm Bureau — *✓ MATCHES: Kentucky Farm Bureau*

### Client (3 consolidated)
- [ ] Colleen Colvin — *✓ MATCHES: Colleen M. Colvin*
- [ ] Jessa Galosmo — *✓ MATCHES: Jessa Galosmo (WHALEY STAFF → should be CaseManager, not Client)*
- [ ] Shannon Colvin — *✓ MATCHES: Shannon Colvin*

### Court (6 consolidated)
- [ ] Case 24-CI-01568 — *IGNORED - case number*
- [ ] Hardin (Circuit) — *✓ MATCHES: Hardin County Circuit Court, Division III*
- [ ] Hardin County — *✓ MATCHES: Hardin County Circuit Court, Division III*
- [ ] Hardin County (docket 24-CI-01568) — *✓ MATCHES: Hardin County Circuit Court, Division III*
- [ ] Hardin County Circuit Court — *✓ MATCHES: Hardin County Circuit Court, Division III*
- [ ] Jefferson Circuit Court — *✓ MATCHES: Jefferson County Circuit Court*

### Defendant (1 consolidated)
- [ ] Paul Rafferty — *✓ MATCHES: Paul Rafferty*

### Insurer (2 consolidated)
- [ ] Kentucky Farm Bureau — *✓ MATCHES: Kentucky Farm Bureau*
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*

### LawFirm (2 consolidated)
- [ ] LOCHMILLER BOND — *✓ MATCHES: Lochmiller Bond*
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### Lien (1 consolidated)
- [ ] United Healthcare — *✓ MATCHES: United Healthcare*

### MedicalProvider (5 consolidated)
- [ ] Baptist Health Breckenridge Imaging Hardin — *✓ MATCHES: Baptist Health Breckenridge Imaging Hardin*
- [ ] Elizabethtown Emergency Physicians — *✓ MATCHES: Elizabethtown Emergency Physicians*
- [ ] Radiology Associates Inc — *✓ MATCHES: Radiology Associates Inc*
- [ ] UL Health Primary Care — *✓ MATCHES: UL Health Primary Care*
- [ ] Zip Clinic Urgent Care — *✓ MATCHES: Zip Clinic Urgent Care*

### Organization (2 consolidated)
- [ ] Kentucky Court of Justice — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Kentucky Court of Justice eFiling system — *✓ MATCHES: Kentucky Court Of Justice*

### PIPClaim (4 consolidated)
- [ ] PIPClaim: State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*
- [ ] State Farm Insurance Company PIP claim — *✓ MATCHES: State Farm Insurance Company*
- [ ] State Farm PIPClaim — *✓ MATCHES: State Farm Insurance Company*

### UIMClaim (1 consolidated)
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*

### Vendor (1 consolidated)
- [ ] RCFax (8008428810@rcfax.com) — *IGNORED - fax service*
 
---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships