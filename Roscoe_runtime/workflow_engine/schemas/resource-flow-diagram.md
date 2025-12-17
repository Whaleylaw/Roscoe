Resource flow diagram (skills/tools/resources: “what should load where”)
This is the intended integration flow described by schemas/resource_mappings.json. Today it’s mostly an index, not executed by state_machine.py.

flowchart TD
  A[Caller: agent runtime] --> B[Needs context for current phase/workflow]
  B --> C[current_phase + active workflow(s)]
  C --> D[resource_mappings.json]
  D --> D1[phase_to_resource_mapping]
  D --> D2[workflow_to_tool_mapping]
  D --> D3[skills + tools catalogs]
  D --> D4[workflows dirs mapping]

  D1 --> E[Load phase skill set]
  D1 --> F[Load phase tool set]
  D1 --> G[Load phase workflow_dir docs]

  D2 --> H[Load workflow-specific skills]
  D2 --> I[Load workflow-specific tool calls / missing_tools]
  D2 --> J[Attach checklists/templates references]

  E --> K[Skill loader opens Skills/.../SKILL.md]
  F --> L[Tool runner imports/executes Tools/... scripts]
  G --> M[Workflow docs loader reads workflows/phase_*/ files]
  H --> K
  I --> L
  J --> N[Forms/checklists reference loader]

  K --> O[Agent has procedural instructions]
  L --> P[Automation available (tool calls)]
  M --> Q[Agent has narrative SOP + checklists]
  N --> Q

  O --> R[Agent executes workflow step]
  P --> R
  Q --> R

  R --> S[Updates "truth" case files +/or case_state]
  S --> T[Next get_case_status run reflects progress]

  Where this mapping lives: Roscoe_workflows/workflow_engine/schemas/resource_mappings.json
Key idea: Phase/workflow selection comes from the state machine; resource loading comes from the mapping index.
Current wiring reality: state_machine.py does not read resource_mappings.json yet (so the “resource loader” box is a separate layer you’d implement in the agent/orchestrator).
