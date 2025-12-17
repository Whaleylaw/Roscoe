flowchart TD
  A[Caller: agent/UI/orchestrator] --> B[get_case_status_message(case_state)]
  B --> C[StateMachine.__init__ loads JSON defs]
  C --> C1[phase_definitions.json]
  C --> C2[workflow_definitions.json]
  C --> C3[derivation_rules.json (optional)]

  B --> D[get_case_status(case_state)]
  D --> E[current_phase = case_state.current_phase]
  D --> F[CaseData adapter loads "truth" case files]
  F --> F1[Case Information/*.json, Database/*.json]
  D --> G[sync_workflows_with_data(case_state, case_data)]
  G --> G1[validate_workflow_against_data() uses derivation_rules.workflow_derivations (partial)]
  G --> G2[Upgrades workflow status + audit_log entries]

  D --> H{Litigation phase?}
  H -->|yes| I[load_litigation_data() + validate_litigation_state()]
  H -->|no| J[skip litigation validation]

  D --> K[suggest_phase_change(case_state, case_data)]
  K --> K1[Checks phase_definitions.exit_criteria.hard_blockers]
  K --> K2[Checks all workflows in phase are complete/skipped]
  K --> K3[Sets case_state.pending_phase_change (suggestion only)]

  D --> L[compute_sol_status(case_data, litigation_data)]
  L --> L1[Uses derivation_rules.sol_tracking thresholds]

  D --> M[_determine_next_actions(case_state, current_phase)]
  M --> M1[Uses phase_definitions.phases[phase].workflows list]
  M --> M2[Uses workflow_definitions.workflows[wf].steps + workflow_dependencies]
  M --> M3[Returns NextAction list (owner/can_automate/tool_available/manual_fallback/prompt)]

  D --> N[_check_alerts(case_state) + SOL alert injection]
  D --> O[Return status dict]
  O --> P[format_status_for_agent(status)]


  Where this lives: Roscoe_workflows/workflow_engine/orchestrator/state_machine.py
What it consumes: schemas/phase_definitions.json, schemas/workflow_definitions.json, schemas/derivation_rules.json (+ CaseData’s case JSON files)
What it produces: a status object + human-readable status message (next actions, pending items, alerts, suggested phase change)