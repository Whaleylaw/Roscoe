# Relationship Review: Michael-Johnston-WC-05-03-2023

**Total Episodes:** 148

**Total Proposed Relationships:** 376


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (9)
- Anchorage Middletown Fire & EMS (emergency medical services)
- Kentucky Truck Plant Medical
- KORT Physical Therapy (physical therapy)
- Louisville Bone & Joint Specialists
- M. Joseph Medical
- Mohana Arla
- ULP Radiological Associates (radiology)
- Norton Audubon Hospital (hospital)
- UofL Physicians – Podiatric Medicine & Surgery

### Insurance Claims (1)
- **PIPClaim**: UniCare Life & Health Insurance Company

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (4 consolidated)
- [ ] Megan — *IGNORED - too generic, need last name*
- [ ] Rawlings — *IGNORED - likely Rawlings company (lienholder), not adjuster*
- [ ] WC adjuster — *IGNORED - generic term*
- [ ] workers' compensation adjuster — *IGNORED - generic term*

### Attorney (6 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Sarena — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Sarena Tuttle — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] W. Bryce Koon, Esq. — *✓ MATCHES: Bryce Koon (WHALEY ATTORNEY, not Attorney)*
- [ ] davidsonb@obtlaw.com — *IGNORED - email address, not entity*
- [ ] swecj@obtlaw.com — *IGNORED - email address, not entity*

### Client (2 consolidated)
- [ ] Michael Johnston — *✓ MATCHES: Michael Johnston*
- [ ] Michael Johnston (ID 841603) — *✓ MATCHES: Michael Johnston*

### Insurer (4 consolidated)
- [ ] Blue Cross — *IGNORED - generic reference to personal insurance*
- [ ] Blue Cross (personal insurance) — *IGNORED - personal insurance, not case-related*
- [ ] Ford Worker's Compensation — *✓ MATCHES: Ford Worker's Compensation*
- [ ] UniCare Life & Health Insurance Company — *✓ MATCHES: UniCare Life & Health Insurance Company*

### LawFirm (1 consolidated)
- [ ] **The Whaley Law Firm** — *✓ MATCHES: The Whaley Law Firm*
      ↳ _Whaley Lawfirm_

### MedicalProvider (16 consolidated)
- [ ] Anchorage Middletown Fire & EMS — *✓ MATCHES: Anchorage Middletown Fire & EMS*
- [ ] Baptist Health Breckenridge Imaging — *✓ MATCHES: 3000 Baptist Health Breckenridge Imaging Blvd, ABOUT*
- [ ] Commonwealth IME — *✓ MATCHES: Commonwealth IME (Vendor, not MedicalProvider)*
- [ ] Dr Nicholas Lao — *IGNORED - IME doctor, variant of Dr. Laco*
- [ ] Dr. Bloemer — *IGNORED - Commonwealth IME doctor (already matched as vendor)*
- [ ] Dr. Gary Bloemer (Commonwealth IME) — *✓ MATCHES: Commonwealth IME (Vendor, not MedicalProvider)*
- [ ] Dr. Gary F. Bloemer, MD — *IGNORED - variant of Dr. Bloemer above*
- [ ] Dr. Laco — *IGNORED - variant of Nicholas Lao above*
- [ ] KORT Physical Therapy — *✓ MATCHES: KORT Physical Therapy*
- [ ] Kentucky Truck Plant Medical — *✓ MATCHES: Kentucky Truck Plant Medical*
- [ ] Louisville Bone & Joint Specialists — *✓ MATCHES: Louisville Bone & Joint Specialists*
- [ ] M. Joseph Medical — *✓ MATCHES: M. Joseph Medical*
- [ ] Mohana Arla — *✓ MATCHES: Mohana Arla*
- [ ] ULP Radiological Associates — *✓ MATCHES: ULP Radiological Associates*
- [ ] Norton Audubon Hospital — *✓ MATCHES: Norton Audubon Hospital*
- [ ] UofL Physicians – Podiatric Medicine & Surgery — *✓ MATCHES: UofL Physicians – Podiatric Medicine & Surgery*

### Organization (4 consolidated)
- [ ] Commonwealth IME — *✓ MATCHES: Commonwealth IME (Vendor, not Organization)*
- [ ] **Ford Motor Company** — *✓ MATCHES: Ford Motor Company (from directory)*
      ↳ _Ford_
- [ ] OasisSpace — *✓ MATCHES: OasisSpace (from directory)*

### PIPClaim (1 consolidated)
- [ ] UniCare Life & Health Insurance Company — *✓ MATCHES: UniCare Life & Health Insurance Company*

### Vendor (5 consolidated)
- [ ] Acuity Scheduling — *IGNORED - scheduling software, not vendor entity*
- [ ] Commonwealth IME — *✓ MATCHES: Commonwealth IME (Vendor, not Vendor)*
- [ ] Commonwealth IME Scheduling — *✓ MATCHES: Commonwealth IME (Vendor, not Vendor)*
- [ ] ROI Tech — *IGNORED - records retrieval software*
- [ ] Vinesign Certification — *IGNORED - VineSign document software, not vendor*

### WCClaim (8 consolidated)
- [ ] Michael Johnston WC Claim (05-03-2023) — *✓ MATCHES: Michael Johnston (from directory)*
- [ ] Michael Johnston WC claim — *✓ MATCHES: Michael Johnston (from directory)*
- [ ] Michael-Johnston-WC-05-03-2023 — *IGNORED - case name, not claim entity*
- [ ] WC #841603 — *IGNORED - claim number*
- [ ] WC Claim #841603 — *IGNORED - claim number*
- [ ] WC-05-03-2023 — *IGNORED - case identifier*
- [ ] Workers' Compensation (WC) claim — *IGNORED - generic claim description*
- [ ] Workers' Compensation claim for Michael Johnston — *✓ MATCHES: Michael Johnston (from directory)*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships