# LOR Generator Error Handling

## Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Template not found | Invalid path | Verify template exists at specified location |
| Missing required placeholder | Data not in case files | Prompt user for missing information |
| LibreOffice not installed | PDF export dependency | Provide .docx only, skip PDF |
| Output path not writable | Permission issue | Check folder exists and has write access |
| Invalid date format | Date parsing failed | Use fallback formatting |

## Error Response Patterns

### Template Not Found

```
⚠️ Template not found: templates/2022 Whaley LOR to BI Adjuster.docx

Please verify the template file exists in the workflow templates folder.
Expected location: workflows/insurance_bi_claim/templates/
```

### Missing Required Data

```
⚠️ Cannot generate LOR - missing required information:

Missing fields:
- Client name (required)
- Insurance company address (required)

Please provide:
1. Client's full legal name: _______
2. Insurance company mailing address: _______
```

### PDF Export Failed

```
ℹ️ PDF export unavailable (LibreOffice not installed)

Word document generated successfully:
- LOR_to_BI_2024-12-06.docx

To create PDF manually:
1. Open the .docx file
2. File → Save As → PDF
```

## Validation Checklist

Before generating LOR, verify:

- [ ] Template file exists and is accessible
- [ ] Client name is populated
- [ ] Insurance company address is complete
- [ ] Accident date is formatted correctly
- [ ] Output folder exists

## Recovery Actions

| Scenario | Action |
|----------|--------|
| Partial data available | Generate with defaults, flag missing fields |
| Template corrupted | Use backup template or report error |
| User cancels | Save draft for later completion |
| Network error (if cloud) | Retry with exponential backoff |

