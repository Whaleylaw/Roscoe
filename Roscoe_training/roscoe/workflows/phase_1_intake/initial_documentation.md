# Workflow: Initial Documentation

## Phase: intake
## Goal: Obtain all required client signatures and authorizations

---

## When to Trigger

- Case accepted after intake screening
- User requests document preparation
- Missing signatures identified

---

## Inputs Required

- Completed intake information
- Client contact details
- List of providers to include on HIPAA

---

## Step-by-Step Process

### Step 1: Prepare Document Package
Prepare the following documents:

**Required Documents:**
1. **Retainer Agreement** - Attorney-client contract
2. **HIPAA Authorization** - Medical records release
3. **Fee Agreement** - Contingency fee terms
4. **Client Information Sheet** - Contact and emergency info

**Case-Specific Documents:**
5. **Medicare/Medicaid Authorization** (if applicable)
6. **Employment Authorization** (for wage loss claims)
7. **Social Security Authorization** (if disability involved)

### Step 2: Review Documents with Client
1. Explain each document's purpose
2. Answer client questions
3. Highlight key terms (fee percentage, costs, etc.)
4. Ensure client understands obligations

### Step 3: Obtain Signatures
1. Get signatures on all documents
2. Verify signatures are dated
3. Provide client with copies
4. Note any documents client declined to sign

### Step 4: Process HIPAA Authorizations
1. Identify all known medical providers
2. Prepare provider-specific HIPAA forms if needed
3. Include catch-all HIPAA for unknown providers
4. Set expiration dates appropriately

### Step 5: Organize and Store
1. Scan all signed documents
2. Store in `Documents/Signed/` folder
3. Update case management system
4. Send confirmation to client

### Step 6: Create Provider Contact List
From HIPAA authorizations:
1. List all authorized providers
2. Get contact information for each
3. Add to `medical_providers.json`

---

## Skills Used

- **document-organization**: Organize signed documents
- **client-communication**: Explain documents and answer questions

---

## Completion Criteria

- [ ] Retainer agreement signed
- [ ] Fee agreement signed
- [ ] HIPAA authorization(s) signed
- [ ] Client information sheet completed
- [ ] All documents scanned and filed
- [ ] Client provided copies

---

## Outputs

- `Documents/Signed/retainer_agreement.pdf`
- `Documents/Signed/fee_agreement.pdf`
- `Documents/Signed/hipaa_authorization.pdf`
- `Documents/Signed/client_info_sheet.pdf`
- Updated `medical_providers.json`

---

## Phase Exit Contribution

This workflow directly satisfies:
- `client_documents_signed`
- `hipaa_authorizations_obtained`
- `contracts_signed`

---

## Document Templates

Ensure templates are available in `Templates/`:
- `retainer_agreement_template.docx`
- `fee_agreement_template.docx`
- `hipaa_authorization_template.docx`
- `client_info_sheet_template.docx`

