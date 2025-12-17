# Lien Reduction Request Template

## Usage

Use this template to request reduction of lien amounts. Customize based on lien type.

---

## Standard Reduction Request

```
[DATE]

[LIEN HOLDER NAME]
[SUBROGATION/RECOVERY DEPARTMENT]
[ADDRESS LINE 1]
[ADDRESS LINE 2]
[CITY, STATE ZIP]

RE: Lien Reduction Request
    Plan Member/Patient: [CLIENT NAME]
    Your Reference: [LIEN HOLDER REFERENCE]
    Date of Loss: [ACCIDENT DATE]
    Your Claimed Amount: $[LIEN AMOUNT]
    Our File: [FIRM FILE NUMBER]

Dear [ADDRESSEE / Subrogation Administrator]:

This firm represents [CLIENT NAME] in connection with injuries sustained 
on [ACCIDENT DATE]. A settlement has been reached and we are writing to 
request a reduction of your claimed lien amount.

SETTLEMENT BREAKDOWN:

    Gross Settlement:                  $[GROSS SETTLEMENT]
    Less: Attorney Fee ([RATE]%):     -$[FEE AMOUNT]
    Less: Case Expenses:              -$[EXPENSES]
    Less: Your Lien (as claimed):     -$[LIEN AMOUNT]
    Less: Other Liens:                -$[OTHER LIENS]
                                      ─────────────
    Net to Client:                     $[NET TO CLIENT]

REDUCTION REQUEST:

Based on [SELECT APPLICABLE ARGUMENTS]:

□ Common Fund Doctrine: Your recovery was made possible only through our 
  legal efforts. You should bear your proportionate share of attorney 
  fees and costs.

□ Limited Recovery: The settlement represents only [X]% of our client's 
  total damages of approximately $[DAMAGES], demonstrating the limited 
  recovery available.

□ Hardship: After payment of your full lien, our client would receive 
  only $[NET] to address ongoing medical needs and living expenses.

□ Plan Language: [CITE SPECIFIC PLAN PROVISIONS ALLOWING REDUCTION]

We respectfully request that you accept $[PROPOSED AMOUNT] in full 
satisfaction of your claim, representing a [X]% reduction.

This reduction would result in:
    Your Recovery:                     $[PROPOSED AMOUNT]
    Revised Net to Client:             $[REVISED NET]

Please respond to this request within [TIMEFRAME]. We are prepared to 
process payment promptly upon your agreement.

Sincerely,



_________________________
[ATTORNEY NAME]
[FIRM NAME]

Enclosures:
- Settlement Statement
- [Additional documentation as applicable]
```

---

## Medicare Compromise Request

```
[DATE]

Medicare Secondary Payer Recovery Contractor
PO Box 138899
Oklahoma City, OK 73113-8899

RE: Request for Compromise of Medicare Lien
    Medicare Beneficiary: [CLIENT NAME]
    HICN/MBI: [MEDICARE ID]
    Date of Accident: [ACCIDENT DATE]
    Your Case ID: [BCRC CASE ID]
    Final Demand Amount: $[MEDICARE AMOUNT]
    Our File: [FIRM FILE NUMBER]

Dear MSPRC:

This firm represents the above-referenced Medicare beneficiary. We have 
received the Final Demand Letter dated [FINAL DEMAND DATE] in the amount 
of $[MEDICARE AMOUNT]. We respectfully request a compromise of this amount.

SETTLEMENT AND FINANCIAL INFORMATION:

    Gross Settlement:                  $[GROSS SETTLEMENT]
    Less: Attorney Fee:               -$[FEE AMOUNT]
    Less: Case Expenses:              -$[EXPENSES]
    Less: Medicare Lien:              -$[MEDICARE AMOUNT]
    Less: Other Liens:                -$[OTHER LIENS]
                                      ─────────────
    Net to Beneficiary:                $[NET TO CLIENT]

BENEFICIARY FINANCIAL STATUS:

    Monthly Income:                    $[INCOME]
    Monthly Expenses:                  $[EXPENSES_MONTHLY]
    Assets:                            $[ASSETS]
    Ongoing Medical Needs:             [DESCRIPTION]

COMPROMISE REQUEST:

We request Medicare accept $[PROPOSED AMOUNT] in full satisfaction 
of its claim based on the following:

1. INADEQUATE RECOVERY: After payment of the full Medicare lien, the 
   beneficiary would receive only $[NET], which is insufficient to 
   meet ongoing medical and living needs.

2. LIMITED SETTLEMENT: The settlement of $[GROSS] represents only 
   [X]% of total damages, demonstrating the limited recovery.

3. ONGOING MEDICAL NEEDS: The beneficiary requires continued treatment 
   for [CONDITIONS] and depleting the settlement would prevent access 
   to necessary care.

4. FINANCIAL HARDSHIP: The beneficiary has limited income of $[INCOME] 
   monthly and minimal assets.

DOCUMENTATION ENCLOSED:

- Settlement Statement
- Final Demand Letter
- Financial Statement/Affidavit
- Medical Records documenting ongoing needs
- [Additional documentation]

We respectfully request favorable consideration of this compromise request.

Sincerely,



_________________________
[ATTORNEY NAME]
[FIRM NAME]

Enclosures: As noted above
```

---

## Field Definitions

| Field | Source | Notes |
|-------|--------|-------|
| `LIEN AMOUNT` | Lien record | Current claimed amount |
| `PROPOSED AMOUNT` | Calculated | Reduction target |
| `NET TO CLIENT` | Calculated | After full lien payment |
| `REVISED NET` | Calculated | After proposed reduction |
| `DAMAGES` | Case evaluation | Total estimated damages |
| `INCOME` | Client financial | Monthly income |
| `EXPENSES_MONTHLY` | Client financial | Monthly expenses |
| `ASSETS` | Client financial | Total assets |
| `CONDITIONS` | Medical records | Ongoing conditions |
| `FINAL DEMAND DATE` | Medicare correspondence | Date of final demand |

