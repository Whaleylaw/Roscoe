# Relationship Review: Jerome-Hedinger-Premise-DB-10-24-2023

**Total Episodes:** 196

**Total Proposed Relationships:** 793


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (3)
- Baptist Health Breckenridge Imaging ER & Urgent Care
- Jefferson Animal Hospital & Regional Emergency Center (hospital)
- Ultimate  MD

### Insurance Claims (1)
- **BIClaim**: None

### Liens (1)
- Aetna Life Insurance Company ($15.09)

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (11 consolidated)
- [ ] Adjuster — *IGNORED - generic term*
- [ ] BI adjuster — *IGNORED - generic term*
- [ ] David Ryan — *✓ MATCHES: David Ryan (from adjusters)*
- [ ] David Ryan, LVM — *✓ MATCHES: David Ryan (from adjusters)*
- [ ] Jerome's adjuster — *IGNORED - generic reference*
- [ ] Jerry's adjuster — *IGNORED - generic reference*
- [ ] Jessica L. Paolini — *✓ MATCHES: Jessica L. Paolini (from adjusters)*
- [ ] State Farm adjuster — *IGNORED - generic term*
- [ ] State Farm adjuster supervisor — *IGNORED - generic reference*
- [ ] at-fault adjuster — *IGNORED - generic term*
- [ ] unspecified adjuster — *IGNORED - generic term*

### Attorney (14 consolidated)
- [ ] Betsy R. Catron — *✓ MATCHES: Betsy R. Catron*
- [ ] David T. Klapheke — *✓ MATCHES: David Klapheke*
- [ ] Elizabeth Harbolt — *✓ MATCHES: Elizabeth Harbolt (from attorneys - paralegal)*
- [ ] Jessica Poalini — *✓ MATCHES: Jessica L. Paolini (from adjusters)*
- [ ] Linda Bandy — *✓ MATCHES: Linda Bandy (from attorneys)*
- [ ] Opposing counsel — *IGNORED - generic term*
- [ ] Paige E. Hornback — *✓ MATCHES: Paige E. Hornback (from attorneys)*
- [ ] Plaintiff's counsel — *IGNORED - generic term*
- [ ] Sarena — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Sarena (The Whaley Law Firm) — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Sarena M. Tuttle — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Serena — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] W. Bryce Koon, Esq. — *✓ MATCHES: Bryce Koon (WHALEY ATTORNEY, not Attorney)*
- [ ] Whaley, Aaron Gregory — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*

### BIClaim (4 consolidated)
- [ ] 17N8360G8 — *IGNORED - claim number*
- [ ] Bodily Injury (BI) — *IGNORED - generic term*
- [ ] Bodily Injury claim (State Farm) — *IGNORED - generic claim reference*
- [ ] Premise Liability (Dog Bite) Complaint — *IGNORED - case caption*

### Client (1 consolidated)
- [ ] Jerome Hedinger — *✓ MATCHES: Jerome Hedinger*

### Court (10 consolidated)
- [ ] Case 23-M-011470 (Jefferson County District Court) — *✓ MATCHES: Jefferson County District Court*
- [ ] Criminal Court — *IGNORED - generic term*
- [ ] District Court — *IGNORED - generic term*
- [ ] Jefferson 24-CI-006943 — *✓ MATCHES: Jefferson County Circuit Court, Division I*
- [ ] Jefferson Circuit Court (Circuit 24) — *✓ MATCHES: Jefferson County Circuit Court, Division I*
- [ ] Jefferson County (24-CI-006943) — *✓ MATCHES: Jefferson County Circuit Court, Division I*
- [ ] Jefferson County (Docket 24-CI-006943) — *✓ MATCHES: Jefferson County Circuit Court, Division I*
- [ ] Jefferson County Circuit Court — *✓ MATCHES: Jefferson County Circuit Court, Division I*
- [ ] Jefferson County District Court - Case 23-P-403711-1 — *✓ MATCHES: Jefferson County District Court*
- [ ] Kentucky Court of Justice — *✓ MATCHES: Kentucky Court Of Justice*

