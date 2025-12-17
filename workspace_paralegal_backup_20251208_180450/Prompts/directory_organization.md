# 8-Bucket Directory Organization System

## Individual Case Folders (`projects/{case-name}/`)

Each case folder uses the 8-bucket organization system:

| Bucket | Purpose | Contents |
|--------|---------|----------|
| `case_information/` | Case metadata, summaries, timelines | READ-ONLY - generated reports, NOT source documents |
| `Client/` | Client-related documents | Intake docs, contracts, firm-client communication |
| `Investigation/` | Evidence and investigation | Photos, reports, hard evidence, witness statements |
| `Medical Records/` | Clinical documentation | Clinical notes, provider records (most have companion .md files) |
| `Insurance/` | Insurance documentation | Dec pages, EOBs, carrier correspondence |
| `Lien/` | Lien documentation | Lien notices, correspondence, resolutions |
| `Expenses/` | Case costs | Case costs, expert fees, filing fees |
| `Negotiation Settlement/` | Settlement process | Demands, offers, settlement docs, releases |
| `Litigation/` | Court filings | Court filings, pleadings, discovery, depositions |

## File Format Notes

- Most PDFs have companion `.md` (markdown) files from batch pre-processing
- **Always read `.md` files when available** (instant access vs re-processing PDFs)
- Both `.pdf` and `.md` files maintain matching names

## Path Examples

```
projects/Abby-Sitgraves-MVA-07-13-2024/           # Case folder root
├── case_information/                             # Generated summaries (read-only)
├── Client/                                       # Intake, contracts
├── Investigation/                                # Photos, evidence
├── Medical Records/                              # Clinical notes
│   ├── Dr_Smith_Progress_Note.pdf
│   └── Dr_Smith_Progress_Note.md                 # ← Read this one!
├── Insurance/                                    # Dec pages, EOBs
├── Lien/                                         # Lien notices
├── Expenses/                                     # Case costs
├── Negotiation Settlement/                       # Demands, offers
├── Litigation/                                   # Court filings
├── notes.json                                    # Project-specific notes
├── overview.json                                 # Project overview
├── contacts.json                                 # Project contacts
├── insurance.json                                # Project insurance
├── liens.json                                    # Project liens
├── medical_providers.json                        # Project providers
└── expenses.json                                 # Project expenses
```

## When to Use Each Bucket

### Saving New Files

- Analysis reports → `Reports/` (centralized, NOT in case folder)
- Case summaries → `case_information/`
- Client intake forms → `Client/`
- Photos/videos → `Investigation/`
- Medical records → `Medical Records/`
- Insurance documents → `Insurance/`
- Lien notices → `Lien/`
- Expense receipts → `Expenses/`
- Settlement documents → `Negotiation Settlement/`
- Court filings → `Litigation/`

### Reading Files

1. Check for `.md` companion file first
2. If no `.md`, read the `.pdf`
3. Use `ls` to explore folder contents before reading

