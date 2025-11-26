#!/bin/bash
# Case File Reorganization Script
# Generated for: Abby-Sitgraves-MVA-7-13-2024
# Date: January 7, 2025

cd "/projects/Abby-Sitgraves-MVA-7-13-2024"

echo "Starting reorganization of Abby-Sitgraves-MVA-7-13-2024 case files..."

# Create 8-bucket directory structure
echo "Creating bucket directories..."
mkdir -p "case_information"
mkdir -p "Client"
mkdir -p "Investigation"
mkdir -p "Medical Records"
mkdir -p "Insurance"
mkdir -p "Lien"
mkdir -p "Expenses"
mkdir -p "Negotiation Settlement"
mkdir -p "Litigation"
mkdir -p "Review_Needed"

# ============================================
# CLIENT
# ============================================
echo "Moving Client files..."
mv "2024.07.29 Sitgraves Executed MVA Intake Packet - VineSign Audit Verification.pdf" "Client/2024-07-30 - Abby Sitgraves - Client - The Whaley Law Firm - Intake Packet VineSign Verification.pdf"
[ -f "2024.07.29 Sitgraves Executed MVA Intake Packet - VineSign Audit Verification.md" ] && mv "2024.07.29 Sitgraves Executed MVA Intake Packet - VineSign Audit Verification.md" "Client/2024-07-30 - Abby Sitgraves - Client - The Whaley Law Firm - Intake Packet VineSign Verification.md"

mv "2024.07.29 Sitgraves Executed MVA Intake Packet.pdf" "Client/2024-07-30 - Abby Sitgraves - Client - The Whaley Law Firm - Executed MVA Intake Packet.pdf"
[ -f "2024.07.29 Sitgraves Executed MVA Intake Packet.md" ] && mv "2024.07.29 Sitgraves Executed MVA Intake Packet.md" "Client/2024-07-30 - Abby Sitgraves - Client - The Whaley Law Firm - Executed MVA Intake Packet.md"

# ============================================
# INVESTIGATION
# ============================================
echo "Moving Investigation files..."
mv "2024.07.24 Sitgraves Adadevoh Civilian MVA Report - Jefferson Co.pdf" "Investigation/2024-07-13 - Abby Sitgraves - Investigation - Jefferson County - Civilian Traffic Collision Report.pdf"
[ -f "2024.07.24 Sitgraves Adadevoh Civilian MVA Report - Jefferson Co.md" ] && mv "2024.07.24 Sitgraves Adadevoh Civilian MVA Report - Jefferson Co.md" "Investigation/2024-07-13 - Abby Sitgraves - Investigation - Jefferson County - Civilian Traffic Collision Report.md"

mv "2025.02.05 Sitgraves Invest CAAL Worldwide Reviews on The Knot.pdf" "Investigation/2025-02-05 - Abby Sitgraves - Investigation - The Whaley Law Firm - CAAL Worldwide Reviews.pdf"
[ -f "2025.02.05 Sitgraves Invest CAAL Worldwide Reviews on The Knot.md" ] && mv "2025.02.05 Sitgraves Invest CAAL Worldwide Reviews on The Knot.md" "Investigation/2025-02-05 - Abby Sitgraves - Investigation - The Whaley Law Firm - CAAL Worldwide Reviews.md"

mv "2025.02.05 Sitgraves Invest CourtNet Case List on Def CAAL Worldwide.pdf" "Investigation/2025-02-05 - Abby Sitgraves - Investigation - The Whaley Law Firm - CAAL Worldwide Court Records Search.pdf"
[ -f "2025.02.05 Sitgraves Invest CourtNet Case List on Def CAAL Worldwide.md" ] && mv "2025.02.05 Sitgraves Invest CourtNet Case List on Def CAAL Worldwide.md" "Investigation/2025-02-05 - Abby Sitgraves - Investigation - The Whaley Law Firm - CAAL Worldwide Court Records Search.md"

# ============================================
# MEDICAL RECORDS
# ============================================
echo "Moving Medical Records files..."
mv "+15025889500-0602-090915-115.pdf" "Medical Records/2025-05-29 - Abby Sitgraves - Medical Record - UofL Physicians - Primary Care Visit Records.pdf"
[ -f "+15025889500-0602-090915-115.md" ] && mv "+15025889500-0602-090915-115.md" "Medical Records/2025-05-29 - Abby Sitgraves - Medical Record - UofL Physicians - Primary Care Visit Records.md"

mv "2023 Whaley Initial Medical Billing Request to Provider (MBR) 2024-12-02 1525.pdf" "Medical Records/2024-12-02 - Abby Sitgraves - Medical Record - The Whaley Law Firm - Jewish Hospital Billing Request.pdf"
[ -f "2023 Whaley Initial Medical Billing Request to Provider (MBR) 2024-12-02 1525.md" ] && mv "2023 Whaley Initial Medical Billing Request to Provider (MBR) 2024-12-02 1525.md" "Medical Records/2024-12-02 - Abby Sitgraves - Medical Record - The Whaley Law Firm - Jewish Hospital Billing Request.md"

mv "2023 Whaley Initial Medical Billing Request to Provider (MBR) 2025-05-29 1036.pdf" "Medical Records/2025-05-29 - Abby Sitgraves - Medical Record - The Whaley Law Firm - UofL Orthopedics Billing Request.pdf"
[ -f "2023 Whaley Initial Medical Billing Request to Provider (MBR) 2025-05-29 1036.md" ] && mv "2023 Whaley Initial Medical Billing Request to Provider (MBR) 2025-05-29 1036.md" "Medical Records/2025-05-29 - Abby Sitgraves - Medical Record - The Whaley Law Firm - UofL Orthopedics Billing Request.md"

mv "2023 Whaley Law Firm Medical Request Template 2024-12-02 1525.pdf" "Medical Records/2024-12-02 - Abby Sitgraves - Medical Record - The Whaley Law Firm - Jewish Hospital Records Request.pdf"
[ -f "2023 Whaley Law Firm Medical Request Template 2024-12-02 1525.md" ] && mv "2023 Whaley Law Firm Medical Request Template 2024-12-02 1525.md" "Medical Records/2024-12-02 - Abby Sitgraves - Medical Record - The Whaley Law Firm - Jewish Hospital Records Request.md"

mv "2023 Whaley Law Firm Medical Request Template 2024-12-06 1122.pdf" "Medical Records/2024-12-06 - Abby Sitgraves - Medical Record - The Whaley Law Firm - Medical Records Request.pdf"
[ -f "2023 Whaley Law Firm Medical Request Template 2024-12-06 1122.md" ] && mv "2023 Whaley Law Firm Medical Request Template 2024-12-06 1122.md" "Medical Records/2024-12-06 - Abby Sitgraves - Medical Record - The Whaley Law Firm - Medical Records Request.md"

mv "2024-07-13-Abby-Sitgraves-Jewish-Hospital-Knee-Pain.pdf" "Medical Records/2024-07-13 - Abby Sitgraves - Medical Record - Jewish Hospital - Knee Pain ER Billing Summary.pdf"
[ -f "2024-07-13-Abby-Sitgraves-Jewish-Hospital-Knee-Pain.md" ] && mv "2024-07-13-Abby-Sitgraves-Jewish-Hospital-Knee-Pain.md" "Medical Records/2024-07-13 - Abby Sitgraves - Medical Record - Jewish Hospital - Knee Pain ER Billing Summary.md"

mv "2024-12-02-Aaron-G-Whaley-Esq-Jewish-Hospital-Medical-Records-Request.pdf" "Medical Records/2024-12-02 - Abby Sitgraves - Medical Record - The Whaley Law Firm - Jewish Hospital Records Request (2).pdf"
[ -f "2024-12-02-Aaron-G-Whaley-Esq-Jewish-Hospital-Medical-Records-Request.md" ] && mv "2024-12-02-Aaron-G-Whaley-Esq-Jewish-Hospital-Medical-Records-Request.md" "Medical Records/2024-12-02 - Abby Sitgraves - Medical Record - The Whaley Law Firm - Jewish Hospital Records Request (2).md"

mv "2024.04.17 Sitgraves MB UL Hosptial.pdf" "Medical Records/2024-07-13 - Abby Sitgraves - Medical Record - Jewish Hospital - ER Visit Billing Statement.pdf"
[ -f "2024.04.17 Sitgraves MB UL Hosptial.md" ] && mv "2024.04.17 Sitgraves MB UL Hosptial.md" "Medical Records/2024-07-13 - Abby Sitgraves - Medical Record - Jewish Hospital - ER Visit Billing Statement.md"

mv "2024.07.13 MB Foundation Radiology.pdf" "Medical Records/2024-07-13 - Abby Sitgraves - Medical Record - Foundation Radiology - Radiology Services Billing.pdf"
[ -f "2024.07.13 MB Foundation Radiology.md" ] && mv "2024.07.13 MB Foundation Radiology.md" "Medical Records/2024-07-13 - Abby Sitgraves - Medical Record - Foundation Radiology - Radiology Services Billing.md"

mv "2024.07.13 MB UofL Physicians.pdf" "Medical Records/2024-07-13 - Abby Sitgraves - Medical Record - UofL Physicians - Emergency Medicine Visit Billing.pdf"
[ -f "2024.07.13 MB UofL Physicians.md" ] && mv "2024.07.13 MB UofL Physicians.md" "Medical Records/2024-07-13 - Abby Sitgraves - Medical Record - UofL Physicians - Emergency Medicine Visit Billing.md"

mv "2024.08.06 MB UofL Orthopedics.pdf" "Medical Records/2024-08-06 - Abby Sitgraves - Medical Record - UofL Orthopedics - Office Visit Billing.pdf"
[ -f "2024.08.06 MB UofL Orthopedics.md" ] && mv "2024.08.06 MB UofL Orthopedics.md" "Medical Records/2024-08-06 - Abby Sitgraves - Medical Record - UofL Orthopedics - Office Visit Billing.md"

mv "2024.08.06 to 2024.08.16 MR UofL Orthopedics.pdf" "Medical Records/2024-08-06 - Abby Sitgraves - Medical Record - UofL Orthopedics - Visit Records and Orders.pdf"
[ -f "2024.08.06 to 2024.08.16 MR UofL Orthopedics.md" ] && mv "2024.08.06 to 2024.08.16 MR UofL Orthopedics.md" "Medical Records/2024-08-06 - Abby Sitgraves - Medical Record - UofL Orthopedics - Visit Records and Orders.md"

mv "2024.12.02 Sitgraves Executed Med Auth - Master - Blank (Dated).pdf" "Medical Records/2024-12-02 - Abby Sitgraves - Medical Record - General - HIPAA Authorization Master.pdf"
[ -f "2024.12.02 Sitgraves Executed Med Auth - Master - Blank (Dated).md" ] && mv "2024.12.02 Sitgraves Executed Med Auth - Master - Blank (Dated).md" "Medical Records/2024-12-02 - Abby Sitgraves - Medical Record - General - HIPAA Authorization Master.md"

mv "2024.12.24 Sitgraves RR Resp UL Physician - Need RHC Attestation.pdf" "Medical Records/2024-12-24 - Abby Sitgraves - Medical Record - UofL Physicians - Records Request Response Need Attestation.pdf"
[ -f "2024.12.24 Sitgraves RR Resp UL Physician - Need RHC Attestation.md" ] && mv "2024.12.24 Sitgraves RR Resp UL Physician - Need RHC Attestation.md" "Medical Records/2024-12-24 - Abby Sitgraves - Medical Record - UofL Physicians - Records Request Response Need Attestation.md"

mv "2024.12.28 Sitgraves RR Resp - Rejection - Jewish Hospital - Attestation Required.pdf" "Medical Records/2024-12-28 - Abby Sitgraves - Medical Record - Jewish Hospital - Records Request Rejection Attestation Required.pdf"
[ -f "2024.12.28 Sitgraves RR Resp - Rejection - Jewish Hospital - Attestation Required.md" ] && mv "2024.12.28 Sitgraves RR Resp - Rejection - Jewish Hospital - Attestation Required.md" "Medical Records/2024-12-28 - Abby Sitgraves - Medical Record - Jewish Hospital - Records Request Rejection Attestation Required.md"

