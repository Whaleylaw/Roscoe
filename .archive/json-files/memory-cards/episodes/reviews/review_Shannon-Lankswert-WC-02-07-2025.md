# Relationship Review: Shannon-Lankswert-WC-02-07-2025

**Total Episodes:** 88

**Total Proposed Relationships:** 403


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (4)
- Physical Therapy
- Concentra Medical Center
- Flaget Memorial Hospital (hospital)
- The Injury Centers

### Liens (1)
- Anthem Blue Cross Blue Shield

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (8 consolidated)
- [ ] DC/Adj — *IGNORED - abbreviation*
- [ ] George Stewart — *✓ MATCHES: George Stewart*
- [ ] Kaitlin Ericksen — *✓ MATCHES: Kaitlin Ericksen*
- [ ] Lance Lucas — *✓ MATCHES: Lance Lucas (Attorney, not Adjuster)*
- [ ] Liberty Mutual adjuster — *IGNORED - unnamed entity*
- [ ] Unnamed adjuster — *IGNORED - unnamed entity*
- [ ] Unnamed workers' compensation adjuster — *IGNORED - unnamed entity*
- [ ] workers' compensation adjuster (Liberty Mutual) — *IGNORED - generic term*

### Attorney (7 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Defense Counsel — *IGNORED - generic term*
- [ ] Lance Lucas, Esq. — *✓ MATCHES: Lance Lucas*
- [ ] Sarena — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Sarena M. Tuttle — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Taylor Wood — *✓ MATCHES: Dr. Taylor Jesse Wood (licensed KY doctor), not Attorney*
- [ ] W. Bryce Koon, Esq. — *✓ MATCHES: Bryce Koon (WHALEY ATTORNEY, not Attorney)*

### Client (1 consolidated)
- [ ] Shannon Lankswert — *✓ MATCHES: Shannon Lankswert*

### Defendant (2 consolidated)
- [ ] UPS — *✓ MATCHES: UPS*
- [ ] United Parcel Service (UPS) — *✓ MATCHES: UPS*

### Insurer (5 consolidated)
- [ ] Liberty Mutual — *✓ MATCHES: Liberty Mutual Insurance Company*
- [ ] Liberty Mutual Claims — *IGNORED - department*
- [ ] Liberty Mutual Insurance — *✓ MATCHES: Liberty Mutual Insurance Company*
- [ ] Liberty Mutual Workers' Compensation — *✓ MATCHES: Liberty Mutual Workers' Compensation*
- [ ] Workers' compensation carrier (unnamed) — *IGNORED - unnamed entity*

### LawFirm (3 consolidated)
- [ ] LUCAS & DIETZ, PLLC — *✓ MATCHES: LUCAS & DIETZ, PLLC*
- [ ] Lucas Dietz Law — *✓ MATCHES: LUCAS & DIETZ, PLLC*
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### Lien (1 consolidated)
- [ ] Anthem Blue Cross Blue Shield — *✓ MATCHES: Anthem Blue Cross Blue Shield*

### LienHolder (1 consolidated)
- [ ] Anthem Blue Cross Blue Shield — *✓ MATCHES: Anthem Blue Cross Blue Shield*

### MedicalProvider (11 consolidated)
- [ ] Advanced Injury Rehab — *✓ MATCHES: Advanced Injury Rehab*
- [ ] Physical Therapy — *✓ MATCHES: Advanced Injury Rehab*
- [ ] Center Metro Pain Relief — *✓ MATCHES: Center Metro Pain Relief*
- [ ] Concentra Medical Center — *✓ MATCHES: Concentra Medical Center*
- [ ] Concentra Medical Center — *✓ MATCHES: Concentra Medical Center*
- [ ] Flaget Memorial Hospital — *✓ MATCHES: Flaget Memorial Hospital*
- [ ] Flaget Memorial Hospital (hospital) — *✓ MATCHES: Flaget Memorial Hospital*
- [ ] Memphis CBO — *IGNORED - out of state*
- [ ] Center Metro Pain Relief — *IGNORED - variant of Center Metro Pain Relief*
- [ ] The Injury Centers — *✓ MATCHES: The Injury Centers*
- [ ] The Injury Centers — *✓ MATCHES: The Injury Centers*

### Organization (4 consolidated)
- [ ] LiMu — *IGNORED - Liberty Mutual abbreviation*
- [ ] UPS — *✓ MATCHES: UPS (Defendant, not Organization)*
- [ ] UPS Risk Management — *✓ MATCHES: ESIS Risk Management*
- [ ] United Parcel Service (UPS) — *✓ MATCHES: UPS (Defendant, not Organization)*

### Vendor (2 consolidated)
- [ ] Datavant (Smart Request) — *✓ MATCHES: DataVant (Vendor, not Vendor)*
- [ ] Smart Request (Datavant) — *✓ MATCHES: DataVant (Vendor, not Vendor)*

### WCClaim (11 consolidated)
- [ ] Shannon Lankswert (WC80D-H07503) — *IGNORED - claim description*
- [ ] Shannon Lankswert - WC Claim — *IGNORED - claim description*
- [ ] Shannon Lankswert WC Claim (DOI 02/07/2025) — *IGNORED - claim description*
- [ ] Shannon-Lankswert-WC-02-07-2025 — *IGNORED - case name*
- [ ] Shannon-Lankswert-WC-02-07-2025 (WC80D-H07503) — *IGNORED - case name*
- [ ] WC Claim DOI 02/07/2025 — *IGNORED - claim description*
- [ ] WC claim - Shannon Lankswert — *IGNORED - claim description*
- [ ] WC80D-807503 — *IGNORED - claim number*
- [ ] WC80D-H07503 (Shannon Lankswert) — *IGNORED - claim number*
- [ ] Workers' Compensation claim — *IGNORED - generic term*
- [ ] Workers' Compensation claim (Shannon Lankswert) — *IGNORED - claim description*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships