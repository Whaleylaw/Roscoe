from __future__ import annotations

import json
import re
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ParsedStep:
    number: int
    title: str
    description: str
    owner: str
    tool_available: bool
    can_automate: bool
    manual_fallback: str


_STEP_HEADING_RE = re.compile(r"^###\s+(?:Step\s+)?(?P<num>\d+)\s*[:\.]\s*(?P<title>.+?)\s*$")
_H2_RE = re.compile(r"^##\s+(.+?)\s*$")


def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "step"


def _parse_frontmatter(md: str) -> Dict[str, Any]:
    # Minimal YAML-ish parser to avoid hard dependency on PyYAML.
    # Handles scalars, [] list, and simple dash-lists.
    lines = md.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    fm_lines: List[str] = []
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm_lines = lines[1:i]
            break
    if not fm_lines:
        return {}

    out: Dict[str, Any] = {}
    key: Optional[str] = None
    list_mode = False
    for raw in fm_lines:
        line = raw.rstrip("\n")
        if not line.strip():
            continue

        if re.match(r"^\s*-\s+", line) and key and list_mode:
            out.setdefault(key, [])
            out[key].append(re.sub(r"^\s*-\s+", "", line).strip())
            continue

        m = re.match(r"^([A-Za-z0-9_\-]+)\s*:\s*(.*)$", line)
        if m:
            key = m.group(1)
            val = m.group(2).strip()
            list_mode = False
            if val == "":
                out[key] = []
                list_mode = True
            elif val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                out[key] = [] if not inner else [x.strip().strip('"\'') for x in inner.split(",")]
            else:
                out[key] = val.strip('"\'')
            continue

        # Allow multiline description with ">" (we just keep raw line content appended)
        if key and isinstance(out.get(key), str):
            out[key] = (out[key] + "\n" + line).strip()

    return out


def _extract_steps(markdown: str, sop_path: str) -> List[Dict[str, Any]]:
    lines = markdown.splitlines()

    # Find "## Steps"
    steps_start = None
    for i, line in enumerate(lines):
        if line.strip() == "## Steps":
            steps_start = i + 1
            break
    if steps_start is None:
        return []

    # Steps section ends at next H2
    steps_end = len(lines)
    for j in range(steps_start, len(lines)):
        if _H2_RE.match(lines[j]) and lines[j].strip() != "## Steps":
            steps_end = j
            break

    section = lines[steps_start:steps_end]

    # Collect step heading indices
    headings: List[Tuple[int, ParsedStep]] = []

    def parse_owner(block: List[str]) -> str:
        for l in block:
            m = re.search(r"\*\*Owner:\*\*\s*(.+?)\s*$", l)
            if m:
                return m.group(1).strip()
        return "agent"

    def parse_tool_available(block: List[str]) -> bool:
        for l in block:
            if re.search(r"\*\*Tool:\*\*", l):
                return True
        return False

    def parse_description(block: List[str], title: str) -> str:
        # Prefer **Action:**/**Actions:** line
        for l in block:
            m = re.search(r"\*\*Action[s]?:\*\*\s*(.+?)\s*$", l)
            if m and m.group(1).strip():
                return m.group(1).strip()
        # Else first non-empty, non-heading line
        for l in block:
            if l.strip().startswith("###"):
                continue
            if l.strip().startswith("**") and l.strip().endswith("**"):
                continue
            if l.strip():
                return l.strip()
        return title

    # Find headings in section
    for idx, line in enumerate(section):
        m = _STEP_HEADING_RE.match(line.strip())
        if not m:
            continue
        num = int(m.group("num"))
        title = m.group("title").strip()
        headings.append((idx, ParsedStep(
            number=num,
            title=title,
            description=title,
            owner="agent",
            tool_available=False,
            can_automate=False,
            manual_fallback=f"Open and follow {sop_path} (Steps → {title})",
        )))

    if not headings:
        return []

    # Build blocks
    steps: List[Dict[str, Any]] = []
    for h_i, (start_idx, step_stub) in enumerate(headings):
        end_idx = headings[h_i + 1][0] if h_i + 1 < len(headings) else len(section)
        block = section[start_idx:end_idx]

        owner = parse_owner(block)
        tool_avail = parse_tool_available(block)
        desc = parse_description(block, step_stub.title)

        step_id = f"step_{step_stub.number:02d}_{_slugify(step_stub.title)[:50]}"

        steps.append({
            "id": step_id,
            "name": step_stub.title,
            "description": desc,
            "owner": "user" if owner.lower().startswith("user") else "agent",
            "can_automate": bool(tool_avail),
            "tool_available": bool(tool_avail),
            "manual_fallback": step_stub.manual_fallback,
        })

    return steps


