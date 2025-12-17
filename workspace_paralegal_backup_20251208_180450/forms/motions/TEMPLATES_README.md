# Motions Templates - Conversion Summary

## Overview

Word documents in this directory have been converted to Markdown templates with placeholders replacing specific case information.

## What Was Done

1. **Conversion**: 28 Word files were processed
   - 27 .docx files successfully converted to Markdown
   - 1 .doc file failed conversion (older format compatibility issue)

2. **Template Creation**: Specific information was replaced with placeholders:
   - Case numbers → `[CASE_NUMBER]`
   - Dates → `[DATE]`
   - Plaintiff/Defendant names → `[PLAINTIFF_NAME]`, `[DEFENDANT_NAME]`
   - Attorney information → `[ATTORNEY_NAME]`, `[LAW_FIRM_NAME]`
   - Court information → `[COURT_NAME]`, `[JUDGE_NAME]`
   - Company names (State Farm, Franklin) → `[COMPANY_NAME]`
   - Addresses, phone numbers, emails → `[STREET_ADDRESS]`, `[PHONE]`, `[EMAIL]`

## Template Files

All templates follow the naming pattern: `[Original_Filename]_Template.md`

## Template Categories

### Motions
- **Motion to Compel**: Motions to compel discovery responses
- **Motion to Withdraw**: Motions to withdraw as counsel
- **Motion to Substitute**: Motions to substitute defendants
- **Motion to Transfer Venue**: Venue transfer motions
- **Motion for Default Judgment**: Default judgment motions
- **Motion for Leave**: Motions for leave to file cross-claims
- **Motion in Limine (MIL)**: Various motions in limine, including Daubert challenges
- **Motion for Summary Judgment (MSJ)**: Summary judgment motions

### Orders
- **Agreed Orders**: Agreed orders for dismissal, partial dismissal, discovery responses
- **Proposed Orders**: Proposed orders granting motions
- **General Orders**: Various court orders

### Other
- **Petitions**: Petitions for special needs trusts
- **Responses**: Responses to motions to dismiss
- **Standards**: Summary judgment standards

## Using the Templates

1. Open the desired template file
2. Replace all placeholders (text in square brackets) with actual case information
3. Review the document for accuracy
4. Convert back to Word format if needed using:
   ```bash
   pandoc template.md -o output.docx
   ```

## Statistics

- **Total Word files**: 28
- **Successfully converted**: 27 (.docx files)
- **Failed conversions**: 1 (.doc file - older format)
- **Success rate**: 96.4%

## Failed Files

The following .doc file could not be converted due to format compatibility:
- `MSJ.Memorandum.PIP.Denial.doc`

This may need manual conversion or alternative conversion tools.

