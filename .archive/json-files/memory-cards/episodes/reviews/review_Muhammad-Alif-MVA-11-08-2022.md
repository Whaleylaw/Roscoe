# Relationship Review: Muhammad-Alif-MVA-11-08-2022

**Total Episodes:** 600

**Total Proposed Relationships:** 2648


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (18)
- Aptiva Health Health
- Axon Medical Centers
- Chiufang Hwang M.D.
- Cutting Edge Orthopedics
- Innovation Open MRI
- Physical Therapy
- Lynn Family Sports & Vision Training - TBI & Concussion Therapy
- Mark Lynn & Associates
- Mayo Spine Clinic
- Modern Chiropractic And Injury Care (chiropractic)
- Norton Community Medical Associates
- Norton Leatherman Spine
- Neurology-Downtown (neurology)
- Norton Neurosciences and Spine Rehabilitation Center (physical therapy)
- Parkridge Medical Center
- Radiology Alliance PC (Infinity Management)
- Spring Creek Emergency Phy
- Starlite Chiropractic (chiropractic)

### Insurance Claims (4)
- **BIClaim**: West Bend Mutual Insurance
  - Adjuster: Ashley Becerra
- **PIPClaim**: Farmers Insurance
  - Adjuster: Michael Santos
- **PIPClaim**: Farmers Insurance
  - Adjuster: Michael Santos
- **PIPClaim**: USAA Insurance Company

### Liens (6)
- ASP Cares
- Optum ($1,707.00)
- Plano Surgical Hospital Funding LLC ($2,553.70)
- None ($25,763.75)
- None
- None

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (9 consolidated)
- [ ] Ashley Becerra — *✓ MATCHES: Ashley Becerra*
- [ ] Chevan Douglas — *✓ MATCHES: Chevan Douglas*
- [ ] **Ryan Gorelick** — *IGNORED - defense adjuster (West Bend Mutual)*
      ↳ _Gorelick_
      ↳ _RGorlick (RGorlick@wbmi.com)_
- [ ] Michael Santos — *✓ MATCHES: Michael Santos*
- [ ] Natasha Fortune — *✓ MATCHES: Natasha Fortune*
- [ ] Sarena Tuttle — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Adjuster)*
- [ ] Unnamed adjuster — *IGNORED - generic reference*

### Attorney (27 consolidated)
- [ ] Aaron G. Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Ashley K. Brown — *✓ MATCHES: Dr. Ashley Brown (licensed KY doctor), not Attorney*
- [ ] Attorney (drafting) — *IGNORED - generic reference to staff attorney*
- [ ] Betsy R. Catron — *✓ MATCHES: Betsy R. Catron*
- [ ] Bryce Koon — *✓ MATCHES: Bryce Koon (WHALEY ATTORNEY, not Attorney)*
- [ ] Christianna A. Livas — *IGNORED - defense attorney*
- [ ] Deborah Jackson — *✓ MATCHES: Deborah Jackson (from directory)*
- [ ] George B. Hocker — *✓ MATCHES: George B. Hocker*
- [ ] Graham D. Barth — *IGNORED - defense attorney*
- [ ] Harry O'Donnell — *IGNORED - defense attorney*
- [ ] Jared M. Hudson — *✓ MATCHES: Jared M. Hudson*
- [ ] Jeanette L. Jayne — *IGNORED - defense attorney*
- [ ] Jessica Bottorff — *✓ MATCHES: Jessica Bottorff (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jillian D. House — *✓ MATCHES: Jillian D. House*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Kaylee F. Collins — *✓ MATCHES: Kaylee F. Collins*
- [ ] Lacy T. Smith — *IGNORED - defense attorney*
- [ ] **Maxwell D. Smith** — *✓ MATCHES: Maxwell D. Smith*
      ↳ _Max D. Smith_
- [ ] Misty Harmon — *IGNORED - defense attorney*
- [ ] Ryan J. McElroy — *✓ MATCHES: Ryan J. McElroy*
- [ ] Sarena — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Sarena M. Tuttle — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] William J. Barker, II — *✓ MATCHES: Dr. William M. Baker (licensed KY doctor), not Attorney*
- [ ] agwhaley@whaleylawfirm.com — *IGNORED - email address*
- [ ] bryce@whaleylawfirm.com — *IGNORED - email address*
- [ ] kaylee.collins@whtlaw.com — *IGNORED - email address*
- [ ] max.smith@whtlaw.com — *IGNORED - email address*

