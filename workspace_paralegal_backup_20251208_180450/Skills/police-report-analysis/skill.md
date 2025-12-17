# Police Report Analysis Skill

## When to Use
Use this skill when you receive a Kentucky police/accident report (typically from BuyCrash) and need to extract key information for the case file.

## Input
- Kentucky Collision Report PDF (from BuyCrash or similar)
- Client's name and role in accident (driver/passenger of which unit)

## Output
A structured extraction with:
1. Human-readable accident summary
2. Client involvement details
3. Insurance information for all parties
4. Liability indicators
5. Story comparison (client's version vs. report narrative)
6. Red flags
7. PIP-relevant ownership information

---

## Step 1: Identify the Client's Unit

Before extracting, determine which "Unit" the client is:
- **Unit 1** = typically the first vehicle listed
- **Unit 2** = second vehicle
- **Unit 3+** = additional vehicles

The client may be:
- Driver of a unit
- Passenger in a unit
- Pedestrian
- Other (cyclist, etc.)

---

## Step 2: Extract Core Information

### Accident Details
Extract from the report header:
- **Report Number**: (top of form)
- **Date of Accident**: 
- **Time of Accident**:
- **Location**: (street/intersection, city, county)
- **Weather Conditions**: (use code reference)
- **Road Conditions**: (use code reference)
- **Manner of Collision**: (use code reference - codes 1-10)

### For Each Unit (Vehicle)

#### Unit Information
- Unit Number (1, 2, 3...)
- Vehicle Year/Make/Model
- License Plate
- VIN (if listed)

#### Driver Information
- Driver Name
- Driver Address
- Driver License Number
- **Is Driver the Owner?** (YES/NO - critical for PIP)
- Owner Name (if different from driver)

#### Insurance Information
- Insurance Company Name
- Policy Number
- Insurance Phone (if listed)

#### Injury Information
- Injury Severity Code (use code reference)
- Transported? (Y/N)
- Transported To (hospital name)

---

## Step 3: Liability Analysis

Extract liability indicators:

### Citations Issued
- Who was cited?
- Citation type/code
- Violation description

### Contributing Factors
- Driver contributing factors (code reference)
- Environmental factors
- Vehicle factors

### Fault Indicators
- Point of impact on each vehicle
- Direction of travel
- Traffic control present?
- Who had right of way?

---

## Step 4: Narrative Analysis

### Officer's Narrative
Copy the officer's narrative section verbatim, then summarize.

### Diagram
Describe the accident diagram if present.

### Witness Information
- Witness names
- Witness contact info
- Witness statements (if included)

---

## Step 5: Story Comparison

Compare client's version of events to the police report:

| Element | Client's Version | Police Report | Match? |
|---------|------------------|---------------|--------|
| Who was at fault? | | | |
| How collision occurred | | | |
| Traffic signals/signs | | | |
| Speed estimates | | | |
| Weather/visibility | | | |

Note any **discrepancies** that need to be addressed.

---

## Step 6: Red Flags

Flag any of the following:
- [ ] Client was cited
- [ ] Client found partially at fault
- [ ] Client's version differs significantly from report
- [ ] Pre-existing damage noted on client's vehicle
- [ ] Client refused medical attention at scene
- [ ] Delayed injury report (injury not noted at scene)
- [ ] Alcohol/drug involvement noted
- [ ] Client was uninsured
- [ ] Client was driving uninsured vehicle they own (PIP disqualifier)
- [ ] Witnesses contradict client's story
- [ ] Inconsistent statements in report

---

## Step 7: PIP-Relevant Information

Extract for PIP waterfall:
- **Was client the driver?** (Y/N)
- **Was client on the title of the vehicle?** (check owner field)
- **Was the vehicle insured?** (Y/N + insurer name)
- **Client's own insurance** (if listed)

This feeds into: `/Tools/insurance/pip_waterfall.py`

---

## Output Template

Save extraction to: `/Reports/extractions/police_report_{{REPORT_NUMBER}}.md`

Use the output template at: `/Skills/police-report-analysis/output_template.md`

---

## Code Reference

For decoding Kentucky collision report codes, see:
`/Skills/police-report-analysis/kentucky_codes.md`

---

## After Extraction

1. Update `insurance.json` with all insurance companies identified
2. Run PIP waterfall if ownership info indicates potential issue
3. Flag any red flags for attorney review
4. Compare to client's intake story

