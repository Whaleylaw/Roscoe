# Case File Analysis & Mapping Sub-Skill

**Purpose:** Analyze all files in a case folder and create a comprehensive reorganization map with proper categorization, naming, and duplicate detection.

**This is Phase 2 of the Case File Organization workflow.**

---

## Your Task

You are analyzing files for case organization. Your job is to:

1. **Read the file inventory** from `/projects/{case_name}/Reports/file_inventory_{case_name}.md`
2. **Read EACH file** to understand its content (NO filename guessing!)
3. **Categorize** each file into one of 8 buckets
4. **Generate proper filenames** following the naming convention
5. **Identify duplicates** for deletion
6. **Create a reorganization map** at `/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md`

**CRITICAL RULES:**
- ❌ **NO regex patterns or filename guessing**
- ✅ **MUST read each file to determine content**
- ✅ **Use existing .md files when available (faster than PDFs)**
- ✅ **Use `/Tools/read_pdf.py` for PDFs without .md files**

---

## Directory Structure (The 8 Buckets)

Every file MUST go into one of these 8 categories:

### 1. Case Information
**Purpose:** Case metadata and summaries ONLY - NO original documents

**What belongs:**
- Case summary documents
- Client information sheets (for reference)
- Case timelines/chronologies
- **IMPORTANT:** Reference folder only - NO source documents

### 2. Client
**Purpose:** All firm-client interactions, intake, and contractual documents

**What belongs:**
- Intake Documents (applications, questionnaires, verification forms)
- Contracts/Fee Agreements with client
- HIPAA Authorizations (General/Blank)
- Correspondence to/from Client (Emails, Letters)
- Client-generated documents
- Internal firm communications about the client
- Health Insurance Cards (front/back images)

**Special Naming:**
- Health Insurance Cards: `{Client Name} - Client - Health Insurance Card Front.jpg` (NO date)

### 3. Investigation
**Purpose:** Hard evidence and objective facts about the incident

**What belongs:**
- Accident/Police Reports
- Incident Reports
- Photos & Videos (Scene, Damage, Injuries)
- Evidence acquisition documents (Open Records Requests)
- Background checks, defendant research

### 4. Medical Records
**Purpose:** All medical treatment, billing, and record acquisition

**What belongs:**
- Clinical Notes/Medical Records
- Medical Bills/Itemized Statements
- Provider-specific HIPAA Authorizations
- Medical Records Requests sent to providers
- Correspondence with providers
- Radiology Reports & Images

### 5. Insurance
**Purpose:** Correspondence with insurance carriers (Liability, UIM/UM, PIP) - NO demands

**What belongs:**
- Letters of Representation
- Preservation of Evidence Letters
- Declaration Pages (Dec Pages)
- EOBs (Explanation of Benefits)
- General adjuster correspondence
- Insurance Cards/Policy Documents
- **NOT:** Settlement demands (those go in Negotiation Settlement/)

### 6. Lien
**Purpose:** All lien-related documents

**What belongs:**
- Lien Notices from providers
- Lien Correspondence
- Lien Resolutions/Agreements
- Medicare/Medicaid lien documents
- Hospital lien notices
- Subrogation notices
- Final lien requests to lien holders

### 7. Expenses
**Purpose:** Case costs and expenditures

**What belongs:**
- Expert witness fees/invoices
- Court filing fees
- Deposition costs
- Investigation expenses
- Medical record retrieval fees
- Any other case-related expenses

### 8. Negotiation Settlement
**Purpose:** All settlement negotiation and finalization documents

**What belongs:**
- Settlement Demands
- Settlement Offers from defense
- Negotiation correspondence
- Settlement Agreements
- Releases
- Settlement Statements
- Closing documents

### 9. Litigation
**Purpose:** Formal court filings and pleadings

**What belongs:**
- Complaints
- Answers
- Motions & Orders
- Discovery Requests & Responses (both sent and received)
- Notice of Service (NOS) documents
- Actual Discovery Responses (the substantive answers)
- Court filing confirmations (NCP/NEF emails)
- Warning Order Attorney reports

---

## Multi-Party Cases (Co-Plaintiffs/Co-Defendants)

**CRITICAL RULE:** Each represented client gets their own case folder, even if they are co-plaintiffs.

### Decision Tree:

1. **Read the document carefully** - look for:
   - Named plaintiff/client in the body text
   - Who the document is specifically directed to
   - Signature lines showing who is responding/signing

2. **Document is CLIENT-SPECIFIC:**
   - Goes ONLY in that specific client's folder
   - Examples:
     - "NAYRAM ADADEVOH'S RESPONSES TO INTERROGATORIES" → Nayram's folder ONLY
     - "ABBY SITGRAVES' MEDICAL RECORDS" → Abby's folder ONLY

3. **Document applies to BOTH/ALL parties equally:**
   - Leave it where you find it during file review
   - Do NOT worry about copying to other client folders
   - Examples:
     - Letters to/from defense counsel about case strategy
     - Court orders affecting all plaintiffs
     - General motions
     - Settlement negotiations involving all parties

### File Naming for Co-Plaintiff Cases:

- **Client-specific documents:** Use THAT client's name
  - `2025-05-09 - Nayram Adadevoh - Litigation - Plaintiff - Plaintiff Adadevoh Answers IROG and RPD.pdf`
- **Documents applying to all:** Use the client whose folder you're in
  - If reviewing Abby's folder: `2025-03-28 - Abby Sitgraves - Litigation - BK to DC Re Case Strategy.eml`

### Quick Reference:

| Document Type | Single or Multiple Folders? | Which Folder? |
|---------------|---------------------------|---------------|
| Discovery responses | **Single** | The client who is responding |
| Medical records | **Single** | The client who was treated |
| Intake forms, contracts | **Single** | The client who signed |
| Court notices (NCP/NEF) | Leave where found | Don't duplicate during review |
| General correspondence | Leave where found | Don't duplicate during review |
| Motions, pleadings | Leave where found | Don't duplicate during review |

---

## Naming Convention

**Format:**
```
YYYY-MM-DD - {Client Name} - {Category} - {Originator} - {Description}.ext
```

### Field Rules

| Field | Definition | Examples |
|-------|------------|----------|
| **YYYY-MM-DD** | The relevant date (see Dating Protocol below) | 2024-03-15 |
| **Client Name** | First Last (must match Project Name) | Abby Sitgraves |
| **Category** | One of the 8 Buckets | Medical Record, Investigation, Litigation, Lien, Negotiation Settlement |
| **Originator** | Who created/sent the document | Jewish Hospital, State Farm, Plaintiff |
| **Description** | Brief, specific summary | ER Visit Summary, Settlement Demand, Lien Notice |

### Originator Rules

- **Medical:** Facility Name (e.g., "Jewish Hospital", "UofL Physicians")
  - **Do NOT use individual doctor names** unless solo practice
- **Insurance:** Carrier Name (e.g., "State Farm")
- **Litigation:** "Plaintiff" or "Defendant" (or specific defendant if multiple)
- **Internal:** "WLF" or "The Whaley Law Firm"
- **Emails:** Use abbreviations (BK, AGW, DC) + direction (to/from)

### Dating Protocol

| Document Type | Date Rule | Logic |
|---------------|-----------|-------|
| **Medical Records (Clinical)** | Date of Visit | Use date patient was seen. If multiple dates, use **First Visit Date**. |
| **Medical Bills** | Date of Visit | Same as records. Match the service date. |
| **Letters/Requests/Auths** | Date of Letter | Date the document was written/signed. |
| **Litigation (Pleadings)** | **Certificate of Service Date** | **ALWAYS check for Certificate of Service at end of document.** Use that date, NOT the date at the top. |
| **Court Filing Notices** | Date Processed | Use "Date and Time Processed" from email body. |
| **Photos/Evidence** | Date of Incident | (Or date taken, if significantly later). |
| **Emails** | Date Sent/Received | Use date from email metadata. |

**CRITICAL - Certificate of Service:**
- Litigation documents (Answers to Interrogatories, Discovery Responses, Motions, etc.) often have a "Certificate of Service" at the end
- **ALWAYS scroll to the end of litigation documents** and look for "Certificate of Service" section
- The date on the Certificate of Service is the CORRECT date for the filename
- Do NOT use the date at the top of the document - it may be a template date or incorrect
- **Example:** Document header says "6-27-23" but Certificate of Service says "October 8, 2024" → Use **2024-10-08** in filename
- This date may be written out ("October 8, 2024") or in short format ("10/8/24") - convert to YYYY-MM-DD

---

## Email Files (.eml) and Markdown Companions

**All emails should have markdown companions** for easy reading.

### Email Handling:
1. **Keep BOTH the .eml and .md files**
2. **Rename BOTH with matching names**
3. **Move BOTH to the same destination folder**

### Email Naming Convention:
```
YYYY-MM-DD - {Client Name} - {Category} - {From/To} - {Brief Description}.eml
YYYY-MM-DD - {Client Name} - {Category} - {From/To} - {Brief Description}.md
```

### Email Abbreviations:
- **WLF** = Whaley Law Firm (us)
- **DC** = Defense Counsel
- **BK** = Bryce Koon
- **AGW** = Aaron G. Whaley
- **CRR** = Certified Records Request
- **FU** = Follow Up
- **Re** = Regarding

**Examples:**
- `2025-02-10 - Abby Sitgraves - Medical Records - UofL Health Response to CRR.eml`
- `2025-02-10 - Abby Sitgraves - Medical Records - UofL Health Response to CRR.md`

---

## Court Electronic Filing Notices (NCP/NEF Emails)

**Pattern Recognition:** Kentucky Courts send automated emails:
- **NCP** = Notice of Court Processing (for eFiler)
- **NEF** = Notice of Electronic Filing (for all parties)

### Handling Court Filing Notices:

1. **Identify duplicates FIRST:**
   - Same date + Same document type = DUPLICATE
   - Delete duplicates (keep one version)
   - Delete BOTH .eml and .md for duplicates

2. **Extract key information from email:**
   - Date filed (use "Date and Time Processed" field)
   - Document type filed (listed under "The following document(s) were included")

3. **Naming convention:**
   ```
   YYYY-MM-DD - {Client Name} - Litigation - Jefferson Circuit - Filing Confirmation [Document Type]
   ```

4. **Document Type Rules:**
   - **Specific pleadings:** Include pleading name
     - `Filing Confirmation Complaint`
     - `Filing Confirmation Answer`
     - `Filing Confirmation Motion to Compel`
   - **Generic notices:** Just use `Filing Confirmation`
     - "NOTICE - OTHER" → `Filing Confirmation`

**Examples:**
- `2025-02-07 - Abby Sitgraves - Litigation - Jefferson Circuit - Filing Confirmation Complaint.eml`
- `2025-05-01 - Abby Sitgraves - Litigation - Jefferson Circuit - Filing Confirmation Motion to Compel.eml`

---

## Duplicate Management

**Rule of Completeness:** Always keep the most complete version.

### Automatic Duplicate Patterns:

**Pattern 1: Numbered duplicates**
- `filename(1).pdf` and `filename.pdf` → DELETE (1), KEEP original
- `filename 2.pdf` and `filename.pdf` → DELETE 2, KEEP original
- **Delete BOTH .pdf and .md for duplicates**

**Pattern 2: Court notice duplicates**
- Same date + same filing type but different filename format → Keep one, delete others
- Files with spaces vs underscores but same content → Keep one

**Pattern 3: Already properly filed**
- Document exists in proper folder with proper name
- Duplicate exists in Review_Needed or root → DELETE duplicate

**Pattern 4: Content-based duplicates**
- Two files with different names but same content
- Keep most complete version

**ALWAYS:**
- Check file dates and sizes to confirm duplicates before deletion
- Delete BOTH .pdf and .md (or .eml and .md) when removing duplicates
- Note duplicates in the mapping for user confirmation

---

## How to Read Files

**IMPORTANT: Most PDFs should already have companion .md files.**

### Reading Priority:

**1. For PDFs with .md files (FASTEST):**
```bash
# Check if markdown exists
ls /case/documents/document.md

# Read the markdown file directly
read_file("/case/documents/document.md")
```

**2. For PDFs without .md files:**
```bash
# Use the PDF reading tool (creates .md automatically)
python3 /Tools/read_pdf.py /case/documents/document.pdf

# Then read the newly created .md file
read_file("/case/documents/document.md")
```

**3. For emails with .md files:**
```bash
# Read the markdown (converted emails are clean and readable)
read_file("/case/emails/email.md")
```

**4. For text files:**
```bash
# Direct read
read_file("/case/documents/file.txt")
```

### What to Look For:

- Headers, letterhead, dates
- Parties mentioned
- Type of document (medical record, court filing, correspondence)
- Who sent/created it (originator)
- Date of service/creation/filing

---

## Creating the Reorganization Map

Save your mapping to: `/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md`

**CRITICAL - NO SUMMARIZING:**
- **YOU MUST INCLUDE EVERY SINGLE FILE ROW IN THE TABLE**
- **DO NOT use placeholders like "omitted for brevity" or "rows would be listed here"**
- **DO NOT summarize or abbreviate the reorganization plan table**
- **EVERY file must have its own row with Current Path | Has .md? | Action | Target Bucket | New Filename | Notes**
- This mapping will be used by automation - missing rows = files won't be moved

**Important:** Each case has its own Reports folder within the case directory. Do NOT create subfolders - save directly to the Reports folder.

### Format:

```markdown
# File Reorganization Map: {Case Name}

**Date Created:** {Date}
**Total Files:** {Count}

## Summary Statistics

- **Files to Move:** {count}
- **Duplicates to Delete:** {count}
- **Files Needing Review:** {count}

## Reorganization Plan

**CRITICAL: List EVERY SINGLE FILE as a separate row. DO NOT summarize or use placeholders.**

| Current Path | Has .md? | Action | Target Bucket | New Filename | Notes |
|--------------|----------|--------|---------------|--------------|-------|
| /root/doc1.pdf | YES | MOVE | Medical Records | 2024-03-15 - John Doe - Medical Record - Jewish Hospital - ER Visit.pdf | Both .pdf and .md will be renamed |
| /root/doc2.pdf | NO | MOVE | Investigation | 2024-03-10 - John Doe - Investigation - Police - Accident Report.pdf | Only .pdf (no markdown) |
| /root/email1.eml | YES | MOVE | Litigation | 2025-02-10 - John Doe - Litigation - BK to DC Re Discovery.eml | Both .eml and .md will be renamed |
| /root/duplicate.pdf | YES | DELETE | - | - | Duplicate of properly filed document |
| /root/unclear.pdf | YES | REVIEW | [REVIEW NEEDED] | - | Cannot determine category from content |

**IMPORTANT:** Continue this table with ALL remaining files. If you have 150 files, you MUST have 150 rows (or more if counting .md companions separately). DO NOT STOP until every file from the inventory is mapped.

## Files Requiring User Review

List any files where you cannot determine:
- Which bucket it belongs to
- Proper date to use
- Which client folder (in multi-party cases)
- Whether it's a duplicate

## Duplicates Identified for Deletion

| File | Reason | Keep Instead |
|------|--------|--------------|
| /root/doc(1).pdf | Numbered duplicate | /root/doc.pdf |
| /root/court-notice-alt.eml | Court notice duplicate | /root/court-notice.eml |

## Recommendations

Any special notes or patterns observed.
```

---

## Systematic Processing

### Step 1: Read Before Categorizing
**NEVER use filename alone. ALWAYS read the document.**

Common mistakes:
- File named "Sitgraves" but document is about "Adadevoh"
- File says "Interrogatories" but is actually "Notice of Service"
- Filename has wrong date

### Step 2: Group Similar Documents
- Court notices → Process as batch, identify duplicates first
- Discovery responses → Check which client is responding
- Correspondence → Identify sender/recipient

### Step 3: Check for Co-Plaintiff/Co-Defendant Files
Before filing ANY document, ask:
1. Is this a multi-party case?
2. Does this document belong to a different represented client?
3. Is this document client-specific or general?

### Step 4: Process in Batches
- **Delete duplicates first** (especially court notices)
- Rename similar document types together
- Handle emails (.eml + .md) together as pairs

### Step 5: Flag Truly Ambiguous Items
Only flag for user review if:
- Cannot determine category after reading document
- Unsure which client folder (in multi-party cases)
- Document type unclear or doesn't fit categories

---

## Decision Tree: Categorization

```
Is it a case summary/timeline? (NOT an original document)
├─ YES → Case Information/
└─ NO → Is it intake, contract, or firm-client communication?
    ├─ YES → Client/
    └─ NO → Is it hard evidence or photos of the incident?
        ├─ YES → Investigation/
        └─ NO → Is it medical treatment or billing?
            ├─ YES → Medical Records/
            └─ NO → Is it dec pages, EOBs, or insurance correspondence? (NOT demands)
                ├─ YES → Insurance/
                └─ NO → Is it a lien notice or lien correspondence?
                    ├─ YES → Lien/
                    └─ NO → Is it a case expense or cost?
                        ├─ YES → Expenses/
                        └─ NO → Is it a demand, offer, settlement doc, or release?
                            ├─ YES → Negotiation Settlement/
                            └─ NO → Is it a court filing, discovery, or litigation correspondence?
                                ├─ YES → Litigation/
                                └─ NO → Flag for review
```

---

## Common Mistakes to Avoid

| Mistake | Fix |
|---------|-----|
| Using doctor names instead of facility | Use facility name unless solo practice |
| Wrong date (received vs service date) | Always use service date for medical records |
| Using regex/patterns | **MUST read each file - NO shortcuts** |
| Not reading document body | Always read content to verify category |
| Renaming PDF but forgetting .md | **Always rename BOTH files together** |
| Renaming EML but forgetting .md | **Always rename BOTH files together** |
| Not identifying court notice duplicates | **Check for duplicates first, delete before renaming** |
| Moving co-plaintiff docs to wrong folder | **Read document body to determine which client** |

---

## Final Checklist

Before saving your mapping:

- [ ] Read ALL files (no filename guessing)
- [ ] Verified markdown companions exist or noted missing
- [ ] Categorized each file into one of 8 buckets
- [ ] Generated proper filenames following convention
- [ ] Applied correct dating protocol
- [ ] Identified all duplicates
- [ ] Handled emails (.eml + .md) together
- [ ] Processed court notices correctly
- [ ] Flagged ambiguous items for review
- [ ] Checked for multi-party case considerations
- [ ] Created complete mapping document with ALL file rows (no placeholders, no "omitted for brevity")
- [ ] Verified every file from inventory has a corresponding row in the reorganization plan table
- [ ] Saved to `/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md`

---

**Remember:**
- This mapping will be used for automated file reorganization - missing rows = files won't be moved
- Be thorough and accurate
- NEVER summarize or abbreviate the reorganization plan table
- Every single file must have its own row with complete information