mv "2025.01.06 Sitgraves MR - UL Physicians - Not Certified.pdf" "Medical Records/2025-01-06 - Abby Sitgraves - Medical Record - UofL Physicians - Medical Records Not Certified.pdf"
[ -f "2025.01.06 Sitgraves MR - UL Physicians - Not Certified.md" ] && mv "2025.01.06 Sitgraves MR - UL Physicians - Not Certified.md" "Medical Records/2025-01-06 - Abby Sitgraves - Medical Record - UofL Physicians - Medical Records Not Certified.md"

mv "2025.02.10 Sitgraves CRR Foundation Radiology.pdf" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - The Whaley Law Firm - Foundation Radiology Certified Records Request.pdf"
[ -f "2025.02.10 Sitgraves CRR Foundation Radiology.md" ] && mv "2025.02.10 Sitgraves CRR Foundation Radiology.md" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - The Whaley Law Firm - Foundation Radiology Certified Records Request.md"

mv "2025.02.10 Sitgraves CRR UL (Jewish) Hospital.pdf" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - The Whaley Law Firm - Jewish Hospital Certified Records Request.pdf"
[ -f "2025.02.10 Sitgraves CRR UL (Jewish) Hospital.md" ] && mv "2025.02.10 Sitgraves CRR UL (Jewish) Hospital.md" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - The Whaley Law Firm - Jewish Hospital Certified Records Request.md"

mv "2025.02.10 Sitgraves CRR UL Orthopedics.pdf" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - The Whaley Law Firm - UofL Orthopedics Certified Records Request.pdf"
[ -f "2025.02.10 Sitgraves CRR UL Orthopedics.md" ] && mv "2025.02.10 Sitgraves CRR UL Orthopedics.md" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - The Whaley Law Firm - UofL Orthopedics Certified Records Request.md"

mv "2025.02.10 Sitgraves CRR UL Physicians.pdf" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - The Whaley Law Firm - UofL Physicians Certified Records Request.pdf"
[ -f "2025.02.10 Sitgraves CRR UL Physicians.md" ] && mv "2025.02.10 Sitgraves CRR UL Physicians.md" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - The Whaley Law Firm - UofL Physicians Certified Records Request.md"

mv "2025.02.10 Sitgraves Executed Med Auth - Foundation Radiology.pdf" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - Foundation Radiology - HIPAA Authorization.pdf"
[ -f "2025.02.10 Sitgraves Executed Med Auth - Foundation Radiology.md" ] && mv "2025.02.10 Sitgraves Executed Med Auth - Foundation Radiology.md" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - Foundation Radiology - HIPAA Authorization.md"

mv "2025.02.10 Sitgraves Executed Med Auth - UL (Jewish) Hospital.pdf" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - Jewish Hospital - HIPAA Authorization.pdf"
[ -f "2025.02.10 Sitgraves Executed Med Auth - UL (Jewish) Hospital.md" ] && mv "2025.02.10 Sitgraves Executed Med Auth - UL (Jewish) Hospital.md" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - Jewish Hospital - HIPAA Authorization.md"

mv "2025.02.10 Sitgraves Executed Med Auth - UL Orthopedics.pdf" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - UofL Orthopedics - HIPAA Authorization.pdf"
[ -f "2025.02.10 Sitgraves Executed Med Auth - UL Orthopedics.md" ] && mv "2025.02.10 Sitgraves Executed Med Auth - UL Orthopedics.md" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - UofL Orthopedics - HIPAA Authorization.md"

mv "2025.02.10 Sitgraves Executed Med Auth - UL Physicians.pdf" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - UofL Physicians - HIPAA Authorization.pdf"
[ -f "2025.02.10 Sitgraves Executed Med Auth - UL Physicians.md" ] && mv "2025.02.10 Sitgraves Executed Med Auth - UL Physicians.md" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - UofL Physicians - HIPAA Authorization.md"

mv "2025.03.11 Sitgraves CRR Resp - UL Phy - No Records Located.pdf" "Medical Records/2025-03-11 - Abby Sitgraves - Medical Record - UofL Physicians - Certified Records Request Response No Records.pdf"
[ -f "2025.03.11 Sitgraves CRR Resp - UL Phy - No Records Located.md" ] && mv "2025.03.11 Sitgraves CRR Resp - UL Phy - No Records Located.md" "Medical Records/2025-03-11 - Abby Sitgraves - Medical Record - UofL Physicians - Certified Records Request Response No Records.md"

mv "2025.03.13 Sitgraves CMR UL Health - Jewish Hospital - Certification Page.pdf" "Medical Records/2025-03-13 - Abby Sitgraves - Medical Record - Jewish Hospital - Certified Medical Records Affidavit.pdf"
[ -f "2025.03.13 Sitgraves CMR UL Health - Jewish Hospital - Certification Page.md" ] && mv "2025.03.13 Sitgraves CMR UL Health - Jewish Hospital - Certification Page.md" "Medical Records/2025-03-13 - Abby Sitgraves - Medical Record - Jewish Hospital - Certified Medical Records Affidavit.md"

mv "2025.03.13 Sitgraves CMR UL Health - Jewish Hospital - EMR.pdf" "Medical Records/2025-03-13 - Abby Sitgraves - Medical Record - Jewish Hospital - Certified EMR.pdf"
[ -f "2025.03.13 Sitgraves CMR UL Health - Jewish Hospital - EMR.md" ] && mv "2025.03.13 Sitgraves CMR UL Health - Jewish Hospital - EMR.md" "Medical Records/2025-03-13 - Abby Sitgraves - Medical Record - Jewish Hospital - Certified EMR.md"

mv "2025.03.26 Sitgraves CMB UL Physicians - \$1724.00.pdf" "Medical Records/2025-03-26 - Abby Sitgraves - Medical Record - UofL Physicians - Certified Medical Bill \$1724.pdf"
[ -f "2025.03.26 Sitgraves CMB UL Physicians - \$1724.00.md" ] && mv "2025.03.26 Sitgraves CMB UL Physicians - \$1724.00.md" "Medical Records/2025-03-26 - Abby Sitgraves - Medical Record - UofL Physicians - Certified Medical Bill \$1724.md"

mv "2025.04.07 Sitgraves MB UL Hospital - \$3223.00.pdf" "Medical Records/2024-07-13 - Abby Sitgraves - Medical Record - Jewish Hospital - Medical Bill \$3223.pdf"
[ -f "2025.04.07 Sitgraves MB UL Hospital - \$3223.00.md" ] && mv "2025.04.07 Sitgraves MB UL Hospital - \$3223.00.md" "Medical Records/2024-07-13 - Abby Sitgraves - Medical Record - Jewish Hospital - Medical Bill \$3223.md"

mv "2025.05.29 UL Ortho Billing Request.pdf" "Medical Records/2025-05-29 - Abby Sitgraves - Medical Record - The Whaley Law Firm - UofL Orthopedics Billing Request (2).pdf"
[ -f "2025.05.29 UL Ortho Billing Request.md" ] && mv "2025.05.29 UL Ortho Billing Request.md" "Medical Records/2025-05-29 - Abby Sitgraves - Medical Record - The Whaley Law Firm - UofL Orthopedics Billing Request (2).md"

mv "Stigraves - ULP Primary Rec and Bill Request.pdf" "Medical Records/2025-05-29 - Abby Sitgraves - Medical Record - The Whaley Law Firm - UofL Primary Care Records and Billing Request.pdf"
[ -f "Stigraves - ULP Primary Rec and Bill Request.md" ] && mv "Stigraves - ULP Primary Rec and Bill Request.md" "Medical Records/2025-05-29 - Abby Sitgraves - Medical Record - The Whaley Law Firm - UofL Primary Care Records and Billing Request.md"

mv "Jewish Billing.pdf" "Medical Records/2024-07-13 - Abby Sitgraves - Medical Record - Jewish Hospital - ER Billing Summary (2).pdf"
[ -f "Jewish Billing.md" ] && mv "Jewish Billing.md" "Medical Records/2024-07-13 - Abby Sitgraves - Medical Record - Jewish Hospital - ER Billing Summary (2).md"

# Medical Records EML files
mv "2025.02.10-Sitgraves-CRR-UL-Health-x3-Email.eml" "Medical Records/2025-02-10 - Abby Sitgraves - Medical Record - The Whaley Law Firm - Email Certified Records Requests UofL Health.eml"

mv "2025.02.11 Sitgraves CRR Resp - UL Health - Ackd.eml" "Medical Records/2025-02-11 - Abby Sitgraves - Medical Record - UofL Health - Email Acknowledgment Certified Records Requests.eml"

mv "securerecords.eml" "Medical Records/2025-03-13 - Abby Sitgraves - Medical Record - UofL Health - Email Secure Records Ready for Pickup.eml"

# ============================================
# INSURANCE
# ============================================
echo "Moving Insurance files..."
mv "2024.08.19 Sitgraves Turn Over to Ins Ltr to Def Caal Worldwide.pdf" "Insurance/2024-08-19 - Abby Sitgraves - Insurance - The Whaley Law Firm - Letter to Defendant Preservation and Insurance Notice.pdf"
[ -f "2024.08.19 Sitgraves Turn Over to Ins Ltr to Def Caal Worldwide.md" ] && mv "2024.08.19 Sitgraves Turn Over to Ins Ltr to Def Caal Worldwide.md" "Insurance/2024-08-19 - Abby Sitgraves - Insurance - The Whaley Law Firm - Letter to Defendant Preservation and Insurance Notice.md"

mv "Sitgraves Subro LoR.pdf" "Insurance/2024-08-19 - Abby Sitgraves - Insurance - The Whaley Law Firm - Letter of Representation Subrogation.pdf"
[ -f "Sitgraves Subro LoR.md" ] && mv "Sitgraves Subro LoR.md" "Insurance/2024-08-19 - Abby Sitgraves - Insurance - The Whaley Law Firm - Letter of Representation Subrogation.md"

# ============================================
# LIEN
# ============================================
echo "Moving Lien files..."
mv "2025.04.16 Sitgraves ML UL Health One - Subro DC - Davenport.pdf" "Lien/2025-04-16 - Abby Sitgraves - Lien - UofL Health One - Subrogation Demand Letter.pdf"
[ -f "2025.04.16 Sitgraves ML UL Health One - Subro DC - Davenport.md" ] && mv "2025.04.16 Sitgraves ML UL Health One - Subro DC - Davenport.md" "Lien/2025-04-16 - Abby Sitgraves - Lien - UofL Health One - Subrogation Demand Letter.md"

mv "2025.02.10 Sitgraves ML Executed Med Auth - Key Benefits.pdf" "Lien/2025-02-10 - Abby Sitgraves - Lien - Key Benefits - HIPAA Authorization for Lien Investigation.pdf"
[ -f "2025.02.10 Sitgraves ML Executed Med Auth - Key Benefits.md" ] && mv "2025.02.10 Sitgraves ML Executed Med Auth - Key Benefits.md" "Lien/2025-02-10 - Abby Sitgraves - Lien - Key Benefits - HIPAA Authorization for Lien Investigation.md"

mv "2025.02.10 Sitgraves ML Final Lien Request - Key Benefits.pdf" "Lien/2025-02-10 - Abby Sitgraves - Lien - The Whaley Law Firm - Final Lien Request to Key Benefits.pdf"
[ -f "2025.02.10 Sitgraves ML Final Lien Request - Key Benefits.md" ] && mv "2025.02.10 Sitgraves ML Final Lien Request - Key Benefits.md" "Lien/2025-02-10 - Abby Sitgraves - Lien - The Whaley Law Firm - Final Lien Request to Key Benefits.md"

# ============================================
# EXPENSES
# ============================================
echo "Moving Expenses files..."
mv "2025.01.08 Sitgraves Adadevoh Exp Recpt - Jeff Cir Crt - \$313.72 (\$156.86 ea).PDF" "Expenses/2025-01-08 - Abby Sitgraves - Expenses - Jefferson Circuit Court - Filing Fee Receipt \$313.72.pdf"
[ -f "2025.01.08 Sitgraves Adadevoh Exp Recpt - Jeff Cir Crt - \$313.72 (\$156.86 ea).md" ] && mv "2025.01.08 Sitgraves Adadevoh Exp Recpt - Jeff Cir Crt - \$313.72 (\$156.86 ea).md" "Expenses/2025-01-08 - Abby Sitgraves - Expenses - Jefferson Circuit Court - Filing Fee Receipt \$313.72.md"

mv "2025.02.07 Sitgraves Adadevoh Exp Recpt - Jeff Cir Crt - Alias - \$62.20 (\$31.10 ea).PDF" "Expenses/2025-02-07 - Abby Sitgraves - Expenses - Jefferson Circuit Court - Alias Summons Fee Receipt \$62.20.pdf"
[ -f "2025.02.07 Sitgraves Adadevoh Exp Recpt - Jeff Cir Crt - Alias - \$62.20 (\$31.10 ea).md" ] && mv "2025.02.07 Sitgraves Adadevoh Exp Recpt - Jeff Cir Crt - Alias - \$62.20 (\$31.10 ea).md" "Expenses/2025-02-07 - Abby Sitgraves - Expenses - Jefferson Circuit Court - Alias Summons Fee Receipt \$62.20.md"

# ============================================
# NEGOTIATION SETTLEMENT
# ============================================
echo "Moving Negotiation Settlement files..."
mv "Abby Sitgraves Demand.pdf" "Negotiation Settlement/2025-06-30 - Abby Sitgraves - Negotiation Settlement - The Whaley Law Firm - UM Settlement Demand.pdf"
[ -f "Abby Sitgraves Demand.md" ] && mv "Abby Sitgraves Demand.md" "Negotiation Settlement/2025-06-30 - Abby Sitgraves - Negotiation Settlement - The Whaley Law Firm - UM Settlement Demand.md"

mv "Nayram Adadevoh Demand.pdf" "Negotiation Settlement/2025-06-30 - Abby Sitgraves - Negotiation Settlement - The Whaley Law Firm - UM Settlement Demand Nayram Adadevoh.pdf"
[ -f "Nayram Adadevoh Demand.md" ] && mv "Nayram Adadevoh Demand.md" "Negotiation Settlement/2025-06-30 - Abby Sitgraves - Negotiation Settlement - The Whaley Law Firm - UM Settlement Demand Nayram Adadevoh.md"

# ============================================
# LITIGATION
# ============================================
echo "Moving Litigation files..."
mv "2025.01.08 Sitgraves Adadevoh MVA Complaint.pdf" "Litigation/2025-01-08 - Abby Sitgraves - Litigation - Plaintiff - Complaint.pdf"
[ -f "2025.01.08 Sitgraves Adadevoh MVA Complaint.md" ] && mv "2025.01.08 Sitgraves Adadevoh MVA Complaint.md" "Litigation/2025-01-08 - Abby Sitgraves - Litigation - Plaintiff - Complaint.md"

mv "2025.01.08 Sitgraves Adadevoh Disc Req PP Def CAAL.pdf" "Litigation/2025-01-08 - Abby Sitgraves - Litigation - Plaintiff - Discovery Requests to Defendant CAAL.pdf"
[ -f "2025.01.08 Sitgraves Adadevoh Disc Req PP Def CAAL.md" ] && mv "2025.01.08 Sitgraves Adadevoh Disc Req PP Def CAAL.md" "Litigation/2025-01-08 - Abby Sitgraves - Litigation - Plaintiff - Discovery Requests to Defendant CAAL.md"

mv "2025.01.08 Sitgraves Adadevoh WOA Affidavit - Executed & Notarized.pdf" "Litigation/2025-01-08 - Abby Sitgraves - Litigation - Plaintiff - Warning Order Attorney Affidavit.pdf"
[ -f "2025.01.08 Sitgraves Adadevoh WOA Affidavit - Executed & Notarized.md" ] && mv "2025.01.08 Sitgraves Adadevoh WOA Affidavit - Executed & Notarized.md" "Litigation/2025-01-08 - Abby Sitgraves - Litigation - Plaintiff - Warning Order Attorney Affidavit.md"

mv "2025.01.29 Sitgraves POS Def Moore - Served 01.28.2025 910a - Signed Fred Moore.pdf" "Litigation/2025-01-29 - Abby Sitgraves - Litigation - Plaintiff - Proof of Service Defendant Moore.pdf"
[ -f "2025.01.29 Sitgraves POS Def Moore - Served 01.28.2025 910a - Signed Fred Moore.md" ] && mv "2025.01.29 Sitgraves POS Def Moore - Served 01.28.2025 910a - Signed Fred Moore.md" "Litigation/2025-01-29 - Abby Sitgraves - Litigation - Plaintiff - Proof of Service Defendant Moore.md"

mv "2025.02.05 Sitgraves WOA Report - Delivered but Not Served - Not given adequate notice.pdf" "Litigation/2025-02-05 - Abby Sitgraves - Litigation - WOA - Report Delivered But Not Served.pdf"
[ -f "2025.02.05 Sitgraves WOA Report - Delivered but Not Served - Not given adequate notice.md" ] && mv "2025.02.05 Sitgraves WOA Report - Delivered but Not Served - Not given adequate notice.md" "Litigation/2025-02-05 - Abby Sitgraves - Litigation - WOA - Report Delivered But Not Served.md"

mv "2025.02.17 Sitgraves Adadevoh DC CAAL Answer to Complaint.pdf" "Litigation/2025-02-17 - Abby Sitgraves - Litigation - Defendant - Answer to Complaint.pdf"
[ -f "2025.02.17 Sitgraves Adadevoh DC CAAL Answer to Complaint.md" ] && mv "2025.02.17 Sitgraves Adadevoh DC CAAL Answer to Complaint.md" "Litigation/2025-02-17 - Abby Sitgraves - Litigation - Defendant - Answer to Complaint.md"

mv "2025.03.24 Sitgraves Adadevoh DC CAAL NOS Resp to Disc Req.pdf" "Litigation/2025-03-24 - Abby Sitgraves - Litigation - Defendant - Notice of Service Discovery Responses.pdf"
[ -f "2025.03.24 Sitgraves Adadevoh DC CAAL NOS Resp to Disc Req.md" ] && mv "2025.03.24 Sitgraves Adadevoh DC CAAL NOS Resp to Disc Req.md" "Litigation/2025-03-24 - Abby Sitgraves - Litigation - Defendant - Notice of Service Discovery Responses.md"

mv "2025.05.01 Sitgraves Adadevoh DC MTC Resp to DC Disc Req - 05.05.2025 915a.pdf" "Litigation/2025-05-01 - Abby Sitgraves - Litigation - Defendant - Motion to Compel Discovery Responses.pdf"
[ -f "2025.05.01 Sitgraves Adadevoh DC MTC Resp to DC Disc Req - 05.05.2025 915a.md" ] && mv "2025.05.01 Sitgraves Adadevoh DC MTC Resp to DC Disc Req - 05.05.2025 915a.md" "Litigation/2025-05-01 - Abby Sitgraves - Litigation - Defendant - Motion to Compel Discovery Responses.md"

mv "2025.05.08 Sitgraves Adadevoh ORDER DC CAAL MTC - Resp Due in 14 Days.pdf" "Litigation/2025-05-08 - Abby Sitgraves - Litigation - Court - Order Granting Motion to Compel.pdf"
[ -f "2025.05.08 Sitgraves Adadevoh ORDER DC CAAL MTC - Resp Due in 14 Days.md" ] && mv "2025.05.08 Sitgraves Adadevoh ORDER DC CAAL MTC - Resp Due in 14 Days.md" "Litigation/2025-05-08 - Abby Sitgraves - Litigation - Court - Order Granting Motion to Compel.md"

mv "2025.05.09 LT DC re CAAL Discovery.pdf" "Litigation/2025-05-09 - Abby Sitgraves - Litigation - The Whaley Law Firm - Letter to Defense Counsel re Discovery.pdf"
[ -f "2025.05.09 LT DC re CAAL Discovery.md" ] && mv "2025.05.09 LT DC re CAAL Discovery.md" "Litigation/2025-05-09 - Abby Sitgraves - Litigation - The Whaley Law Firm - Letter to Defense Counsel re Discovery.md"

mv "2025-05-09-Abby-Sitgraves-Responses-to-Interrogatories-filed-Nayram-Adadevoh.pdf" "Litigation/2025-05-09 - Abby Sitgraves - Litigation - Plaintiff - Discovery Responses Nayram Adadevoh.pdf"
[ -f "2025-05-09-Abby-Sitgraves-Responses-to-Interrogatories-filed-Nayram-Adadevoh.md" ] && mv "2025-05-09-Abby-Sitgraves-Responses-to-Interrogatories-filed-Nayram-Adadevoh.md" "Litigation/2025-05-09 - Abby Sitgraves - Litigation - Plaintiff - Discovery Responses Nayram Adadevoh.md"

mv "Adadevoh Discovery Responses.pdf" "Litigation/2025-05-09 - Abby Sitgraves - Litigation - Plaintiff - Discovery Responses Adadevoh.pdf"
[ -f "Adadevoh Discovery Responses.md" ] && mv "Adadevoh Discovery Responses.md" "Litigation/2025-05-09 - Abby Sitgraves - Litigation - Plaintiff - Discovery Responses Adadevoh.md"

mv "Adadevoh Notice.pdf" "Litigation/2025-05-09 - Abby Sitgraves - Litigation - Plaintiff - Notice of Service Adadevoh.pdf"
[ -f "Adadevoh Notice.md" ] && mv "Adadevoh Notice.md" "Litigation/2025-05-09 - Abby Sitgraves - Litigation - Plaintiff - Notice of Service Adadevoh.md"

mv "Sitgraves Discovery Responses.pdf" "Litigation/2025-05-09 - Abby Sitgraves - Litigation - Plaintiff - Discovery Responses Sitgraves.pdf"
[ -f "Sitgraves Discovery Responses.md" ] && mv "Sitgraves Discovery Responses.md" "Litigation/2025-05-09 - Abby Sitgraves - Litigation - Plaintiff - Discovery Responses Sitgraves.md"

mv "Sitgraves Notice.pdf" "Litigation/2025-05-09 - Abby Sitgraves - Litigation - Plaintiff - Notice of Service Sitgraves.pdf"
[ -f "Sitgraves Notice.md" ] && mv "Sitgraves Notice.md" "Litigation/2025-05-09 - Abby Sitgraves - Litigation - Plaintiff - Notice of Service Sitgraves.md"

mv "Ds Answers to Ps 1st ROGS & RFPD.pdf" "Litigation/2025-03-24 - Abby Sitgraves - Litigation - Defendant - Answers to Interrogatories and Requests for Production.pdf"
[ -f "Ds Answers to Ps 1st ROGS & RFPD.md" ] && mv "Ds Answers to Ps 1st ROGS & RFPD.md" "Litigation/2025-03-24 - Abby Sitgraves - Litigation - Defendant - Answers to Interrogatories and Requests for Production.md"

mv "NOS D Caal Ans to Pfs 1st ROGS + RFPD.pdf" "Litigation/2025-03-24 - Abby Sitgraves - Litigation - Defendant - Notice of Service Answers to Discovery (2).pdf"
[ -f "NOS D Caal Ans to Pfs 1st ROGS + RFPD.md" ] && mv "NOS D Caal Ans to Pfs 1st ROGS + RFPD.md" "Litigation/2025-03-24 - Abby Sitgraves - Litigation - Defendant - Notice of Service Answers to Discovery (2).md"

# Litigation EML files (court notifications and attorney correspondence)
mv "ncp_for_efiler_jefferson_circuit_25-ci-000133_sitgraves_.eml" "Litigation/2025-01-08 - Abby Sitgraves - Litigation - Court - Email Notice of Court Proceedings Efiler.eml"

mv "ncp_for_efiler_jefferson_circuit_25-ci-000133_sitgraves_(1).eml" "Litigation/2025-01-08 - Abby Sitgraves - Litigation - Court - Email Notice of Court Proceedings Efiler (2).eml"

mv "ncp_for_efiler_jefferson_circuit_25-ci-000133_sitgraves_(2).eml" "Litigation/2025-01-08 - Abby Sitgraves - Litigation - Court - Email Notice of Court Proceedings Efiler (3).eml"

mv "ncp_jefferson_circuit_25-ci-000133_sitgraves_abby_et_al_vs.eml" "Litigation/2025-01-08 - Abby Sitgraves - Litigation - Court - Email Notice of Court Proceedings.eml"

mv "ncpforefilerjeffersoncircuit25-ci-000133sitgraves.eml" "Litigation/2025-01-08 - Abby Sitgraves - Litigation - Court - Email Notice for Efiler (Alt Format).eml"

mv "ncpjeffersoncircuit25-ci-000133sitgravesabbyetalvs.eml" "Litigation/2025-01-08 - Abby Sitgraves - Litigation - Court - Email Notice (Alt Format 2).eml"

mv "nef_for_efiler_jefferson_circuit_25-ci-000133_sitgraves.eml" "Litigation/2025-02-17 - Abby Sitgraves - Litigation - Court - Email Notice of Electronic Filing Efiler.eml"

mv "nef_for_efiler_jefferson_circuit_25-ci-000133_sitgraves(1).eml" "Litigation/2025-02-17 - Abby Sitgraves - Litigation - Court - Email Notice of Electronic Filing Efiler (2).eml"

mv "nef_for_efiler_jefferson_circuit__sitgraves__abby_et_al.eml" "Litigation/2025-03-24 - Abby Sitgraves - Litigation - Court - Email Notice of Electronic Filing.eml"

mv "nef_jefferson_circuit_25-ci-000133_sitgraves_abby_et_al_v.eml" "Litigation/2025-02-17 - Abby Sitgraves - Litigation - Court - Email Notice of Electronic Filing (Alt).eml"

mv "nefforefilerjeffersoncircuit25-ci-000133sitgraves.eml" "Litigation/2025-02-17 - Abby Sitgraves - Litigation - Court - Email NEF for Efiler (Alt Format).eml"

mv "nefforefilerjeffersoncircuitsitgravesabbyetal.eml" "Litigation/2025-03-24 - Abby Sitgraves - Litigation - Court - Email NEF (Alt Format 2).eml"

mv "nefjeffersoncircuit25-ci-000133sitgravesabbyetalv.eml" "Litigation/2025-02-17 - Abby Sitgraves - Litigation - Court - Email NEF (Alt Format 3).eml"

mv "notice_of_entry__jefferson_circuit_25-ci-000133_sitgraves_.eml" "Litigation/2025-05-08 - Abby Sitgraves - Litigation - Court - Email Notice of Entry Order.eml"

mv "noticeofentryjeffersoncircuit25-ci-000133sitgraves.eml" "Litigation/2025-05-08 - Abby Sitgraves - Litigation - Court - Email Notice of Entry (Alt Format).eml"

mv "sitgraves__adadevoh_v_caal_worldwide_jefferson_25-ci-0001.eml" "Litigation/2025-01-08 - Abby Sitgraves - Litigation - Court - Email Case Filing Confirmation.eml"

mv "sitgravesadadevohvcaalworldwidejefferson25-ci-0001.eml" "Litigation/2025-01-08 - Abby Sitgraves - Litigation - Court - Email Case Filing Confirmation (Alt Format).eml"

mv "2025.03.28 Sitgraves Adadevoh BK Upd to DC - Resp to DC Disc Req Coming in following days - Request Vehicle Inspection.eml" "Litigation/2025-03-28 - Abby Sitgraves - Litigation - The Whaley Law Firm - Email Update to Defense Counsel re Discovery.eml"

mv "2025.04.14 Sitgraves DC FU on Resp to DC Disc Req.eml" "Litigation/2025-04-14 - Abby Sitgraves - Litigation - The Whaley Law Firm - Email Follow Up to Defense Counsel re Discovery.eml"

# ============================================
# MOVE FILES NEEDING REVIEW
# ============================================
echo "Moving files needing review to Review_Needed folder..."
# Duplicate EML files
mv "2025.02.11-Sitgraves-CRR-Resp-UL-Health-Ackd.eml" "Review_Needed/"
mv "ncp_jefferson_circuit_25-ci-000133_sitgraves_abby_et_al_vs(1)(1).eml" "Review_Needed/"
mv "ncp_jefferson_circuit_25-ci-000133_sitgraves_abby_et_al_vs(1).eml" "Review_Needed/"
mv "ncp_jefferson_circuit_25-ci-000133_sitgraves_abby_et_al_vs(2).eml" "Review_Needed/"
mv "ncp_jefferson_circuit_25-ci-000133_sitgraves_abby_et_al_vs(3).eml" "Review_Needed/"
mv "ncpforefilerjeffersoncircuit25-ci-000133sitgraves1.eml" "Review_Needed/"
mv "ncpforefilerjeffersoncircuit25-ci-000133sitgraves2.eml" "Review_Needed/"
mv "ncpjeffersoncircuit25-ci-000133sitgravesabbyetalvs1.eml" "Review_Needed/"
mv "ncpjeffersoncircuit25-ci-000133sitgravesabbyetalvs11.eml" "Review_Needed/"
mv "ncpjeffersoncircuit25-ci-000133sitgravesabbyetalvs2.eml" "Review_Needed/"
mv "ncpjeffersoncircuit25-ci-000133sitgravesabbyetalvs3.eml" "Review_Needed/"
mv "nef_jefferson_circuit_25-ci-000133_sitgraves_abby_et_al_v(1).eml" "Review_Needed/"
mv "nef_jefferson_circuit_25-ci-000133_sitgraves_abby_et_al_v(2).eml" "Review_Needed/"
mv "nef_jefferson_circuit_25-ci-000133_sitgraves_abby_et_al_v(3).eml" "Review_Needed/"
mv "nefforefilerjeffersoncircuit25-ci-000133sitgraves1.eml" "Review_Needed/"
mv "nefjeffersoncircuit25-ci-000133sitgravesabbyetalv1.eml" "Review_Needed/"
mv "nefjeffersoncircuit25-ci-000133sitgravesabbyetalv2.eml" "Review_Needed/"
mv "nefjeffersoncircuit25-ci-000133sitgravesabbyetalv3.eml" "Review_Needed/"
mv "2025.03.28-Sitgraves-Adadevoh-BK-Upd-to-DC-Resp-to-DC-Disc-Req-Coming-in-following-days-Request-Vehicle-Inspection.eml" "Review_Needed/"
mv "2025.04.14-Sitgraves-DC-FU-on-Resp-to-DC-Disc-Req.eml" "Review_Needed/"

