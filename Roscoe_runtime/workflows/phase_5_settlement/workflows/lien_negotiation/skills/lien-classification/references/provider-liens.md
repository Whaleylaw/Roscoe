# Provider Lien Reference

## Overview

Provider liens include hospital statutory liens and letters of protection (LOPs). These are generally more negotiable than government or ERISA liens.

## Types of Provider Liens

### Hospital Statutory Liens (KRS 216.935)

**Legal Basis**: Kentucky statute creates automatic lien for hospital services
**Attachment**: Lien attaches to any recovery from third party
**Perfection**: Hospital must file notice with County Clerk

**Statutory Limits**:
- Limited to reasonable charges
- Must be filed within 120 days of discharge
- Must provide notice to patient and attorney

**Negotiation Considerations**:
- Often reduced 20-40%
- Hospitals want to maintain referral relationships
- Large bills may warrant hardship arguments

### Letters of Protection (LOPs)

**Legal Basis**: Contract between attorney/client and provider
**Attachment**: Creates contractual obligation to pay from settlement
**Enforceability**: Contract law governs

**Common LOP Terms**:
- Provider agrees to treat without immediate payment
- Attorney agrees to protect provider's interest from settlement
- Balance may be negotiated at settlement

**Negotiation Leverage**:
- LOPs are highly negotiable (30-50% reduction common)
- Provider chose to wait for payment
- Provider benefited from guaranteed payment source
- Settlement limitations affect available funds

## Classification Process

### Step 1: Identify Provider Lien Type

| Indicator | Hospital Statutory | Letter of Protection |
|-----------|-------------------|---------------------|
| Filed with County Clerk | Yes | No |
| Written LOP agreement | No | Yes |
| Hospital/ER charges | Typically | Can be any provider |
| Perfection required | Yes | No (contract) |

### Step 2: Verify Lien Validity

**Hospital Statutory**:
- Was lien filed within 120 days?
- Was proper notice given?
- Are charges reasonable?

**Letters of Protection**:
- Is LOP signed by client?
- What are specific terms?
- Any caps or limitations?

### Step 3: Assess Reduction Potential

| Factor | Hospital Statutory | LOP |
|--------|-------------------|-----|
| Limited settlement | Moderate leverage | Strong leverage |
| Multiple liens | Some consideration | Good leverage |
| Relationship value | Depends on facility | Strong leverage |
| Disputed charges | Can challenge | Can negotiate |

## Negotiation Strategies

### Hospital Statutory Liens

1. **Challenge perfection**: Was lien properly filed?
2. **Dispute charges**: Request itemized bill, challenge unreasonable fees
3. **Limited funds**: Show settlement barely covers medical expenses
4. **Comparative fault**: Reduced recovery = reduced lien
5. **Multiple injuries**: Only accident-related charges covered

### Letters of Protection

1. **Standard reduction**: Start at 40-50% off
2. **Settlement percentage**: Provider gets same % reduction as client
3. **Prompt payment**: Offer quick payment for larger reduction
4. **Future referrals**: Leverage ongoing relationship
5. **Bill padding**: Challenge inflated charges

## Common Providers with LOPs

| Provider Type | Typical LOP Terms | Negotiation Range |
|---------------|-------------------|-------------------|
| Chiropractor | Full bill owed | 30-50% reduction |
| Pain Management | Full bill owed | 25-40% reduction |
| Surgery Center | May have caps | 20-35% reduction |
| Imaging Center | Usually lower bills | 20-30% reduction |
| Physical Therapy | Accumulated charges | 30-40% reduction |

## Documentation Requirements

### For Hospital Liens
- Copy of filed lien
- Itemized bill
- Medical records
- Proof of notice

### For LOPs
- Signed LOP agreement
- Itemized bills
- All treatment records
- Any communications about payment

## Data Target

```json
{
  "type": "hospital_statutory|lop",
  "provider_name": "Norton Hospital",
  "asserted_amount": 25000,
  "perfection_status": "valid|defective|not_required",
  "reduction_potential": "high",
  "negotiation_range": "30-50%"
}
```