def main() -> None:
    # Runtime bundle root. In the VM you can set ROSCOE_ROOT explicitly.
    roscoe_root = Path(os.environ.get("ROSCOE_ROOT", Path(__file__).resolve().parents[2]))
    base = roscoe_root / "workflows"

    phase_dirs = {
        'phase_0_onboarding': base/'phase_0_onboarding'/'workflows',
        'phase_1_file_setup': base/'phase_1_file_setup'/'workflows',
        'phase_2_treatment': base/'phase_2_treatment'/'workflows',
        'phase_3_demand': base/'phase_3_demand'/'workflows',
        'phase_4_negotiation': base/'phase_4_negotiation'/'workflows',
        'phase_5_settlement': base/'phase_5_settlement'/'workflows',
        'phase_6_lien': base/'phase_6_lien'/'workflows',
    }

    subphase_map = {
        '7_1_complaint': 'phase_7_1_complaint',
        '7_2_discovery': 'phase_7_2_discovery',
        '7_3_mediation': 'phase_7_3_mediation',
        '7_4_trial_prep': 'phase_7_4_trial_prep',
        '7_5_trial': 'phase_7_5_trial',
    }

    workflows: Dict[str, Dict[str, Any]] = {}

    def add_workflow(wf_id: str, wf_def: Dict[str, Any]) -> None:
        if wf_id in workflows:
            raise RuntimeError(f"Duplicate workflow id: {wf_id}")
        workflows[wf_id] = wf_def

    def _rel(p: Path) -> str:
        try:
            return str(p.relative_to(roscoe_root))
        except Exception:
            return str(p)

    def build_workflow_def(wf_id: str, phase_id: str, sop_path: Path, subphase_id: Optional[str] = None) -> Dict[str, Any]:
        md = sop_path.read_text()
        fm = _parse_frontmatter(md)

        steps = _extract_steps(md, _rel(sop_path))
        if not steps:
            # fallback
            steps = [{
                'id': 'follow_sop',
                'name': 'Follow SOP',
                'description': f"Follow the procedure in {sop_path.name}",
                'owner': 'agent',
                'can_automate': False,
                'tool_available': False,
                'manual_fallback': f"Open and follow {_rel(sop_path)}"
            }]

        out: Dict[str, Any] = {
            'name': fm.get('name') or wf_id.replace('_', ' ').title(),
            'phase_id': phase_id,
            'description': (fm.get('description') or f"See SOP: {sop_path}").strip(),
            'sop_path': _rel(sop_path),
            'steps': steps,
            'related_skills': fm.get('related_skills') or [],
            'related_tools': fm.get('related_tools') or [],
            'templates': fm.get('templates') or [],
            'resources': {
                'tools_manifest': _rel(base/'tools'/'tools_manifest.json'),
                'skills_manifest': _rel(base/'skills'/'skills_manifest.json'),
                'templates_manifest': _rel(base/'templates'/'templates_manifest.json'),
            }
        }
        if subphase_id:
            out['subphase_id'] = subphase_id
        return out

    # Non-litigation
    for phase_id, wdir in phase_dirs.items():
        if not wdir.exists():
            continue
        for wf_dir in sorted([p for p in wdir.iterdir() if p.is_dir()]):
            workflow_md = wf_dir/'workflow.md'
            if not workflow_md.exists():
                continue
            wf_id = wf_dir.name
            add_workflow(wf_id, build_workflow_def(wf_id, phase_id, workflow_md))

    # Litigation
    lit_base = base/'phase_7_litigation'/'subphases'
    for folder, subphase_id in subphase_map.items():
        wdir = lit_base/folder/'workflows'
        if not wdir.exists():
            continue
        for wf_dir in sorted([p for p in wdir.iterdir() if p.is_dir()]):
            workflow_md = wf_dir/'workflow.md'
            if not workflow_md.exists():
                continue
            wf_id = wf_dir.name
            add_workflow(wf_id, build_workflow_def(wf_id, 'phase_7_litigation', workflow_md, subphase_id=subphase_id))

    # Closed legacy
    close_md = base/'phase_8_closed'/'workflows'/'close_case.md'
    if close_md.exists():
        add_workflow('close_case', build_workflow_def('close_case', 'phase_8_closed', close_md))

    out = {
        'workflows': workflows,
        'workflow_dependencies': {}
    }

    out_path = roscoe_root / "workflow_engine" / "schemas" / "workflow_definitions.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"Wrote {len(workflows)} workflow definitions with step-level steps -> {out_path}")


if __name__ == '__main__':
    main()
