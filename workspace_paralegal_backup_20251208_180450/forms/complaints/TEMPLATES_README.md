# Complaint Templates - Conversion Summary

## Overview

All Word document (.docx) files in this directory have been converted to Markdown templates with placeholders replacing specific case information.

## What Was Done

1. **Conversion**: All 32 .docx files were converted to Markdown using `pandoc`
2. **Template Creation**: Specific information was replaced with placeholders:
   - Case numbers → `[CASE_NUMBER]`
   - Dates → `[DATE]`
   - Phone numbers → `[PHONE]`
   - Email addresses → `[EMAIL]`
   - Zip codes → `[ZIP_CODE]`
   - Plaintiff names → `[PLAINTIFF_NAME]`
   - Defendant names → `[DEFENDANT_NAME]`
   - Company names → `[COMPANY_NAME]`
   - Attorney names → `[ATTORNEY_NAME]`
   - Law firm names → `[LAW_FIRM_NAME]`
   - Street addresses → `[STREET_ADDRESS]`
   - Cities → `[CITY]`
   - Bar numbers → `[BAR_NUMBER]`
   - Years → `[YEAR]`

## Template Files

All templates follow the naming pattern: `[Original_Filename]_Template.md`

## Using the Templates

1. Open the desired template file
2. Replace all placeholders (text in square brackets) with actual case information
3. Review the document for any remaining placeholders that may need adjustment
4. Convert back to Word format if needed using:
   ```bash
   pandoc template.md -o output.docx
   ```

## Known Issues

Some templates may have minor issues that require manual cleanup:
- Some placeholders may appear in unexpected places (e.g., `[DATE]` where `[CITY]` should be)
- Some legal terminology may have been replaced and needs to be restored
- Header sections may need manual adjustment for proper formatting

## Template Categories

- **Motor Vehicle Accident (MVA) Complaints**: Various MVA complaint templates
- **Premises Liability Complaints**: Premises liability and dog bite complaints
- **Bodily Injury (BI) Complaints**: BI complaints with various scenarios
- **Bad Faith Complaints**: Complaints including bad faith claims
- **UIM/UM Complaints**: Underinsured/Uninsured motorist complaints
- **Certificates and Affidavits**: Service certificates and affidavits
- **Amended Complaints**: Templates for amended complaints

## Next Steps

1. Review each template for accuracy
2. Manually fix any placeholder issues
3. Test templates with actual case data
4. Update templates based on feedback

## Scripts Used

- `convert_to_templates.py` - Initial conversion script
- `improve_templates.py` - Name replacement improvements
- `final_cleanup.py` - Final cleanup of placeholders

These scripts can be reused or modified for future template conversions.

