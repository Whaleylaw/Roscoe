#!/usr/bin/env python3
"""
Ingest Workflow Definitions into Graphiti Knowledge Graph

This script loads workflow structure from two sources:
1. /mnt/workspace/workflow_engine/ - Structural definitions (JSON schemas)
2. /mnt/workspace/workflows/ - Operational implementation (workflow.md, landmarks.md)

Unlike case data migration (which uses Graphiti episodes for LLM extraction),
this script uses direct Cypher queries to create nodes and relationships
since workflow definitions are structured metadata, not natural language.

Usage:
    python -m roscoe.scripts.ingest_workflow_definitions
    python -m roscoe.scripts.ingest_workflow_definitions --dry-run
    python -m roscoe.scripts.ingest_workflow_definitions --clear-first
"""

import os
import re
import json
import yaml
import asyncio
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Group ID for workflow definitions (distinguishes from case data)
WORKFLOW_GROUP_ID = "__workflow_definitions__"


def load_json_file(path: Path) -> Dict:
    """Load a JSON file, returning empty dict if not found."""
    if not path.exists():
        logger.warning(f"JSON file not found: {path}")
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {path}: {e}")
        return {}


def parse_yaml_frontmatter(content: str) -> tuple[Dict, str]:
    """Parse YAML frontmatter from markdown file."""
    if not content.startswith('---'):
        return {}, content
    
    try:
        # Find end of frontmatter
        end_match = re.search(r'\n---\s*\n', content[3:])
        if not end_match:
            return {}, content
        
        yaml_content = content[3:end_match.start() + 3]
        body = content[end_match.end() + 3:]
        
        frontmatter = yaml.safe_load(yaml_content)
        return frontmatter or {}, body
    except Exception as e:
        logger.warning(f"Error parsing YAML frontmatter: {e}")
        return {}, content


def parse_landmarks_md(content: str) -> List[Dict]:
    """
    Parse landmarks.md file to extract landmark definitions.

    Looks for patterns like:
    ### L3.1: All Records Received
    or
    ## Landmark 1: Full Intake Complete
    """
    landmarks = []

    # Try new format first: ### L3.1: Name
    landmark_pattern = r'###\s+L\d+\.\d+:\s*([^\n]+)\n(.*?)(?=###\s+L\d+\.\d+:|## |$)'
    matches = re.findall(landmark_pattern, content, re.DOTALL)

    # Fallback to old format: ## Landmark 1: Name
    if not matches:
        landmark_pattern = r'## Landmark \d+: ([^\n]+)\n(.*?)(?=## Landmark \d+:|## Landmark Verification|## Phase Advancement|$)'
        matches = re.findall(landmark_pattern, content, re.DOTALL)
    
    for i, (name, section) in enumerate(matches, 1):
        landmark_id = name.lower().replace(' ', '_').replace('-', '_')
        
        # Extract description
        desc_match = re.search(r'\*\*Description:\*\*\s*([^\n]+)', section)
        description = desc_match.group(1).strip() if desc_match else None
        
        # Check if mandatory (hard blocker)
        mandatory = 'hard blocker' in section.lower()
        
        # Extract verification fields (look for JSON code blocks)
        fields_match = re.search(r'```json\s*(\{[^`]+\})\s*```', section, re.DOTALL)
        verification_fields = None
        if fields_match:
            try:
                verification_fields = json.dumps(json.loads(fields_match.group(1)))
            except:
                pass
        
        # Check for sub-landmarks (e.g., BI Sub-Landmarks, PIP Sub-Landmarks)
        sub_landmarks = []
        sub_pattern = r'### ([A-Z]+) .*?Sub-Landmarks?\s*\n(.*?)(?=###|## |$)'
        sub_matches = re.findall(sub_pattern, section, re.DOTALL)
        for sub_type, sub_section in sub_matches:
            # Parse table rows for sub-landmarks
            row_pattern = r'\| (\d+\w?) \| ([^|]+) \|'
            for row_match in re.finditer(row_pattern, sub_section):
                step_num, sub_name = row_match.groups()
                sub_id = f"{landmark_id}_{sub_type.lower()}_{step_num.lower()}"
                sub_landmarks.append({
                    'id': sub_id,
                    'name': sub_name.strip(),
                    'parent': landmark_id,
                })
        
        landmarks.append({
            'id': landmark_id,
            'name': name.strip(),
            'description': description,
            'mandatory': mandatory,
            'verification_fields': verification_fields,
            'order': i,
            'sub_landmarks': sub_landmarks,
        })
    
    return landmarks