### BIClaim (6 consolidated)
- [ ] **West Bend Mutual Insurance** — *✓ MATCHES: West Bend Mutual Insurance*
      ↳ _AP92071_
      ↳ _BI #92071_
      ↳ _BI Claim AP92071_
      ↳ _West Bend Mutual Insurance - AP92071_
- [ ] BI insurance (NY PR search) — *IGNORED - generic research note*
- [ ] Bodily Injury Claim - Muhammad Alif & Kendra Fogle (12/10/2022) — *IGNORED - claim description, not entity*

### Client (4 consolidated)
- [ ] **Muhammad Alif** — *✓ MATCHES: Muhammad Alif*
      ↳ _ALIF, MUHAMMAD_
- [ ] Kendra Fogle — *IGNORED - passenger in separate accident, not our client*
- [ ] Sarena — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Client)*

### Court (7 consolidated)
- [ ] CourtNet (envelope 6555341) — *IGNORED - filing system reference*
- [ ] District Court (Division 7) — *IGNORED - this is Jefferson County Circuit Court, Division VII (matched below)*
- [ ] **Jefferson County Circuit Court, Division VII** — *✓ MATCHES: Jefferson County Circuit Court, Division VII*
      ↳ _Jeff Cir Div 7_
- [ ] Jefferson Circuit Court (Kentucky Court of Justice) — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Kentucky Court of Justice — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Kentucky Court of Justice eFiling system — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Pretrial Conference (NMO PTC) - telephonic, Aug 12, 2024 11:45 a.m. — *IGNORED - calendar event, not court entity*

### Defendant (5 consolidated)
- [ ] Defendant (defense) — *IGNORED - generic term*
- [ ] Drivers from Nov 8 and Dec 9 accidents — *IGNORED - generic reference*
- [ ] Harbor House Of Louisville — *✓ MATCHES: Harbor House Of Louisville*
- [ ] Jacquelyn B. Wickcliffe — *✓ MATCHES: Jacquelyn B. Wickcliffe*
- [ ] Wickliffe / WickCliffe — *IGNORED - variant already consolidated above*

### Insurer (8 consolidated)
- [ ] American Transit — *✓ MATCHES: American Transit Insurance*
- [ ] American Transit Insurance Company — *✓ MATCHES: American Transit Insurance*
- [ ] Farmers Insurance — *✓ MATCHES: Farmers Insurance*
- [ ] Insurer (unspecified) — *IGNORED - generic term*
- [ ] Progressive — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Casualty Insurance Company — *✓ MATCHES: Progressive Insurance Company*
- [ ] West Bend Mutual Insurance (West Bend Specialty) — *✓ MATCHES: West Bend Mutual Insurance*
- [ ] West Bend Mutual Insurance Company — *✓ MATCHES: West Bend Mutual Insurance*

### LawFirm (4 consolidated)
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*
- [ ] Ward, Hocker & Thornton, PLLC — *✓ MATCHES: Ward, Hocker & Thornton, PLLC*
- [ ] Whitehall/Hubbard — *IGNORED - defense law firm*
- [ ] whtlaw.com — *IGNORED - website reference*

### Lien (5 consolidated)
- [ ] ASP Cares — *✓ MATCHES: ASP Cares*
- [ ] Cutting Edge Orthopedics — *✓ MATCHES: Cutting Edge Orthopedics*
- [ ] Optum — *✓ MATCHES: Optum*
- [ ] Plano Surgical Hospital Funding LLC — *✓ MATCHES: Plano Surgical Hospital Funding LLC*
- [ ] medical lien — *IGNORED - generic term*

### LienHolder (3 consolidated)
- [ ] ASP Cares — *✓ MATCHES: ASP Cares*
- [ ] Optum — *✓ MATCHES: Optum*
- [ ] Plano Surgical Hospital Funding LLC — *✓ MATCHES: Plano Surgical Hospital Funding LLC*