# Duplicate PDF pairs
mv "2025-05-09-Abby-Sitgraves-PLAINTIFFS-RESPONSES-TO-INTERROGATORIES.pdf" "Review_Needed/"
[ -f "2025-05-09-Abby-Sitgraves-PLAINTIFFS-RESPONSES-TO-INTERROGATORIES.md" ] && mv "2025-05-09-Abby-Sitgraves-PLAINTIFFS-RESPONSES-TO-INTERROGATORIES.md" "Review_Needed/"

mv "2025-05-09-Abby-Sitgraves-Plaintiffs-Responses-Interrogatories-and-Production.pdf" "Review_Needed/"
[ -f "2025-05-09-Abby-Sitgraves-Plaintiffs-Responses-Interrogatories-and-Production.md" ] && mv "2025-05-09-Abby-Sitgraves-Plaintiffs-Responses-Interrogatories-and-Production.md" "Review_Needed/"

mv "2025-05-09-Abby-Sitgraves-Plaintiffs-Responses-to-Interrogatories-filed-by-Plaintiff.pdf" "Review_Needed/"
[ -f "2025-05-09-Abby-Sitgraves-Plaintiffs-Responses-to-Interrogatories-filed-by-Plaintiff.md" ] && mv "2025-05-09-Abby-Sitgraves-Plaintiffs-Responses-to-Interrogatories-filed-by-Plaintiff.md" "Review_Needed/"

mv "Adadevoh Discovery Responses(1).pdf" "Review_Needed/"
[ -f "Adadevoh Discovery Responses(1).md" ] && mv "Adadevoh Discovery Responses(1).md" "Review_Needed/"

mv "Adadevoh Notice(1).pdf" "Review_Needed/"
[ -f "Adadevoh Notice(1).md" ] && mv "Adadevoh Notice(1).md" "Review_Needed/"

mv "Sitgraves Discovery Responses(1).pdf" "Review_Needed/"
[ -f "Sitgraves Discovery Responses(1).md" ] && mv "Sitgraves Discovery Responses(1).md" "Review_Needed/"

mv "Sitgraves Notice(1).pdf" "Review_Needed/"
[ -f "Sitgraves Notice(1).md" ] && mv "Sitgraves Notice(1).md" "Review_Needed/"

mv "Production.pdf" "Review_Needed/"
[ -f "Production.md" ] && mv "Production.md" "Review_Needed/"

mv "Copier Scans_20250902_131241.pdf" "Review_Needed/"
[ -f "Copier Scans_20250902_131241.md" ] && mv "Copier Scans_20250902_131241.md" "Review_Needed/"

mv "4-1-25 Processed.pdf" "Review_Needed/"
[ -f "4-1-25 Processed.md" ] && mv "4-1-25 Processed.md" "Review_Needed/"

mv "2025.02.10 Sitgraves ML Executed Med Auth - Key Benefits(1).pdf" "Review_Needed/"
[ -f "2025.02.10 Sitgraves ML Executed Med Auth - Key Benefits(1).md" ] && mv "2025.02.10 Sitgraves ML Executed Med Auth - Key Benefits(1).md" "Review_Needed/"

mv "Fax_2025.02.10 Sitgraves ML Final Lien Request - Key Benefits_2025-02-10-1100-PST.pdf" "Review_Needed/"
[ -f "Fax_2025.02.10 Sitgraves ML Final Lien Request - Key Benefits_2025-02-10-1100-PST.md" ] && mv "Fax_2025.02.10 Sitgraves ML Final Lien Request - Key Benefits_2025-02-10-1100-PST.md" "Review_Needed/"

mv "health insurance card - back.jpg" "Review_Needed/"
mv "health insurance card - front.jpg" "Review_Needed/"

mv "filename.md" "Review_Needed/"
mv "initial-todo.md" "Review_Needed/"

# ============================================
# DELETE NON-CASE FILES
# ============================================
echo "Deleting non-case files..."
rm "4-1-25 Processed(1).pdf"
[ -f "4-1-25 Processed(1).md" ] && rm "4-1-25 Processed(1).md"

echo "Reorganization complete!"
echo ""
echo "Summary:"
echo "- Files moved to Client: $(find "Client" -type f | wc -l)"
echo "- Files moved to Investigation: $(find "Investigation" -type f | wc -l)"
echo "- Files moved to Medical Records: $(find "Medical Records" -type f | wc -l)"
echo "- Files moved to Insurance: $(find "Insurance" -type f | wc -l)"
echo "- Files moved to Lien: $(find "Lien" -type f | wc -l)"
echo "- Files moved to Expenses: $(find "Expenses" -type f | wc -l)"
echo "- Files moved to Negotiation Settlement: $(find "Negotiation Settlement" -type f | wc -l)"
echo "- Files moved to Litigation: $(find "Litigation" -type f | wc -l)"
echo "- Files moved to Review_Needed: $(find "Review_Needed" -type f | wc -l)"