def execute_cypher(graph, query: str, params: Dict = None):
    """Execute a Cypher query on the FalkorDB graph."""
    params = params or {}
    return graph.query(query, params)


async def clear_workflow_definitions(graph):
    """Clear existing workflow definition nodes from the graph."""
    logger.info("Clearing existing workflow definitions...")
    
    # Delete nodes with group_id = __workflow_definitions__
    query = """
        MATCH (n:Entity)
        WHERE n.group_id = $group_id
        DETACH DELETE n
    """
    execute_cypher(graph, query, {"group_id": WORKFLOW_GROUP_ID})
    logger.info("Cleared existing workflow definitions")


async def create_phase_nodes(graph, phase_definitions: Dict, dry_run: bool = False):
    """Create Phase nodes from phase_definitions.json."""
    phases = phase_definitions.get('phases', {})
    phase_order = phase_definitions.get('phase_order', [])
    
    logger.info(f"Creating {len(phases)} Phase nodes...")
    
    for i, phase_id in enumerate(phase_order, 1):
        phase_data = phases.get(phase_id, {})
        
        node_props = {
            'name': phase_id,
            'display_name': phase_data.get('name', phase_id),
            'description': phase_data.get('description', ''),
            'order': phase_data.get('order', i),
            'track': phase_data.get('track', 'pre_litigation'),
            'next_phase': phase_data.get('next_phase'),
            'entity_type': 'Phase',
            'group_id': WORKFLOW_GROUP_ID,
            'uuid': f"phase_{phase_id}",
        }
        
        if dry_run:
            logger.info(f"  [DRY RUN] Would create Phase: {phase_id}")
        else:
            query = """
                MERGE (p:Entity {uuid: $uuid})
                SET p += $props
            """
            execute_cypher(graph, query, {"uuid": node_props['uuid'], "props": node_props})
            logger.info(f"  Created Phase: {phase_id}")
    
    # Create NEXT_PHASE relationships
    if not dry_run:
        for phase_id, phase_data in phases.items():
            next_phase = phase_data.get('next_phase')
            if next_phase:
                query = """
                    MATCH (p1:Entity {uuid: $from_uuid})
                    MATCH (p2:Entity {uuid: $to_uuid})
                    MERGE (p1)-[:NEXT_PHASE]->(p2)
                """
                execute_cypher(graph, query, {
                    "from_uuid": f"phase_{phase_id}",
                    "to_uuid": f"phase_{next_phase}"
                })
            
            # Create CAN_SKIP_TO relationships
            for skip_to in phase_data.get('can_skip_to', []):
                query = """
                    MATCH (p1:Entity {uuid: $from_uuid})
                    MATCH (p2:Entity {uuid: $to_uuid})
                    MERGE (p1)-[:CAN_SKIP_TO]->(p2)
                """
                execute_cypher(graph, query, {
                    "from_uuid": f"phase_{phase_id}",
                    "to_uuid": f"phase_{skip_to}"
                })


async def create_workflow_nodes(graph, workflow_definitions: Dict, phase_definitions: Dict, dry_run: bool = False):
    """Create WorkflowDef and WorkflowStep nodes from workflow_definitions.json."""
    workflows = workflow_definitions.get('workflows', {})
    
    logger.info(f"Creating {len(workflows)} Workflow nodes...")
    
    for wf_name, wf_data in workflows.items():
        phase = wf_data.get('phase', 'file_setup')
        
        node_props = {
            'name': wf_name,
            'display_name': wf_data.get('name', wf_name),
            'phase': phase,
            'description': wf_data.get('description', ''),
            'entity_type': 'WorkflowDef',
            'group_id': WORKFLOW_GROUP_ID,
            'uuid': f"workflow_{wf_name}",
        }
        
        if dry_run:
            logger.info(f"  [DRY RUN] Would create Workflow: {wf_name}")
        else:
            query = """
                MERGE (w:Entity {uuid: $uuid})
                SET w += $props
            """
            execute_cypher(graph, query, {"uuid": node_props['uuid'], "props": node_props})
            
            # Link to phase
            query = """
                MATCH (w:Entity {uuid: $wf_uuid})
                MATCH (p:Entity {uuid: $phase_uuid})
                MERGE (p)-[:HAS_WORKFLOW]->(w)
            """
            execute_cypher(graph, query, {
                "wf_uuid": f"workflow_{wf_name}",
                "phase_uuid": f"phase_{phase}"
            })
            
            logger.info(f"  Created Workflow: {wf_name} (phase: {phase})")
        
        # Create steps
        steps = wf_data.get('steps', [])
        for i, step in enumerate(steps, 1):
            step_id = step.get('id', f"step_{i}")
            
            step_props = {
                'step_id': step_id,
                'name': step.get('name', step_id),
                'workflow': wf_name,
                'description': step.get('description', ''),
                'owner': step.get('owner', 'agent'),
                'can_automate': step.get('can_automate', False),
                'prompt_user': step.get('prompt_user'),
                'completion_check': step.get('completion_check'),
                'order': i,
                'entity_type': 'WorkflowStep',
                'group_id': WORKFLOW_GROUP_ID,
                'uuid': f"step_{wf_name}_{step_id}",
            }
            
            if dry_run:
                logger.info(f"    [DRY RUN] Would create Step: {step_id}")
            else:
                query = """
                    MERGE (s:Entity {uuid: $uuid})
                    SET s += $props
                """
                execute_cypher(graph, query, {"uuid": step_props['uuid'], "props": step_props})
                
                # Link step to workflow
                query = """
                    MATCH (s:Entity {uuid: $step_uuid})
                    MATCH (w:Entity {uuid: $wf_uuid})
                    MERGE (w)-[:HAS_STEP {order: $order}]->(s)
                """
                execute_cypher(graph, query, {
                    "step_uuid": f"step_{wf_name}_{step_id}",
                    "wf_uuid": f"workflow_{wf_name}",
                    "order": i
                })


async def create_checklist_nodes(graph, checklists_dir: Path, dry_run: bool = False):
    """Create WorkflowChecklist nodes from checklists/*.md files."""
    if not checklists_dir.exists():
        logger.warning(f"Checklists directory not found: {checklists_dir}")
        return
    
    checklist_files = list(checklists_dir.glob("*.md"))
    logger.info(f"Creating {len(checklist_files)} Checklist nodes...")
    
    for md_file in checklist_files:
        name = md_file.stem
        
        # Read file to extract when_to_use
        content = md_file.read_text(encoding='utf-8')
        
        # Look for "When to Use" section
        when_match = re.search(r'## When to Use\s*\n(.*?)(?=\n##|\n---|\Z)', content, re.DOTALL)
        when_to_use = when_match.group(1).strip() if when_match else None
        
        node_props = {
            'name': name,
            'path': f"/workflow_engine/checklists/{md_file.name}",
            'when_to_use': when_to_use,
            'entity_type': 'WorkflowChecklist',
            'group_id': WORKFLOW_GROUP_ID,
            'uuid': f"checklist_{name}",
        }
        
        if dry_run:
            logger.info(f"  [DRY RUN] Would create Checklist: {name}")
        else:
            query = """
                MERGE (c:Entity {uuid: $uuid})
                SET c += $props
            """
            execute_cypher(graph, query, {"uuid": node_props['uuid'], "props": node_props})
            logger.info(f"  Created Checklist: {name}")


async def create_skill_nodes(graph, resource_mappings: Dict, dry_run: bool = False):
    """Create WorkflowSkill nodes from resource_mappings.json."""
    skills = resource_mappings.get('skills', {})
    
    logger.info(f"Creating {len(skills)} Skill nodes from resource_mappings...")
    
    for skill_name, skill_data in skills.items():
        node_props = {
            'name': skill_name,
            'path': skill_data.get('path', ''),
            'description': ', '.join(skill_data.get('capabilities', [])),
            'capabilities': json.dumps(skill_data.get('capabilities', [])),
            'agent_ready': skill_data.get('agent_ready', False),
            'quality_score': skill_data.get('quality_score', 0),
            'entity_type': 'WorkflowSkill',
            'group_id': WORKFLOW_GROUP_ID,
            'uuid': f"skill_{skill_name}",
        }
        
        if dry_run:
            logger.info(f"  [DRY RUN] Would create Skill: {skill_name}")
        else:
            query = """
                MERGE (s:Entity {uuid: $uuid})
                SET s += $props
            """
            execute_cypher(graph, query, {"uuid": node_props['uuid'], "props": node_props})
            
            # Link skill to phases
            for phase in skill_data.get('phases', []):
                query = """
                    MATCH (s:Entity {uuid: $skill_uuid})
                    MATCH (p:Entity {uuid: $phase_uuid})
                    MERGE (s)-[:APPLIES_TO_PHASE]->(p)
                """
                execute_cypher(graph, query, {
                    "skill_uuid": f"skill_{skill_name}",
                    "phase_uuid": f"phase_{phase}"
                })
            
            # Link skill to workflows
            for wf_name in skill_data.get('workflows', []):
                if wf_name != '*':
                    query = """
                        MATCH (s:Entity {uuid: $skill_uuid})
                        MATCH (w:Entity {uuid: $wf_uuid})
                        MERGE (w)-[:USES_SKILL]->(s)
                    """
                    execute_cypher(graph, query, {
                        "skill_uuid": f"skill_{skill_name}",
                        "wf_uuid": f"workflow_{wf_name}"
                    })
            
            logger.info(f"  Created Skill: {skill_name}")


