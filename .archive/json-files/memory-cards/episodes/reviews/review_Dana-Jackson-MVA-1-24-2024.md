# Relationship Review: Dana-Jackson-MVA-1-24-2024

**Total Episodes:** 175

**Total Proposed Relationships:** 485


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (5)
- Foundation Radiology (radiology)
- Southeastern Emergency Physician Services
- Starlite Chiropractic (chiropractic)
- University Of Louisville Hospital Radiology (hospital)
- UofL Health – Brown Cancer Center – Medical Oncology - Mary & Elizabeth UofL Health – Brown Cancer Center – Medical Oncology – Mary & Elizabeth Hospital (hospital)

### Insurance Claims (2)
- **BIClaim**: State Farm Insurance Company
  - Adjuster: Sharika Moses
- **PIPClaim**: The General Insurance
  - Adjuster: Dana Cohen

### Liens (2)
- Aetna Better Health of Kentucky ($607.41)
- Capital Strategies

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (2 consolidated)
- [ ] Ashley Joyner — *✓ MATCHES: Ashley Joyner (from adjusters)*
- [ ] Dana Cohen — *✓ MATCHES: Dana Cohen*

### Attorney (14 consolidated)
- [ ] Aaron Gregory Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Aries Paul Peñaflor — *✓ MATCHES: Aries Penaflor (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Betsy R. Catron — *✓ MATCHES: Betsy R. Catron*
- [ ] Cecil Finley — *✓ MATCHES: Cecil Finley (from clients - client in related case)*
- [ ] Debora(h) Dilbeck — *✓ MATCHES: Deborah Myers*
- [ ] Deborah Campbell Myers — *✓ MATCHES: Deborah Myers*
- [ ] Defense Counsel — *IGNORED - generic term*
- [ ] Defense counsel (DC) — *IGNORED - generic term*
- [ ] Gerold Reynolds — *IGNORED - attorney name only*
- [ ] Jessica Bottorff — *✓ MATCHES: Jessica Bottorff (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Sarena — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Sarena M. Tuttle — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] W. Bryce Koon, Esq. — *✓ MATCHES: Bryce Koon (WHALEY ATTORNEY, not Attorney)*

### BIClaim (1 consolidated)
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*

### Client (2 consolidated)
- [ ] Cecil Finley — *✓ MATCHES: Cecil Finley (from clients)*
- [ ] Dana Jackson — *✓ MATCHES: Dana Jackson (from clients)*

### Court (6 consolidated)
- [ ] Jefferson 24-CI-005774 — *✓ MATCHES: Jefferson County Circuit Court, Division VII*
- [ ] Jefferson Circuit Court — *✓ MATCHES: Jefferson County Circuit Court, Division VII*
- [ ] Jefferson County (24-CI-005774) — *✓ MATCHES: Jefferson County Circuit Court, Division VII*
- [ ] Jefferson County (Jefferson 24-CI-005774) — *✓ MATCHES: Jefferson County Circuit Court, Division VII*
- [ ] Kentucky Court of Justice — *✓ MATCHES: Kentucky Court Of Justice (from organizations)*
- [ ] courts — *IGNORED - generic term*

### Defendant (4 consolidated)
- [ ] Companion Finley — *✓ MATCHES: Cecil Finley (from clients - companion in related case)*
- [ ] Defendant Driver — *IGNORED - generic term*
- [ ] Justin KieblER — *✓ MATCHES: Justin Kiebler (from defendants)*
- [ ] Kiebler — *✓ MATCHES: Justin Kiebler (from defendants)*

### Insurer (3 consolidated)
- [ ] Aetna Better Health of Kentucky — *✓ MATCHES: Aetna Better Health of Kentucky (from directory)*
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*
- [ ] The General Insurance — *✓ MATCHES: The General Insurance*

### LawFirm (6 consolidated)
- [ ] Deborah Dilbeck & Myers — *✓ MATCHES: Deborah Myers (→ ATTORNEY, not law firm)*
- [ ] Dilbeck & Myers, PLLC — *✓ MATCHES: Dilbeck & Myers*
- [ ] Finley & Jackson — *IGNORED - these are the clients, not a law firm*
- [ ] Sarena Tuttle — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not LawFirm)*
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*
- [ ] Tyson, Schwab, Short & Weiss — *✓ MATCHES: Tyson, Schwab, Short & Weiss (from lienholders)*

### Lien (2 consolidated)
- [ ] Aetna Better Health of Kentucky — *✓ MATCHES: Aetna Better Health of Kentucky*
- [ ] Capital Strategies — *✓ MATCHES: Capital Strategies*

### LienHolder (2 consolidated)
- [ ] Capital Strategies — *✓ MATCHES: Capital Strategies*
- [ ] Legal Lending Company — *IGNORED - generic lien company reference*

### MedicalProvider (6 consolidated)
- [ ] Foundation Radiology — *✓ MATCHES: Foundation Radiology*
- [ ] Southeastern Emergency Physician Services — *✓ MATCHES: Southeastern Emergency Physician Services*
- [ ] Starlite Chiropractic — *✓ MATCHES: Starlite Chiropractic*
- [ ] University Of Louisville Hospital Radiology — *✓ MATCHES: University Of Louisville Hospital Radiology*
- [ ] UofL Health – Brown Cancer Center – Medical Oncology - Mary & Elizabeth UofL Health – Brown Cancer Center – Medical Oncology – Mary & Elizabeth Hospital — *✓ MATCHES: UofL Health – Brown Cancer Center – Medical Oncology - Mary & Elizabeth UofL Health – Brown Cancer Center – Medical Oncology – Mary & Elizabeth Hospital*
- [ ] Imaging — *✓ MATCHES: Imaging, PLLC*

### Organization (1 consolidated)
- [ ] ChartSwap.com — *✓ MATCHES: ChartSwap (from organizations)*

### PIPClaim (1 consolidated)
- [ ] The General Insurance (PIP) — *✓ MATCHES: The General Insurance*

### Vendor (4 consolidated)
- [ ] ChartSwap.com — *✓ MATCHES: ChartSwap (from organizations)*
- [ ] Etscorn & Sons — *IGNORED - vendor name only*
- [ ] Sarena M. Tuttle — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Vendor)*
- [ ] Stuttle — *IGNORED - misspelling*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships