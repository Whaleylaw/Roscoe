# Workflow: Medical Chronology Completion

## Phase: demand
## Goal: Finalize comprehensive medical chronology for demand package

---

## When to Trigger

- Client finished treating
- All final records received
- Preparing demand package
- User requests final chronology

---

## Inputs Required

- All medical records
- Draft chronology from treatment phase
- Client injury information
- List of all providers

---

## Step-by-Step Process

### Step 1: Verify Record Completeness
1. Compare provider list to received records
2. Identify any missing records
3. Make final requests if needed
4. Document any intentionally excluded records

### Step 2: Review Draft Chronology
1. Load existing `chronology_draft.json`
2. Verify all visits are captured
3. Check for gaps or missing entries
4. Review existing comments and definitions

### Step 3: Research Outstanding Terms
**Use skill: medical-chronology-generation**

For any undefined medical terms:
1. Use `internet_search` tool:
   ```
   python /Tools/research/internet_search.py "[term] definition site:mayoclinic.org" --include-content
   ```
2. Extract definition from authoritative source
3. Add to research cache with citation:
   ```
   python /Tools/medical_chronology/chronology_add_term.py --term "[Term]" --definition "[Definition]" --source "[Source]" --url "[URL]"
   ```

### Step 4: Add Final Comments
For each entry, ensure:
- Medical term definitions (with citations)
- Red flags highlighted
- Causation statements noted
- Author's notes for inconsistencies
- Treatment recommendations documented

### Step 5: Identify Causation Statements
**Use skill: causation-analysis**

Search records for:
- "Caused by"
- "Related to"
- "As a result of"
- "Due to"
- "Consistent with"
- Provider opinions on causation

Document in chronology comments.

### Step 6: Generate Final PDF
Using chronology tools:
```
python /Tools/medical_chronology/chronology_generate_pdf.py \
  --client-name "[Name]" \
  --dob "[DOB]" \
  --injury-date "[Date]" \
  --entries-json Reports/chronology_data.json \
  --output Reports/ \
  --firm-name "[Firm Name]"
```

### Step 7: Merge with Source Records
Create combined PDF with clickable links:
```
python /Tools/medical_chronology/chronology_merge_with_records.py \
  --chronology Reports/[Client]_Medical_Chronology.pdf \
  --records Records/all_medical_records.pdf \
  --output Reports/[Client]_Chronology_and_Records.pdf
```

### Step 8: Quality Review
Verify final document:
- [ ] All dates in chronological order
- [ ] Every entry has page reference
- [ ] Page links are clickable (in combined PDF)
- [ ] Medical terms defined with citations
- [ ] Red flags clearly marked
- [ ] Causation statements highlighted
- [ ] Professional formatting throughout
- [ ] Disclaimer on each page

### Step 9: Attorney Review
Present to attorney:
1. Summary of treatment
2. Key findings
3. Identified issues
4. Causation support
5. Get approval

---

## Skills Used

- **medical-chronology-generation**: Generate final chronology
- **medical-record-extraction**: Final review of records
- **red-flag-identification**: Ensure all flags documented
- **causation-analysis**: Document all causation statements

---

## Completion Criteria

- [ ] All records processed
- [ ] All medical terms researched and cited
- [ ] Comments complete (definitions, red flags, causation)
- [ ] PDF generated with proper formatting
- [ ] Page links functional
- [ ] Attorney reviewed and approved

---

## Outputs

- `Reports/[Client]_Medical_Chronology.pdf`
- `Reports/[Client]_chronology_data.json`
- `Reports/[Client]_Chronology_and_Records.pdf` (combined)
- Updated `Resources/medical_research_cache.json`

---

## Phase Exit Contribution

This workflow directly satisfies:
- `medical_chronology_complete`

---

## Chronology Format Reference

| Column | Content |
|--------|---------|
| Date | MM.DD.YYYY format |
| Provider | Name [Specialty/Facility/Location] |
| Medical Facts | Detailed summary of visit |
| Comments | Definitions, red flags, causation, notes |
| Page # | Bates number with link |

---

## Citation Requirements

ALL medical definitions MUST include:
- Source name (e.g., "Mayo Clinic")
- Source URL
- Formatted: *Source: [Name] ([URL])*

Do NOT use definitions without citations.

