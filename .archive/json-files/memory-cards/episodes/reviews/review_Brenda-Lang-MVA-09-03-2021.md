# Relationship Review: Brenda-Lang-MVA-09-03-2021

**Total Episodes:** 211

**Total Proposed Relationships:** 853


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (10)
- Baptist Health Breckenridge Imaging
- Baptist Health Breckenridge Imaging Hardin
- Baptist Health Breckenridge Imaging Louisville
- Gould's Discount Medical
- Louisville Emergency Medical Associates
- Louisville Metro EMS (emergency medical services)
- Norton Hospital (hospital)
- Okolona Fire/EMS (emergency medical services)
- Southern Medical Specialist
- Xray Associates of Louisville

### Insurance Claims (3)
- **BIClaim**: TARC Risk Management Services Company
  - Adjuster: J. Clarke McCulloch
- **PIPClaim**: State Farm Insurance Company
  - Adjuster: Steve Campbell
- **PIPClaim**: State Farm Insurance Company
  - Adjuster: Randy Carney

### Liens (2)
- Humana ($1,513.45)
- Medicare

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (2 consolidated)
- [ ] J. Clarke McCulloch — *✓ MATCHES: J. Clarke McCulloch*
- [ ] Steve Campbell — *✓ MATCHES: Steve Campbell*

### Attorney (10 consolidated)
- [ ] Aaron Whaley, Esquire — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Allison L. Rief — *✓ MATCHES: Allison L. Rief*
- [ ] Chauncey Hiestand — *✓ MATCHES: Chauncey Hiestand*
- [ ] Gregory Scott Gowen — *✓ MATCHES: Gregory Scott Gowen*
- [ ] Jessa Galosmo — *✓ MATCHES: Jessa Galosmo (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Sarena — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Sarena M. Tuttle — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Sarena Whaley — *✓ MATCHES: Sarena Whaley (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] W. Bryce Koon, Esq. — *✓ MATCHES: Bryce Koon (WHALEY ATTORNEY, not Attorney)*
- [ ] Wendy McLaughlin — *? NEW*

### BIClaim (2 consolidated)
- [ ] TARC Risk Management Services Company — *✓ MATCHES: TARC Risk Management Services Company*
- [ ] TARC Risk Management Services Company (Claim 410220052) — *✓ MATCHES: TARC Risk Management Services Company*

### Client (1 consolidated)
- [ ] Brenda Lang — *✓ MATCHES: Brenda D. Lang*

### Court (7 consolidated)
- [ ] Division 7, Docket 23-CI-005662 — *? NEW*
- [ ] Jefferson 23-CI-005931 — *✓ MATCHES: Jefferson County Circuit Court, Division VII*
- [ ] Jefferson County (23-CI-005931) — *✓ MATCHES: Jefferson County Circuit Court, Division VII*
- [ ] Jefferson County Attorney's Office — *? NEW*
- [ ] Jefferson County Circuit Court — *✓ MATCHES: Jefferson County Circuit Court, Division VII*
- [ ] Kentucky Court of Justice — *✓ MATCHES: Kentucky Court Of Justice (from directory)*
- [ ] Kentucky Court of Justice eFiling system — *✓ MATCHES: Kentucky Court Of Justice (from directory)*

### Defendant (5 consolidated)
- [ ] Brenda Lang — *✓ MATCHES: Brenda D. Lang (from directory)*
- [ ] Louisville Metro — *✓ MATCHES: Louisville MRI (from directory)*
- [ ] Louisville Metro Government — *✓ MATCHES: Louisville Metro (from directory)*
- [ ] Louisville Metro Police Department (LMPD) — *✓ MATCHES: Louisville Metro (from directory)*
- [ ] Marcus Hamlet — *✓ MATCHES: Marcus Hamlet*

### Insurer (3 consolidated)
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*
- [ ] TARC Risk Management Services Company — *✓ MATCHES: TARC Risk Management Services Company*
- [ ] Travelers — *✓ MATCHES: Travelers Insurance*

### LawFirm (7 consolidated)
- [ ] Assistant Jefferson County Attorneys — *✓ MATCHES: Assistant Jefferson County Attorneys*
- [ ] Dilbeck & Myers — *✓ MATCHES: Dilbeck & Myers*
- [ ] Fulton, Maddox, Dickens & Stewart PLLC — *✓ MATCHES: Fulton, Maddox, Dickens & Stewart PLLC*
- [ ] Isaacs and Isaacs Law Firm — *✓ MATCHES: Isaacs and Isaacs Law Firm*
- [ ] **Sarena Tuttle** — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not LawFirm)*
      ↳ _Sarena Whaley Law Firm_
- [ ] **The Whaley Law Firm** — *✓ MATCHES: The Whaley Law Firm*
      ↳ _Whaley & Whaley Law Firm_
- [ ] Winton & Hiestand Law Group — *✓ MATCHES: Winton & Hiestand Law Group*

### Lien (2 consolidated)
- [ ] Humana — *✓ MATCHES: Humana*
- [ ] Medicare — *✓ MATCHES: Medicare*

### MedicalProvider (9 consolidated)
- [ ] Baptist Health Breckenridge Imaging — *✓ MATCHES: Baptist Health Breckenridge Imaging*
- [ ] Baptist Health Breckenridge Imaging Hardin — *✓ MATCHES: Baptist Health Breckenridge Imaging*
- [ ] Baptist Health Breckenridge Imaging Louisville — *✓ MATCHES: Baptist Health Breckenridge Imaging*
- [ ] Gould's Discount Medical — *✓ MATCHES: Gould's Discount Medical*
- [ ] Louisville Emergency Medical Associates — *✓ MATCHES: Louisville Emergency Medical Associates*
- [ ] Norton Hospital — *✓ MATCHES: Norton Hospital*
- [ ] Okolona Fire/EMS — *✓ MATCHES: Okolona Fire/EMS*
- [ ] Southern Medical Specialist — *✓ MATCHES: Southern Medical Specialist*
- [ ] Xray Associates of Louisville — *✓ MATCHES: Xray Associates of Louisville*

### Organization (7 consolidated)
- [ ] ChartSwap.com — *✓ MATCHES: ChartSwap (from directory)*
- [ ] Jefferson County Attorney's Office — *✓ MATCHES: Jefferson County Attorney's Office*
- [ ] Kentucky Court of Justice — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Kentucky Court of Justice eFiling system — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] LMPD — *✓ MATCHES: LMPD (from directory)*
- [ ] Louisville Metro — *✓ MATCHES: Louisville Metro Police Department*
- [ ] **Louisville Metro Government** — *✓ MATCHES: Louisville Metro Government*
      ↳ _Louisville/Jefferson County government_

### PIPClaim (4 consolidated)
- [ ] PIPClaim: State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*
- [ ] PIPClaim: State Farm Insurance Company (Adjuster: Steve Campbell) — *✓ MATCHES: State Farm Insurance Company*
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*
- [ ] State Farm Insurance Company (PIP claim) — *✓ MATCHES: State Farm Insurance Company*

### Vendor (1 consolidated)
- [ ] **Kentuckiana Court Reporters** — *✓ MATCHES: Kentuckiana Court Reporters*
      ↳ _Kentuckiana Reporters Scheduling Department_

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships