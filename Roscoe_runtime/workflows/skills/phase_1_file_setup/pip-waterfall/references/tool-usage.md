# PIP Waterfall Tool Usage

## pip_waterfall.py

**Location**: `tools/pip_waterfall.py`

## Command Line Usage

### Interactive Mode
```bash
python pip_waterfall.py --interactive
```

Walks through each question interactively and returns result.

### Pre-filled Answers
```bash
python pip_waterfall.py \
  --client-on-title no \
  --vehicle-insured yes \
  --vehicle-insurer "State Farm" \
  --vehicle-policy "POL-12345"
```

### From JSON File
```bash
python pip_waterfall.py --from-json /path/to/answers.json
```

JSON format:
```json
{
  "client_on_title": false,
  "vehicle_insured": true,
  "vehicle_insurer": "State Farm",
  "vehicle_policy": "POL-12345"
}
```

## Python API Usage

### Basic Call

```python
from pip_waterfall import run_waterfall

result = run_waterfall(
    client_on_title=False,
    vehicle_insured=True,
    vehicle_insurer="State Farm",
    vehicle_policy="POL-12345"
)
```

### Full Parameters

```python
result = run_waterfall(
    # Step 1
    client_on_title=False,           # Is client on title of vehicle?
    client_vehicle_insured=None,     # If on title, was it insured?
    
    # Step 2
    vehicle_insured=True,            # Was vehicle occupied insured?
    vehicle_insurer="State Farm",    # Insurer name
    vehicle_policy="POL-12345",      # Policy number
    
    # Step 3
    client_has_own_insurance=None,   # Does client have own policy?
    client_insurer=None,
    client_policy=None,
    
    # Step 4
    household_has_insurance=None,    # Does household member have policy?
    household_member_name=None,
    household_insurer=None,
    household_policy=None
)
```

## Return Value

```python
{
    "pip_insurer": "State Farm",
    "pip_insurer_type": "vehicle",      # vehicle, client, household, kac, disqualified
    "policy_number": "POL-12345",
    "is_kac": False,
    "is_disqualified": False,
    "waterfall_step": 2,                # Which step determined result
    "recommendation": "PIP coverage through vehicle's insurer",
    "next_steps": [
        "Complete KACP Application",
        "Send LOR to State Farm PIP department",
        "Open PIP claim",
        "Verify ready to pay bills"
    ],
    "waterfall_path": [
        "Step 1: Client not on vehicle title",
        "Step 2: Vehicle occupied was insured",
        "Determined: State Farm"
    ]
}
```

## Result Types

| pip_insurer_type | Meaning |
|------------------|---------|
| `vehicle` | PIP from vehicle's insurer |
| `client` | PIP from client's own insurer |
| `household` | PIP from household member's insurer |
| `kac` | Kentucky Assigned Claims required |
| `disqualified` | Client cannot receive PIP |

## Integration Example

```python
import json
from pathlib import Path
from pip_waterfall import run_waterfall

def determine_pip_carrier(case_folder: str, answers: dict) -> dict:
    """
    Run PIP waterfall and save result to case file.
    """
    result = run_waterfall(**answers)
    
    # Update insurance.json
    case_path = Path(case_folder)
    insurance_path = case_path / "Case Information/insurance.json"
    
    with open(insurance_path) as f:
        insurance = json.load(f)
    
    insurance["pip"] = {
        "pip_insurer": result["pip_insurer"],
        "pip_insurer_type": result["pip_insurer_type"],
        "policy_number": result.get("policy_number"),
        "is_kac": result["is_kac"],
        "is_disqualified": result["is_disqualified"],
        "waterfall_step": result["waterfall_step"],
        "waterfall_date": datetime.now().isoformat(),
        "waterfall_path": result["waterfall_path"]
    }
    
    with open(insurance_path, "w") as f:
        json.dump(insurance, f, indent=2)
    
    return result
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Missing required parameter | Not enough info to determine | Prompt for more information |
| Invalid insurer type | Bad data | Validate input before calling |
| File not found | JSON path wrong | Check case folder structure |