async def process_subphases(graph, phase_folder: Path, phase_name: str, dry_run: bool = False):
    """
    Process litigation sub-phases from phase_7_litigation/subphases/ folder.

    Creates SubPhase nodes, parses their landmarks, and their workflows.
    """
    subphases_dir = phase_folder / 'subphases'
    if not subphases_dir.exists():
        return

    logger.info(f"  Processing litigation sub-phases from {subphases_dir.name}/...")

    for subphase_folder in sorted(subphases_dir.iterdir()):
        if not subphase_folder.is_dir():
            continue

        # Parse folder name: 7_1_complaint → (1, 'complaint')
        match = re.match(r'7_(\d+)_(\w+)', subphase_folder.name)
        if not match:
            logger.warning(f"    Skipping folder with unexpected name: {subphase_folder.name}")
            continue

        order = int(match.group(1))
        subphase_name = match.group(2)

        logger.info(f"    SubPhase {order}: {subphase_name}")

        # Create SubPhase node
        subphase_props = {
            'name': subphase_name,
            'display_name': subphase_name.replace('_', ' ').title(),
            'parent_phase': phase_name,
            'order': order,
            'entity_type': 'SubPhase',
            'group_id': WORKFLOW_GROUP_ID,
            'uuid': f'subphase_{phase_name}_{subphase_name}'
        }

        if not dry_run:
            query = "MERGE (sp:Entity {uuid: $uuid}) SET sp += $props"
            execute_cypher(graph, query, {"uuid": subphase_props['uuid'], "props": subphase_props})

            # Link to parent Phase
            query = """
            MATCH (sp:Entity {uuid: $sp_uuid})
            MATCH (p:Entity {uuid: $phase_uuid})
            MERGE (p)-[:HAS_SUBPHASE {order: $order}]->(sp)
            """
            execute_cypher(graph, query, {
                "sp_uuid": subphase_props['uuid'],
                "phase_uuid": f'phase_{phase_name}',
                "order": order
            })

            logger.info(f"      Created SubPhase: {subphase_name}")

        # Parse landmarks.md for this subphase
        landmarks_file = subphase_folder / 'landmarks.md'
        if landmarks_file.exists():
            content = landmarks_file.read_text(encoding='utf-8')
            landmarks = parse_landmarks_md(content)

            for landmark in landmarks:
                node_props = {
                    'landmark_id': landmark['id'],
                    'name': landmark['name'],
                    'phase': phase_name,
                    'subphase': subphase_name,
                    'description': landmark.get('description'),
                    'is_hard_blocker': landmark.get('mandatory', False),
                    'order': landmark.get('order', 0),
                    'entity_type': 'Landmark',
                    'group_id': WORKFLOW_GROUP_ID,
                    'uuid': f"landmark_{phase_name}_{subphase_name}_{landmark['id']}",
                }

                if not dry_run:
                    query = "MERGE (l:Entity {uuid: $uuid}) SET l += $props"
                    execute_cypher(graph, query, {"uuid": node_props['uuid'], "props": node_props})

                    # Link to SubPhase
                    query = """
                    MATCH (l:Entity {uuid: $lm_uuid})
                    MATCH (sp:Entity {uuid: $sp_uuid})
                    MERGE (sp)-[:HAS_LANDMARK {order: $order}]->(l)
                    """
                    execute_cypher(graph, query, {
                        "lm_uuid": node_props['uuid'],
                        "sp_uuid": subphase_props['uuid'],
                        "order": landmark.get('order', 0)
                    })

                    logger.info(f"        Created SubPhase Landmark: {landmark['id']}")

        # Parse workflows in this subphase
        workflows_subdir = subphase_folder / 'workflows'
        if workflows_subdir.exists():
            for wf_folder in workflows_subdir.iterdir():
                if not wf_folder.is_dir():
                    continue

                wf_md = wf_folder / 'workflow.md'
                if wf_md.exists():
                    content = wf_md.read_text(encoding='utf-8')
                    frontmatter, _ = parse_yaml_frontmatter(content)

                    if frontmatter:
                        wf_name = frontmatter.get('name', wf_folder.name)

                        wf_props = {
                            'name': wf_name,
                            'display_name': frontmatter.get('display_name', wf_name.replace('_', ' ').title()),
                            'phase': phase_name,
                            'subphase': subphase_name,
                            'description': frontmatter.get('description', ''),
                            'trigger': frontmatter.get('trigger'),
                            'prerequisites': frontmatter.get('prerequisites'),
                            'instructions_path': f"/workflows/{phase_folder.name}/subphases/{subphase_folder.name}/workflows/{wf_folder.name}/workflow.md",
                            'entity_type': 'WorkflowDef',
                            'group_id': WORKFLOW_GROUP_ID,
                            'uuid': f'workflow_{wf_name}'
                        }

                        if not dry_run:
                            query = "MERGE (w:Entity {uuid: $uuid}) SET w += $props"
                            execute_cypher(graph, query, {"uuid": wf_props['uuid'], "props": wf_props})

                            # Link to SubPhase
                            query = """
                            MATCH (w:Entity {uuid: $wf_uuid})
                            MATCH (sp:Entity {uuid: $sp_uuid})
                            MERGE (sp)-[:HAS_WORKFLOW]->(w)
                            """
                            execute_cypher(graph, query, {
                                "wf_uuid": wf_props['uuid'],
                                "sp_uuid": subphase_props['uuid']
                            })

                            logger.info(f"        Created SubPhase Workflow: {wf_name}")


