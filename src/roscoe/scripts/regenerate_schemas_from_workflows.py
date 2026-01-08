#!/usr/bin/env python3
"""
Regenerate Workflow Schema Files from Workflows Folder

This script scans /mnt/workspace/workflows/ folder structure (Dec 15 - current reality)
and regenerates all schema files in /workflow_engine/schemas/.

Replaces stale Dec 8 schema files with fresh definitions derived from folder structure.

Usage:
    python regenerate_schemas_from_workflows.py
    python regenerate_schemas_from_workflows.py --dry-run
    python regenerate_schemas_from_workflows.py --workspace /path/to/workspace
"""

import os
import re
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import shutil

def parse_yaml_frontmatter(content: str) -> tuple:
    """Parse YAML frontmatter from markdown file."""
    if not content.startswith('---'):
        return {}, content

    try:
        end_match = re.search(r'\n---\s*\n', content[3:])
        if not end_match:
            return {}, content

        yaml_content = content[3:end_match.start() + 3]
        body = content[end_match.end() + 3:]

        frontmatter = yaml.safe_load(yaml_content)
        return frontmatter or {}, body
    except Exception as e:
        print(f"Warning: Error parsing YAML: {e}")
        return {}, content


def scan_phases(workflows_dir: Path) -> Dict:
    """
    Scan phase folders to build phase_definitions.json.

    Source: /workflows/phase_N_name/ folders

    Returns dict with:
    - phase_order: list of phase names in order
    - phases: dict of phase metadata
    """
    phase_folders = sorted([
        d for d in workflows_dir.iterdir()
        if d.is_dir() and d.name.startswith('phase_')
    ])

    phases = {}
    phase_order = []

    for phase_folder in phase_folders:
        match = re.match(r'phase_(\d+)_(\w+)', phase_folder.name)
        if not match:
            continue

        phase_num = int(match.group(1))
        phase_name = match.group(2)

        phases[phase_name] = {
            "name": phase_name.replace('_', ' ').title(),
            "description": f"{phase_name.title()} phase",
            "order": phase_num,
            "track": "pre_litigation" if phase_num < 7 else "litigation",
            "next_phase": None  # Will be set below
        }

        phase_order.append(phase_name)

    # Set next_phase relationships
    for i, phase_name in enumerate(phase_order[:-1]):
        phases[phase_name]["next_phase"] = phase_order[i + 1]

    return {
        "phase_order": phase_order,
        "phases": phases,
        "global_rules": {
            "description": "Phase progression rules",
            "generated_from": "workflows folder structure",
            "generated_at": datetime.now().isoformat()
        },
        "tracks": {
            "pre_litigation": {
                "phases": [p for p in phase_order if phases[p]["track"] == "pre_litigation"]
            },
            "litigation": {
                "phases": [p for p in phase_order if phases[p]["track"] == "litigation"]
            }
        }
    }


def scan_workflows(workflows_dir: Path) -> Dict:
    """
    Scan workflow.md files to build workflow_definitions.json.

    Source: /workflows/phase_*/workflows/*/workflow.md files

    Returns dict with:
    - workflows: dict of workflow metadata and steps
    """
    workflows = {}

    for phase_folder in sorted(workflows_dir.iterdir()):
        if not phase_folder.is_dir() or not phase_folder.name.startswith('phase_'):
            continue

        match = re.match(r'phase_\d+_(\w+)', phase_folder.name)
        if not match:
            continue
        phase_name = match.group(1)

        workflows_subdir = phase_folder / 'workflows'
        if not workflows_subdir.exists():
            continue

        for wf_folder in workflows_subdir.iterdir():
            if not wf_folder.is_dir():
                continue

            wf_md = wf_folder / 'workflow.md'
            if not wf_md.exists():
                continue

            content = wf_md.read_text(encoding='utf-8')
            frontmatter, body = parse_yaml_frontmatter(content)

            if not frontmatter:
                continue

            wf_name = frontmatter.get('name', wf_folder.name)

            workflows[wf_name] = {
                "name": frontmatter.get('description', wf_name).split('\n')[0][:100],
                "phase": phase_name,
                "description": frontmatter.get('description', ''),
                "workflow_id": frontmatter.get('workflow_id', wf_name),
                "related_skills": frontmatter.get('related_skills', []),
                "related_tools": frontmatter.get('related_tools', []),
                "templates": frontmatter.get('templates', []),
                "steps": []  # Could parse from body if needed
            }

    return {
        "workflows": workflows,
        "workflow_dependencies": {},
        "version": "2.0",
        "generated_from": "workflows folder",
        "generated_at": datetime.now().isoformat()
    }


def scan_skills(workflows_dir: Path) -> Dict:
    """
    Scan skills to build resource_mappings.json skills section.

    Source: /workflows/phase_*/skills/*/SKILL.md files

    Returns dict with skills mapped to phases
    """
    skills = {}

    for phase_folder in sorted(workflows_dir.iterdir()):
        if not phase_folder.is_dir() or not phase_folder.name.startswith('phase_'):
            continue

        match = re.match(r'phase_\d+_(\w+)', phase_folder.name)
        if not match:
            continue
        phase_name = match.group(1)

        # Scan skills in this phase
        for item in phase_folder.iterdir():
            if not item.is_dir():
                continue

            # Check if it's a skill folder
            skill_md = item / 'SKILL.md' if (item / 'SKILL.md').exists() else item / 'skill.md'
            if not skill_md.exists():
                continue

            content = skill_md.read_text(encoding='utf-8')
            frontmatter, _ = parse_yaml_frontmatter(content)

            if frontmatter:
                skill_name = frontmatter.get('name', item.name)

                if skill_name not in skills:
                    skills[skill_name] = {
                        "path": f"Skills/{item.name}/SKILL.md",
                        "phases": [],
                        "workflows": ["*"],
                        "capabilities": [frontmatter.get('description', '')],
                        "quality_score": 5,
                        "agent_ready": True
                    }

                if phase_name not in skills[skill_name]["phases"]:
                    skills[skill_name]["phases"].append(phase_name)

    return {
        "skills": skills,
        "tools": {},  # Generated from Tools folder separately
        "workflows": {},
        "phase_to_resource_mapping": {},
        "workflow_to_tool_mapping": {},
        "version": "2.0",
        "generated_from": "workflows folder",
        "generated_at": datetime.now().isoformat(),
        "description": "Resource mappings generated from workflows folder structure"
    }


def generate_derivation_rules(phases: Dict, workflows: Dict) -> Dict:
    """
    Generate derivation_rules.json based on phases and workflows.

    Returns basic phase transition rules.
    """
    return {
        "phase_derivation": {
            "description": "Phase automatically derived from case state",
            "rules": []  # Simple sequential progression
        },
        "workflow_derivations": {},
        "blocker_detection": {
            "description": "Hard blockers prevent phase advancement"
        },
        "next_action_derivation": {
            "description": "Suggested next actions based on phase and incomplete landmarks"
        },
        "sol_tracking": {
            "mva": 2,
            "premise": 1,
            "wc": 2,
            "dog_bite": 1
        },
        "version": "2.0",
        "generated_from": "workflows folder",
        "generated_at": datetime.now().isoformat(),
        "description": "Derivation rules for phase transitions and next actions"
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Regenerate schema files from workflows folder')
    parser.add_argument('--workspace', type=str, default='/mnt/workspace', help='Workspace directory')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be generated without writing files')
    args = parser.parse_args()

    workspace = Path(args.workspace)
    workflows_dir = workspace / 'workflows'
    schemas_dir = workspace / 'workflow_engine' / 'schemas'

    if not workflows_dir.exists():
        print(f"❌ Workflows directory not found: {workflows_dir}")
        return

    print("=" * 70)
    print("REGENERATING WORKFLOW SCHEMA FILES FROM WORKFLOWS FOLDER")
    print("=" * 70)
    print(f"Source: {workflows_dir}")
    print(f"Target: {schemas_dir}")
    print(f"Dry run: {args.dry_run}")
    print()

    # Backup existing files
    if not args.dry_run and schemas_dir.exists():
        backup_dir = schemas_dir / f"backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        backup_dir.mkdir(exist_ok=True)
        print(f"📦 Backing up existing schemas to {backup_dir.name}/")
        for schema_file in schemas_dir.glob('*.json'):
            if 'backup' not in schema_file.name:
                shutil.copy(schema_file, backup_dir / schema_file.name)
        print()

    # Generate schemas
    print("🔍 Scanning workflows folder...\n")

    phase_defs = scan_phases(workflows_dir)
    print(f"✅ Scanned {len(phase_defs['phases'])} phases")

    workflow_defs = scan_workflows(workflows_dir)
    print(f"✅ Scanned {len(workflow_defs['workflows'])} workflows")

    resource_mappings = scan_skills(workflows_dir)
    print(f"✅ Scanned {len(resource_mappings['skills'])} skills")

    derivation_rules = generate_derivation_rules(phase_defs['phases'], workflow_defs['workflows'])
    print(f"✅ Generated derivation rules")

    print()

    # Write files
    if args.dry_run:
        print("[DRY RUN] Would write:")
        print(f"  - phase_definitions.json ({len(json.dumps(phase_defs))} bytes)")
        print(f"  - workflow_definitions.json ({len(json.dumps(workflow_defs))} bytes)")
        print(f"  - resource_mappings.json ({len(json.dumps(resource_mappings))} bytes)")
        print(f"  - derivation_rules.json ({len(json.dumps(derivation_rules))} bytes)")
    else:
        schemas_dir.mkdir(parents=True, exist_ok=True)

        with open(schemas_dir / 'phase_definitions.json', 'w') as f:
            json.dump(phase_defs, f, indent=2)
        print("✅ Wrote phase_definitions.json")

        with open(schemas_dir / 'workflow_definitions.json', 'w') as f:
            json.dump(workflow_defs, f, indent=2)
        print("✅ Wrote workflow_definitions.json")

        with open(schemas_dir / 'resource_mappings.json', 'w') as f:
            json.dump(resource_mappings, f, indent=2)
        print("✅ Wrote resource_mappings.json")

        with open(schemas_dir / 'derivation_rules.json', 'w') as f:
            json.dump(derivation_rules, f, indent=2)
        print("✅ Wrote derivation_rules.json")

        print()
        print("=" * 70)
        print("✅ SCHEMA REGENERATION COMPLETE")
        print("=" * 70)
        print(f"Next steps:")
        print(f"  1. Run: python /deps/roscoe/src/roscoe/scripts/ingest_workflow_definitions.py --clear-first")
        print(f"  2. Run: python /deps/roscoe/src/roscoe/scripts/initialize_case_states.py")
        print(f"  3. Test: get_case_workflow_status(case_name)")


if __name__ == "__main__":
    main()
