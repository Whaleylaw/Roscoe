High-level mental model
There are two layers of “state” in this design:
Case “truth” data (facts of the file): loaded via the CaseData adapter (from your case JSON files like Case Information/*.json). state_machine.py uses this to validate/auto-correct workflow status.
Workflow engine state (progress tracking): the case_state dict that tracks phase/workflow statuses, pending items, next actions, etc. Its expected shape is described by schemas/case_state.schema.json.
The schemas JSONs define the rules of the game:
phase_definitions.json: what phases exist, ordering, what workflows belong to each phase, and how to decide a phase can exit.
workflow_definitions.json: what each workflow is, its steps, dependencies, and per-step metadata (owner, prompts, tool availability, skill/template hints, etc).
derivation_rules.json: heuristics to infer/confirm progress from the “truth” case data (and SOL rules). In this code, only some parts are wired in.
resource_mappings.json: a “resource index” of Skills/Tools/workflow folders and mappings. Important: state_machine.py does not read this file currently; it’s for orchestration/documentation/integration elsewhere.
Step-by-step: what StateMachine actually does at runtime
1) Boot: load the engine definitions
When you construct StateMachine, it loads JSON definitions from schemas/:
phase_definitions.json → self.phase_defs
workflow_definitions.json → self.workflow_defs
derivation_rules.json → self.derivation_rules (optional)
You can see that load path and what gets loaded here:
state_machine.pyLines 99-127
def __init__(self, schemas_dir: Optional[Path] = None):
    """Initialize with path to schema definitions."""
    if schemas_dir is None:
        schemas_dir = Path(__file__).parent.parent / "schemas"

    self.schemas_dir = schemas_dir
    self._load_definitions()
    self._load_derivation_rules()

    # Cache for CaseData instances
    self._case_data_cache = {}

def _load_definitions(self):
    """Load phase and workflow definitions from JSON schemas."""
    with open(self.schemas_dir / "phase_definitions.json") as f:
        self.phase_defs = json.load(f)

    with open(self.schemas_dir / "workflow_definitions.json") as f:
        self.workflow_defs = json.load(f)

def _load_derivation_rules(self):
    """Load derivation rules for validation."""
    rules_path = self.schemas_dir / "derivation_rules.json"
    if rules_path.exists():
        with open(rules_path) as f:
            self.derivation_rules = json.load(f)
    else:
        self.derivation_rules = {}
def __init__(self, schemas_dir: Optional[Path] = None):    """Initialize with path to schema definitions."""    if schemas_dir is None:        schemas_dir = Path(__file__).parent.parent / "schemas"    self.schemas_dir = schemas_dir    self._load_definitions()    self._load_derivation_rules()    # Cache for CaseData instances    self._case_data_cache = {}def _load_definitions(self):    """Load phase and workflow definitions from JSON schemas."""    with open(self.schemas_dir / "phase_definitions.json") as f:        self.phase_defs = json.load(f)    with open(self.schemas_dir / "workflow_definitions.json") as f:        self.workflow_defs = json.load(f)def _load_derivation_rules(self):    """Load derivation rules for validation."""    rules_path = self.schemas_dir / "derivation_rules.json"    if rules_path.exists():        with open(rules_path) as f:            self.derivation_rules = json.load(f)    else:        self.derivation_rules = {}
2) The “main loop” entrypoint: get_case_status(case_state)
get_case_status is the primary function the agent/orchestrator calls to compute “where are we and what next?”
At a high level, it does:
Read case_state.current_phase
Load “truth” case data via CaseData
Use truth data to auto-upgrade workflow statuses (sync_workflows_with_data)
If in litigation phases, load litigation data and validate that too
Potentially create a pending phase change suggestion (doesn’t auto-advance)
Compute SOL status
Compute completed/pending/blocking items
Compute next actions from workflow step definitions
Compute alerts
This is the core control flow:
state_machine.pyLines 1075-1176
def get_case_status(self, case_state: Dict[str, Any]) -> Dict[str, Any]:    current_phase = case_state.get("current_phase", "file_setup")    phase_state = case_state.get("phases", {}).get(current_phase, {})    # NEW: Load case data and sync workflows    corrections = []    case_data = self.load_case_data(case_state.get("case_id"))    if case_data:        corrections = self.sync_workflows_with_data(case_state, case_data)    # NEW: Check for litigation and validate if in litigation track    litigation_phases = ["complaint", "discovery", "mediation", "trial_prep", "trial"]    if current_phase in litigation_phases:        litigation_data = self.load_litigation_data(case_state.get("case_id"))        if litigation_data:            lit_corrections = self.validate_litigation_state(case_state, litigation_data)            corrections.extend(lit_corrections)    # NEW: Check for phase change suggestion    phase_suggestion = None    if case_data:        phase_suggestion = self.suggest_phase_change(case_state, case_data)        if phase_suggestion:            case_state["pending_phase_change"] = phase_suggestion    # NEW: Compute SOL status with litigation check    sol_status = None    if case_data:        litigation_data = None        if current_phase in ["complaint", "discovery", "mediation", "trial_prep", "trial"]:            litigation_data = self.load_litigation_data(case_state.get("case_id"))        sol_status = self.compute_sol_status(case_data, litigation_data)    completed = self._get_completed_items(case_state, current_phase)    pending = case_state.get("pending_items", [])    active_pending = [p for p in pending if not p.get("resolved_at")]    blocking = [p for p in active_pending if p.get("blocking")]    next_actions = self._determine_next_actions(case_state, current_phase)    alerts = self._check_alerts(case_state)    # (adds SOL alert and returns status dict)
3) Where “workflows come in”
Workflows are introduced in two stages:
Phase chooses which workflows are relevant: phase_definitions.json has "workflows": [...] per phase (e.g., file_setup includes intake, send_documents_for_signature, etc.).
Workflow defines what to do: workflow_definitions.json defines each workflow’s steps and metadata.
At runtime:
_determine_next_actions() looks at the current phase’s workflow list, then for each workflow:
checks dependencies (workflow_dependencies in workflow_definitions.json)
if not started → returns the first step as a NextAction
if in progress → returns the first incomplete step whose condition passes
This is exactly implemented here (also shows the very simple condition/requirement language it supports):
state_machine.pyLines 1204-1366
def _determine_next_actions(self, case_state: Dict, phase: str) -> List[NextAction]:    actions = []    phase_def = self.phase_defs["phases"].get(phase, {})    phase_state = case_state.get("phases", {}).get(phase, {})    phase_workflows = phase_def.get("workflows", [])    for wf_name in phase_workflows:        wf_state = phase_state.get("workflows", {}).get(wf_name, {})        wf_def = self.workflow_defs["workflows"].get(wf_name, {})        if not wf_def:            continue        wf_status = wf_state.get("status", "not_started")        if wf_status in ["complete", "skipped"]:            continue        if wf_status == "not_started":            if self._can_start_workflow(case_state, wf_name):                actions.append(self._get_first_action(wf_def, wf_name))            continue        steps = wf_def.get("steps", [])        steps_state = wf_state.get("steps", {})        for step in steps:            step_id = step.get("id")            step_state = steps_state.get(step_id, {})            step_status = step_state.get("status", "not_started")            if step_status == "complete":                continue            condition = step.get("condition")            if condition and not self._evaluate_condition(case_state, condition):                continue            actions.append(NextAction(                description=step.get("description", step.get("name")),                owner=step.get("owner", "agent"),                workflow=wf_name,                step=step_id,                blocking=True,                can_automate=step.get("can_automate", False),                prompt=step.get("prompt_user"),                tool_available=step.get("tool_available", False),                manual_fallback=step.get("manual_fallback")            ))            breakdef _can_start_workflow(self, case_state: Dict, workflow_name: str) -> bool:    deps = self.workflow_defs.get("workflow_dependencies", {}).get(workflow_name, {})    requires = deps.get("requires", [])    # supports " OR " and checks documents/workflow completion/field existence via _check_requirement()def _evaluate_condition(self, case_state: Dict, condition: str) -> bool:    # supports "==", " OR ", " AND ", else truthy existence check
Step-by-step: how phase advancement works
4) Phase exit criteria come from phase_definitions.json
Each phase includes an exit_criteria object with:
hard_blockers: must be satisfied to exit (e.g., documents.retainer.status == signed)
soft_blockers: trackable but overridable (the code doesn’t currently enforce override logic; it’s specified in JSON)
sometimes early_exit_conditions (again defined, but not fully executed by this file’s generic logic)
5) The state machine does not auto-advance phases
It creates a suggestion and requires explicit approval.
suggest_phase_change(case_state, case_data) checks:
all hard blockers satisfied (currently it checks only case_state fields, not case_data fields, despite comment)
all workflows in that phase are complete or skipped
then adds some phase-specific “data evidence” using case_data (e.g., providers completed / demand sent)
it returns a pending_phase_change dict that the UI/agent can show the user
approve_phase_change(... approve=True) calls _advance_phase(...) and records audit/history
Those mechanics are here:
state_machine.pyLines 702-864
def suggest_phase_change(self, case_state: Dict, case_data: 'CaseData') -> Optional[Dict]:    current_phase = case_state.get("current_phase")    phase_def = self.phase_defs["phases"].get(current_phase, {})    next_phase = phase_def.get("next_phase")    if not next_phase:        return None    exit_criteria = phase_def.get("exit_criteria", {})    hard_blockers = exit_criteria.get("hard_blockers", {})    # hard blockers checked against case_state field_path/required_value    # then checks all workflows in phase are complete/skipped    # then adds extra case_data evidence (providers complete, demand sent, etc.)    return {"from_phase": current_phase, "to_phase": next_phase, ...}def approve_phase_change(self, case_state: Dict, approve: bool = True, reason: Optional[str] = None) -> Dict:    pending_change = case_state.get("pending_phase_change")    if approve:        self._advance_phase(case_state, from_phase)        self._log_audit(...)        case_state["phase_change_history"].append(...)    else:        self._log_audit(...)        case_state["rejected_phase_changes"].append(...)    case_state.pop("pending_phase_change", None)    return case_state
Step-by-step: where “skills/resources/tools” come in
There are three different concepts in your JSONs:
6) “Skills/Tools/Templates” inside workflow_definitions.json (per-step metadata)
In workflow_definitions.json, steps can include fields like:
skill: a path like "Skills/docx/SKILL.md"
tool / tool_available: hints about automation
template: path into forms/...
In state_machine.py, these are not executed. The only fields that affect logic are mostly:
owner, can_automate, tool_available, manual_fallback, prompt_user, condition
because those drive NextAction objects and messaging.
So: skills are “recommended context” for the agent, not something the state machine loads.
7) “Derivation rules” inside derivation_rules.json (data-driven validation + SOL)
This file contains a lot:
workflow_derivations: mapping each workflow to “complete when X exists in data”
blocker_detection, next_action_derivation: richer, more declarative rule engines
sol_tracking: SOL types + thresholds
In this code, only two pieces are actively used:
workflow_derivations → used by validate_workflow_against_data() / sync_workflows_with_data() to upgrade workflow statuses when the case data proves completion.
sol_tracking → used by compute_sol_status() to calculate urgency thresholds.
The blocker_detection and next_action_derivation sections are currently not referenced in state_machine.py (they’re “planned / future” or used by a different component).
8) resource_mappings.json (global inventory + mapping)
This JSON is a catalog + mapping layer:
skills: skill IDs → Skills/... paths + coverage (phases/workflows) + quality
tools: tool groups → Tools/... paths + capabilities
workflows: which markdown workflow folders map to which phases
phase_to_resource_mapping: “if we’re in phase X, likely load these skills/tools and look in this workflow_dir”
workflow_to_tool_mapping: “for workflow X, these tool calls/skills are relevant; these are missing tools”
gap_analysis_summary: coverage + known gaps
Critical detail: I confirmed there are no references to resource_mappings.json anywhere in workflow_engine/orchestrator/ right now. So this file is not part of the state machine’s runtime decision-making yet—it’s an integration map for the agent layer / future orchestration.
What each schema file “is” in one line
case_state.schema.json: the formal shape of case_state (phases/workflows/pending_items/documents/etc.) and allowed enums.
phase_definitions.json: the phase graph (order + next_phase), per-phase workflow membership, and exit criteria definitions.
workflow_definitions.json: the workflow library (steps, dependencies, prompts, tool availability, and resource hints).
derivation_rules.json: rulebook for inferring progress from underlying case data + SOL configuration (partially implemented here).
resource_mappings.json: the “Roscoe knowledge index” tying phases/workflows to Skills/Tools/workflow folders (not executed by state_machine.py currently).
Two important “gotchas” you should be aware of
resource_mappings.json uses lien as a phase key, but phase_definitions.json uses lien_phase as the phase id. That mismatch will matter if/when you wire resource loading off phase IDs.
The condition/requirement evaluation in state_machine.py is intentionally simple (string parsing, basic AND/OR/==), so complex expressions in JSON won’t behave like a real expression language unless you extend _evaluate_condition() / _check_requirement().
If you want, I can also draw the “data flow diagram” (CaseData → sync_workflows_with_data → suggest_phase_change → determine_next_actions) and separately the “resource flow” (phase/workflow → resource_mappings → skill load), including exactly what’s currently wired vs planned.