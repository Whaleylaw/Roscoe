# Supplemental Settlement Statement Template

## Usage

Use this template to prepare the supplemental settlement statement showing lien resolution and additional distribution to client.

---

## Template

```
═══════════════════════════════════════════════════════════════════════════
                    SUPPLEMENTAL SETTLEMENT STATEMENT
═══════════════════════════════════════════════════════════════════════════

[FIRM NAME]
[FIRM ADDRESS]
[PHONE] | [FAX]

───────────────────────────────────────────────────────────────────────────

Client:                  [CLIENT NAME]
Date of Accident:        [ACCIDENT DATE]
Original Settlement:     [ORIGINAL SETTLEMENT DATE]
This Statement:          [CURRENT DATE]
File Number:             [FILE NUMBER]

═══════════════════════════════════════════════════════════════════════════
SECTION 1: REFERENCE - ORIGINAL SETTLEMENT
═══════════════════════════════════════════════════════════════════════════

(For reference only - these amounts were previously distributed)

Gross Settlement Amount:                              $[GROSS]

Less: Attorney Fee ([RATE]%):                        -$[FEE]
Less: Case Expenses:                                 -$[EXPENSES]
Less: Liens Held in Trust:                           -$[TOTAL HELD]
                                                     ───────────
INITIAL NET TO CLIENT:                                $[INITIAL NET]

(Distributed on [INITIAL DISTRIBUTION DATE])

═══════════════════════════════════════════════════════════════════════════
SECTION 2: LIEN RESOLUTION
═══════════════════════════════════════════════════════════════════════════

AMOUNT HELD IN TRUST FOR LIENS:                       $[TOTAL HELD]

LIENS PAID:

  [LIEN HOLDER 1]:
    Original Estimate:            $[ESTIMATE 1]
    Final/Negotiated Amount:     -$[PAID 1]         [DATE PAID]

  [LIEN HOLDER 2]:
    Original Estimate:            $[ESTIMATE 2]
    Final/Negotiated Amount:     -$[PAID 2]         [DATE PAID]

  [ADDITIONAL LIENS AS NEEDED]

                                                     ───────────
TOTAL LIENS PAID:                                    -$[TOTAL PAID]

═══════════════════════════════════════════════════════════════════════════
SECTION 3: ADDITIONAL DISTRIBUTION
═══════════════════════════════════════════════════════════════════════════

Trust Account Balance After Liens:                    $[REMAINING]

No additional fees or expenses are charged on this distribution.

ADDITIONAL DISTRIBUTION TO CLIENT:                    $[ADDITIONAL]

═══════════════════════════════════════════════════════════════════════════
SECTION 4: TOTAL NET TO CLIENT
═══════════════════════════════════════════════════════════════════════════

Initial Distribution ([INITIAL DATE]):                $[INITIAL NET]
Additional Distribution (this statement):            +$[ADDITIONAL]
                                                     ═══════════
TOTAL NET TO CLIENT:                                  $[TOTAL NET]

═══════════════════════════════════════════════════════════════════════════
SECTION 5: TRUST ACCOUNT STATUS
═══════════════════════════════════════════════════════════════════════════

Trust Account Opening Balance:                        $[TOTAL HELD]
Total Liens Paid:                                    -$[TOTAL PAID]
Additional Distribution to Client:                   -$[ADDITIONAL]
                                                     ───────────
TRUST ACCOUNT CLOSING BALANCE:                        $0.00

Account Status: CLOSED
Case Status: COMPLETE

═══════════════════════════════════════════════════════════════════════════

CLIENT ACKNOWLEDGMENT

I, [CLIENT NAME], acknowledge receipt of the additional distribution
of $[ADDITIONAL] and agree that the total net recovery of $[TOTAL NET]
represents the full settlement of my claim.



_____________________________________     _______________
Client Signature                          Date



_____________________________________     _______________
Attorney Signature                        Date

═══════════════════════════════════════════════════════════════════════════
                         [FIRM NAME] | [PHONE]
═══════════════════════════════════════════════════════════════════════════
```

---

## Field Definitions

| Field | Source | Notes |
|-------|--------|-------|
| `FIRM NAME` | Firm config | Firm name |
| `CLIENT NAME` | Case overview | Full legal name |
| `ACCIDENT DATE` | Case overview | Date of incident |
| `FILE NUMBER` | Case overview | Internal file number |
| `ORIGINAL SETTLEMENT DATE` | Settlement record | When settled |
| `CURRENT DATE` | Generated | Today's date |
| `GROSS` | Original statement | Gross settlement |
| `RATE` | Fee agreement | Fee percentage |
| `FEE` | Original statement | Attorney fee amount |
| `EXPENSES` | Original statement | Case expenses |
| `TOTAL HELD` | Original statement | Amount held for liens |
| `INITIAL NET` | Original statement | Initial to client |
| `INITIAL DATE` | Original statement | Initial distribution date |
| `LIEN HOLDER X` | Lien records | Name of each lien holder |
| `ESTIMATE X` | Lien records | Original estimated amount |
| `PAID X` | Lien records | Actual amount paid |
| `DATE PAID` | Lien records | Payment date |
| `TOTAL PAID` | Calculated | Sum of all lien payments |
| `REMAINING` | Calculated | Trust balance after liens |
| `ADDITIONAL` | Calculated | Additional to client |
| `TOTAL NET` | Calculated | Sum of all distributions |

---

## Calculation Verification

Before finalizing, verify:

```
CHECK 1: Trust Account Balance
TOTAL HELD - TOTAL PAID - ADDITIONAL = 0

CHECK 2: Additional Distribution
TOTAL HELD - TOTAL PAID = ADDITIONAL

CHECK 3: Total Net
INITIAL NET + ADDITIONAL = TOTAL NET
```