### MedicalProvider (45 consolidated)
- [ ] Anointed Hands Injury Rehab — *✓ MATCHES: Anointed Hands Injury Rehab*
- [ ] Aptiva Health Health — *✓ MATCHES: Aptiva Health Health*
- [ ] Axon Medical Centers — *✓ MATCHES: Axon Medical Centers*
- [ ] Axon Medical Centers — *✓ MATCHES: Axon Medical Centers*
- [ ] Chiufang Hwang M.D. — *✓ MATCHES: Chiufang Hwang M.D.*
- [ ] Cutting Edge Hospital (Parkland, TN) — *IGNORED - this is Cutting Edge Orthopedics Surgery Center in TN, not UofL Health – Brown Cancer Center – Medical Oncology – UofL Hospital*
- [ ] Cutting Edge Orthopedics — *✓ MATCHES: Cutting Edge Orthopedics*
- [ ] Cutting Edge Orthopedics — *✓ MATCHES: Cutting Edge Orthopedics*
- [ ] Dr. Allen Starkey — *✓ MATCHES: Dr. Allen Starkey (licensed KY doctor, inactive)*
- [ ] Dr. Chris Stephens — *✓ MATCHES: Dr. Chris Stephens (licensed KY doctor, inactive)*
- [ ] Dr. Claude Fortin — *IGNORED - out of state provider*
- [ ] Dr. Fortin — *IGNORED - variant already handled above*
- [ ] Dr. Matt — *IGNORED - too generic*
- [ ] Dr. Matt DeGaetano — *IGNORED - out of state provider*
- [ ] **Dr. Richard Edelson (neuropsychologist)** — *✓ MATCHES: Dr. Richard Edelson (Expert, not MedicalProvider)*
      ↳ _Dr. Richard Edelson_
- [ ] Dr. Robert Van Boven — *IGNORED - out of state radiologist*
- [ ] Dr. Stephens — *IGNORED - variant already handled above*
- [ ] Dr. Steven Patton — *✓ MATCHES: Dr. Steven Patton (licensed KY doctor)*
- [ ] Dr. Van Boven — *IGNORED - variant already handled above*
- [ ] Dr. William Hwang, MD — *✓ MATCHES: Dr. William Hwang (licensed KY doctor, inactive)*
- [ ] Imaging — *IGNORED - out of state imaging center*
- [ ] Imaging — *IGNORED - variant already handled above*
- [ ] Healix Pathology, LLP — *IGNORED - out of state lab*
- [ ] Innovation Open MRI — *✓ MATCHES: Innovation Open MRI*
- [ ] Jeanne Bennett (psychologist) — *IGNORED - psychologist, not medical provider*
- [ ] KORT Physical Therapy - Shelbyville — *✓ MATCHES: KORT Physical Therapy - Shelbyville*
- [ ] Lynn Family Sports & Vision Training - TBI & Concussion Therapy — *✓ MATCHES: Lynn Family Sports & Vision Training - TBI & Concussion Therapy*
- [ ] Mariela Cruz — *IGNORED - admin staff, not provider*
- [ ] Mark Lynn & Associates — *✓ MATCHES: Mark Lynn & Associates*
- [ ] Mayo Spine Clinic — *✓ MATCHES: Mayo Spine Clinic*
- [ ] Modern Chiropractic And Injury Care — *✓ MATCHES: Modern Chiropractic And Injury Care*
- [ ] Neurology — *IGNORED - too generic*
- [ ] Norton Community Medical Associates — *✓ MATCHES: Norton Community Medical Associates*
- [ ] Norton Leatherman Spine — *✓ MATCHES: Norton Leatherman Spine*
- [ ] Neurology-Downtown — *✓ MATCHES: Neurology-Downtown*
- [ ] Norton Neurosciences and Spine Rehabilitation Center — *✓ MATCHES: Norton Neurosciences and Spine Rehabilitation Center*
- [ ] Norton Women & Children's Hospital — *✓ MATCHES: Norton Women's and Children's Hospital*
- [ ] Parkridge East Hospital — *IGNORED - this is Parkridge Medical Center in TN*
- [ ] Parkridge Medical Center — *✓ MATCHES: Parkridge Medical Center*
- [ ] Prime MRI — *IGNORED - out of state imaging center*
- [ ] Radiology Alliance PC — *✓ MATCHES: Radiology Alliance PC*
- [ ] Radiology Alliance PC (Infinity Management) — *✓ MATCHES: Radiology Alliance PC*
- [ ] Spine Vue Dallas — *IGNORED - out of state imaging center*
- [ ] Spring Creek Emergency Phy — *✓ MATCHES: Spring Creek Emergency Phy*
- [ ] Starlite Chiropractic — *✓ MATCHES: Starlite Chiropractic*

