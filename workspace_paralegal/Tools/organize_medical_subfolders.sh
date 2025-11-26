#!/bin/bash
# Organize Medical Records into 3 subfolders
# 1. Medical Bills - billing statements, invoices, charges
# 2. Medical Records - clinical notes, treatment records, imaging reports
# 3. Medical Requests - HIPAA authorizations, records requests, certifications

set -e
cd "/Volumes/X10 Pro/Roscoe/workspace/projects/Alma-Cristobal-MVA-2-15-2024/Medical Records"

echo "=========================================="
echo "ORGANIZING MEDICAL RECORDS INTO SUBFOLDERS"
echo "=========================================="
echo ""

# MEDICAL REQUESTS (HIPAA Authorizations and Records Requests)
echo "Moving Medical Requests files..."

# Pattern: HIPAA Authorization, Records Request, Certification, Authorization
for file in *"HIPAA Authorization"*.pdf *"HIPAA Authorization"*.md \
            *"Records Request"*.pdf *"Records Request"*.md \
            *"Record Request"*.pdf *"Record Request"*.md \
            *"Medical Records Request"*.pdf *"Medical Records Request"*.md \
            *"Certification"*.pdf *"Certification"*.md \
            *"Affidavit"*.pdf *"Affidavit"*.md \
            *"Authorization"*.pdf *"Authorization"*.md; do
    if [ -f "$file" ]; then
        echo "  → Medical Requests: $file"
        mv "$file" "Medical Requests/"
    fi
done

echo ""

# MEDICAL BILLS (Bills, Billing Statements, Charges, Invoices)
echo "Moving Medical Bills files..."

# Pattern: Bill, Billing, Charges, Invoice, Itemization, Statement (if billing context)
for file in *"Bill"*.pdf *"Bill"*.md \
            *"Billing"*.pdf *"Billing"*.md \
            *"Charges"*.pdf *"Charges"*.md \
            *"Invoice"*.pdf *"Invoice"*.md \
            *"Itemization"*.pdf *"Itemization"*.md; do
    if [ -f "$file" ]; then
        # Check if it's a billing statement (not just "Billing Statement" in provider name)
        if [[ "$file" == *"Billing Statement"* ]] || \
           [[ "$file" == *"Ambulance Bill"* ]] || \
           [[ "$file" == *"Medical Bill"* ]] || \
           [[ "$file" == *"Physician Services Bill"* ]] || \
           [[ "$file" == *"Itemization"* ]] || \
           [[ "$file" == *"Charges"* ]]; then
            echo "  → Medical Bills: $file"
            mv "$file" "Medical Bills/"
        fi
    fi
done

echo ""

# MEDICAL RECORDS (Everything else - clinical notes, reports, treatment records)
echo "Moving Medical Records files..."

# All remaining files go to Medical Records
for file in *.pdf *.md; do
    if [ -f "$file" ]; then
        echo "  → Medical Records: $file"
        mv "$file" "Medical Records/"
    fi
done

echo ""
echo "=========================================="
echo "✅ ORGANIZATION COMPLETE"
echo "=========================================="
echo ""

# Count files in each subfolder
echo "Final counts:"
echo "  Medical Requests: $(ls -1 "Medical Requests/" | wc -l | tr -d ' ') files"
echo "  Medical Bills: $(ls -1 "Medical Bills/" | wc -l | tr -d ' ') files"
echo "  Medical Records: $(ls -1 "Medical Records/" | wc -l | tr -d ' ') files"
echo ""
echo "Files remaining in parent folder: $(ls -1 | grep -v "^Medical" | wc -l | tr -d ' ')"

