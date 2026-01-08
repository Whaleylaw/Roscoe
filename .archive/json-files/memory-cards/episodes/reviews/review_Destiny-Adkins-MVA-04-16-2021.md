# Relationship Review: Destiny-Adkins-MVA-04-16-2021

**Total Episodes:** 263

**Total Proposed Relationships:** 1376


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (2)
- Norton Audubon Hospital (hospital)
- University Of Louisville Hospital Radiology (hospital)

### Insurance Claims (1)
- **BIClaim**: Allstate Insurance
  - Adjuster: Patrice Gaines

### Liens (1)
- Conduent

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (3 consolidated)
- [ ] Campbell Ewen — *✓ MATCHES: A. Campbell Ewen (from attorneys)*
- [ ] Hineman — *IGNORED - attorney name only*
- [ ] Patrice Gaines — *✓ MATCHES: Patrice Gaines*

### Attorney (23 consolidated)
- [ ] A. Campbell Ewen — *✓ MATCHES: A. Campbell Ewen (from attorneys)*
- [ ] A. Ewen — *✓ MATCHES: A. Campbell Ewen (from attorneys)*
- [ ] Aaron Whaley, Esquire — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Beth Alexander — *IGNORED - attorney name only*
- [ ] Betsy R. Catron — *✓ MATCHES: Betsy R. Catron*
- [ ] DC Ewen — *IGNORED - defense counsel abbreviation*
- [ ] DC Nail — *IGNORED - defense counsel abbreviation*
- [ ] DC Stempien — *IGNORED - defense counsel abbreviation*
- [ ] DC Turner — *IGNORED - defense counsel abbreviation*
- [ ] Daniel Gumm — *✓ MATCHES: Daniel Gumm (from attorneys)*
- [ ] Eric S. Rice — *✓ MATCHES: Eric Rice (from attorneys)*
- [ ] Ewen, Allen Campbell — *✓ MATCHES: A. Campbell Ewen (from attorneys)*
- [ ] Hon. Thomas J. Knopf (Ret.) — *✓ MATCHES: Hon. Thomas J. Knopf (Ret.) (from mediators)*
- [ ] Kinney, Kevin Paul — *✓ MATCHES: Kevin Kinney (from attorneys)*
- [ ] Krista Rice — *✓ MATCHES: Krista Rice (from attorneys)*
- [ ] Mr. Stempien — *✓ MATCHES: Brian Stempien (from attorneys)*
- [ ] Mr. Turner's Counsel — *IGNORED - generic reference*
- [ ] Paul Klapheke — *IGNORED - attorney name only*
- [ ] Sarena M. Tuttle — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Sarena Whaley — *✓ MATCHES: Sarena Whaley (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Stempien — *✓ MATCHES: Brian Stempien (from attorneys)*
- [ ] Stempien, Brian David — *✓ MATCHES: Brian Stempien (from attorneys)*
- [ ] W. Bryce Koon, Esq. — *✓ MATCHES: Bryce Koon (WHALEY ATTORNEY, not Attorney)*

### BIClaim (4 consolidated)
- [ ] Allstate Insurance — *✓ MATCHES: Allstate Insurance*
- [ ] Allstate Insurance (Adjuster: Patrice Gaines) — *✓ MATCHES: Allstate Insurance*
- [ ] Allstate Insurance BI claim — *✓ MATCHES: Allstate Insurance*
- [ ] BIClaim - Allstate Insurance — *✓ MATCHES: Allstate Insurance*

### Client (6 consolidated)
- [ ] Destiny Adkins — *✓ MATCHES: Destiny Adkins*
- [ ] Downs — *✓ MATCHES: Juanita Nicole Downs*
- [ ] Juanita Downs — *✓ MATCHES: Juanita Nicole Downs*
- [ ] Juanita Nicole Downs — *✓ MATCHES: Juanita Nicole Downs*
- [ ] Mr. Stempien — *✓ MATCHES: Brian Stempien (from attorneys)*
- [ ] Mr. Turner — *IGNORED - defendant reference*

### Court (22 consolidated)
- [ ] CourtNet Envelope 7240362 — *IGNORED - system reference*
- [ ] District Court — *IGNORED - generic court reference*
- [ ] District Court Administration — *IGNORED - generic reference*
- [ ] Hon. Eric Haner — *✓ MATCHES: Hon. Eric Haner (from circuit_judges)*
- [ ] Jeff Cir Crt — *✓ MATCHES: Jefferson County Circuit Court, Division I*
- [ ] Jefferson Circuit Court — *✓ MATCHES: Jefferson County Circuit Court, Division I*
- [ ] Jefferson County (22-CI-002878) — *✓ MATCHES: Jefferson County Circuit Court, Division I*
- [ ] Jefferson County Circuit Court Clerk — *✓ MATCHES: Jefferson County Circuit Court, Division I*
- [ ] Jefferson County Court — *✓ MATCHES: Jefferson County Circuit Court, Division I*
- [ ] Jefferson County OCCC Video Department — *IGNORED - department reference*
- [ ] Jennifer Miles (KY Courts) — *IGNORED - staff reference*
- [ ] Judge Hon. Thomas Knopf — *✓ MATCHES: Hon. Thomas J. Knopf (Ret.) (from mediators)*
- [ ] Kentucky Court of Justice — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Kentucky Court of Justice eFiling System — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Kentucky Courts — *IGNORED - generic reference*
- [ ] Kentucky Courts (CourtNet) — *IGNORED - system reference*
- [ ] Kentucky State Office of the Administrative Office of the Courts — *IGNORED - administrative office*
- [ ] Kentucky courts (Mary Stephenson) — *IGNORED - staff reference*
- [ ] Motion Hour (judge's order) — *IGNORED - hearing reference*
- [ ] Motion hearing (Sept 6, 2022) — *IGNORED - hearing reference*
- [ ] judge (unnamed) — *IGNORED - generic term*
- [ ] unspecified court — *IGNORED - generic term* 
 
### Defendant (16 consolidated)
- [ ] DC Nail — *✓ MATCHES: Stephanie Nail (from defendants)*
- [ ] Def Nail — *✓ MATCHES: Stephanie Nail (from defendants)*
- [ ] Def Turner — *✓ MATCHES: Demetrius E. Turner (from defendants)*
- [ ] Defendant (hearing April 15, 2021) — *IGNORED - generic reference*
- [ ] Defendant Turner — *✓ MATCHES: Demetrius E. Turner (from defendants)*
- [ ] Defendants (DCs) — *IGNORED - generic term*
- [ ] Demetrius E. Turner — *✓ MATCHES: Demetrius E. Turner (from defendants)*
- [ ] Mr. Turner — *✓ MATCHES: Demetrius E. Turner (from defendants)*
- [ ] NAIL, STEPHANIE M. ET AL — *IGNORED - case caption format*
- [ ] Nail — *✓ MATCHES: Stephanie Nail (from defendants)*
- [ ] Nail, Stephanie M. — *✓ MATCHES: Stephanie Nail (from defendants)*
- [ ] Nail, et al. — *IGNORED - case caption format*
- [ ] Stephanie M. Nail — *✓ MATCHES: Stephanie Nail (from defendants)*
- [ ] Turner — *IGNORED - last name only, ambiguous*
- [ ] Unk Driver — *IGNORED - unknown driver reference*
- [ ] defense (unnamed) — *IGNORED - generic term*

### Insurer (3 consolidated)
- [ ] Allstate — *✓ MATCHES: Allstate Insurance*
- [ ] Allstate Insurance — *✓ MATCHES: Allstate Insurance*
- [ ] Defendant's insurance company — *IGNORED - generic reference*

### LawFirm (9 consolidated)
- [ ] AW & Assoc Franklin — *IGNORED - abbreviation/office reference*
- [ ] Adkins & Downs — *IGNORED - client names, not law firm*
- [ ] Ewen and Kinney — *✓ MATCHES: Ewen & Kinney, PLLC*
- [ ] Rice Gumm Law — *✓ MATCHES: Rice Gumm, PLLC (from lawfirms)*
- [ ] Rice Gumm, PLLC — *✓ MATCHES: Rice Gumm, PLLC (from lawfirms)*
- [ ] Stempien — *✓ MATCHES: Brian Stempien (from attorneys)*
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*
- [ ] Travis Herbert & Stempien, PLLC — *✓ MATCHES: Travis Herbert & Stempien, PLLC (from lawfirms)*
- [ ] Whaley & Whaley — *IGNORED - informal name variant*

### MedicalProvider (2 consolidated)
- [ ] University Of Louisville Hospital Radiology — *✓ MATCHES: Norton Audubon Hospital*
- [ ] Norton Audubon Hospital — *✓ MATCHES: Norton Audubon Hospital*

### Organization (9 consolidated)
- [ ] Adkins & Downs — *IGNORED - client names, not organization*
- [ ] DC Rice Office — *IGNORED - law firm reference*
- [ ] Jeff Co. Sheriff — *✓ MATCHES: Jefferson County Sheriff's Office (from organizations)*
- [ ] Jefferson County OCC Video Department — *IGNORED - court department*
- [ ] Kentuckiana Court Reporters — *✓ MATCHES: Kentuckiana Court Reporters (from vendors)*
- [ ] Kentuckiana Court Reporters / Kentucky Court Reporters — *✓ MATCHES: Kentuckiana Court Reporters (from vendors)*
- [ ] Kentucky Court of Justice — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Kentucky Court of Justice eFiling system — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] United States Postal Service — *✓ MATCHES: United States Postal Service (from organizations)*

### Vendor (2 consolidated)
- [ ] Kentuckiana Court Reporters — *✓ MATCHES: Kentuckiana Court Reporters*
- [ ] Paul Klapheke — *IGNORED - person name only*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships