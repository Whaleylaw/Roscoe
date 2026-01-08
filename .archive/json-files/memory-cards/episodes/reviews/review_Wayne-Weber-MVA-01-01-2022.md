# Relationship Review: Wayne-Weber-MVA-01-01-2022

**Total Episodes:** 268

**Total Proposed Relationships:** 712


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (20)
- Anchorage Middletown Fire & EMS (emergency medical services)
- Baptist Health Breckenridge Imaging La Grange
- Baptist Health Breckenridge Imaging Medical Group - Eastpoint
- Baptist Health Breckenridge Imaging Medical Group Orthopedics - Floyd (orthopedic)
- Baptist Health Breckenridge Imaging Medical Group Sports Medicine
- Baptist Health Breckenridge Imaging Vascular Surgery
- Cassol Eye
- Clinical Associates
- Commonwealth Anesthesia
- Gould's Discount Medical
- Kentucky Indiana Foot & Ankle
- Louisville Emergency Medical Associates
- Louisville Hospitalist Associates PLLC (hospital)
- Nephrology Associates of Kentuckiana
- Norton Brownsboro Hospital (hospital)
- One Anesthesia, PLLC
- Premier Surgery Center of Louisville
- Retina Associates Of KY
- Southern Emergency Medical Specialists
- Xray Associates of Louisville

### Insurance Claims (2)
- **BIClaim**: State Farm Insurance Company
  - Adjuster: Lyn Zangmeister
- **PIPClaim**: Kentucky Farm Bureau
  - Adjuster: Ashley Mcneese

### Liens (2)
- Medicare
- Southern Guaranty Insurance Company - Medicare Supplement

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (3 consolidated)
- [ ] Ashley McNeese — *✓ MATCHES: Ashley Mcneese*
- [ ] Ashley Stewart — *✓ MATCHES: Ashley Stewart*
- [ ] Lyn Zangmeister — *✓ MATCHES: Lyn Zangmeister*

### Attorney (13 consolidated)
- [ ] Aaron Gregory Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Allison Dilbeck — *✓ MATCHES: Allison L. Rief*
- [ ] Allison L. Rief — *✓ MATCHES: Allison L. Rief*
- [ ] Amy Romine — *✓ MATCHES: Amy Romine*
- [ ] Defendant's Attorney — *IGNORED - generic term*
- [ ] Defense Counsel — *IGNORED - generic term*
- [ ] J. Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessa Galosmo — *✓ MATCHES: Jessa Galosmo (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessica Bottorff — *✓ MATCHES: Jessica Bottorff (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Mary Johnson — *✓ MATCHES: Dr. Mary Johanson (licensed KY doctor), not Attorney*
- [ ] Sarena — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Sarena M. Tuttle — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] W. Bryce Koon, Esq. — *✓ MATCHES: Bryce Koon (WHALEY ATTORNEY, not Attorney)*

### BIClaim (2 consolidated)
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*
- [ ] State Farm Insurance Company (BIClaim) — *✓ MATCHES: State Farm Insurance Company*

### Client (2 consolidated)
- [ ] Bryce Koon — *✓ MATCHES: Bryce Koon (WHALEY ATTORNEY, not Client)*
- [ ] Wayne Weber — *✓ MATCHES: Wayne Weber*

### Court (4 consolidated)
- [ ] Jefferson Circuit Court — *✓ MATCHES: Jefferson County Circuit Court, Division XII*
- [ ] Jefferson County (23-CI-008019) — *✓ MATCHES: Jefferson County Circuit Court, Division XII*
- [ ] Kentucky Court of Justice — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Kentucky Court of Justice eFiling system — *✓ MATCHES: Kentucky Court Of Justice*

### Defendant (5 consolidated)
- [ ] Fenwick — *✓ MATCHES: James R. Fenwick*
- [ ] Fenwick, James — *✓ MATCHES: James R. Fenwick*
- [ ] James Fenwick — *✓ MATCHES: James R. Fenwick*
- [ ] Mr. Fenwick — *✓ MATCHES: James R. Fenwick*
- [ ] Wayne Weber — *IGNORED - client, not defendant*

### Insurer (2 consolidated)
- [ ] Kentucky Farm Bureau — *✓ MATCHES: Kentucky Farm Bureau*
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*

### LawFirm (3 consolidated)
- [ ] Dilbeck and Myers, PLLC — *✓ MATCHES: Dilbeck & Myers*
- [ ] Law firm — *✓ MATCHES: Isaacs and Isaacs Law Firm*
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### Lien (4 consolidated)
- [ ] Aetna lien — *✓ MATCHES: Aetna (LienHolder, not Lien)*
- [ ] Initial Lien Request — *IGNORED - request document*
- [ ] Medicare — *✓ MATCHES: Medicare*
- [ ] Southern Guaranty Insurance Company - Medicare Supplement — *✓ MATCHES: Southern Guaranty Insurance Company - Medicare Supplement*

### LienHolder (1 consolidated)
- [ ] Southern Guaranty Insurance Company - Medicare Supplement — *✓ MATCHES: Southern Guaranty Insurance Company - Medicare Supplement*

### MedicalProvider (23 consolidated)
- [ ] Anchorage Middletown Fire & EMS — *✓ MATCHES: Anchorage Middletown Fire & EMS*
- [ ] Baptist Health Breckenridge Imaging — *✓ MATCHES: Baptist Health Breckenridge Imaging La Grange*
- [ ] Baptist Health Breckenridge Imaging La Grange — *✓ MATCHES: Baptist Health Breckenridge Imaging La Grange*
- [ ] Baptist Health Breckenridge Imaging Medical Group - Eastpoint — *✓ MATCHES: Baptist Health Breckenridge Imaging Medical Group - Eastpoint*
- [ ] Baptist Health Breckenridge Imaging Medical Group Orthopedics - Floyd — *✓ MATCHES: Baptist Health Breckenridge Imaging Medical Group Orthopedics - Floyd*
- [ ] Baptist Health Breckenridge Imaging Medical Group Sports Medicine — *✓ MATCHES: Baptist Health Breckenridge Imaging Medical Group Sports Medicine*
- [ ] Baptist Health Breckenridge Imaging Vascular Surgery — *✓ MATCHES: Baptist Health Breckenridge Imaging Vascular Surgery*
- [ ] Cassol Eye — *✓ MATCHES: Cassol Eye*
- [ ] Clinical Associates — *✓ MATCHES: Clinical Associates*
- [ ] Commonwealth Anesthesia — *✓ MATCHES: Commonwealth Anesthesia*
- [ ] Diagnostic Imaging Alliance of Louisville — *✓ MATCHES: Diagnostic Imaging Alliance of Louisville*
- [ ] Gould's Discount Medical — *✓ MATCHES: Gould's Discount Medical*
- [ ] Kentucky Indiana Foot & Ankle — *✓ MATCHES: Kentucky Indiana Foot & Ankle*
- [ ] Louisville Emergency Medical Associates — *✓ MATCHES: Louisville Emergency Medical Associates*
- [ ] Louisville Hospitalist Associates PLLC — *✓ MATCHES: Louisville Hospitalist Associates PLLC*
- [ ] Louisville Metro EMS — *✓ MATCHES: Louisville Metro EMS*
- [ ] Nephrology Associates of Kentuckiana — *✓ MATCHES: Nephrology Associates of Kentuckiana*
- [ ] Norton Brownsboro Hospital — *✓ MATCHES: Norton Brownsboro Hospital*
- [ ] One Anesthesia, PLLC — *✓ MATCHES: One Anesthesia, PLLC*
- [ ] Premier Surgery Center of Louisville — *✓ MATCHES: Premier Surgery Center of Louisville*
- [ ] Retina Associates Of KY — *✓ MATCHES: Retina Associates Of KY*
- [ ] Southern Emergency Medical Specialists — *✓ MATCHES: Southern Emergency Medical Specialists*
- [ ] Xray Associates of Louisville — *✓ MATCHES: Xray Associates of Louisville*

### Organization (6 consolidated)
- [ ] Benefits Coordination and Recovery Center (BCRC) — *IGNORED - Medicare office*
- [ ] Centers for Medicare & Medicaid Services (CMS) — *IGNORED - government agency*
- [ ] Kentucky Court of Justice — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Kentucky Court of Justice eFiling system — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Office of Program Operations & Local Engagement (OPOLE) — *IGNORED - Medicare office*
- [ ] Wayne Weber Filevine Project Email Address — *IGNORED - email reference*

### PIPClaim (1 consolidated)
- [ ] PIP - Kentucky Farm Bureau — *✓ MATCHES: Kentucky Farm Bureau*

### Vendor (10 consolidated)
- [ ] Barracuda — *IGNORED - email security service*
- [ ] Barracuda Networks — *IGNORED - email security service*
- [ ] ChartSwap.com — *✓ MATCHES: ChartSwap (Vendor, not Vendor)*
- [ ] Filevine (Wayne Weber project email) — *IGNORED - case management software*
- [ ] Filevine (WayneWeberMVAZ4293302@louisvilleaccidentlawyer.filevineapp.com) — *IGNORED - email reference*
- [ ] Kentuckiana Court Reporters — *✓ MATCHES: Kentuckiana Court Reporters (Vendor, not Vendor)*
- [ ] MCA Billing — *IGNORED - billing service*
- [ ] RecordRequest@mcabilling.com — *IGNORED - email address*
- [ ] mcabilling.com (MCA Billing) — *IGNORED - billing service*
- [ ] rcfax.com (4058693309@rcfax.com) — *IGNORED - fax service*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships