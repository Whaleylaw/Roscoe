# Medical Chronology Generation

## Skill Metadata

- **ID**: medical-chronology-generation
- **Category**: medical-records
- **Model Required**: claude-sonnet-4-20250514 (or higher)
- **Tools Required**: 
  - `read_file`, `write_file` - File operations
  - `python_execute` - Run Python code and chronology_tools.py functions
  - `internet_search` - Research medical terms (Tavily API)
  - `pubmed_search` - Medical literature search (for complex terms)
  - `read_pdf` - Extract text from medical record PDFs

---

## CRITICAL: Research Requirement for Medical Information

**DO NOT hallucinate medical definitions, procedures, or anatomical information.**

When encountering medical terms, procedures, or anatomy that require definition:

1. **ALWAYS research** the term using `internet_search` tool
2. **ALWAYS cite** the source of the information
3. **ALWAYS verify** information from authoritative medical sources
4. **NEVER** make up definitions or describe procedures from memory alone

### Authoritative Sources

| Source | URL | Best For |
|--------|-----|----------|
| **MedlinePlus** | medlineplus.gov | Patient-friendly definitions, medications |
| **Mayo Clinic** | mayoclinic.org | Conditions, symptoms, treatments |
| **Cleveland Clinic** | clevelandclinic.org | Procedures, anatomy |
| **Radiopaedia** | radiopaedia.org | Imaging, radiology terms |
| **Physiopedia** | physio-pedia.com | Physical therapy, anatomy |

### How to Research

```bash
python /Tools/research/internet_search.py "cervical radiculopathy definition site:mayoclinic.org" --include-content
```

### Citation Format

```
**[Term]**: [Definition]
*Source: [Website Name] ([URL])*
```

---

## When to Use This Skill

Use this skill when:
- User requests a professional medical chronology document
- User asks to "create chronology", "generate medical summary", or "compile treatment timeline"
- Medical records have been organized and need to be synthesized
- Preparing demand documents or trial preparation materials

**DO NOT use if:**
- No medical records have been collected yet
- User only needs a simple visit list
- Records haven't been extracted/organized yet

---

## What This Skill Produces

A professional medical chronology document (PDF) with:

| Section | Content |
|---------|---------|
| **Header** | Client name, DOB, date of injury, disclaimer |
| **Chronology Table** | Date, Provider, Medical Facts, Comments, Page # |
| **Per-Visit Entry** | Visit type, history, findings, diagnoses, treatment |
| **Comments Column** | Medical definitions (CITED), red flags, causation notes |
| **Page References** | Clickable links to source PDF pages |

---

## Step-by-Step Process

### Step 1: Gather Records and Client Info

Required information:
- Client's full name
- Date of birth
- Date of injury
- All medical records (organized in `Records/Medical/`)

### Step 2: Process Each Record

For each medical record:
1. Extract date of service
2. Identify provider and specialty
3. Extract key medical facts
4. Note diagnoses and treatment

### Step 3: Research Medical Terms

For each unfamiliar term:
1. Search authoritative source
2. Extract definition
3. Add to cache with citation

Example workflow:
```bash
# Search for definition
python /Tools/research/internet_search.py "lumbar radiculopathy definition site:mayoclinic.org" --include-content

# Add to cache
python /Tools/medical_chronology/chronology_add_term.py \
  --term "Lumbar Radiculopathy" \
  --definition "Compression of nerve roots in the lower spine causing pain, numbness, or weakness radiating down the leg." \
  --source "Mayo Clinic" \
  --url "https://www.mayoclinic.org/diseases-conditions/radiculopathy" \
  --category terms
```

### Step 4: Identify Red Flags

Flag and document:
- Gaps in treatment (> 30 days)
- Inconsistent histories between visits
- Pre-existing conditions mentioned
- Causation statements by providers
- Conflicting diagnoses

### Step 5: Generate Chronology

Use the chronology tools:
```bash
python /Tools/medical_chronology/chronology_generate_pdf.py \
  --client-name "Last, First" \
  --dob "MM/DD/YYYY" \
  --injury-date "MM/DD/YYYY" \
  --entries-json /path/to/chronology_data.json \
  --output /path/to/Reports/
```

### Step 6: Merge with Source Records

Create combined PDF with clickable links:
```bash
python /Tools/medical_chronology/chronology_merge_with_records.py \
  --chronology /Reports/Chronology.pdf \
  --records /Records/all_records.pdf \
  --output /Reports/Chronology_and_Records.pdf
```

---

## Chronology Entry Format

```json
{
  "date": "04.26.2019",
  "provider": "Dr. John Smith [Orthopedic Surgery / Baptist Health / Louisville, KY]",
  "medical_facts": "INITIAL CONSULTATION\n\nHPI: 35 y/o female presenting for evaluation of neck and back pain following MVA on 04.26.2019...\n\nPHYSICAL EXAM: Cervical ROM limited...\n\nDIAGNOSES:\n- Cervical strain\n- Lumbar radiculopathy\n\nPLAN: MRI cervical and lumbar spine, PT referral...",
  "comments": [
    {
      "type": "definition",
      "term": "Radiculopathy",
      "text": "Compression or irritation of nerve roots causing pain, numbness, or weakness that radiates along the nerve pathway.",
      "source": "Mayo Clinic",
      "url": "https://www.mayoclinic.org/diseases-conditions/radiculopathy"
    },
    {
      "type": "causation",
      "text": "Provider notes 'injuries consistent with motor vehicle accident mechanism'"
    }
  ],
  "page_number": "Mills0051",
  "source_file": "Records/Medical/Baptist_Health/records.pdf"
}
```

---

## Comment Types

| Type | Purpose | Example |
|------|---------|---------|
| `definition` | Medical term explanation | "Radiculopathy: nerve compression..." |
| `red_flag` | Inconsistency or concern | "Gap in treatment from 5/1 to 7/15" |
| `causation` | Provider causation statement | "Dr. states injuries from accident" |
| `author_note` | Analyst observation | "Note conflict between ER and ortho hx" |

---

## Quality Checklist

Before finalizing:
- [ ] All visits in chronological order
- [ ] Every entry has source page reference
- [ ] All medical terms defined WITH CITATIONS
- [ ] Red flags clearly documented
- [ ] Causation statements highlighted
- [ ] Page links functional (in combined PDF)
- [ ] Professional formatting throughout
- [ ] Legal disclaimer on each page

---

## Tools Reference

| Tool | Purpose |
|------|---------|
| `chronology_add_term.py` | Add researched definition to cache |
| `chronology_lookup_term.py` | Check if term is cached |
| `chronology_analyze_terms.py` | Find terms needing research |
| `chronology_generate_pdf.py` | Generate formatted PDF |
| `chronology_merge_with_records.py` | Combine with source records |

---

## Related Skills

- `medical-record-extraction` - Extracts data from records
- `red-flag-identification` - Identifies issues in records
- `causation-analysis` - Identifies causation statements

