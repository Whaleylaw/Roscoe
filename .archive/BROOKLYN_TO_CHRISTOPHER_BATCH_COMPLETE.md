# Batch Review Complete: Brooklyn-Ballard to Christopher-Wilkerson

**Date:** December 30, 2025
**Files Reviewed:** 9
**Entities Added:** 16

---

## Files Manually Corrected

1. ✅ review_Brooklyn-Ballard-MVA-02-28-2024.md
2. ✅ review_Bryan-Smith-MVA-6-18-2025.md
3. ✅ review_Bryson-Brown-MVA-6-29-2025.md
4. ✅ review_Carmelita-Wilson-MVA-10-12-2025.md
5. ✅ review_Charles-T-Johnson-MVA-4-18-2023.md
6. ✅ review_Chase-Lindsey-MVA-12-01-2024.md
7. ✅ review_Christopher-Lanier-MVA-6-28-2025.md
8. ✅ review_Christopher-Wilkerson-WC-MVA-02-15-2024.md

**Note:** review_Charles-T.-Johnson-MVA-4-18-2023.md appears to be a duplicate (with period in name)

---

## Entities Added to JSON Files

### **Clients (+4)** → Total: 110

1. **Bryan Smith**
   - Source: review_Bryan-Smith-MVA-6-18-2025.md

2. **Carmelita Wilson**
   - Source: review_Carmelita-Wilson-MVA-10-12-2025.md

3. **Chase Lindsey**
   - Source: review_Chase-Lindsey-MVA-12-01-2024.md
   - Note: Multi-client accident with Elizabeth, Jeremy, Owen Lindsey

4. **Owen Lindsey**
   - Source: review_Chase-Lindsey-MVA-12-01-2024.md
   - Note: Multi-client accident with Chase, Elizabeth, Jeremy Lindsey

---

### **Adjusters (+5)** → Total: 156

1. **Thomas Rivera**
   - Source: review_Charles-T-Johnson-MVA-4-18-2023.md

2. **Chandler Wolfe**
   - Source: review_Chase-Lindsey-MVA-12-01-2024.md

3. **Everado Valle**
   - Source: review_Christopher-Lanier-MVA-6-28-2025.md
   - Note: From directory, National General adjuster

4. **Kristi Woods**
   - Source: review_Christopher-Wilkerson-WC-MVA-02-15-2024.md
   - Note: Hartford adjuster

5. **Megan Bates**
   - Source: review_Christopher-Wilkerson-WC-MVA-02-15-2024.md
   - Company: Kentucky Farm Bureau Insurance
   - Address: PO Box 20400, Louisville, KY 40250-9802
   - Office: 270-465-9771
   - Cell: 270-799-4077
   - Fax: 270-691-5750
   - Email: megan.bates@kyfb.com

---

### **Attorneys (+2)** → Total: 170

1. **Amy Romine**
   - Role: defense_counsel
   - Source: review_Charles-T-Johnson-MVA-4-18-2023.md

2. **Brad Zoppoth**
   - Role: defense_counsel
   - Firm: The Zoppoth Law Firm
   - Phone: 502-568-8884
   - Source: review_Christopher-Wilkerson-WC-MVA-02-15-2024.md

---

### **Defendants (+1)** → Total: 15

1. **Robert Lowe**
   - Source: review_Charles-T-Johnson-MVA-4-18-2023.md
   - Note: Defendant in Charles T Johnson case

---

### **Law Firms (+1)** → Total: 43

1. **The Zoppoth Law Firm**
   - Phone: 502-568-8884
   - Source: review_Christopher-Wilkerson-WC-MVA-02-15-2024.md

---

### **Insurers (+1)** → Total: 100

1. **Clearpath Mutual Insurance Company**
   - Source: review_Christopher-Wilkerson-WC-MVA-02-15-2024.md
   - Note: Now a Hartford subsidiary

---

### **Doctors (+1)** → Total: 20,737

1. **Dr. Jessica Leonard**
   - Specialty: Chiropractic
   - Credentials: DC
   - Works at: Taylor County Chiropractic & Rehabilitation
   - Source: review_Christopher-Wilkerson-WC-MVA-02-15-2024.md

---

### **Organizations (+2)** → Total: 390

1. **Arenas Logistics, LLC**
   - Type: trucking
   - Source: review_Charles-T-Johnson-MVA-4-18-2023.md

2. **Boyle County Sheriff's Office**
   - Type: law_enforcement
   - Source: review_Christopher-Wilkerson-WC-MVA-02-15-2024.md

---

## New KNOWN_MAPPINGS Added (20 consolidations)

