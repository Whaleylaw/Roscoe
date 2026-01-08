# Relationship Review: Abby-Sitgraves-MVA-7-13-2024

**Total Episodes:** 93

**Total Proposed Relationships:** 332


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (3)
- Foundation Radiology (radiology)
- Jewish Hospital (hospital)
- UofL Physicians - Orthopedics (orthopedic)

### Insurance Claims (1)
- **PIPClaim**: National Indemnity Company
  - Adjuster: Jordan Bahr

### Liens (1)
- Key Benefit Administrators ($358.51)

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Review these and decide which to map/create/ignore)*


### Adjuster (1 unique)
- [ ] Jordan Bahr — *✓ EXISTS*

### Attorney (18 unique)
- [ ] Aaron Gregory Whaley — *? NEW*
- [ ] Amy Scott — *? NEW*
- [ ] Bruce Anderson — *? NEW*
- [ ] Bryan Davenport — *? NEW*
- [ ] Bryce Cotton — *? NEW*
- [ ] Bryce Koon — *? NEW*
- [ ] Derek A. Harvey Jr. — *? NEW*
- [ ] Derek Anthony Harvey — *? NEW*
- [ ] Jessa — *? NEW*
- [ ] John Doyle — *? NEW*
- [ ] Marshall Rowland — *? NEW*
- [ ] Sam Leffert — *? NEW*
- [ ] Samuel Robert Leffert — *? NEW*
- [ ] Sarena Tuttle — *? NEW*
- [ ] Seth Gladstein — *? NEW*
- [ ] W. Bryce Koon — *? NEW*
- [ ] W. Bryce Koon, Esq. — *? NEW*
- [ ] Whaley, Aaron Gregory — *? NEW*

### Client (2 unique)
- [ ] Abby Sitgraves — *? NEW*
- [ ] Nayram Adadevoh — *? NEW*

### Court (5 unique)
- [ ] Jefferson (25-CI-000133) — *? NEW*
- [ ] Jefferson 25-CI-00133 — *? NEW*
- [ ] Jefferson Circuit Court — *? NEW*
- [ ] Jefferson County — *? NEW*
- [ ] Jefferson County (25-CI-00133) — *? NEW*

### Defendant (7 unique)
- [ ] CAAL WORLDWIDE, INC. — *? NEW*
- [ ] CAAL Worldwide — *? NEW*
- [ ] CAAL Worldwide, Inc. — *? NEW*
- [ ] Caal Worldwide — *? NEW*
- [ ] Caal Worldwide, Inc. — *? NEW*
- [ ] Unknown Driver — *? NEW*
- [ ] limousine company — *? NEW*

### Insurer (4 unique)
- [ ] Kentucky Farm Bureau (KFB) — *? NEW*
- [ ] Kentucky One Health — *? NEW*
- [ ] National Indemnity Company — *✓ EXISTS*
- [ ] State Farm — *? NEW*

### LawFirm (7 unique)
- [ ] BDB Law (bdblawky.com) — *? NEW*
- [ ] Blackburn Domene & Burchett, PLLC — *? NEW*
- [ ] Bryan Davenport — *? NEW*
- [ ] Carlisle Law — *? NEW*
- [ ] Law Office of Bryan B. Davenport, P.C. — *? NEW*
- [ ] The Whaley Law Firm — *? NEW*
- [ ] Whaley Law Firm — *? NEW*

### Lien (1 unique)
- [ ] Key Benefit Administrators — *✓ EXISTS*

### MedicalProvider (4 unique)
- [ ] Foundation Radiology — *✓ EXISTS*
- [ ] Jewish Hospital — *✓ EXISTS*
- [ ] UofL Health - Mary & Elizabeth Hospital — *? NEW*
- [ ] UofL Physicians - Orthopedics — *✓ EXISTS*

### Organization (3 unique)
- [ ] Kentucky Court of Justice — *? NEW*
- [ ] Kentucky Court of Justice (eFiling system) — *? NEW*
- [ ] Kentucky Court of Justice eFiling system — *? NEW*

### PIPClaim (3 unique)
- [ ] PIP - National Indemnity Company — *? NEW*
- [ ] PIP claim - National Indemnity Company — *? NEW*
- [ ] PIPClaim: National Indemnity Company — *? NEW*

### UMClaim (2 unique)
- [ ] Uninsured motorist demand(s) — *? NEW*
- [ ] uninsured motorist claim — *? NEW*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships

