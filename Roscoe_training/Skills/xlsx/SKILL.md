---
name: xlsx
description: Comprehensive spreadsheet creation, editing, and analysis with formulas, formatting, and data visualization. Use for medical billing summaries, damages calculations, expense tracking, lien analysis, or any Excel work requiring proper formula handling.
---

# XLSX creation, editing, and analysis

## Overview

A user may ask you to create, edit, or analyze the contents of an .xlsx file. You have different tools and workflows available for different tasks.

## Legal Use Cases

Common Excel tasks in personal injury practice:
- **Medical billing summaries**: Compile bills, balances, write-offs
- **Damages calculations**: Calculate economic losses with formulas
- **Lien tracking**: Monitor medical liens, amounts, priorities
- **Expense reports**: Track case expenses with totals
- **Settlement breakdowns**: Calculate distributions after fees/liens
- **Lost wage calculations**: Compute lost income over time

## Requirements for Outputs

### All Excel files

#### Zero Formula Errors
- Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

#### Preserve Existing Templates (when updating templates)
- Study and EXACTLY match existing format, style, and conventions when modifying files
- Never impose standardized formatting on files with established patterns
- Existing template conventions ALWAYS override these guidelines

### Financial models

#### Color Coding Standards
Unless otherwise stated by the user or existing template

- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, and numbers users will change for scenarios
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links pulling from other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention or cells that need to be updated

#### Number Formatting Standards

- **Currency**: Use $#,##0 format; ALWAYS specify units in headers
- **Zeros**: Use number formatting to make all zeros "-", including percentages (e.g., "$#,##0;($#,##0);-")
- **Percentages**: Default to 0.0% format (one decimal)
- **Negative numbers**: Use parentheses (123) not minus -123

## CRITICAL: Use Formulas, Not Hardcoded Values

**Always use Excel formulas instead of calculating values in Python and hardcoding them.** This ensures the spreadsheet remains dynamic and updateable.

### ❌ WRONG - Hardcoding Calculated Values
```python
# Bad: Calculating in Python and hardcoding result
total = df['Bills'].sum()
sheet['B10'] = total  # Hardcodes 5000

# Bad: Computing percentage in Python
pct = amount / total_bills
sheet['C5'] = pct  # Hardcodes 0.15
```

### ✅ CORRECT - Using Excel Formulas
```python
# Good: Let Excel calculate the sum
sheet['B10'] = '=SUM(B2:B9)'

# Good: Percentage as Excel formula
sheet['C5'] = '=C4/B10'
```

## Reading and analyzing data

### Data analysis with pandas
For data analysis, visualization, and basic operations, use **pandas**:

```python
import pandas as pd

# Read Excel
df = pd.read_excel('file.xlsx')  # Default: first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict

# Analyze
df.head()      # Preview data
df.info()      # Column info
df.describe()  # Statistics

# Write Excel
df.to_excel('output.xlsx', index=False)
```

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**: Use the recalc.py script
   ```bash
   python scripts/recalc.py output.xlsx
   ```
6. **Verify and fix any errors**: 
   - The script returns JSON with error details
   - If `status` is `errors_found`, check `error_summary` for specific error types and locations
   - Fix the identified errors and recalculate again

### Creating new Excel files

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active

# Add data
sheet['A1'] = 'Provider'
sheet['B1'] = 'Amount'
sheet.append(['Hospital', 5000])
sheet.append(['Doctor', 1500])

# Add formula
sheet['B4'] = '=SUM(B2:B3)'

# Formatting
sheet['A1'].font = Font(bold=True)
sheet['B4'].font = Font(bold=True)
sheet.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```

### Editing existing Excel files

```python
from openpyxl import load_workbook

# Load existing file
wb = load_workbook('existing.xlsx')
sheet = wb.active

# Modify cells
sheet['A1'] = 'New Value'
sheet.insert_rows(2)  # Insert row at position 2

# Add new sheet
new_sheet = wb.create_sheet('Summary')
new_sheet['A1'] = 'Total'

wb.save('modified.xlsx')
```

## Recalculating formulas

Excel files created or modified by openpyxl contain formulas as strings but not calculated values. Use the provided `recalc.py` script:

```bash
python scripts/recalc.py <excel_file> [timeout_seconds]
```

Example:
```bash
python scripts/recalc.py output.xlsx 30
```

The script:
- Automatically sets up LibreOffice macro on first run
- Recalculates all formulas in all sheets
- Scans ALL cells for Excel errors (#REF!, #DIV/0!, etc.)
- Returns JSON with detailed error locations and counts

### Interpreting recalc.py Output
```json
{
  "status": "success",           // or "errors_found"
  "total_errors": 0,             // Total error count
  "total_formulas": 42,          // Number of formulas in file
  "error_summary": {             // Only present if errors found
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

## Best Practices

### Library Selection
- **pandas**: Best for data analysis, bulk operations, and simple data export
- **openpyxl**: Best for complex formatting, formulas, and Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 refers to cell A1)
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: If opened with `data_only=True` and saved, formulas are replaced with values and permanently lost
- Formulas are preserved but not evaluated - use recalc.py to update values

### Working with pandas
- Specify data types to avoid inference issues: `pd.read_excel('file.xlsx', dtype={'id': str})`
- For large files, read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates properly: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Dependencies

- **pandas**: `pip install pandas openpyxl` (for data analysis)
- **openpyxl**: `pip install openpyxl` (for formula/formatting work)
- **LibreOffice**: Required for formula recalculation via recalc.py

