# Medical Term Research Process

## Why Research Is Required

The agent must NOT generate medical definitions from memory. All definitions must be:
1. Researched from authoritative sources
2. Cited with source name and URL
3. Written in patient-friendly language

## Authoritative Sources

| Source | URL | Best For |
|--------|-----|----------|
| **Mayo Clinic** | mayoclinic.org | Conditions, symptoms, treatments |
| **Cleveland Clinic** | clevelandclinic.org | Procedures, anatomy, conditions |
| **MedlinePlus** | medlineplus.gov | Patient-friendly, medications |
| **Radiopaedia** | radiopaedia.org | Imaging, radiology terms |
| **Physiopedia** | physio-pedia.com | Physical therapy, anatomy |
| **WebMD** | webmd.com | General conditions (secondary) |

## Research Workflow

### Step 1: Identify Unknown Terms

As you process records, note terms that:
- Are unfamiliar to lay readers
- Are diagnoses that need explanation
- Are procedures being recommended
- Have legal significance for the case

### Step 2: Search Authoritative Source

Use internet search with site restriction:

```bash
# Search Mayo Clinic
"cervical radiculopathy definition site:mayoclinic.org"

# Search Cleveland Clinic
"lumbar fusion procedure site:clevelandclinic.org"

# Search MedlinePlus
"tramadol medication site:medlineplus.gov"
```

### Step 3: Extract Definition

From the search result, extract:
- Clear, patient-friendly definition
- Key symptoms or characteristics
- Relevance to the case

### Step 4: Format Citation

```json
{
  "type": "definition",
  "term": "Cervical Radiculopathy",
  "text": "A condition where nerve roots in the neck are compressed or irritated, causing pain, numbness, or weakness that radiates into the shoulder and arm.",
  "source": "Mayo Clinic",
  "url": "https://www.mayoclinic.org/diseases-conditions/cervical-radiculopathy/symptoms-causes/syc-20370451"
}
```

## Common Terms by Category

### Orthopedic Terms
- Radiculopathy
- Herniated disc / Bulging disc
- Stenosis (spinal, foraminal)
- Spondylosis / Spondylolisthesis
- Arthritis / Arthrosis
- Strain / Sprain

### Neurological Terms
- Neuropathy
- Paresthesia
- Myelopathy
- Concussion / TBI

### Imaging Terms
- MRI findings
- CT findings
- X-ray findings
- Degenerative changes

### Procedural Terms
- Epidural steroid injection
- Facet injection
- Discectomy
- Fusion
- Laminectomy

### Medication Terms
- Analgesics
- NSAIDs
- Muscle relaxants
- Neuropathic pain medications

## Citation Format in Chronology

In the comments column:

```
**Radiculopathy**: Compression or irritation of nerve roots causing pain, 
numbness, or weakness that radiates along the nerve pathway.
*Source: Mayo Clinic (mayoclinic.org)*
```

## Quality Checklist

Before including a definition:
- [ ] Sourced from authoritative medical website
- [ ] URL is specific to the term (not generic page)
- [ ] Definition is accurate and complete
- [ ] Written in patient-friendly language
- [ ] Relevant to the specific case context

## Do Not Research

Some terms don't need definitions:
- Common medications (Tylenol, Ibuprofen)
- Basic anatomy (neck, back, arm)
- General terms (pain, swelling, bruising)
- Obvious procedures (X-ray, blood test)

## Research Cache

Once a term is researched, add to case cache to avoid re-researching:

```json
{
  "term": "Cervical Radiculopathy",
  "definition": "...",
  "source": "Mayo Clinic",
  "url": "...",
  "date_researched": "2024-12-14"
}
```

Reference cached terms for subsequent entries using the same term.

