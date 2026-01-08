# Relationship Review: Robin-Wilder-Hamilton-MVA-6-15-2023

**Total Episodes:** 343

**Total Proposed Relationships:** 680


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (4)
- SCIOTO VALLEY CHIROPRACTIC AND REHAB CENTER, LLC (chiropractic)
- The Body Shop Physical Therapy (physical therapy)
- THOMPSON CHIROPRACTIC CENTER
- VA Medical Center Lexington

### Insurance Claims (2)
- **PIPClaim**: Auto Owners Insurance
  - Adjuster: Donald Thomas
- **BIClaim**: Sea Harbor Insurance

### Liens (1)
- U.S Department of Veterans Affairs

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (14 consolidated)
- [ ] Adjuster from Sea Harbor Insurance — *✓ MATCHES: Sea Harbor Insurance*
- [ ] Chandler Wolfe — *✓ MATCHES: Chandler Wolfe*
- [ ] Chris Williams — *✓ MATCHES: Chris Williams (from directory)*
- [ ] Donald Thomas — *✓ MATCHES: Donald Thomas*
- [ ] Ethan Bailey — *✓ MATCHES: Ethan Bailey (from directory)*
- [ ] Jessa Galosmo — *✓ MATCHES: Jessa Galosmo (WHALEY STAFF → should be CaseManager, not Adjuster)*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Adjuster)*
- [ ] La Monica White — *IGNORED - too generic*
- [ ] Michael McGee — *✓ MATCHES: Micheal Mcgee (from directory)*
- [ ] Sea Harbor Insurance adjuster — *✓ MATCHES: Sea Harbor Insurance*
- [ ] Sea Harbor adjuster (unnamed) — *IGNORED - unnamed entity*
- [ ] adjuster (unnamed) — *IGNORED - unnamed entity*
- [ ] pd adj — *IGNORED - too generic*
- [ ] property damage adjuster — *IGNORED - generic term*

### Attorney (8 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Aries Penaflor — *✓ MATCHES: Aries Penaflor (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessa Galosmo — *✓ MATCHES: Jessa Galosmo (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessica Bottorff — *✓ MATCHES: Jessica Bottorff (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Justin — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] K. Hedgecock — *✓ MATCHES: Karen Hedgecock*
- [ ] Karen Hedgecock — *✓ MATCHES: Karen Hedgecock*
- [ ] Steven B. Lowery, Esq. — *✓ MATCHES: Steven B. Lowery*

### BIClaim (6 consolidated)
- [ ] BI Claim C0119952 — *IGNORED - claim number*
- [ ] BIClaim (Sea Harbor Insurance) — *✓ MATCHES: Sea Harbor Insurance*
- [ ] BIClaim - Sea Harbor Insurance (C0119952) — *✓ MATCHES: Sea Harbor Insurance*
- [ ] Sea Harbor Insurance — *✓ MATCHES: Sea Harbor Insurance*
- [ ] Sea Harbor Insurance BI claim — *✓ MATCHES: Sea Harbor Insurance*
- [ ] Sea Harbor Insurance Claim C0119952 — *✓ MATCHES: Sea Harbor Insurance*

### Client (2 consolidated)
- [ ] Micheal Mcgee — *IGNORED - not client*
- [ ] Robin Wilder Hamilton — *✓ MATCHES: Robin Wilder-Hamilton*

### Insurer (5 consolidated)
- [ ] Amax Auto Insurance — *IGNORED - no match found*
- [ ] Auto Owners Insurance — *✓ MATCHES: Auto Owners Insurance*
- [ ] Kentucky PIP — *IGNORED - coverage type, not insurer*
- [ ] Sea Harbor Insurance — *✓ MATCHES: Sea Harbor Insurance*
- [ ] Wells & Middleton Insurance Inc. — *✓ MATCHES: Wells & Middleton Insurance Inc.*

### LawFirm (1 consolidated)
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### Lien (1 consolidated)
- [ ] U.S Department of Veterans Affairs: $None — *✓ MATCHES: U.S Department of Veterans Affairs*

### MedicalProvider (6 consolidated)
- [ ] SCIOTO VALLEY CHIROPRACTIC AND REHAB CENTER, LLC — *✓ MATCHES: SCIOTO VALLEY CHIROPRACTIC AND REHAB CENTER, LLC*
- [ ] THOMPSON CHIROPRACTIC CENTER — *✓ MATCHES: THOMPSON CHIROPRACTIC CENTER*
- [ ] THOMPSON CHIROPRACTIC CENTER — *✓ MATCHES: THOMPSON CHIROPRACTIC CENTER*
- [ ] The Body Shop Physical Therapy — *✓ MATCHES: The Body Shop Physical Therapy*
- [ ] VA Medical Center Lexington — *✓ MATCHES: VA Medical Center Lexington*
- [ ] VA Medical Center Lexington — *✓ MATCHES: VA Medical Center Lexington*

### Organization (4 consolidated)
- [ ] Department of Veterans Affairs, Office of General Counsel, Revenue Law Group — *IGNORED - department*
- [ ] Jerry Towing — *IGNORED - vendor*
- [ ] Myatt and Associates — *IGNORED - need more info*
- [ ] VA Office of the General Counsel — *IGNORED - department*

### PIPClaim (5 consolidated)
- [ ] Auto Owners Insurance PIPClaim — *✓ MATCHES: Auto Owners Insurance*
- [ ] PIP Claim 300-0377210-2023 — *IGNORED - claim number*
- [ ] PIP claim with Wells & Middleton Insurance Inc. — *✓ MATCHES: Wells & Middleton Insurance Inc. (Insurer, not PIPClaim)*
- [ ] PIPClaim: Auto Owners Insurance — *✓ MATCHES: Auto Owners Insurance*
- [ ] PIPClaim: Auto Owners Insurance (Adjuster: Donald Thomas) — *✓ MATCHES: Auto Owners Insurance*

### Vendor (2 consolidated)
- [ ] Copier Scans — *IGNORED - scanning service*
- [ ] RCFax (8592814979@rcfax.com) — *IGNORED - fax service*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships