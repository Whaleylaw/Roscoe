# Amy Mills Review - Manual Consolidation Notes

## Attorneys to Consolidate

### Aaron G. Whaley (Whaley Law Firm - Plaintiff Counsel)
- A. G. Whaley → Aaron G. Whaley
- AW → Aaron G. Whaley
- Aaron → Aaron G. Whaley (already matched)
- Greg Whaley → Aaron G. Whaley (his middle name is Gregory, goes by Greg)

### Betsy R. Catron (Defense Counsel)
- BK → Betsy R. Catron (initials)
- Betsy → Betsy R. Catron
- Betsy R. Catron (already matched)
- Mrs. Catron → Betsy R. Catron

### Clay E. Thornton (Defense Counsel)
- Clay E. Thornton
- G. Thornton → Could be Clay or Gregg, need context

### Gregg E. Thornton (Defense Counsel)
- Gregg E. Thornton
- G. Thornton → Could be Clay or Gregg, need context
**Note:** Clay and Gregg are different people unless they're the same person with name variation

### Thomas J. Knopf (Retired Judge - Mediator)
**Entity Type:** Should be MEDIATOR, not Attorney
- Hon. Thomas J. Knopf → Mediator
- Hon. Thomas Knopf → Mediator
- Hon. Judge Thomas Knopf → Mediator
- Judge Knopf → Mediator
- Knopf → Mediator
- Thomas Knopf → Mediator
- Hon. Thomas J. Knopf (Ret.) → Mediator
**Organization:** Thomas J. Knopf Mediation Services

### Sarena Tuttle (Whaley Law Firm - Case Manager)
**Already correctly consolidated** - all matched to Sarena Tuttle (WHALEY STAFF)

### Bryce Koon (Whaley Law Firm - Plaintiff Counsel)
- W. Bryce Koon, Esq. → already matched
- Bryce Whaley → This is Bryce Koon (works at Whaley Law Firm, not named Whaley)

---

## Courts to Consolidate

### Knox Circuit Court
All of these are the same court:
- Knox → Knox Circuit Court
- Knox Cir II → Knox Circuit Court, Division II
- Knox Circuit Court
- Knox Circuit Court (Kentucky)
- Knox Circuit Court (Knox County, Kentucky)
- Knox Circuit Court, Division II
- Knox Circuit Court, Division II (Civil Action 20-CI-00112) → same court, just with case number
- Knox Circuit II → Knox Circuit Court, Division II
- Knox County → Knox Circuit Court
- Knox County Circuit Court → Knox Circuit Court (matched wrong to Boone County!)
- Knox Division 2 → Knox Circuit Court, Division II

**Knox County Clerk** → Organization, not Court

---

## Law Firms to Consolidate

### WHT Law / Whaley Harrison & Thorne
**Research needed:** Multiple variations, unclear if same firm or different:
- WHT Law (7 variants with different domains/addresses)
- Whaley Harrison & Thorne (WHT Law) → suggests WHT = Whaley Harrison & Thorne
- Whitt, Catron & Henderson (WHTLaw) → Different firm? "Whitt" vs "Whaley"
- Vine Center (appears 4 times) → Could be building/location, not law firm

**My analysis:**
- "Whaley Harrison & Thorne" appears to be the full name
- "WHT Law" is the short form
- "Vine Center" is likely the office location/building
- "Whitt, Catron & Henderson" is a DIFFERENT law firm (Whitt ≠ Whaley, Catron ≠ Harrison)

**Consolidation:**
- **Group 1:** Whaley Harrison & Thorne (WHT Law)
  - WHT Law
  - WHT Law (Vine Center)
  - WHT Law (www.whtlaw.com)
  - WHT Law (www.whtlaw.com / Vine Center)
  - WHT Law Center
  - WHT Law Firm
  - Whaley Harrison & Thorne (WHT Law)
  - www.whtlaw.com

- **Group 2:** Whitt, Catron & Henderson (DIFFERENT FIRM)
  - Whitt, Catron & Henderson (WHTLaw)

- **Group 3:** The Whaley Law Firm (DIFFERENT FIRM - Plaintiff counsel)
  - The Whaley Law Firm, PSC (already matched)
  - Whaley Law Firm (whaleylawfirm.com)
  - Whaley Law Office
  - WhaleyLawFirm

- **Group 4:** Ward, Hocker & Thornton, PLLC
  - Ward, Hocker & Thornton, PLLC
  - Ward Hawker at Thornton → should be "Ward, Hocker & Thornton" (Hawker is typo for Hocker)

### Other Law Firms
- DECAMILLIS & MATTINGLY, PLLC → new
- EMWN Law → new (emwnlaw.com is same)
- Sturgill Turner → new

---

## Doctors to Extract (from MedicalProvider)

These should be **Doctor entities** (with WORKS_AT relationship):

### Dr. Wallace Huff (Orthopedic)
- Dr. Huff → Dr. Wallace Huff
- Dr. Wallace Huff (already matched to directory)
- Wallace L. Huff → Dr. Wallace Huff
**Works at:** Bluegrass Orthopaedics

### Dr. Cyna Khalily
- Dr. Khalily → Dr. Cyna Khalily
- Dr. Cyna Khalily (already matched)
**Works at:** Unknown (need context)

### Dr. Gregory Nazar
- Dr. Nazar → Dr. Gregory Nazar
- Dr. Gregory Nazar (already matched)
- Nazar → Dr. Gregory Nazar
**Works at:** Commonwealth IME

### Dr. Kevin Magone
- Dr. Magone → Dr. Kevin Magone, MD
- Dr. Kevin Magone, MD
**Works at:** Unknown

### Dr. Lisa Manderino
- Dr. Manderino → Dr. Lisa Manderino
- Dr. Lisa Manderino (Aptiva) → already shows affiliation
**Works at:** Aptiva Health

### Dr. Marc Orlando
- Dr. Orlando → Dr. Marc Orlando
- Marc Orlando (already matched)
**Works at:** Unknown

### Other Doctors (Need more info)
- Dr. Alsorogi
- Dr. Barefoot
- Dr. Hunt
- Dr. Paul McCombs
- Dr. Richard Edelson
- Dr. Shannon Voor
- Dr. Ronald Dubin (already in provider name: "Kentucky Orthopedic Clinic - Dr. Ronald Dubin")

---

## Experts to Extract

### Vocational Experts
- **Linda Jones** (Person - Expert entity)
  - Works at: Vocational Economics (Organization)
- **David Johnson** (Person - Expert entity, matched from directory)
  - Works at: Unknown

### Life Care Planners
- **PMR Life Care Plans, LLC** → Organization (expert firm)

### Biomechanics/Engineering
- **BioKinetics** → Organization (expert firm)
- **Brian Dietsche** → Expert (person)

### Independent Medical Examination
- **Commonwealth IME** → Organization (IME firm)
- **Dr. Gregory Nazar** → Doctor/Expert working at Commonwealth IME

---

## Mediators to Extract

### Hon. Thomas J. Knopf (Retired Judge)
**Consolidate all these as MEDIATOR entity:**
- Hon. Thomas J. Knopf
- Hon. Thomas Knopf
- Hon. Judge Thomas Knopf
- Judge Knopf
- Knopf
- Thomas Knopf
- Hon. Thomas J. Knopf (Ret.)

**Organization:** Thomas J. Knopf Mediation Services

### Mediation Organizations
- National Academy of Distinguished Neutrals (NADN) → Organization
- Retired Judges Mediation & Arbitration Services, Inc. → Organization

---

## Generic Terms to IGNORE

### Attorneys
- Counsel → ignore (too generic)
- DC → ignore (generic abbreviation)
- Defense Attorney for Forcht Bank → ignore (describes role, not name)
- Defense Counsel (DC) → ignore
- Defense attorney → ignore
- Defense counsel → ignore

### Courts
- Court (CourtNet) → ignore
- CourtNet → ignore (software system)
- Courts → ignore
- Amanda Murphy (Kentucky Courts) → Amanda Murphy is person, not court

### Defendants
- Bobby Evans → need context (could be defendant or someone else)
- Defendants → ignore
- Jason → ignore (first name only)
- Walter, Casey → need context

### BIClaim
All the generic claim descriptions should be IGNORED:
- Bodily Injury (TBI, surgeries, lost income) → ignore
- Bodily Injury claim → ignore
- Impairment of future earning capacity claim → ignore
- Personal Injury Claim → ignore
- Personal injury claim (Premise 04-26-2019) → ignore

### Medical Providers
- Orthopedic specialist (unspecified) → ignore
- PCP → ignore (generic abbreviation for Primary Care Physician)
- Medical providers (unspecified) → ignore

### Organizations - Software/Tools
- Adobe Systems Incorporated → ignore
- Box → ignore (cloud storage)
- Dropbox → ignore
- Filevine → ignore (case management software)
- FreshBooks → ignore (accounting)
- Google LLC → ignore
- Mandrillapp → ignore (email service)
- RingCentral → ignore (phone system)
- Vocecon → ignore (voice recording?)
- Zoom → ignore (video conferencing)
- bellabeautyinstitute@gmail.com → ignore (email address)

### Vendors - Same Software Tools
- Box → ignore
- DocuSign → ignore
- Dropbox → ignore
- FileVine → ignore
- FreshBooks → ignore
- RingCentral → ignore
- VineSign → ignore (same as Filevine VineSign)
- Vocecon → ignore
- Zoom → ignore

---

## Action Items

1. Consolidate Aaron Whaley variants (A. G. Whaley, Greg Whaley, etc.)
2. Consolidate Betsy Catron variants (BK, Betsy, Mrs. Catron)
3. Consolidate Thomas Knopf variants and reclassify as MEDIATOR
4. Consolidate Knox Circuit Court variants
5. Research and consolidate WHT Law variants (Whaley Harrison & Thorne)
6. Extract doctors from MedicalProvider (Dr. Huff, Dr. Nazar, etc.)
7. Identify experts and create Expert entities (Linda Jones, David Johnson, etc.)
8. Remove all generic/software entities
