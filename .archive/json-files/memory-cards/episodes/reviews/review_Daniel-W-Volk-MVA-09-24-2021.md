# Relationship Review: Daniel-W-Volk-MVA-09-24-2021

**Total Episodes:** 171

**Total Proposed Relationships:** 507


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (9)
- Aptiva Health Health
- Baptist Health Breckenridge Imaging Medical Group Primary Care St. Mathews
- Baptist Health Breckenridge Imaging Medical Group Sports Medicine
- Norton Norton Audubon Hospital (hospital)
- Norton Brownsboro Hospital (hospital)
- Norton Cancer Institute
- Norton Neuroscience Institute
- OSF PromptCare
- Results Physiotherapy

### Insurance Claims (3)
- **BIClaim**: Grange Insurance
  - Adjuster: Kayla Kinzel
- **PIPClaim**: SafeCo Insurance Company
  - Adjuster: Bethany Pineda
- **PIPClaim**: SafeCo Insurance Company
  - Adjuster: Kimberle Pishke

### Liens (1)
- None ($2,452.30)

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (6 consolidated)
- [ ] Bethany Pineda — *✓ MATCHES: Bethany Pineda*
- [ ] Ebon I. Moore — *✓ MATCHES: Ebon Moore (from adjusters)*
- [ ] Kayla Kinzel — *✓ MATCHES: Kayla Kinzel*
- [ ] Kimberle Pischke — *✓ MATCHES: Kimberle Pishke*
- [ ] SafeCo adjuster — *✓ MATCHES: SafeCo Insurance Company (from insurers)*
- [ ] jchumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Adjuster)*

### Attorney (9 consolidated)
- [ ] Aaron Gregory Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Allison Orberson-Wiles — *✓ MATCHES: Allison Orberson-Wiles*
- [ ] Faye Gaither — *✓ MATCHES: Faye Gaither (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessica (Whaley Law Firm) — *✓ MATCHES: Jessica Bottorff (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessica Bottorff — *✓ MATCHES: Jessica Bottorff (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Sarena Whaley — *✓ MATCHES: Sarena Whaley (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] W. Bryce Koon — *✓ MATCHES: Bryce Koon (WHALEY ATTORNEY, not Attorney)*
- [ ] William B. Orber-son — *✓ MATCHES: William B. Orberson*

### BIClaim (2 consolidated)
- [ ] Grange Insurance — *✓ MATCHES: Grange Insurance*
- [ ] ZPA003356461 — *IGNORED - claim number*

### Client (1 consolidated)
- [ ] Daniel W. Volk — *✓ MATCHES: Daniel W. Volk*

### Court (4 consolidated)
- [ ] Kentucky Court of Justice — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Oldham County — *✓ MATCHES: Oldham County Circuit Court, Division I*
- [ ] Oldham County (Case No. 25-CI-00111) — *✓ MATCHES: Oldham County Circuit Court, Division I*
- [ ] Oldham County Circuit Court — *✓ MATCHES: Oldham County Circuit Court, Division I*

### Defendant (2 consolidated)
- [ ] Safeco — *✓ MATCHES: SafeCo Insurance Company (from insurers)*
- [ ] Safeco Insurance Company of Illinois — *✓ MATCHES: SafeCo Insurance Company (from insurers)*

### Insurer (6 consolidated)
- [ ] Blue Cross Blue Shield — *✓ MATCHES: Anthem Blue Cross Blue Shield (from lienholders)*
- [ ] Grange Insurance — *✓ MATCHES: Grange Insurance*
- [ ] Liberty Mutual — *✓ MATCHES: Liberty Mutual Insurance Company*
- [ ] SafeCo Insurance Company — *✓ MATCHES: SafeCo Insurance Company*
- [ ] Safeco Insurance Company of America — *✓ MATCHES: SafeCo Insurance Company*
- [ ] Safeco Insurance Company of Illinois — *✓ MATCHES: SafeCo Insurance Company*

### LawFirm (3 consolidated)
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*
- [ ] Whaley Law — *✓ MATCHES: The Whaley Law Firm*
- [ ] Whaley Law Firm (Whaley Law Office) — *✓ MATCHES: The Whaley Law Firm*

### Lien (1 consolidated)
- [ ] None: $2452.3 — *IGNORED - invalid lien entry*

### MedicalProvider (14 consolidated)
- [ ] Aptiva Health Health — *✓ MATCHES: Aptiva Health Health*
- [ ] Baptist Health Breckenridge Imaging - Neurology — *✓ MATCHES: Baptist Health Breckenridge Imaging*
- [ ] Baptist Health Breckenridge Imaging Medical Group Primary Care St. Mathews — *✓ MATCHES: Baptist Health Breckenridge Imaging Medical Group Primary Care St. Mathews*
- [ ] Baptist Health Breckenridge Imaging Medical Group Sports Medicine — *✓ MATCHES: Baptist Health Breckenridge Imaging Medical Group Sports Medicine*
- [ ] Cressman Neurological Rehabilitation — *✓ MATCHES: Cressman Neurological Rehabilitation*
- [ ] Physical Therapy — *IGNORED - generic provider reference*
- [ ] Dr Gilbert — *IGNORED - doctor name only*
- [ ] Dr. Cassenele — *IGNORED - doctor name only*
- [ ] Norton Norton Audubon Hospital — *✓ MATCHES: Norton Norton Audubon Hospital*
- [ ] Norton Brownsboro Hospital — *✓ MATCHES: Norton Brownsboro Hospital*
- [ ] Norton Cancer Institute — *✓ MATCHES: Norton Cancer Institute*
- [ ] Norton Neuroscience Institute — *✓ MATCHES: Norton Neuroscience Institute*
- [ ] OSF PromptCare — *✓ MATCHES: OSF PromptCare*
- [ ] Results Physiotherapy — *✓ MATCHES: Results Physiotherapy*

### Organization (4 consolidated)
- [ ] Cressman Neurological Rehabilitation — *✓ MATCHES: Cressman Neurological Rehabilitation (from medical providers)*
- [ ] Kentucky Court of Justice — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Kentucky Court of Justice eFiling system — *✓ MATCHES: Kentucky Court Of Justice*
- [ ] Liberty Mutual Insurance — *✓ MATCHES: Liberty Mutual Insurance Company (from insurers)*

### PIPClaim (4 consolidated)
- [ ] PIPClaim #047060829 — *IGNORED - claim number*
- [ ] PIPClaim - SafeCo Insurance Company — *✓ MATCHES: SafeCo Insurance Company*
- [ ] PIPClaim: SafeCo Insurance Company (Adjuster: Kimberle Pishke) — *✓ MATCHES: SafeCo Insurance Company*
- [ ] SafeCo Insurance Company PIPClaim — *✓ MATCHES: SafeCo Insurance Company*

### UIMClaim (3 consolidated)
- [ ] SafeCo UIM claim — *IGNORED - generic claim reference*
- [ ] Under Insured Motorist (UIM) claim — *IGNORED - generic claim type*
- [ ] Underinsured Motorist (UIM) claim with SafeCo Insurance Company — *✓ MATCHES: SafeCo Insurance Company (from insurers)*

### UMClaim (1 consolidated)
- [ ] UM claim — *IGNORED - generic claim type*

### Vendor (1 consolidated)
- [ ] EpicLink — *IGNORED - software/service reference*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships