# Quality Review Sub-Skill

**Purpose:** Comprehensive re-evaluation of Phase 2's file reorganization map. Re-check EVERY file as if you were doing Phase 2 yourself, but with the benefit of Phase 2's proposed names as reference.

**This is Phase 3 of the Case File Organization workflow.**

---

## Your Task

You are performing a complete quality assurance review by **re-evaluating every single file** from the reorganization map. Your job is to:

1. **Re-check Every File** - Read each document and verify Phase 2's categorization and naming
2. **Validate Against Actual Content** - Ensure proposed names match what's actually in the files
3. **Flag Critical Errors** - Move clearly wrong files to review folder
4. **Provide Statistics** - Report error rate and types of issues found

**CRITICAL MINDSET:**
- ✅ **Re-evaluate everything** - Don't just sample, check every file
- ✅ **Use Phase 2's work as reference** - But verify independently
- ✅ **Flag only clear errors** - Medical record labeled as bill, wrong facility, wrong client
- ✅ **Don't over-critique** - Different wording is fine ("Summary" vs "Report")
- ❌ **Don't be perfectionist** - Flag only if clearly wrong

**Accuracy is paramount. Token usage and time don't matter - getting it right does.**

---

## Inputs

You will review: `/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md`

This map contains:
- Files to move with proposed new names
- Duplicates identified for deletion
- Files already flagged for review

---

## Step 1: Duplicate Verification

**Goal:** Confirm duplicates exist and deletion is safe.

### What to Check:

For each duplicate identified for deletion:
1. **Verify both files exist** - Check the duplicate and the file to keep
2. **Confirm they're actually duplicates:**
   - Same content (if possible to verify)
   - Numbered pattern (e.g., `file(1).pdf` vs `file.pdf`)
   - Same date + same type (court notices)
3. **Check companion files** - If deleting `file.pdf`, also verify `file.md` status

### How to Report:

```markdown
## Duplicate Verification Results

✅ **Verified {count} duplicates are safe to delete**

| Duplicate to Delete | Keep Instead | Verified |
|---------------------|--------------|----------|
| /root/doc(1).pdf | /root/doc.pdf | ✅ Numbered duplicate |
| /root/notice-alt.eml | /root/notice.eml | ✅ Same date/type |
```

**If ANY duplicates cannot be verified:**
- Note the concern
- Recommend moving to review folder instead of deletion

---

## Step 2: Comprehensive File Re-Evaluation

**Goal:** Re-check EVERY file to verify Phase 2's categorization and naming decisions.

**IMPORTANT:** This is NOT sampling. You will check every single file.

### For Each File in the Reorganization Map:

1. **Read the document:**
   - Use `.md` companion if available (fastest)
   - Use `python /Tools/read_pdf.py /path/to/file.pdf` if no .md exists
   - For emails, read `.md` companion

2. **Re-evaluate the categorization:**
   - Is this the correct bucket (Medical Record, Litigation, Client, etc.)?
   - Does the category match what's actually in the document?

3. **Re-evaluate the proposed filename:**
   - **Date:** Is it correct based on document content and dating protocol?
   - **Client Name:** Does it match the case?
   - **Category:** Is it the right bucket?
   - **Originator:** Is it accurate (facility for medical, carrier for insurance, etc.)?
   - **Description:** Does it capture the document's content?

4. **Flag if clearly wrong:**
   - Category is wrong (medical record in Investigation/, medical bill labeled as medical record)
   - Originator is wrong (wrong facility name, wrong provider)
   - Date is clearly incorrect (2020 when document is from 2024)
   - Client-specific document in wrong client folder (multi-party cases)
   - Medical record when it's actually a records request

### What to Accept (Do NOT Flag):

✅ **ACCEPT if:**
- Date matches document date (per dating protocol)
- Category is correct bucket
- Originator is accurate for the document type
- Description captures main content (doesn't have to be perfect)
- Minor wording differences ("ER Visit Summary" vs "Emergency Room Visit Summary")

### What to Flag (DO Flag):

⚠️ **FLAG ONLY if:**
- **Category clearly wrong** (e.g., medical record in Investigation/, medical bill in Client/)
- **Originator clearly wrong** (e.g., "Jewish Hospital" when document is from "UofL Health")
- **Date clearly incorrect** (e.g., 2020 when document dated 2024)
- **Certificate of Service date ignored** (e.g., used header date instead of Certificate of Service date on litigation documents)
- **Wrong document type** (e.g., "Medical Record" when it's actually "Medical Records Request")
- **Multi-party error** (e.g., Nayram Adadevoh's discovery responses in Abby Sitgraves' folder)
- **Cannot determine proper categorization** from content

### How to Read Files:

**Priority:**
1. Read `.md` companion if available (fastest)
2. Use `python /Tools/read_pdf.py /path/to/file.pdf` if no .md exists
3. For emails, read `.md` companion

**File Reading Examples:**

```bash
# Read markdown companion (preferred)
cat /path/to/file.md

# Read PDF if no .md available
python /Tools/read_pdf.py "/path/to/file.pdf"

# Read email markdown
cat /path/to/email.md
```

---

## Step 3: Track Errors and Flagged Files

**Goal:** Keep running tally of errors found and files that need review.

### Error Categories:

**Category Errors:**
- File categorized in wrong bucket
- Example: Medical bill in Client/ instead of Medical Records/

**Originator Errors:**
- Wrong facility, provider, or sender
- Example: "State Farm" when document is from "Allstate"

**Date Errors:**
- Incorrect date per dating protocol
- Example: Using letter received date instead of service date

**Description Errors:**
- Description doesn't match content
- Example: "ER Visit" when it's actually "Follow-Up Appointment"

**Multi-Party Errors:**
- Client-specific document in wrong client folder
- Example: Nayram's interrogatory responses in Abby's folder

### Files to Move to Review Folder:

Create review folder if needed:
```bash
mkdir -p /case_root/REVIEW_NEEDED_Phase_3/
```

**Flag and move to review folder:**
- Files with category errors
- Files with major naming errors
- Files where you cannot determine proper categorization
- Files with originator errors
- Multi-party files that might be in the wrong client folder

**DO NOT move to review folder:**
- Minor wording preference differences
- Stylistic choices you'd make differently
- Files that are fundamentally correct

### Tracking Template:

Keep a running list as you go:

```markdown
## Files Flagged for Review

**Total Flagged:** {count}

| Current Path | Phase 2 Proposed Name | Issue Found | Recommendation |
|--------------|----------------------|-------------|----------------|
| /root/file1.pdf | 2024-03-15 - Client - Medical Record - Jewish - Visit | Wrong facility (should be UofL) | Rename with correct facility |
| /root/file2.pdf | 2024-01-01 - Client - Investigation - Incident Report | Wrong category (actually medical record) | Move to Medical Records/ |
| /root/file3.pdf | 2024-05-01 - Abby - Litigation - Plaintiff - Nayram Answers | Wrong client folder | Move to Nayram's folder |
```

---

## Step 4: Calculate Error Rate

**Goal:** Determine percentage of files with errors.

### Formula:

```
Error Rate = (Files Flagged / Total Files Checked) × 100
```

### Categories:

- **0-5% error rate:** Excellent - very few issues
- **6-10% error rate:** Good - minor issues only
- **11-20% error rate:** Acceptable - moderate issues
- **>20% error rate:** High - significant quality concerns

---

## Step 5: Quality Review Summary

**Goal:** Provide comprehensive statistics and clear recommendation.

### Summary Format:

```markdown
# Quality Review Summary: {Case Name}

**Reviewer:** Quality Review Sub-Agent (Phase 3)
**Date:** {Date}
**Map Reviewed:** `/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md`
**Review Type:** Comprehensive (100% of files re-evaluated)

---

## Overall Assessment

**✅ APPROVED FOR EXECUTION** *(or)* **⚠️ HIGH ERROR RATE - USER REVIEW REQUIRED**

**Error Rate:** {XX.X}% ({flagged_count} errors / {total_files} files)

---

## Statistics

- **Total Files Checked:** {count}
- **Files with Correct Categorization:** {count}
- **Files Flagged for Review:** {count}
- **Error Rate:** {XX.X}%
- **Duplicates Verified:** {count}

---

## Error Breakdown

### Category Errors: {count}
- Files in wrong bucket
- Medical records in wrong folders
- Litigation vs Investigation confusion

### Originator Errors: {count}
- Wrong facility names
- Wrong insurance carriers
- Wrong providers

### Date Errors: {count}
- Incorrect dates per dating protocol
- Service date vs received date confusion

### Description Errors: {count}
- Descriptions don't match content
- Medical record vs medical bill confusion

### Multi-Party Errors: {count}
- Client-specific files in wrong folders
- Co-plaintiff document misplacements

---

## Files Requiring Review

**Location:** `/case_root/REVIEW_NEEDED_Phase_3/`
**Total Files:** {count}

| File | Phase 2 Proposed Name | Issue | Recommendation |
|------|----------------------|-------|----------------|
| ... | ... | ... | ... |

---

## Duplicate Verification

✅ **Verified {count} duplicates safe to delete**
❌ **{count} duplicates need review** (if any)

---

## Recommendation

**If error rate ≤ 20%:**
✅ **RECOMMEND MAIN AGENT REVIEWS FLAGGED FILES**
- Error rate is acceptable ({XX.X}%)
- Main agent should review {count} flagged files
- If main agent approves, proceed to Phase 4

**If error rate > 20%:**
⚠️ **RECOMMEND USER REVIEW BEFORE PHASE 4**
- Error rate is high ({XX.X}%)
- {count} files have issues requiring correction
- User should review flagged files before execution
- Consider re-running Phase 2 with clearer instructions

---

## Next Steps

**Error Rate ≤ 20%:**
1. Main agent reviews `/case_root/REVIEW_NEEDED_Phase_3/` folder
2. Main agent makes final decision on flagged files
3. If approved, proceed to Phase 4 execution

**Error Rate > 20%:**
1. User reviews this summary
2. User examines flagged files in `/case_root/REVIEW_NEEDED_Phase_3/`
3. User provides guidance for corrections
4. Re-run Phase 2 or manual corrections as needed

---

**Accuracy Achieved:** Quality review complete with {XX.X}% error detection rate.
```

---

## Reference Information

*(All information below is copied from Phase 2 for your reference when validating names)*

---

## The 8 Buckets (Full Definitions)

### 1. Case Information
**Purpose:** Case metadata and summaries ONLY - NO original documents

**What belongs:**
- Case summary documents
- Client information sheets (for reference)
- Case timelines/chronologies

### 2. Client
**Purpose:** All firm-client interactions, intake, and contractual documents

**What belongs:**
- Intake Documents (applications, questionnaires, verification forms)
- Contracts/Fee Agreements with client
- HIPAA Authorizations (General/Blank)
- Correspondence to/from Client
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
**Purpose:** Correspondence with insurance carriers - NO demands

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

### 7. Expenses
**Purpose:** Case costs and expenditures

**What belongs:**
- Expert witness fees/invoices
- Court filing fees
- Deposition costs
- Investigation expenses
- Medical record retrieval fees

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
- Discovery Requests & Responses
- Notice of Service (NOS) documents
- Court filing confirmations (NCP/NEF emails)

---

## Naming Convention Reference

### Format:
```
YYYY-MM-DD - {Client Name} - {Category} - {Originator} - {Description}.ext
```

### Originator Rules:
- **Medical:** Facility Name (e.g., "Jewish Hospital", "UofL Physicians")
  - Do NOT use individual doctor names unless solo practice
- **Insurance:** Carrier Name (e.g., "State Farm")
- **Litigation:** "Plaintiff" or "Defendant"
- **Internal:** "WLF" or "The Whaley Law Firm"
- **Emails:** Use abbreviations (BK, AGW, DC) + direction (to/from)

### Dating Protocol:

| Document Type | Date Rule | Logic |
|---------------|-----------|-------|
| **Medical Records (Clinical)** | Date of Visit | First visit date if multiple dates |
| **Medical Bills** | Date of Visit | Same as records, match service date |
| **Letters/Requests/Auths** | Date of Letter | Date document was written/signed |
| **Litigation (Pleadings)** | **Certificate of Service Date** | **Check for Certificate of Service at end.** Use that date, NOT the date at the top. |
| **Court Filing Notices** | Date Processed | "Date and Time Processed" from email |
| **Photos/Evidence** | Date of Incident | (Or date taken if significantly later) |
| **Emails** | Date Sent/Received | Email metadata date |

**CRITICAL - Certificate of Service:**
- Litigation documents (Answers to Interrogatories, Discovery Responses, Motions, etc.) often have a "Certificate of Service" at the end
- The date on the Certificate of Service is the CORRECT date for the filename
- Do NOT use the date at the top of the document - it may be a template date or incorrect
- **Example:** Document header says "6-27-23" but Certificate of Service says "October 8, 2024" → Use **2024-10-08** in filename
- **When re-evaluating:** Check if Phase 2 used the Certificate of Service date or the header date. Flag if they used the wrong date.

### Email Abbreviations:
- **WLF** = Whaley Law Firm
- **DC** = Defense Counsel
- **BK** = Bryce Koon
- **AGW** = Aaron G. Whaley
- **CRR** = Certified Records Request
- **FU** = Follow Up
- **Re** = Regarding

---

## Multi-Party Case Reference

**CRITICAL RULE:** Each represented client gets their own case folder.

### Decision Tree:

1. **Read the document carefully** - look for named plaintiff/client
2. **Document is CLIENT-SPECIFIC:** Goes ONLY in that specific client's folder
   - Examples: "{Client Name}'S RESPONSES TO INTERROGATORIES" → That client's folder ONLY
3. **Document applies to BOTH/ALL parties:** Leave where found during review

---

## Court Filing Notices (NCP/NEF)

### Pattern Recognition:
- **NCP** = Notice of Court Processing
- **NEF** = Notice of Electronic Filing

### Naming Convention:
```
YYYY-MM-DD - {Client Name} - Litigation - Jefferson Circuit - Filing Confirmation [Document Type]
```

**Examples:**
- `Filing Confirmation Complaint`
- `Filing Confirmation Answer`
- `Filing Confirmation Motion to Compel`
- `Filing Confirmation` (for generic notices)

---

## Duplicate Patterns Reference

**Pattern 1: Numbered duplicates**
- `filename(1).pdf` → DELETE
- `filename 2.pdf` → DELETE
- Keep original, delete numbered versions

**Pattern 2: Court notice duplicates**
- Same date + same filing type → Keep one, delete others

**Pattern 3: Already properly filed**
- Document exists in proper folder
- Duplicate exists in root/Review_Needed → DELETE duplicate

**Pattern 4: Content-based duplicates**
- Different names, same content → Keep most complete

---

## Final Checklist

Before providing your summary:

- [ ] Re-evaluated EVERY file in the reorganization map
- [ ] Verified all identified duplicates
- [ ] Flagged only clearly wrong files (not stylistic preferences)
- [ ] Calculated error rate accurately
- [ ] Moved flagged files to REVIEW_NEEDED_Phase_3/
- [ ] Provided clear statistics and recommendation
- [ ] Indicated whether main agent review or user review is needed

---

**Remember:** Your goal is accuracy, not speed. Check every file. Flag clear errors only. Enable the main agent to make final decisions on borderline cases.