### Defendant (15 consolidated)
- [ ] 432 Atwood, LLC — *IGNORED - defendant name*
- [ ] 432 Atwood, et al. — *IGNORED - case caption*
- [ ] Atwood LLC — *IGNORED - defendant name*
- [ ] Brown — *IGNORED - last name only*
- [ ] Brown, Dahlyn — *IGNORED - defendant name*
- [ ] Brown, Dahlyn (et al) — *IGNORED - case caption*
- [ ] Brown/Burden — *IGNORED - defendant names*
- [ ] Burden — *IGNORED - last name only*
- [ ] DC Atwood — *IGNORED - defense counsel reference*
- [ ] Dahlyn Brown — *IGNORED - defendant name*
- [ ] Draylen Round — *IGNORED - defendant name*
- [ ] Jessica Burden — *IGNORED - defendant name*
- [ ] Mr. Brown — *IGNORED - defendant reference*
- [ ] defendant (neighbor with pitbull) — *IGNORED - generic reference*
- [ ] homeowner — *IGNORED - generic term*

### Insurer (7 consolidated)
- [ ] Aetna Life Insurance Company — *✓ MATCHES: Aetna Life Insurance Company (from lienholders)*
- [ ] Homeowners insurance company — *IGNORED - generic term*
- [ ] State Farm — *✓ MATCHES: State Farm Insurance Company*
- [ ] State Farm - BK — *✓ MATCHES: State Farm Insurance Company*
- [ ] State Farm Fire & Casualty Company — *✓ MATCHES: State Farm Insurance Company (from insurers)*
- [ ] State Farm Fire Claims — *✓ MATCHES: State Farm Insurance Company*
- [ ] homeowner's insurer — *IGNORED - generic term*

### LawFirm (2 consolidated)
- [ ] Dinsmore & Shohl LLP — *✓ MATCHES: Dinsmore & Shohl LLP*
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### Lien (1 consolidated)
- [ ] Aetna Life Insurance Company — *✓ MATCHES: Aetna Life Insurance Company*

### LienHolder (1 consolidated)
- [ ] Aetna Life Insurance Company — *✓ MATCHES: Aetna Life Insurance Company*

### MedicalProvider (12 consolidated)
- [ ] Baptist Health Breckenridge Imaging ER & Urgent Care — *✓ MATCHES: Baptist Health Breckenridge Imaging ER & Urgent Care*
- [ ] Dr Jeff Stidam — *✓ MATCHES: Dr. Jeffrey M. Stidam (licensed KY doctor, valid MedicalProvider)*
- [ ] Dr Lazlo Maak — *✓ MATCHES: Dr. Lazlo T. Maak (licensed KY doctor, valid MedicalProvider)*
- [ ] Dr. Haney — *✓ MATCHES: Dr. William H. Haney (licensed KY doctor, valid MedicalProvider)*
- [ ] Dr. Haney Office — *✓ MATCHES: Dr. William H. Haney (licensed KY doctor, valid MedicalProvider)*
- [ ] Dr. William H. Haney, M.D. — *✓ MATCHES: Dr. William H. Haney (licensed KY doctor, valid MedicalProvider)*
- [ ] Jefferson Animal Hospital & Regional Emergency Center — *✓ MATCHES: Jefferson Animal Hospital & Regional Emergency Center*
- [ ] Ultimate  MD — *✓ MATCHES: Ultimate  MD*
- [ ] William H. Haney, M.D. (Dr. Haney's Office) — *✓ MATCHES: Dr. William H. Haney (licensed KY doctor, valid MedicalProvider)*
- [ ] client's physicians — *IGNORED - generic term*
- [ ] psychiatrist — *IGNORED - generic term*
- [ ] therapist (PTSD specialist) — *IGNORED - generic term*

### Organization (3 consolidated)
- [ ] 432 Atwood LLC — *IGNORED - defendant organization*
- [ ] Kentucky Court of Justice eFiling System — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Rawlings Company — *✓ MATCHES: Rawlings Company (from lienholders)*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships