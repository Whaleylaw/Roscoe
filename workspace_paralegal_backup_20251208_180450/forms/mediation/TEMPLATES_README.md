# Mediation Templates - Conversion Summary

## Overview

Word documents in this directory have been converted to Markdown templates with placeholders replacing specific case information.

## What Was Done

1. **Conversion**: 3 .docx files were successfully converted to Markdown
2. **Template Creation**: Specific information was replaced with placeholders:
   - Dates → `[DATE]`
   - Case numbers → `[CASE_NUMBER]`
   - Client information → `[CLIENT_NAME]`
   - Attorney information → `[ATTORNEY_NAME]`, `[LAW_FIRM_NAME]`
   - Mediation details → `[MEDIATION_DATE]`, `[MEDIATION_TIME]`, `[MEDIATION_LOCATION]`
   - Addresses, phone numbers, emails → `[STREET_ADDRESS]`, `[PHONE]`, `[EMAIL]`

## Template Files

All templates follow the naming pattern: `[Original_Filename]_Template.md`

## Template Categories

- **Mediation Notices**: Notices of mediation to clients
- **Mediation Pleadings**: Formal mediation pleadings
- **Client Letters**: Letters to clients regarding mediation

## Using the Templates

1. Open the desired template file
2. Replace all placeholders (text in square brackets) with actual case information
3. Review the document for accuracy
4. Convert back to Word format if needed using:
   ```bash
   pandoc template.md -o output.docx
   ```

## Statistics

- **Total Word files**: 3
- **Successfully converted**: 3 (.docx files)
- **Failed conversions**: 0
- **Success rate**: 100%