async def ingest_workflows_folder(graph, workflows_dir: Path, dry_run: bool = False):
    """
    Ingest workflow definitions from the /workflows/ folder structure.

    Parses:
    - phase_*/landmarks.md - Landmark nodes
    - phase_*/workflows/*/workflow.md - Workflow metadata from YAML frontmatter
    - phase_7_litigation/subphases/ - SubPhase nodes, landmarks, workflows
    - Embedded skills, templates, tools
    """
    if not workflows_dir.exists():
        logger.warning(f"Workflows directory not found: {workflows_dir}")
        return

    # Process each phase folder
    phase_folders = sorted([d for d in workflows_dir.iterdir() if d.is_dir() and d.name.startswith('phase_')])

    for phase_folder in phase_folders:
        # Extract phase number and name
        match = re.match(r'phase_(\d+)_(\w+)', phase_folder.name)
        if not match:
            continue
        
        phase_num = int(match.group(1))
        phase_name = match.group(2)
        
        logger.info(f"Processing {phase_folder.name}...")
        
        # Parse landmarks.md
        landmarks_file = phase_folder / 'landmarks.md'
        if landmarks_file.exists():
            content = landmarks_file.read_text(encoding='utf-8')
            landmarks = parse_landmarks_md(content)
            
            for landmark in landmarks:
                node_props = {
                    'landmark_id': landmark['id'],
                    'name': landmark['name'],
                    'phase': phase_name,
                    'description': landmark.get('description'),
                    'mandatory': landmark.get('mandatory', False),
                    'verification_fields': landmark.get('verification_fields'),
                    'order': landmark.get('order', 0),
                    'entity_type': 'Landmark',
                    'group_id': WORKFLOW_GROUP_ID,
                    'uuid': f"landmark_{phase_name}_{landmark['id']}",
                }
                
                if dry_run:
                    logger.info(f"  [DRY RUN] Would create Landmark: {landmark['id']}")
                else:
                    query = """
                        MERGE (l:Entity {uuid: $uuid})
                        SET l += $props
                    """
                    execute_cypher(graph, query, {"uuid": node_props['uuid'], "props": node_props})
                    
                    # Link to phase
                    query = """
                        MATCH (l:Entity {uuid: $lm_uuid})
                        MATCH (p:Entity {uuid: $phase_uuid})
                        MERGE (p)-[:HAS_LANDMARK {order: $order}]->(l)
                    """
                    execute_cypher(graph, query, {
                        "lm_uuid": node_props['uuid'],
                        "phase_uuid": f"phase_{phase_name}",
                        "order": landmark.get('order', 0)
                    })
                    
                    logger.info(f"  Created Landmark: {landmark['id']}")
                
                # Create sub-landmarks
                for sub in landmark.get('sub_landmarks', []):
                    sub_props = {
                        'landmark_id': sub['id'],
                        'name': sub['name'],
                        'phase': phase_name,
                        'parent_landmark': landmark['id'],
                        'entity_type': 'Landmark',
                        'group_id': WORKFLOW_GROUP_ID,
                        'uuid': f"landmark_{phase_name}_{sub['id']}",
                    }
                    
                    if not dry_run:
                        query = """
                            MERGE (l:Entity {uuid: $uuid})
                            SET l += $props
                        """
                        execute_cypher(graph, query, {"uuid": sub_props['uuid'], "props": sub_props})
                        
                        # Link to parent landmark
                        query = """
                            MATCH (child:Entity {uuid: $child_uuid})
                            MATCH (parent:Entity {uuid: $parent_uuid})
                            MERGE (parent)-[:HAS_SUB_LANDMARK]->(child)
                        """
                        execute_cypher(graph, query, {
                            "child_uuid": sub_props['uuid'],
                            "parent_uuid": f"landmark_{phase_name}_{landmark['id']}"
                        })
                        
                        logger.info(f"    Created Sub-Landmark: {sub['id']}")

        # Process sub-phases (for litigation only)
        if phase_name == 'litigation':
            await process_subphases(graph, phase_folder, phase_name, dry_run)

        # Process workflow folders
        workflows_subdir = phase_folder / 'workflows'
        if workflows_subdir.exists():
            for wf_folder in workflows_subdir.iterdir():
                if not wf_folder.is_dir():
                    continue
                
                wf_md = wf_folder / 'workflow.md'
                if wf_md.exists():
                    content = wf_md.read_text(encoding='utf-8')
                    frontmatter, body = parse_yaml_frontmatter(content)
                    
                    if frontmatter:
                        wf_name = frontmatter.get('name', wf_folder.name)
                        
                        # Update or create workflow with additional metadata
                        update_props = {
                            'instructions_path': f"/workflows/{phase_folder.name}/workflows/{wf_folder.name}/workflow.md",
                            'trigger': frontmatter.get('trigger'),
                            'prerequisites': frontmatter.get('prerequisites'),
                        }
                        
                        if not dry_run:
                            # Try to update existing workflow first
                            query = """
                                MATCH (w:Entity {uuid: $uuid})
                                SET w += $props
                            """
                            execute_cypher(graph, query, {
                                "uuid": f"workflow_{wf_name}",
                                "props": update_props
                            })
                            
                            # Link to skills mentioned in frontmatter
                            for skill_name in frontmatter.get('related_skills', []):
                                query = """
                                    MATCH (w:Entity {uuid: $wf_uuid})
                                    MATCH (s:Entity {uuid: $skill_uuid})
                                    MERGE (w)-[:USES_SKILL]->(s)
                                """
                                execute_cypher(graph, query, {
                                    "wf_uuid": f"workflow_{wf_name}",
                                    "skill_uuid": f"skill_{skill_name}"
                                })
                        
                        logger.info(f"  Updated Workflow from workflow.md: {wf_name}")
                
                # Process templates in workflow folder
                templates_dir = wf_folder / 'templates'
                if templates_dir.exists():
                    for template_file in templates_dir.iterdir():
                        if template_file.is_file() and not template_file.name.startswith('.'):
                            tpl_name = template_file.stem
                            tpl_props = {
                                'name': tpl_name,
                                'path': f"/workflows/{phase_folder.name}/workflows/{wf_folder.name}/templates/{template_file.name}",
                                'file_type': template_file.suffix.lstrip('.'),
                                'entity_type': 'WorkflowTemplate',
                                'group_id': WORKFLOW_GROUP_ID,
                                'uuid': f"template_{wf_folder.name}_{tpl_name}",
                            }
                            
                            if not dry_run:
                                query = """
                                    MERGE (t:Entity {uuid: $uuid})
                                    SET t += $props
                                """
                                execute_cypher(graph, query, {"uuid": tpl_props['uuid'], "props": tpl_props})
                                
                                # Link to workflow
                                query = """
                                    MATCH (t:Entity {uuid: $tpl_uuid})
                                    MATCH (w:Entity {uuid: $wf_uuid})
                                    MERGE (w)-[:USES_TEMPLATE]->(t)
                                """
                                execute_cypher(graph, query, {
                                    "tpl_uuid": tpl_props['uuid'],
                                    "wf_uuid": f"workflow_{wf_folder.name}"
                                })
                
                # Process tools in workflow folder
                tools_dir = wf_folder / 'tools'
                if tools_dir.exists():
                    for tool_file in tools_dir.glob('*.py'):
                        tool_name = tool_file.stem
                        tool_props = {
                            'name': tool_name,
                            'path': f"/workflows/{phase_folder.name}/workflows/{wf_folder.name}/tools/{tool_file.name}",
                            'entity_type': 'WorkflowTool',
                            'group_id': WORKFLOW_GROUP_ID,
                            'uuid': f"tool_{wf_folder.name}_{tool_name}",
                        }
                        
                        if not dry_run:
                            query = """
                                MERGE (t:Entity {uuid: $uuid})
                                SET t += $props
                            """
                            execute_cypher(graph, query, {"uuid": tool_props['uuid'], "props": tool_props})