### Organization (12 consolidated)
- [ ] American Transit — *✓ MATCHES: American Transit Insurance (Insurer, not Organization)*
- [ ] DFW MRI — *IGNORED - out of state imaging center*
- [ ] Harbor House — *✓ MATCHES: Harbor House Of Louisville (Defendant, not Organization)*
- [ ] Harbor House of Louisville, Inc. — *✓ MATCHES: Harbor House Of Louisville (Defendant, not Organization)*
- [ ] Jefferson Circuit Clerk — *IGNORED - court office, not entity*
- [ ] Justice Bolt Support — *IGNORED - software/support service*
- [ ] Kentuckiana Court Reporters — *✓ MATCHES: Kentuckiana Court Reporters (Vendor, not Organization)*
- [ ] Kentuckiana Court Reporters / Kentucky Court Reporters — *✓ MATCHES: Kentuckiana Court Reporters (Vendor, not Organization)*
- [ ] Kentucky Court of Justice eFiling system — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Prime LOP — *IGNORED - record service software*
- [ ] Verisma — *✓ MATCHES: Verisma (Vendor, not Organization)*
- [ ] Verizon — *IGNORED - phone service, not case entity*

### PIPClaim (14 consolidated)
- [ ] 1123215 — *IGNORED - claim number*
- [ ] Farmers Insurance (PIP claim 700528477781) — *✓ MATCHES: Farmers Insurance*
- [ ] Farmers Insurance (PIP claim) — *✓ MATCHES: Farmers Insurance*
- [ ] Farmers Insurance (PIP from 11/08 accident) — *✓ MATCHES: Farmers Insurance*
- [ ] Farmers Insurance PIP — *✓ MATCHES: Farmers Insurance*
- [ ] Farmers PIP — *IGNORED - variant already consolidated above*
- [ ] NY MVA PIP (50k limit) — *IGNORED - claim description*
- [ ] NY MVA PIP (limit $50,000) — *IGNORED - variant already handled above*
- [ ] PIP claim (Personal Injury Protection) — *IGNORED - generic term*
- [ ] PIPClaim (Farmers Insurance) — *✓ MATCHES: Farmers Insurance*
- [ ] PIPClaim - Farmers Insurance (Adjuster: Michael Santos) — *✓ MATCHES: Farmers Insurance*
- [ ] Personal Injury Protection (PIP) — *IGNORED - generic term*
- [ ] USAA Insurance Company — *✓ MATCHES: USAA Insurance Company*
- [ ] USAA Insurance Company (Adjuster: None) — *✓ MATCHES: USAA Insurance Company*

### UIMClaim (2 consolidated)
- [ ] Farmers UIM — *IGNORED - generic claim reference*
- [ ] UM/UIM coverage — *IGNORED - generic coverage term*

### UMClaim (2 consolidated)
- [ ] UM/UIM coverage — *IGNORED - generic coverage term*
- [ ] Uninsured motorist — *IGNORED - generic term*

### Vendor (14 consolidated)
- [ ] Amy Murguia — *IGNORED - admin staff*
- [ ] Billing Team (ceostx.com) — *IGNORED - department, not vendor*
- [ ] CIOX Health — *✓ MATCHES: Ciox Health (Vendor, not Vendor)*
- [ ] ChartSwap.com — *✓ MATCHES: ChartSwap (Vendor, not Vendor)*
- [ ] Edelson Forensics — *IGNORED - expert witness company (out of state)*
- [ ] Faye Gaither — *✓ MATCHES: Faye Gaither (WHALEY STAFF → should be CaseManager, not Vendor)*
- [ ] Kentuckiana Court Reporters — *✓ MATCHES: Kentuckiana Court Reporters (Vendor, not Vendor)*
- [ ] Kentuckiana Reporters Scheduling Team — *IGNORED - this is Kentuckiana Court Reporters (already matched above)*
- [ ] Legent — *IGNORED - document management software*
- [ ] Lisset Abundis — *IGNORED - admin staff*
- [ ] NetDocuments — *IGNORED - document management software*
- [ ] Prime LOP — *IGNORED - record service software (variant already handled above)*
- [ ] ReporterBase (kentuckiana.reporterbase.com) — *IGNORED - scheduling software*
- [ ] Transcript Delivery — *IGNORED - service department, not vendor entity*

### WCClaim (1 consolidated)
- [ ] Workers' compensation matter (Muhammad-Alif-MVA-11-08-2022) — *IGNORED - claim description, not entity*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships