# KACP Application Common Issues

## Data Issues

### Missing SSN

```
⚠️ SSN Required

The Social Security Number is required for PIP application processing.

Please provide the client's SSN: _______

Note: This is needed for the insurance carrier's claim processing.
```

### Invalid Date Format

```
⚠️ Date Format Error

The date of birth should be in MM/DD/YYYY format.
Provided: [invalid format]

Please confirm: _______
```

### Incomplete Address

```
⚠️ Address Incomplete

The mailing address needs:
- Street address
- City
- State
- ZIP code

Please provide the complete address: _______
```

## Form Filling Issues

### PDF Form Not Fillable

If the PDF form is not accepting programmatic filling:
1. Check PDF is not locked/encrypted
2. Verify field names match expected values
3. Try alternative fill method (flatten + overlay)

### Field Names Don't Match

Form field names in KACP Application:
- May vary slightly between form versions
- Run field detection to get actual names:

```python
from fill_pdf_form import get_field_names
fields = get_field_names("KACP-Application-03.2021.pdf")
print(fields)
```

### Text Overflow

If text is too long for form field:
- Abbreviate where possible
- Use continuation page if needed
- Attach additional sheet with full details

## Submission Issues

### Wrong Carrier

If application sent to wrong carrier:
1. Verify waterfall determination
2. Contact correct carrier
3. Resend application
4. Update tracking in case file

### Application Returned

Common reasons for return:
| Reason | Resolution |
|--------|------------|
| Incomplete | Fill missing fields |
| Illegible | Resubmit with clearer data |
| Missing signature | Get client signature |
| Wrong form version | Use current KACP form |

### No Response

If no acknowledgment within 14 days:
1. Call carrier to verify receipt
2. Resend with tracking if needed
3. Document all attempts
4. Escalate if continued non-response

## Data Recording After Submission

```json
{
  "pip": {
    "date_pip_application_sent": "2024-12-06",
    "pip_application_method": "fax",
    "pip_application_status": "submitted",
    "pip_application_tracking": {
      "sent_to": "State Farm PIP Department",
      "fax_confirmation": "Y",
      "follow_up_date": "2024-12-20"
    }
  }
}
```

## Pre-Submission Checklist

Before sending application:

- [ ] All required fields completed
- [ ] Client information verified against ID
- [ ] Accident date matches police report
- [ ] Insurance company correct per waterfall
- [ ] Injuries accurately described
- [ ] Form signed and dated
- [ ] Copy saved to case file

