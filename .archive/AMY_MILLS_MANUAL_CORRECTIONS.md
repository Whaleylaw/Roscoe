# Amy Mills Manual Corrections - Action Plan

Based on user annotations in review_Amy-Mills-Premise-04-26-2019.md

---

## Attorney Section Changes

### **Remove (Filter):**
1. **Bob Hammonds** (line 51) - Ignore → Add to IGNORE_ENTITIES
2. **Defense Attorney for Forcht Bank** (line 53) - Ignore → Add to IGNORE_ENTITIES
3. **lfarah@whtlaw.com** (line 74) - Email address, not entity → Add to IGNORE_ENTITIES

### **Type Corrections:**
1. **Hon. Thomas J. Knopf (Ret.)** (lines 59, 92, 224) - Attorney/Court/Vendor sections
   - Should match: Mediator (already exists in mediators.json)
   - Action: Remove from Attorney/Court/Vendor sections, will match correctly in regeneration

2. **Sarena (Whaley Law Firm)** (line 69) - This is Serena Tuttle
   - Action: Add to KNOWN_MAPPINGS: "Sarena (Whaley Law Firm)": "Sarena Tuttle"

3. **Sarena Whaley** (line 71) - There is no Serena Whaley, it's Serena Tuttle
   - Already in WHALEY_STAFF but mapping to wrong name
   - Action: Update WHALEY_STAFF: "Sarena Whaley": ("CaseManager", "paralegal") → maps to "Sarena Tuttle"

---

## BIClaim Section Changes

### **Remove Entire Section:**
All 8 entries marked "Ignore":
- Amy Mills - personal injury claim
- Amy Mills Premise 04/26/2019
- Amy-Mills-Premise-04-26-2019
- Bodily Injury (TBI, surgeries, lost income)
- Bodily Injury claim
- Impairment of future earning capacity claim
- Personal Injury Claim
- Personal injury claim (Premise 04-26-2019)

Action: These are generic claim descriptions, not entity references. Remove entire BIClaim section.

---

## Court Section Changes

### **Match to Court Entities:**

1. **Amanda Murphy (Kentucky Courts)** (line 90)
   - Check: Is she in court_clerks.json? (Yes, she's Knox Circuit Court clerk)
   - Action: Update to match CourtClerk entity

2. **Boyd Circuit Court** (line 91) - Match with new court directory
   - Entity exists: Boyd County Circuit Court
   - Action: Update match

3. **Knox Circuit Court variants** (lines 95-101) - All should match
   - Knox Circuit Court (Knox County, Kentucky)
   - Knox Circuit Court, Division II (2 entries)
   - Knox County Clerk
   - All consolidate to: Knox County Circuit Court with Division II

---

## Defendant Section Changes

### **Corrections:**

1. **Bobby Evans** (line 105) - She is a witness. She works at the bank.
   - Current: Listed as Defendant
   - Correct: Should be Witness
   - Action: Add Bobby Evans to witnesses.json, remove from defendants

2. **Forcht Bank, NA** (line 106) - "Needs to be added as a witness" is ERROR
   - Forcht Bank is the DEFENDANT (organization)
   - Bobby Evans (who works there) is the WITNESS
   - Action: Forcht Bank stays as defendant, Bobby Evans is witness

---

## Insurer Section Changes

### **Add as LienHolder:**

1. **Aetna** (line 110) - Needs to be added as a lienholder
   - Already exists in insurers
   - Also add to lienholders.json
   - Can be both insurer AND lienholder

---

## LawFirm Section Changes

### **CRITICAL ERROR - Delete Wrong Entry:**

1. **"Whaley Harrison & Thorne, PLLC"** - User says: "There is no such thing as Whaley, Harrison, and Thorne. Delete that entry."
   - This law firm DOES NOT EXIST
   - It was created in error
   - Action: Delete from lawfirms.json
   - Remove alias mapping "WHT Law" → "Whaley Harrison & Thorne"

2. **WHT Law** (line 116) - NO, it's Ward, Hocker & Thornton, PLLC
   - Correct mapping: "WHT Law" → "Ward, Hocker & Thornton, PLLC"
   - Action: Update KNOWN_MAPPINGS

3. **Whitt, Catron & Henderson (WHTLaw)** (line 121) - It's Ward, Hocker & Thornton
   - Action: Add to KNOWN_MAPPINGS

---

## MedicalProvider Section Changes

### **Add to Vendors:**

1. **Commonwealth IME** (lines 157-158) - Need to be added as a vendor
   - Currently in organizations (from directory)
   - Action: Add to vendors.json

### **Doctors:**

1. **Dr. Lisa Mandarino** (line 167) - Works for Aptiva
   - Note spelling: Mandarino (user's spelling) vs Manderino (in file)
   - Action: Search doctors.json for Lisa Mand* and match

---

## Organization Section Changes

### **Type Corrections:**

1. **Alexander Landfield PLLC** (line 208) - This is a Dr.
   - Actually a medical practice/doctor
   - Action: Flag for research - is this Dr. Alexander Landfield?

2. **NADA, NADN variants** (lines 211-215) - All = National Academy of Distinguished Neutrals
   - Consolidate all 5 variants to one
   - Action: Add to KNOWN_MAPPINGS

3. **National Academy of Distinguished Neutrals** (line 214) - Needs to be added as a vendor
   - Currently in organizations
   - Action: Add to vendors.json

4. **PMR Life Care Plans, LLC** (line 216) - Needs to be added as a vendor expert
   - Action: Add to vendors.json with vendor_type="expert_witness" or "life_care_planner"

5. **Retired Judges Mediation & Arbitration Services** (line 217) - Thomas Knopf mediator
   - Action: Add to organizations.json (mediation service company)
   - Link to Hon. Thomas J. Knopf (Ret.) mediator

---

## Vendor Section Changes

### **Add Entities from Directory:**

Several are matched "from directory" but not yet in vendors.json:

1. **Aptiva Health** (line 220) - from directory
   - Action: Already in medical_providers, OK

2. **BioKinetics** (line 221) - from directory
   - Action: Add to vendors.json (biomechanics expert)

3. **Commonwealth IME** (line 222) - from directory
   - Action: Add to vendors.json (duplicate from Organization section)

4. **David Johnson** (line 223) - from directory
   - Action: Add to vendors.json

5. **Linda Jones** (line 225) - Economist expert witness
   - Action: Create Expert entity, link to Vocational Economics

6. **Vocational Economics** (line 230) - Linda Jones' company
   - Action: Add to vendors.json
   - Link: Linda Jones (Expert) -[WORKS_AT]-> Vocational Economics (Organization)

---

## Entities to Add to JSON Files

### **Witnesses:**
- Bobby Evans (works at Forcht Bank)

### **LienHolders:**
- Aetna (also exists as Insurer)

### **Vendors:**
- Commonwealth IME (from directory)
- National Academy of Distinguished Neutrals (NADN) (from directory)
- PMR Life Care Plans, LLC (life care planner expert)
- BioKinetics (from directory - biomechanics)
- David Johnson (from directory)
- Vocational Economics (from directory)

### **Experts:**
- Linda Jones (economist, works at Vocational Economics)

### **Organizations:**
- Retired Judges Mediation & Arbitration Services, Inc. (Thomas Knopf's company)

### **CourtClerks:**
- Amanda Murphy (Knox Circuit Court) - verify she's in court_clerks.json

### **Mediators:**
- (Hon. Thomas J. Knopf already exists - just needs to match)

---

## Entities to DELETE

### **LawFirms:**
- ❌ Whaley Harrison & Thorne, PLLC (DOES NOT EXIST per user)

---

## Mappings to Update

### **KNOWN_MAPPINGS to Add:**
```python
"WHT Law": "Ward, Hocker & Thornton, PLLC",  # NOT Whaley Harrison & Thorne
"Whitt, Catron & Henderson (WHTLaw)": "Ward, Hocker & Thornton, PLLC",
"Sarena (Whaley Law Firm)": "Sarena Tuttle",
"NADA": "National Academy of Distinguished Neutrals",
"NADN": "National Academy of Distinguished Neutrals",
"NADN (America's Premier Mediators & Arbitrators)": "National Academy of Distinguished Neutrals",
"National Arbitration and Dispute Association": "National Academy of Distinguished Neutrals",
```

### **IGNORE_ENTITIES to Add:**
```python
"Bob Hammonds",
"Defense Attorney for Forcht Bank",
"lfarah@whtlaw.com",
# All BIClaim generic descriptions (8 entries)
```

---

## Court Matching

**Knox County Circuit Court:**
- Currently shows "Knox Circuit Court" variants
- Need to match to: Knox County Circuit Court, Division II
- All 4 Knox variants consolidate

**Boyd County Circuit Court:**
- Exists in courts.json
- Match "Boyd Circuit Court" to it

**Amanda Murphy:**
- She's a CourtClerk (Knox Circuit Court, Division II)
- Currently showing as "? NEW" under Courts section
- Should match CourtClerk entity

---

## Actions Summary

**Add to JSON Files: 10 entities**
- 1 Witness
- 1 LienHolder
- 6 Vendors
- 1 Expert
- 1 Organization

**Delete from JSON Files: 1**
- Whaley Harrison & Thorne, PLLC law firm

**Update Mappings: 8**
- KNOWN_MAPPINGS additions
- IGNORE_ENTITIES additions

**Consolidations: 5**
- Knox court variants
- NADN variants
- Sarena variants
- WHT Law correction

---

**Ready to apply these changes manually. Proceed?**
