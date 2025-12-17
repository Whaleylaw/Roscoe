# Lien Inventory Template

Document and track all identified liens on the case.

---

## Lien Inventory Report

**Case**: {{client_name}} | DOI: {{accident_date}}
**Report Date**: {{date}}
**Settlement Value**: {{settlement_amount or "Pre-settlement"}}

---

### Lien Summary

| # | Type | Holder | Asserted | Status |
|---|------|--------|----------|--------|
| 1 | {{type}} | {{holder}} | ${{amount}} | {{status}} |
| 2 | {{type}} | {{holder}} | ${{amount}} | {{status}} |

**Total Asserted Liens**: ${{total}}

---

### Government Liens

#### Medicare (if applicable)

| Field | Value |
|-------|-------|
| **Status** | {{identified|registered|final_demand}} |
| **MSPRC Case ID** | {{case_id}} |
| **Conditional Payment Amount** | ${{amount}} |
| **Final Demand Amount** | ${{amount or "Pending"}} |
| **Reduction Calculation** | {{see below}} |

**Procurement Cost Reduction**:
```
Gross Settlement: ${{settlement}}
Attorney Fees: ${{fees}} ({{%}})
Costs: ${{costs}}
Total Procurement: ${{total_procurement}} ({{%}})

Medicare CP: ${{cp_amount}}
Reduction: ${{cp_amount}} × {{%}} = ${{reduction}}
Final Medicare: ${{final_amount}}
```

#### Medicaid (if applicable)

| Field | Value |
|-------|-------|
| **Status** | {{identified|notice_sent|amount_received}} |
| **Lien Amount** | ${{amount}} |
| **Negotiated Amount** | ${{amount or "Pending"}} |
| **Contact** | {{name}} at {{phone}} |

---

### Private Insurance Liens

#### {{Insurance Company Name}}

| Field | Value |
|-------|-------|
| **Plan Type** | {{erisa_self_funded|erisa_fully_insured|non_erisa}} |
| **Governing Law** | {{federal|state}} |
| **Asserted Amount** | ${{amount}} |
| **Plan Documents Obtained** | {{yes|no|pending}} |
| **Made-Whole Applies** | {{yes|no|unknown}} |
| **Attorney Fee Reduction** | {{yes|no|plan_silent}} |
| **Negotiated Amount** | ${{amount or "Pending"}} |

**Key Plan Language**:
{{Quote relevant subrogation/reimbursement language}}

---

### Provider Liens

#### Hospital Statutory Liens

| Hospital | Amount | Filed | Valid | Negotiated |
|----------|--------|-------|-------|------------|
| {{name}} | ${{amount}} | {{date}} | {{yes|no}} | ${{amount}} |

#### Letters of Protection

| Provider | Amount | LOP Date | Negotiated |
|----------|--------|----------|------------|
| {{name}} | ${{amount}} | {{date}} | ${{amount}} |

---

### Lien Classification Summary

| Lien | Type | Law | Reduction Potential |
|------|------|-----|---------------------|
| {{holder}} | {{type}} | {{federal|state}} | {{low|medium|high}} |

---

### Negotiation Status

| Lien | Asserted | Offered | Counter | Final |
|------|----------|---------|---------|-------|
| {{holder}} | ${{amount}} | ${{amount}} | ${{amount}} | ${{amount}} |

---

### Outstanding Actions

| Lien | Action Needed | Due Date | Status |
|------|---------------|----------|--------|
| {{holder}} | {{action}} | {{date}} | {{pending|complete}} |

---

### Settlement Distribution Preview

```
Gross Settlement:           ${{settlement}}
Less Attorney Fee ({{%}}):  ${{fee}}
Less Costs:                 ${{costs}}
Less Liens:                 ${{total_liens}}
  - Medicare:    ${{amount}}
  - Medicaid:    ${{amount}}
  - {{Insurer}}: ${{amount}}
  - {{Hospital}}:${{amount}}
                           ___________
Net to Client:              ${{net}}
```

---

### Notes

{{Additional notes about liens}}

---

**Last Updated**: {{timestamp}}
**Updated By**: {{agent|user}}

