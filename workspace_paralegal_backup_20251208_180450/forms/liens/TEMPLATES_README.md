# Liens Templates - Conversion Summary

## Overview

Word documents in this directory have been converted to Markdown templates with placeholders replacing specific case information.

## What Was Done

1. **Conversion**: 12 Word files were processed
   - 9 .docx files successfully converted to Markdown
   - 3 .doc files failed conversion (older format compatibility issues)

2. **Template Creation**: Specific information was replaced with placeholders:
   - Company names (Xerox, Humana, Medicare, Conduent) → `[COMPANY_NAME]`
   - Dates → `[DATE]`
   - Case numbers → `[CASE_NUMBER]`
   - Client information → `[CLIENT_NAME]`
   - Attorney information → `[ATTORNEY_NAME]`, `[LAW_FIRM_NAME]`
   - Addresses, phone numbers, emails → `[STREET_ADDRESS]`, `[PHONE]`, `[EMAIL]`

## Template Files

All templates follow the naming pattern: `[Original_Filename]_Template.md`

## Template Categories

- **Lien Requests**: Requests for final liens, itemized liens, Medicare liens
- **Subrogation Letters**: Letters of representation for subrogation (Health Plan, Medicare, Workers' Compensation)
- **Negotiation Letters**: Letters to negotiate and reduce liens, including attorney fee reductions
- **HIPAA Letters**: Letters with HIPAA authorizations

## Using the Templates

1. Open the desired template file
2. Replace all placeholders (text in square brackets) with actual case information
3. Review the document for accuracy
4. Convert back to Word format if needed using:
   ```bash
   pandoc template.md -o output.docx
   ```

## Statistics

- **Total Word files**: 12
- **Successfully converted**: 9 (.docx files)
- **Failed conversions**: 3 (.doc files - older format)
- **Success rate**: 75%

## Failed Files

The following .doc files could not be converted due to format compatibility:
- `LOR to Medicare Subro - CH.doc`
- `LOR . WC. to Employer.doc`
- `LOR Conduent Subro.doc`

These may need manual conversion or alternative conversion tools.

