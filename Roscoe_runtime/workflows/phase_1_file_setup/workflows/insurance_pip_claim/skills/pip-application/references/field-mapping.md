# KACP Application Field Mapping

## Form Field to Data Source Mapping

### Section 1: Personal Information

| Form Field | Data Source | JSON Path | Notes |
|------------|-------------|-----------|-------|
| Your Name | overview.json | `client_name` | Full legal name |
| Home Phone | overview.json | `client_phone` | Primary contact |
| Work Phone | contacts.json | `[type=employer].phone` | If employed |
| Your Address | overview.json | `client_address` | Street address |
| City, State, Zip | overview.json | Parsed from `client_address` | |
| Date of Birth | contacts.json | `[type=client].dob` | MM/DD/YYYY format |
| Social Security No. | contacts.json | `[type=client].ssn` | XXX-XX-XXXX |

### Section 2: Accident Information

| Form Field | Data Source | JSON Path | Notes |
|------------|-------------|-----------|-------|
| Date of Accident | overview.json | `accident_date` | From case setup |
| Time of Accident | intake | Captured during intake | Optional |
| Place of Accident | intake/police report | Location description | |
| Brief Description | overview.json | `case_summary` | Short narrative |

### Section 3: Vehicle/Insurance Information

| Form Field | Data Source | JSON Path | Notes |
|------------|-------------|-----------|-------|
| Own Motor Vehicle? | waterfall answers | From waterfall Q1 | Yes/No |
| Insurance Company | insurance.json | `pip.pip_insurer` | From waterfall |
| Policy Number | insurance.json | `pip.policy_number` | If known |

### Section 4: Injury Information

| Form Field | Data Source | JSON Path | Notes |
|------------|-------------|-----------|-------|
| Describe Your Injury | intake | Injury description | From initial interview |

### Section 5: Medical Treatment

| Form Field | Data Source | JSON Path | Notes |
|------------|-------------|-----------|-------|
| Doctor's Name | medical_providers.json | `[0].provider_name` | Primary treating |
| Doctor's Address | medical_providers.json | `[0].address` | |
| Hospital Name | medical_providers.json | `[type=hospital].provider_name` | If applicable |
| Hospital Address | medical_providers.json | `[type=hospital].address` | |

### Section 6: Employment Information

| Form Field | Data Source | JSON Path | Notes |
|------------|-------------|-----------|-------|
| Employer Name | contacts.json | `[type=employer].name` | If employed |
| Employer Address | contacts.json | `[type=employer].address` | |
| Occupation | contacts.json | `[type=employer].occupation` | |

## Python Dictionary Structure

```python
field_values = {
    # Personal Info
    "PatientName": "John Smith",
    "HomePhone": "502-555-1234",
    "WorkPhone": "",
    "StreetAddress": "123 Main St",
    "City": "Louisville",
    "State": "KY",
    "Zip": "40202",
    "DateOfBirth": "01/15/1985",
    "SSN": "123-45-6789",
    
    # Accident Info
    "AccidentDate": "12/01/2024",
    "AccidentTime": "3:30 PM",
    "AccidentLocation": "Intersection of Main St and Broadway, Louisville, KY",
    "AccidentDescription": "Rear-ended while stopped at red light",
    
    # Vehicle/Insurance
    "OwnVehicle_Yes": False,
    "OwnVehicle_No": True,
    "InsuranceCompany": "State Farm",
    "PolicyNumber": "POL-12345",
    
    # Injury
    "InjuryDescription": "Neck pain, back pain, headaches following collision",
    
    # Medical
    "DoctorName": "Dr. Smith",
    "DoctorAddress": "123 Medical Way, Louisville, KY 40202",
    "HospitalName": "University Hospital",
    "HospitalAddress": "550 S Jackson St, Louisville, KY 40202",
    
    # Employment
    "EmployerName": "ABC Company",
    "EmployerAddress": "456 Business Blvd, Louisville, KY 40203",
    "Occupation": "Office Manager"
}
```

## Handling Missing Values

### Required Fields (Must Have)
- Client name
- Client phone
- Client address
- Date of birth
- SSN
- Accident date
- PIP carrier

### Optional Fields (Can Leave Blank)
- Work phone (if not employed)
- Time of accident
- Hospital (if no hospital visit)
- Employer info (if not employed)

### Prompting for Missing Required Data

```
To complete the PIP Application, I need:

1. Client's date of birth (MM/DD/YYYY): _______
2. Client's SSN (XXX-XX-XXXX): _______
3. Brief description of injuries: _______

(Time of accident and employer info are optional if not applicable)
```

