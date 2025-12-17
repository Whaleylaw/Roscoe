# Final Lien Amount Request Template

## Usage

Use this template to request final lien amounts from lien holders after settlement.

---

## Template

```
[DATE]

[LIEN HOLDER NAME]
[DEPARTMENT/UNIT]
[ADDRESS LINE 1]
[ADDRESS LINE 2]
[CITY, STATE ZIP]

RE: Final Lien Amount Request
    Our Client: [CLIENT NAME]
    Your Reference: [LIEN HOLDER REFERENCE NUMBER]
    Date of Loss: [ACCIDENT DATE]
    Our File: [FIRM FILE NUMBER]

Dear [ADDRESSEE / Sir or Madam]:

This firm represents [CLIENT NAME] in connection with injuries sustained 
on [ACCIDENT DATE]. A settlement has been reached in this matter.

SETTLEMENT INFORMATION:

    Settlement Amount:                 $[GROSS SETTLEMENT]
    Settlement Date:                   [SETTLEMENT DATE]
    Attorney Fee ([RATE]%):           -$[FEE AMOUNT]
    Case Expenses:                    -$[EXPENSES]
    Other Liens Being Paid:           -$[OTHER LIENS]

We respectfully request that you provide your FINAL lien amount at your 
earliest convenience. We anticipate completing distribution within 
[TIMEFRAME] and need your final amount to prepare the settlement statement.

If applicable, please also provide:
    - Any reduction or waiver information
    - Payment instructions
    - Required forms or documentation

Please respond to:

    [FIRM NAME]
    [ATTORNEY NAME]
    [ADDRESS]
    [PHONE]
    [FAX]
    [EMAIL]

Thank you for your prompt attention to this matter.

Sincerely,



_________________________
[ATTORNEY NAME]
[FIRM NAME]
```

---

## Medicare-Specific Version

```
[DATE]

Medicare Secondary Payer Recovery Contractor
PO Box 138899
Oklahoma City, OK 73113-8899

RE: Request for Final Demand Letter
    Medicare Beneficiary: [CLIENT NAME]
    HICN/MBI: [MEDICARE ID]
    Date of Accident: [ACCIDENT DATE]
    Your Case ID: [BCRC CASE ID]
    Our File: [FIRM FILE NUMBER]

Dear MSPRC:

This firm represents the above-referenced Medicare beneficiary in a 
personal injury claim. Settlement has been reached and we are requesting 
the Final Demand Letter.

SETTLEMENT INFORMATION:

    Settlement Amount:                 $[GROSS SETTLEMENT]
    Settlement Date:                   [SETTLEMENT DATE]
    Attorney Fee Percentage:           [RATE]%
    Attorney Fee Amount:              -$[FEE AMOUNT]
    Case Expenses:                    -$[EXPENSES]

We have previously received the Conditional Payment Letter dated 
[CPL DATE] reflecting conditional payments of $[CPL AMOUNT].

Please issue the Final Demand Letter reflecting:
1. The automatic procurement cost reduction
2. Any payments that should not be included

Please send the Final Demand Letter to:

    [FIRM NAME]
    [ADDRESS]
    
Or fax to: [FAX NUMBER]

Thank you for your prompt attention.

Sincerely,



_________________________
[ATTORNEY NAME]
[FIRM NAME]
```

---

## Field Definitions

| Field | Source | Notes |
|-------|--------|-------|
| `CLIENT NAME` | Case overview | Full legal name |
| `LIEN HOLDER NAME` | Lien record | Name of lien holder |
| `LIEN HOLDER REFERENCE` | Lien record | Their case/claim number |
| `ACCIDENT DATE` | Case overview | Date of incident |
| `FIRM FILE NUMBER` | Case overview | Internal file number |
| `GROSS SETTLEMENT` | Settlement statement | Total settlement amount |
| `SETTLEMENT DATE` | Settlement statement | Date settlement reached |
| `RATE` | Fee agreement | Attorney fee percentage |
| `FEE AMOUNT` | Settlement statement | Calculated fee |
| `EXPENSES` | Settlement statement | Total case expenses |
| `OTHER LIENS` | Liens record | Sum of other liens |
| `MEDICARE ID` | Client info | HICN or MBI number |
| `BCRC CASE ID` | Medicare correspondence | Assigned by BCRC |
| `CPL DATE` | Medicare correspondence | Date of CPL |
| `CPL AMOUNT` | Medicare correspondence | Conditional amount |

