---
name: medical-records-review
description: Use when analyzing medical records for personal injury legal cases - orchestrates 8 specialized sub-agents through 5-phase pipeline to generate attorney-ready medical analysis reports from case folders containing medical records, bills, and litigation documents
---

# Medical Records Review Workflow

## Overview

Comprehensive medical records analysis workflow for personal injury legal cases. Coordinates 8 specialized sub-agents to analyze medical records, medical bills, and litigation documents, producing attorney-ready summaries with chronology, causation analysis, and strategic recommendations.

## When to Use This Skill

Use this skill when:
- User requests medical records analysis for a personal injury case
- Case folder contains medical records, medical bills, and litigation documents
- Need comprehensive attorney-ready summary with chronology, causation, gap analysis, and strategic recommendations
- Analyzing settlement value or case strengths/weaknesses
- Preparing for depositions or expert witness selection

## Case Folder Structure Expected

The skill expects a case folder in workspace with this structure:

```
/case_name/
├── [Complaint PDF]                    # At root level
├── litigation/
│   ├── discovery/                     # Depositions, interrogatories
│   └── investigation/                 # Police reports, photos, evidence
├── medical_bills/                     # All medical billing documents
└── medical_records/                   # All medical record PDFs
```

Example: `/mo_alif/` folder with complaint, litigation subfolder, medical_bills/, and medical_records/.

## Workflow: 5-Phase Medical Analysis Pipeline

### Phase 0: Setup and Verification

**Before spawning any agents, verify:**

1. **Case folder exists in workspace**
   - Use `ls /` to confirm case folder is present
   - Verify folder structure matches expected format

2. **Required files present**
   - Complaint document (usually at root level, PDF with "complaint" in name)
   - Litigation documents folder (litigation/discovery/ and/or litigation/investigation/)
   - Medical records folder with PDFs (medical_records/)
   - Medical bills folder with PDFs (medical_bills/)

3. **Create reports directory**
   - `mkdir -p /case_name/reports` to store sub-agent outputs
   - This is where intermediate reports will be saved

**If setup fails:** Stop and inform user of missing requirements.

### Phase 1: Fact Investigation (Sequential)

**Objective:** Build factual case background from litigation documents.

**Sub-agent to spawn:** `fact-investigator`

**Task instructions:**
```
Read the litigation documents in the case folder and build a comprehensive factual background:
- Read the complaint document at the root level
- Read police reports in litigation/investigation/
- Read depositions in litigation/discovery/
- Read interrogatories and other discovery documents

Extract and summarize:
- Incident details (date, location, type, mechanism)
- Parties involved (plaintiff, defendants, witnesses)
- Legal claims asserted
- Claimed injuries
- Key facts relevant to medical causation

Save your findings to /case_name/reports/case_facts.md
```

**Wait for completion** before proceeding to Phase 2.

**Output file:** `/case_name/reports/case_facts.md`

### Phase 2: Medical Organization & Extraction (Parallel)

**Objective:** Inventory all medical records/bills AND extract all visit/billing data via batch processing.

This phase uses parallel batch processing to handle large volumes of medical documents efficiently.

#### 2a. Organizer Sub-agent (Runs in parallel with extraction)

**Sub-agent:** `organizer`

**Task instructions:**
```
Scan and organize all medical records and bills in the case folder:
- List and classify files in medical_records/
- List and classify files in medical_bills/
- Read files strategically (bills first, then key records) for overview
- Build comprehensive inventory with dates, providers, types, key findings
- Identify initial gaps (missing records, incomplete sets, treatment gaps)

Save your inventory to /case_name/reports/inventory.md
```

**Output file:** `/case_name/reports/inventory.md`

#### 2b. Batch Document Extraction (Main agent orchestrates)

**Process:**

1. **List all documents:**
   ```
   Use ls to list:
   - All files in /case_name/medical_records/
   - All files in /case_name/medical_bills/
   ```

2. **Create extraction output directory:**
   ```
   mkdir -p /case_name/reports/extractions/
   ```

3. **Batch processing loop:**
   - Group files into batches (1-2 files per extractor)
   - Spawn 3-4 `record-extractor` agents in parallel
   - Each extractor gets assigned specific file(s):
     ```
     Extract all visit and billing data from:
     - /case_name/medical_records/file1.pdf
     - /case_name/medical_records/file2.pdf

     Save your extraction to /case_name/reports/extractions/file1_file2_extraction.md
     ```
   - Wait for batch to complete
   - Spawn next batch of extractors until all files processed

4. **Monitor progress:**
   - Track which files have been processed
   - As extraction reports complete, optionally begin incremental chronology synthesis
   - Continue until all documents extracted

**Output:** Multiple extraction reports in `/case_name/reports/extractions/`

#### 2c. Chronology Synthesis (Main agent builds)

**After all extractions complete**, the main agent synthesizes the chronology:

1. **Read all extraction reports** from `/case_name/reports/extractions/`
2. **Combine all extracted visits and bills**
3. **Sort chronologically** by date
4. **Build narrative chronology** with:
   - Every visit in date order
   - Citations to source documents
   - Treatment gaps identification
   - Key milestones
   - Attorney attention items
5. **Save outputs:**
   - `/case_name/reports/chronology.md` (narrative chronology)
   - `/case_name/reports/visits_summary.md` (structured data)

**Wait for organizer AND chronology synthesis to complete** before proceeding to Phase 3.

### Phase 3: Parallel Analysis (4 agents in parallel)

**Objective:** Comprehensive analysis of medical records across 4 dimensions.

**Spawn these 4 sub-agents in PARALLEL:**

#### 3a. Inconsistency Detector

**Sub-agent:** `inconsistency-detector`

**Task instructions:**
```
Analyze medical records for inconsistencies:
- Read /case_name/reports/chronology.md
- Read /case_name/reports/visits_summary.md
- Identify contradictions in symptoms, diagnoses, timeline, treatment
- Classify as critical/moderate/minor
- Provide impact assessment and possible explanations

Save your analysis to /case_name/reports/inconsistencies.md
```

**Output file:** `/case_name/reports/inconsistencies.md`

#### 3b. Red Flag Identifier

**Sub-agent:** `red-flag-identifier`

**Task instructions:**
```
Identify case weaknesses and red flags:
- Read /case_name/reports/chronology.md
- Read /case_name/reports/case_facts.md (for incident date)
- Identify pre-existing conditions, treatment gaps > 30 days, non-compliance, exaggeration indicators
- Classify as high/medium/low priority
- Provide defense use analysis and mitigation strategies

Save your analysis to /case_name/reports/red_flags.md
```

**Output file:** `/case_name/reports/red_flags.md`

#### 3c. Causation Analyzer

**Sub-agent:** `causation-analyzer`

**Task instructions:**
```
Analyze medical causation evidence:
- Read /case_name/reports/case_facts.md (incident details and date)
- Read /case_name/reports/chronology.md (treatment timeline)
- Read /case_name/reports/visits_summary.md (detailed visit info)
- Evaluate temporal proximity, consistency, medical opinions, alternative causes
- Identify causation strengths and weaknesses
- Provide overall assessment (Strong/Moderate/Weak)

Save your analysis to /case_name/reports/causation.md
```

**Output file:** `/case_name/reports/causation.md`

#### 3d. Missing Records Detective

**Sub-agent:** `missing-records-detective`

**Task instructions:**
```
Identify missing medical records and create acquisition plan:
- Read /case_name/reports/chronology.md
- Search medical records for tests ordered without results, referrals without notes
- Identify timeline gaps, incomplete record sets
- Classify as critical/important/supplemental
- Provide specific action steps for obtaining records

Save your plan to /case_name/reports/missing_records.md
```

**Output file:** `/case_name/reports/missing_records.md`

**Wait for ALL 4 agents to complete** before proceeding to Phase 4.

### Phase 4: Final Synthesis (Sequential)

**Objective:** Synthesize all analysis into comprehensive attorney-ready summary.

**Sub-agent to spawn:** `summary-writer`

**Task instructions:**
```
Create comprehensive medical summary synthesizing all previous analysis:
- Read /case_name/reports/case_facts.md
- Read /case_name/reports/inventory.md
- Read /case_name/reports/chronology.md
- Read /case_name/reports/inconsistencies.md
- Read /case_name/reports/red_flags.md
- Read /case_name/reports/causation.md
- Read /case_name/reports/missing_records.md

Synthesize into attorney-ready summary with:
1. Executive Summary
2. Incident and Initial Treatment
3. Treatment Timeline (narrative synthesis)
4. Current Medical Status
5. Causation Analysis
6. Strengths of Medical Case
7. Weaknesses and Red Flags
8. Missing Records (Priority Items)
9. Strategic Recommendations

Save final summary to /case_name/reports/FINAL_SUMMARY.md
```

**Wait for completion.**

**Output file:** `/case_name/reports/FINAL_SUMMARY.md`

### Phase 5: Delivery

**After summary-writer completes:**

1. Read `/case_name/reports/FINAL_SUMMARY.md`
2. Present executive summary to user
3. Inform user of complete analysis location: `/case_name/reports/`
4. Offer to answer questions or provide specific sections

## Sub-Agent Spawning Pattern (Visual)

```
Main Agent (Roscoe)
│
├─ Phase 1 (Sequential)
│  └─ spawn(fact-investigator) → [WAIT] → case_facts.md
│
├─ Phase 2 (Parallel Batch Processing)
│  ├─ spawn(organizer) ──────────────────┐
│  │                                      │
│  └─ Batch document extraction:          │
│     ├─ List all medical records/bills   │
│     ├─ Create batches (1-2 files each)  │
│     ├─ spawn(record-extractor) x3-4 ────┤
│     ├─ [WAIT for batch]                 │
│     ├─ spawn(record-extractor) x3-4 ────┤─ [WAIT FOR ALL]
│     ├─ Repeat until all files done      │     ↓
│     └─ Main agent synthesizes chronology┘  inventory.md
│                                          extractions/*.md
│                                          chronology.md
│                                          visits_summary.md
│
├─ Phase 3 (Parallel - 4 agents)
│  ├─ spawn(inconsistency-detector) ──┐
│  ├─ spawn(red-flag-identifier) ─────┤
│  ├─ spawn(causation-analyzer) ──────┤─ [WAIT FOR ALL 4]
│  └─ spawn(missing-records-detective)┘    ↓
│                                      inconsistencies.md
│                                      red_flags.md
│                                      causation.md
│                                      missing_records.md
│
├─ Phase 4 (Sequential)
│  └─ spawn(summary-writer) → [WAIT] → FINAL_SUMMARY.md
│
└─ Phase 5 (Delivery)
   └─ Present final summary to user
```

## File Organization in Workspace

All sub-agents work within the case folder in workspace:

```
/case_name/
├── [litigation documents]           # Input: Read by fact-investigator
├── medical_records/                 # Input: Read by record-extractor (batch)
├── medical_bills/                   # Input: Read by record-extractor (batch)
└── reports/                         # Output: All sub-agent reports
    ├── case_facts.md               # Phase 1 output
    ├── inventory.md                # Phase 2 output (organizer)
    ├── extractions/                # Phase 2 output (record-extractors)
    │   ├── file1_extraction.md
    │   ├── file2_extraction.md
    │   └── [more extractions...]
    ├── chronology.md               # Phase 2 output (main agent synthesis)
    ├── visits_summary.md           # Phase 2 output (main agent synthesis)
    ├── inconsistencies.md          # Phase 3 output
    ├── red_flags.md                # Phase 3 output
    ├── causation.md                # Phase 3 output
    ├── missing_records.md          # Phase 3 output
    └── FINAL_SUMMARY.md            # Phase 4 output (primary deliverable)
```

## Common Mistakes to Avoid

### 1. Skipping Fact Investigation
**WRONG:** Jump straight to medical organization
**RIGHT:** Always start with fact-investigator to establish incident context
**WHY:** Causation analysis needs incident date and mechanism of injury

### 2. Running Analysis Before Chronology Completes
**WRONG:** Spawn Phase 3 agents before chronology synthesis finishes
**RIGHT:** Wait for all extractions AND chronology synthesis before Phase 3
**WHY:** All 4 Phase 3 agents need chronology.md to perform analysis

### 3. Not Using Batch Processing for Extraction
**WRONG:** Spawn one record-extractor for all 50+ documents
**RIGHT:** Batch process with 3-4 extractors running in parallel, each handling 1-2 files
**WHY:** Avoids context window overflow, enables parallel processing, fault-tolerant

**WRONG:** Process files sequentially (spawn extractor, wait, spawn next...)
**RIGHT:** Spawn 3-4 extractors in parallel, then next batch when ready
**WHY:** Parallel execution is 3-4x faster

### 4. Serializing What Should Be Parallel
**WRONG:** Spawn organizer, wait for completion, then start extractions
**RIGHT:** Spawn organizer in parallel with extraction batch processing
**WHY:** Organizer and extractors are independent

**WRONG:** Spawn 4 Phase 3 agents sequentially
**RIGHT:** Spawn all 4 in parallel
**WHY:** All read same inputs - parallel execution is 4x faster

### 5. Spawning Summary Before Analysis Complete
**WRONG:** Spawn summary-writer while Phase 3 agents still running
**RIGHT:** Wait for all 4 Phase 3 agents to complete
**WHY:** Summary needs all 7 previous reports to synthesize

### 6. Not Creating Reports Directories
**WRONG:** Let sub-agents try to write to /case_name/reports/ without creating it first
**RIGHT:** Create directories in Phase 0: `mkdir -p /case_name/reports/extractions`
**WHY:** Sub-agents will fail if output directories don't exist

### 7. Wrong Case Folder Path
**WRONG:** Point to absolute filesystem path outside workspace
**RIGHT:** Use workspace-relative path like `/mo_alif/`
**WHY:** FilesystemBackend is sandboxed to workspace - paths are virtual

### 8. Not Verifying Files Before Starting
**WRONG:** Spawn fact-investigator without checking complaint exists
**RIGHT:** Use `ls` commands in Phase 0 to verify structure
**WHY:** Better to fail fast than halfway through workflow

## Handling Errors and Edge Cases

### Missing Files
If expected files are missing:
- Document what's missing in your response to user
- Continue with available files
- Note limitations in analysis
- Skip phases that can't proceed (e.g., skip fact investigation if no complaint)

### Large Case Folders
If case has 100+ medical records:
- All phases still proceed normally
- Sub-agents are instructed to work strategically (don't read every file)
- Trust sub-agents to prioritize critical files

### Incomplete Litigation Documents
If litigation folder is sparse:
- Fact investigator will work with what's available
- Causation may be limited without incident details
- Note limitations in final summary

## Success Criteria

You've successfully completed medical-records-review when:

✅ All 5 phases executed in correct order
✅ All sub-agents completed without errors
✅ All medical documents extracted via batch processing
✅ Chronology synthesized by main agent from extraction reports
✅ Reports directory contains all output files (case_facts, inventory, extractions/*, chronology, visits_summary, analysis reports, FINAL_SUMMARY)
✅ FINAL_SUMMARY.md exists and synthesizes all analysis
✅ User receives executive summary and location of full analysis

## Example Usage

**User:** "I need a medical records analysis for the mo_alif case using the medical-records-review skill."

**Roscoe's workflow:**

1. **Phase 0:** Verify `/mo_alif/` exists, check for complaint, medical records, bills, litigation folder. Create `/mo_alif/reports/` and `/mo_alif/reports/extractions/`.

2. **Phase 1:** Spawn fact-investigator → "Read litigation documents in /mo_alif/ and create case_facts.md"

3. **Phase 2a:** Spawn organizer → "Inventory all medical records and bills"

4. **Phase 2b:** Batch extraction:
   - List all files in medical_records/ and medical_bills/
   - Create batches (1-2 files per extractor)
   - Spawn 3-4 record-extractors in parallel for first batch
   - Wait for batch completion, spawn next batch
   - Repeat until all files extracted

5. **Phase 2c:** Main agent synthesizes chronology from all extraction reports → Save chronology.md and visits_summary.md

6. **Phase 3:** Spawn 4 analysis agents in parallel → "Analyze for inconsistencies, red flags, causation, and missing records"

7. **Phase 4:** Spawn summary-writer → "Synthesize all reports into FINAL_SUMMARY.md"

8. **Phase 5:** Read and present executive summary from FINAL_SUMMARY.md to user

**Result:** User receives comprehensive medical-legal analysis in `/mo_alif/reports/FINAL_SUMMARY.md` with all supporting analysis documents and extraction data.

## Notes for Main Agent

- Use the `task` tool to spawn sub-agents
- For parallel execution, spawn multiple agents in same task invocation
- Each sub-agent has access to FilesystemBackend tools (ls, read_file, grep, write_file)
- Monitor progress and inform user of phase transitions
- If a sub-agent fails, document the error and continue with remaining phases if possible
- The FINAL_SUMMARY.md is the primary deliverable - ensure it's complete before finishing

This skill transforms complex multi-node graph architecture into simple sequential/parallel sub-agent orchestration, making medical records analysis more flexible, maintainable, and powerful.