async def main():
    parser = argparse.ArgumentParser(description='Ingest workflow definitions into Graphiti')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created without making changes')
    parser.add_argument('--clear-first', action='store_true', help='Clear existing workflow definitions before ingesting')
    parser.add_argument('--workspace', type=str, default='/mnt/workspace', help='Workspace root directory')
    args = parser.parse_args()
    
    workspace = Path(args.workspace)
    
    # Check directories exist
    workflow_engine_dir = workspace / 'workflow_engine'
    workflows_dir = workspace / 'workflows'
    
    if not workflow_engine_dir.exists():
        logger.error(f"workflow_engine directory not found: {workflow_engine_dir}")
        return
    
    logger.info("=" * 60)
    logger.info("WORKFLOW DEFINITIONS INGESTION")
    logger.info("=" * 60)
    logger.info(f"Workspace: {workspace}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info("")
    
    graph = None
    
    if args.dry_run:
        logger.info("[DRY RUN MODE] No changes will be made")
    else:
        # Initialize FalkorDB connection using falkordb-py directly
        from falkordb import FalkorDB
        
        falkordb_host = os.getenv("FALKORDB_HOST", "localhost")
        falkordb_port = int(os.getenv("FALKORDB_PORT", "6379"))
        
        logger.info(f"Connecting to FalkorDB at {falkordb_host}:{falkordb_port}...")
        db = FalkorDB(host=falkordb_host, port=falkordb_port)
        graph = db.select_graph("roscoe_graph")
        
        if args.clear_first:
            await clear_workflow_definitions(graph)
    
    # Load JSON schemas from workflow_engine
    phase_definitions = load_json_file(workflow_engine_dir / 'schemas' / 'phase_definitions.json')
    workflow_definitions = load_json_file(workflow_engine_dir / 'schemas' / 'workflow_definitions.json')
    resource_mappings = load_json_file(workflow_engine_dir / 'schemas' / 'resource_mappings.json')
    
    # Create nodes from workflow_engine schemas
    logger.info("")
    logger.info("=" * 40)
    logger.info("Processing workflow_engine/schemas/")
    logger.info("=" * 40)
    
    await create_phase_nodes(graph, phase_definitions, args.dry_run)
    await create_workflow_nodes(graph, workflow_definitions, phase_definitions, args.dry_run)
    await create_checklist_nodes(graph, workflow_engine_dir / 'checklists', args.dry_run)
    await create_skill_nodes(graph, resource_mappings, args.dry_run)
    
    # Process workflows/ folder for landmarks and additional metadata
    if workflows_dir.exists():
        logger.info("")
        logger.info("=" * 40)
        logger.info("Processing workflows/ folder")
        logger.info("=" * 40)
        await ingest_workflows_folder(graph, workflows_dir, args.dry_run)
    else:
        logger.warning(f"workflows/ directory not found: {workflows_dir}")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("INGESTION COMPLETE")
    logger.info("=" * 60)
    
    if not args.dry_run and graph:
        # Print summary
        result = execute_cypher(graph, """
            MATCH (n:Entity)
            WHERE n.group_id = $group_id
            RETURN n.entity_type as type, COUNT(*) as count
            ORDER BY count DESC
        """, {"group_id": WORKFLOW_GROUP_ID})
        
        logger.info("Summary of created nodes:")
        for row in result.result_set:
            logger.info(f"  {row[0]}: {row[1]}")


if __name__ == "__main__":
    asyncio.run(main())
