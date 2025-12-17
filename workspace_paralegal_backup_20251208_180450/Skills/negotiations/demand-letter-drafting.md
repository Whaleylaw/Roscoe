# Demand Letter Drafting

## Skill Metadata

- **ID**: demand-letter-drafting
- **Category**: negotiations
- **Model Required**: opus
- **Reference Material**: education/general_practice/demand-letters/
- **Tools Required**: read_file, write_file

---

## When to Use This Skill

Use this skill when:
- Client has finished treatment (or reached MMI)
- All records and bills collected
- Damages documented
- Ready to initiate settlement negotiations

---

## Demand Letter Structure

### 1. Introduction
- Identify client and incident
- State purpose (demand for settlement)
- Reference claim number

### 2. Liability Summary
- Factual narrative of incident
- Applicable legal standards
- How defendant breached duty
- Causation connection

### 3. Injuries and Treatment
- Nature of injuries
- Treatment timeline
- Current condition
- Prognosis

### 4. Damages
- Medical expenses (itemized)
- Future medical expenses
- Lost wages
- Loss of earning capacity
- Pain and suffering
- Loss of enjoyment of life

### 5. Demand
- Specific dollar amount
- Deadline for response
- Next steps if not resolved

---

## Drafting Guidelines

### Tone
- Professional and confident
- Factual, not emotional
- Advocate but not inflammatory

### Length
- 5-15 pages typical
- Longer for complex cases
- Attachments referenced, not included in letter

### Key Elements

**Liability Section:**
- Establish duty
- Show breach
- Connect to injuries
- Cite relevant law (if helpful)

**Damages Section:**
- Lead with most compelling injuries
- Quantify everything possible
- Support non-economic damages
- Use multiplier appropriate to injuries

---

## Demand Amount Calculation

Consider:
1. Total medical specials
2. Future medical needs
3. Lost income
4. Pain and suffering multiplier
5. Policy limits
6. Venue/jury factors
7. Comparative fault

---

## Supporting Documents

Attach or reference:
- Medical chronology
- Bills summary
- Medical records
- Photos
- Police report
- Expert reports
- Wage documentation

---

## Output

- Draft demand letter
- Supporting documentation list
- Recommended demand amount with rationale

---

## Document Generation Options

### Option 1: Template-Based (Recommended for Standardized Letters)

Use the template filling tools for consistent, professional output:

```
# First, check what placeholders the template needs
list_template_variables("/forms/templates/Demand_Letter_Template.docx")

# Then fill the template
fill_word_template(
    template_path="/forms/templates/Demand_Letter_Template.docx",
    output_path="/wilson-case/Documents/Demand_Letter_StateFarm.docx",
    context={
        "client_name": "John Wilson",
        "insurance_company": "State Farm Insurance",
        "claim_number": "CLM-123456",
        "date_of_accident": "January 15, 2024",
        "total_medical": "$45,678.90",
        "demand_amount": "$150,000.00",
        "response_deadline": "30 days",
        # ... additional fields from case data
    },
    export_pdf=True
)
```

### Option 2: Custom Draft (For Complex/Unique Cases)

For cases requiring unique narrative or non-standard structure:
1. Draft content in Markdown
2. Convert to DOCX using docx-js
3. Export to PDF with `export_pdf_from_docx()`

### PDF Export

Both options support high-fidelity PDF export:
```
export_pdf_from_docx("/wilson-case/Documents/Demand_Letter.docx")
```