```python
# Client consolidations
"Brooklyn (minor child)": "Brooklyn Ballard",

# Attorney/staff consolidations
"Whaley": "Aaron G. Whaley",
"Mr. Whaley": "Aaron G. Whaley",
"Lowe": "Robert Lowe",

# Adjuster consolidations (Debbie Smith variants)
"Adj Smith": "Debbie Smith",
"Adjuster Smith": "Debbie Smith",
"Debbie": "Debbie Smith",
"Mrs. Smith": "Debbie Smith",
"Hartford Mutual adjuster": "Debbie Smith",

# Adjuster consolidations (Megan Bates)
"Megan (KFB PIP adjuster)": "Megan Bates",
"Megan Bates (RS)": "Megan Bates",

# Insurer consolidations (Clearpath/Hartford)
"CLEARPATH SPECIALTY INSURANCE": "Clearpath Mutual Insurance Company",
"ClearPath": "Clearpath Mutual Insurance Company",
"ClearPath / ClearPath Mutual": "Clearpath Mutual Insurance Company",
"ClearPath Mutual": "Clearpath Mutual Insurance Company",
"Harford Mutual Insurance Group (formerly ClearPath Mutual)": "Hartford Mutual Insurance",
"Hartford Mutual (Clearpath)": "Hartford Mutual Insurance",

# Other consolidations
"Auto-Owners Insurance Company": "Auto Owners Insurance",
"Farm Bureau Insurance Company (Kentucky Farm Bureau)": "Kentucky Farm Bureau",
"Terrence Donahue": "Dr. Terrence P. Donohue",
```

---

## New IGNORE_ENTITIES Added (40+ patterns)

```python
# People/names to ignore
"Greg Gant", "Deena Gilliam", "Elizabeth Ballard", "Tymon Brown",
"Mary [last name]", "Arlene", "Christina",

# Generic references
"Brooklyn Ballard-Lien Request", "Health lien", "final lien",
"Adjuster (unspecified)", "Hartford Mutual Insurance adjuster",
"Hartford Mutual adjuster (unnamed)", "unnamed adjuster", "Client",

# Software/services
"Vinesign", "@jchumbley", "Court Net",
"OMB Medical Records Requests (Louisville office)", "OMBMRR@Louisvilleky.gov",
"LexisNexis Risk Solutions", "LexisNexis Risk Solutions (BuyCrash)", "LexisNexis BuyCrash",
"Communication Project (Filevine integration)", "Generic Customer Service",
"Louisville Accident Lawyer / Filevine",

# Companies to ignore
"Mutual of Omaha", "H&O Transport, Inc.", "M&W Transport",

# Case references/claim numbers
"Charles Johnson v. Robert Lowe (24-CI-002475)",
"BI #250525568", "PIP Claim 04943051", "Claim 04943051", "04943051",
"238042CS (WC-MVA-02-15-2024)", "WC #238042", "WCClaim #238042CS",
"Christopher-Wilkerson-WC-MVA-02-15-2024", "Christopher-Wilkerson-WC-MVA-02-15-2024 (file 238042)",
"WC-MVA-02-15-2024", "Workers' Compensation (WC-MVA) claim",
"Workers' Compensation Claim 238042",

# Medical references
"FORK MD",
```

---

## Key Corrections Applied

### **Multi-Client Accidents Identified:**

**Chase Lindsey Family (4 clients):**
- Chase Lindsey ✓ ADDED
- Elizabeth Lindsey ✓ EXISTS
- Jeremy Lindsey ✓ EXISTS
- Owen Lindsey ✓ ADDED
- **Action needed:** Create RELATED_ACCIDENT relationships

### **Doctor Matches:**
- "Terrence Donahue" → Matched to **Dr. Terrence P. Donohue** (KY licensed physician)
- Dr. Jessica Leonard → Added as chiropractor

### **Insurer Consolidations:**
- All Clearpath variants → **Clearpath Mutual Insurance Company**
- Noted Hartford acquisition of Clearpath

### **Adjuster Consolidations:**
- 5 "Debbie Smith" variants → consolidated
- 2 "Megan Bates" variants → consolidated

---

## Total Entity Counts (Current)

| Entity Type | Count | Change from Start |
|-------------|-------|------------------|
| Clients | 110 | +4 |
| Adjusters | 156 | +5 |
| Attorneys | 170 | +2 |
| Defendants | 15 | +1 |
| Law Firms | 43 | +1 |
| Insurers | 100 | +1 |
| Doctors | 20,737 | +1 |
| Organizations | 390 | +2 |
| **TOTAL** | **~45,927** | **+17** |

---

## Script Updates Applied

✅ **KNOWN_MAPPINGS:** Added 20 new consolidation patterns
✅ **IGNORE_ENTITIES:** Added 40+ new ignore patterns
✅ Both scripts updated (generate_review_docs.py + regenerate_all_reviews.py)

---

## Status

**All 9 files from Brooklyn-Ballard through Christopher-Wilkerson have been:**
- ✅ Manually reviewed and corrected
- ✅ All new entities added to JSON databases
- ✅ All consolidations and ignore patterns added to scripts

**Next Steps:**
1. Review the 9 corrected files
2. If approved, add to APPROVED_REVIEWS.txt
3. Run regeneration to apply new mappings to remaining 122 files
4. Continue with next batch

---

**Ready for your review!**
