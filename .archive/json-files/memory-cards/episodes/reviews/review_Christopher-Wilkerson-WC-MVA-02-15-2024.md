# Relationship Review: Christopher-Wilkerson-WC-MVA-02-15-2024

**Total Episodes:** 286

**Total Proposed Relationships:** 813


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (5)
- Adair Family Medical Center (hospital)
- Boyle County Emergency Med Services
- Ephraim McDowell Regional Medical Center (hospital)
- Grant Chiropractic Center (chiropractic)
- Taylor County Chiropractic & Rehabilitation (chiropractic)

### Insurance Claims (2)
- **PIPClaim**: Kentucky Farm Bureau
  - Adjuster: Shellie Cooper
- **BIClaim**: None

### Liens (1)
- Blue Cross Blue Shield of Michigan

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (20 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Adjuster)*
- [ ] Adj Smith — *✓ CONSOLIDATED → Debbie Smith*
- [ ] Adjuster (unspecified) — *IGNORED - unnamed adjuster*
- [ ] Adjuster Smith — *✓ CONSOLIDATED → Debbie Smith*
- [ ] Arlene — *IGNORED - incomplete name*
- [ ] Christina — *IGNORED - incomplete name*
- [ ] Debbie — *✓ CONSOLIDATED → Debbie Smith*
- [ ] Debbie Smith — *✓ ADDED to adjusters.json (Clearpath Mutual/Hartford, Ph: 502-315-4280, Email: DSmith@HM1842.com)*
      ↳ _Mrs. Smith_
- [ ] Hartford Mutual Insurance adjuster — *✓ MATCHES: Hartford Mutual Insurance (insurer reference, not adjuster)*
- [ ] Hartford Mutual adjuster — *✓ CONSOLIDATED → Debbie Smith*
- [ ] Hartford Mutual adjuster (unnamed) — *IGNORED - unnamed*
- [ ] Kristi Woods — *✓ ADDED to adjusters.json (Hartford adjuster)*
- [ ] Megan (KFB PIP adjuster) — *✓ CONSOLIDATED → Megan Bates*
- [ ] Megan Bates — *✓ ADDED to adjusters.json (Kentucky Farm Bureau, Ph: 270-465-9771, Cell: 270-799-4077, Fax: 270-691-5750, Email: megan.bates@kyfb.com)*
      ↳ _Megan Bates (RS)_
- [ ] Megan Bates (RS) — *✓ CONSOLIDATED → Megan Bates*
- [ ] Mrs. Smith — *✓ CONSOLIDATED → Debbie Smith*
- [ ] Sarena Tuttle — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Adjuster)*
- [ ] Shellie Cooper — *✓ MATCHES: Shellie Cooper*
- [ ] unnamed adjuster — *IGNORED - unnamed*

### Attorney (6 consolidated)
- [ ] Aaron G. Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY)*
- [ ] Betsy R. Catron — *✓ MATCHES: Betsy R. Catron*
- [ ] Brad Zoppoth — *✓ ADDED to attorneys.json (The Zoppoth Law Firm, Ph: 502-568-8884)*
- [ ] Mr. Whaley — *✓ CONSOLIDATED → Aaron G. Whaley*
- [ ] Sarena M. Tuttle — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager)*
- [ ] W. Bryce Koon, Esq. — *✓ MATCHES: Bryce Koon (WHALEY ATTORNEY)*

### Client (2 consolidated)
- [ ] Bryce Koon — *✓ MATCHES: Bryce Koon (WHALEY ATTORNEY, not Client)*
- [ ] Christopher A. Wilkerson — *✓ MATCHES: Christopher Wilkerson*

### Insurer (13 consolidated)
- [ ] CLEARPATH SPECIALTY INSURANCE — *✓ CONSOLIDATED → Clearpath Mutual Insurance*
- [ ] ClearPath — *✓ CONSOLIDATED → Clearpath Mutual Insurance*
- [ ] ClearPath / ClearPath Mutual — *✓ CONSOLIDATED → Clearpath Mutual Insurance*
- [ ] ClearPath Mutual — *✓ CONSOLIDATED → Clearpath Mutual Insurance*
- [ ] ClearPath Mutual Insurance Company — *✓ ADDED to insurers.json (now Hartford subsidiary)*
- [ ] Farm Bureau Insurance Company (Kentucky Farm Bureau) — *✓ MATCHES: Kentucky Farm Bureau*
- [ ] Harford Mutual Insurance Group (formerly ClearPath Mutual) — *✓ MATCHES: Hartford Mutual Insurance*
- [ ] Hartford — *✓ MATCHES: Hartford Mutual Insurance*
- [ ] Hartford Mutual (Clearpath) — *✓ MATCHES: Hartford Mutual Insurance*
- [ ] Hartford Mutual Insurance Group — *✓ MATCHES: Hartford Mutual Insurance*
- [ ] Kentucky Farm Bureau — *✓ MATCHES: Kentucky Farm Bureau*
- [ ] Kentucky Farm Bureau Insurance — *✓ MATCHES: Kentucky Farm Bureau*
- [ ] Mutual of Omaha — *IGNORED - not relevant to case*

### LawFirm (2 consolidated)
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*
- [ ] Zoppoth Law Firm — *✓ ADDED to lawfirms.json (Brad Zoppoth's firm)*

### MedicalProvider (8 consolidated)
- [ ] Adair Family Medical Center — *✓ MATCHES: Adair Family Medical Center*
- [ ] Boyle County Emergency Med Services — *✓ MATCHES: Boyle County Emergency Med Services*
- [ ] Dr. Jessica Leonard — *✓ ADDED to doctors.json (chiropractor at Taylor County Chiropractic)*
- [ ] Ephraim McDowell Regional Medical Center — *✓ MATCHES: Ephraim McDowell Regional Medical Center*
- [ ] FORK MD — *IGNORED - unclear reference*
- [ ] Grant Chiropractic Center — *✓ MATCHES: Grant Chiropractic Center*
- [ ] Grant Chiropractic Center — *✓ MATCHES: Grant Chiropractic Center*
- [ ] Taylor County Chiropractic & Rehabilitation — *✓ MATCHES: Taylor County Chiropractic & Rehabilitation*

### Organization (9 consolidated)
- [ ] Boyle County Sheriff's Office — *✓ ADDED to organizations.json*
- [ ] CLEARPATH — *✓ MATCHES: Clearpath Mutual Insurance (insurer, not organization)*
- [ ] Communication Project (Filevine integration) — *IGNORED - software*
- [ ] Generic Customer Service — *IGNORED - generic reference*
- [ ] H&O Transport, Inc. — *IGNORED - not relevant*
- [ ] LexisNexis Risk Solutions — *IGNORED - data service*
- [ ] LexisNexis Risk Solutions (BuyCrash) — *IGNORED - data service*
- [ ] M&W Transport — *IGNORED - not relevant*
- [ ] Nathan Bennett Trucking — *✓ MATCHES: Nathan Bennett Trucking, LLC*

### PIPClaim (5 consolidated)
- [ ] Claim 04943051 (PIP - Kentucky Farm Bureau) — *✓ MATCHES: Kentucky Farm Bureau*
- [ ] Kentucky Farm Bureau Claim #04943051 — *✓ MATCHES: Kentucky Farm Bureau*
- [ ] Kentucky Farm Bureau PIP claim — *✓ MATCHES: Kentucky Farm Bureau*
- [ ] PIP Claim 04943051 — *IGNORED - generic claim reference*
- [ ] PIPClaim (Kentucky Farm Bureau) — *✓ MATCHES: Kentucky Farm Bureau*

### Vendor (1 consolidated)
- [ ] LexisNexis BuyCrash — *IGNORED - data service*

### WCClaim (20 consolidated)
- [ ] 04943051 — *IGNORED - claim number only*
- [ ] 238042CS (WC-MVA-02-15-2024) — *IGNORED - claim number*
- [ ] Christopher Wilkerson (238042) / WC-MVA-02-15-2024 — *✓ MATCHES: Christopher Wilkerson (client reference)*
- [ ] Christopher Wilkerson - WC claim — *✓ MATCHES: Christopher Wilkerson (client reference)*
- [ ] Christopher Wilkerson 238042 — *✓ MATCHES: Christopher Wilkerson (client reference)*
- [ ] Christopher Wilkerson WC Claim (AFC 230577703) — *✓ MATCHES: Christopher Wilkerson (client reference)*
- [ ] Christopher Wilkerson WC Claim (file #238042) — *✓ MATCHES: Christopher Wilkerson (client reference)*
- [ ] Christopher Wilkerson Workers' Compensation claim — *✓ MATCHES: Christopher Wilkerson (client reference)*
- [ ] Christopher-Wilkerson-WC-MVA-02-15-2024 — *IGNORED - case name reference*
- [ ] Christopher-Wilkerson-WC-MVA-02-15-2024 (file 238042) — *IGNORED - case name*
- [ ] Claim 04943051 — *IGNORED - claim number*
- [ ] PPD claim (Christopher Wilkerson) — *✓ MATCHES: Christopher Wilkerson (client reference)*
- [ ] WC #238042 — *IGNORED - claim number*
- [ ] WC Claim (Hartford Mutual Insurance) — *✓ MATCHES: Hartford Mutual Insurance (insurer reference)*
- [ ] WC claim - Christopher Wilkerson (02/15/2024) — *✓ MATCHES: Christopher Wilkerson (client reference)*
- [ ] WC-MVA-02-15-2024 — *IGNORED - case name*
- [ ] WCClaim #238042CS — *IGNORED - claim number*
- [ ] Workers' Compensation (WC-MVA) claim — *IGNORED - generic claim reference*
- [ ] Workers' Compensation Claim 238042 — *IGNORED - claim number*
- [ ] Workers' Compensation claim (Christopher Wilkerson, 02-15-2024) — *✓ MATCHES: Christopher Wilkerson (client reference)*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships
