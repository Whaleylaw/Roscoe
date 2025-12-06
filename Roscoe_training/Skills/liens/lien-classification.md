# Lien Classification

## Skill Metadata

- **ID**: lien-classification
- **Category**: liens
- **Reference Material**: education/liens/lien-fundamentals-and-classification/
- **Tools Required**: read_file, write_file

---

## When to Use This Skill

Use this skill when:
- A new lien is identified
- Determining lien negotiation strategy
- Analyzing lien priority
- Assessing reduction potential

---

## Lien Classification Framework

### By Source

| Category | Examples | Governing Law |
|----------|----------|---------------|
| **Government** | Medicare, Medicaid, TRICARE | Federal/State |
| **Health Insurance** | Group plans, individual plans | State or ERISA |
| **Provider** | Hospital liens, LOPs | State/Contract |
| **Other** | Workers' comp, child support | State/Federal |

### By Legal Basis

| Type | Description | Negotiability |
|------|-------------|---------------|
| **Statutory** | Created by law (hospital liens) | Limited by statute |
| **Contractual** | Plan language (subrogation) | Plan terms control |
| **Equitable** | Common law subrogation | More flexible |
| **Federal** | Medicare, VA, ERISA | Federal law controls |

---

## Classification Process

### Step 1: Identify Lien Source

Determine who is asserting the lien:
- Government program?
- Private insurance?
- Healthcare provider?
- Other entity?

### Step 2: Determine Legal Basis

Research:
- Is there a statutory basis?
- What does the plan/contract say?
- Does ERISA apply?
- Federal or state law governs?

### Step 3: Assess ERISA Status

For health insurance liens:
1. Is it an employer-sponsored plan?
2. Is the plan self-funded or fully insured?
3. If self-funded → ERISA applies
4. If fully insured → State law may apply

### Step 4: Review Plan Language

For ERISA plans:
- Reimbursement vs. subrogation clause?
- Make-whole provision?
- Attorney fee provision?
- Specific recovery language?

### Step 5: Classify Reduction Potential

| Classification | Reduction Potential |
|----------------|---------------------|
| Medicare | Formula-based (procurement costs) |
| Medicaid | State-specific, often significant |
| ERISA self-funded | Plan language controls, often limited |
| Fully insured | Made-whole, common fund apply |
| Hospital statutory | Statutory caps may apply |
| Provider LOP | Highly negotiable |

---

## Key Questions

1. Who is asserting the lien?
2. What is the legal basis?
3. Does ERISA preempt state law?
4. What defenses apply?
5. What is realistic reduction?

---

## Output

- Lien classification in `liens.json`
- Applicable law research
- Reduction strategy recommendation

