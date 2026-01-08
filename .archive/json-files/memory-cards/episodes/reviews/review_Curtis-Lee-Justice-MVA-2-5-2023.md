# Relationship Review: Curtis-Lee-Justice-MVA-2-5-2023

**Total Episodes:** 226

**Total Proposed Relationships:** 518


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (11 consolidated)
- [ ] Adjuster from Trexis Insurance Corporation — *✓ MATCHES: Trexis Insurance Corporation (from insurers)*
- [ ] Coleen Thea Madayag — *✓ MATCHES: Coleen Madayag (WHALEY STAFF → should be CaseManager, not Adjuster)*
- [ ] Emmy Tran — *? NEW*
- [ ] Janeth — *? NEW*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Adjuster)*
- [ ] Ms. Yaneth — *? NEW*
- [ ] PIP Adjuster — *IGNORED - generic term*
- [ ] PIP adjuster (unspecified) — *IGNORED - generic term*
- [ ] Peter Longo — *✓ MATCHES: Peter Longo (from directory)*
- [ ] Stacey Giehl — *? NEW*
- [ ] Yaneth Hernandez — *? NEW*

### Attorney (7 consolidated)
- [ ] Aaron G. Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Aries — *✓ MATCHES: Aries Penaflor (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Aries Paul Peñaflor — *✓ MATCHES: Aries Penaflor (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Coleen Thea Ferry Madayag — *✓ MATCHES: Coleen Madayag (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessica — *✓ MATCHES: Jessica Bottorff (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessica Bottorff — *✓ MATCHES: Jessica Bottorff (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*

### BIClaim (1 consolidated)
- [ ] Bodily Injury claim (Clearcover) — *✓ MATCHES: Clearcover (from insurers)*

### Client (2 consolidated)
- [ ] Curtis Lee Justice — *✓ MATCHES: Curtis Lee Justice (from clients)*
- [ ] Mr Curtis — *✓ MATCHES: Curtis Lee Justice (from clients)*

### Insurer (3 consolidated)
- [ ] Clear Cover — *✓ MATCHES: Clearcover*
- [ ] Clear Cover Insurance — *✓ MATCHES: Clearcover*
- [ ] Trexis Insurance Corporation — *✓ MATCHES: Trexis Insurance Corporation (from insurers)*

### LawFirm (2 consolidated)
- [ ] AGW — *✓ MATCHES: The Whaley Law Firm*
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### Lien (4 consolidated)
- [ ] Final lien — *IGNORED - generic term*
- [ ] Lien from Rawlings — *IGNORED - generic term*
- [ ] health lien — *IGNORED - generic term*
- [ ] health lien ledger — *IGNORED - generic term*

### LienHolder (2 consolidated)
- [ ] Rawlings — *✓ MATCHES: Rawlings Company (from lienholders)*
- [ ] The Rawlings Company (WellCare) — *✓ MATCHES: Rawlings Company (from lienholders)*

### MedicalProvider (16 consolidated)
- [ ] Central Kentucky Radiology — *✓ MATCHES: Central Kentucky Radiology*
- [ ] King's Eye Care — *IGNORED - generic term*
- [ ] H2 Health (Berea, KY) — *✓ MATCHES: H2 Health- Berea, KY*
- [ ] UC Health — *✓ MATCHES: H2 Health- Berea, KY*
- [ ] King's Eye Care — *✓ MATCHES: King's Eye Care*
- [ ] RAWLINGS/WELLCARE — *IGNORED - this is a lienholder, not medical provider*
- [ ] SE ER PHYS — *✓ MATCHES: Southeastern Emergency Physician Services*
- [ ] CHI Saint Joseph Health — *✓ MATCHES:  Saint Joseph Berea*
- [ ] Saint Joseph Berea — *✓ MATCHES:  Saint Joseph Berea*
- [ ] Sound Physicians — *✓ MATCHES: Sound Physicians*
- [ ] Southeastern Emergency Services, LLC — *✓ MATCHES: Southeastern Emergency Physician Services*
- [ ] Spin Clinic — *IGNORED - generic term*
- [ ] TeamHealth — *✓ MATCHES: TeamHealth*
- [ ] White House Clinics Berea — *✓ MATCHES: White House Clinics Berea Berea*
- [ ] White House Clinics Berea (Berea) — *✓ MATCHES: White House Clinics Berea Berea*
- [ ] medical providers — *IGNORED - generic term*

### Organization (5 consolidated)
- [ ] Alcoa — *IGNORED - generic organization*
- [ ] Ciox Health — *✓ MATCHES: Ciox Health (from organizations)*
- [ ] Louisville Accident Lawyer (Filevine) — *IGNORED - software reference*
- [ ] SREscalations — *? NEW*
- [ ] Trexis — *✓ MATCHES: Trexis Insurance Corporation (from insurers)*  

### PIPClaim (10 consolidated)
- [ ] KY PIP APP REV'D — *IGNORED - generic term*
- [ ] Kentucky no-fault PIP application — *IGNORED - generic term*
- [ ] PIP (Personal Injury Protection) - Trexis — *IGNORED - generic claim reference*
- [ ] PIP claim — *IGNORED - generic term*
- [ ] PIP claim #755905 — *IGNORED - generic claim number*
- [ ] PIP claim (Trexis Insurance Corporation) — *✓ MATCHES: Trexis Insurance Corporation (from insurers)*
- [ ] PIP claim (unspecified) — *IGNORED - generic term*
- [ ] PIP claim for Curtis Justice — *IGNORED - generic claim reference*
- [ ] Personal Injury Protection claim — *IGNORED - generic term*
- [ ] Trexis PIP — *IGNORED - generic claim reference*

### Vendor (5 consolidated)
- [ ] Ciox — *✓ MATCHES: Ciox Health (from organizations)*
- [ ] Ciox Health — *✓ MATCHES: Ciox Health (from organizations)*
- [ ] RC Fax — *IGNORED - fax service*
- [ ] RCFax (8599861002@rcfax.com) — *IGNORED - fax service*
- [ ] vinesign — *IGNORED - software reference*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships