#!/usr/bin/env python3
"""
Generate comprehensive graph schema documentation.

Extracts all entity types and relationships from graphiti_client.py
and creates a Markdown schema reference.
"""

import re
from pathlib import Path


def extract_entity_info(content: str) -> list:
    """Extract all Pydantic entity models."""
    entities = []

    # Find all class definitions that inherit from BaseModel
    pattern = r'class (\w+)\(BaseModel\):\s*"""([^"]+)"""(.*?)(?=\nclass |\nENTITY_TYPES|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)

    for class_name, docstring, body in matches:
        # Skip relationship classes
        if any(rel in class_name for rel in ['At', 'By', 'In', 'For', 'Of', 'To', 'On', 'From', 'With', 'Over', 'Status']):
            # Check if it's actually a relationship
            if 'TreatingAt' in class_name or 'FiledIn' in class_name or 'WorksAt' in class_name:
                continue

        # Extract fields
        fields = []
        field_pattern = r'(\w+):\s*Optional\[(\w+)\]\s*=\s*Field\([^)]*description="([^"]+)"'
        field_matches = re.findall(field_pattern, body)

        for field_name, field_type, description in field_matches:
            fields.append({
                "name": field_name,
                "type": field_type,
                "description": description
            })

        entities.append({
            "name": class_name,
            "description": docstring.strip(),
            "fields": fields
        })

    return entities


def extract_relationships(content: str) -> dict:
    """Extract EDGE_TYPE_MAP relationships."""
    relationships = {}

    # Find EDGE_TYPE_MAP section
    edge_map_match = re.search(r'EDGE_TYPE_MAP = \{(.*?)\n\}', content, re.DOTALL)
    if not edge_map_match:
        return relationships

    edge_map_content = edge_map_match.group(1)

    # Parse relationships
    # Pattern: ("Source", "Target"): ["RelType"],
    pattern = r'\("(\w+)",\s*"(\w+)"\):\s*\[([^\]]+)\]'
    matches = re.findall(pattern, edge_map_content)

    for source, target, rel_types in matches:
        rel_list = [r.strip().strip('"') for r in rel_types.split(',')]

        for rel_type in rel_list:
            if rel_type not in relationships:
                relationships[rel_type] = []

            relationships[rel_type].append({
                "source": source,
                "target": target
            })

    return relationships


def generate_schema_doc():
    """Generate schema documentation."""
    graphiti_file = Path("/Volumes/X10 Pro/Roscoe/src/roscoe/core/graphiti_client.py")

    with open(graphiti_file) as f:
        content = f.read()

    print("Extracting entity types...")
    entities = extract_entity_info(content)

    print("Extracting relationships...")
    relationships = extract_relationships(content)

    # Generate markdown
    lines = []
    lines.append("# Roscoe Knowledge Graph - Complete Schema\n")
    lines.append("**Generated from:** `graphiti_client.py`\n")
    lines.append(f"**Entity Types:** {len(entities)}\n")
    lines.append(f"**Relationship Types:** {len(relationships)}\n")
    lines.append("\n---\n")

    # Entity Types
    lines.append("## Entity Types\n")

    # Group by category
    categories = {
        "Core Case": ["Case", "Client", "Defendant", "Note", "Episode"],
        "Insurance": ["Insurer", "Adjuster", "PIPClaim", "BIClaim", "UMClaim", "UIMClaim", "WCClaim", "MedPayClaim"],
        "Medical": ["HealthSystem", "MedicalProvider", "Doctor", "Lien", "LienHolder"],
        "Legal/Courts": ["LawFirm", "Attorney", "CaseManager", "Court", "CircuitDivision", "DistrictDivision",
                        "AppellateDistrict", "SupremeCourtDistrict", "CircuitJudge", "DistrictJudge",
                        "AppellateJudge", "SupremeCourtJustice", "CourtClerk", "MasterCommissioner",
                        "CourtAdministrator", "Pleading"],
        "Professional Services": ["Expert", "Mediator", "Witness", "Vendor"],
        "Documents": ["Document"],
        "Financial": ["Expense", "Settlement"],
        "Organizations": ["Organization"],
        "Workflow": ["Phase", "SubPhase", "Landmark", "WorkflowDef", "WorkflowStep", "WorkflowChecklist",
                    "WorkflowSkill", "WorkflowTemplate", "WorkflowTool", "LandmarkStatus"]
    }

    for category, entity_names in categories.items():
        lines.append(f"\n### {category}\n")

        for entity in entities:
            if entity["name"] in entity_names:
                lines.append(f"#### `{entity['name']}`\n")
                lines.append(f"**Description:** {entity['description']}\n")

                if entity["fields"]:
                    lines.append("\n**Properties:**\n")
                    for field in entity["fields"]:
                        lines.append(f"- `{field['name']}` ({field['type']}): {field['description']}\n")

                lines.append("\n")

    # Relationship Types
    lines.append("---\n\n## Relationship Types\n")

    for rel_type in sorted(relationships.keys()):
        lines.append(f"\n### `{rel_type}`\n")

        # Group by source
        by_source = {}
        for rel in relationships[rel_type]:
            source = rel["source"]
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(rel["target"])

        for source in sorted(by_source.keys()):
            targets = sorted(by_source[source])
            targets_str = ", ".join(targets)
            lines.append(f"- `({source})-[:{rel_type}]->({targets_str})`\n")

    # Professional relationship patterns
    lines.append("\n---\n\n## Professional Relationship Patterns\n")
    lines.append("\nAll professional entities connect to their organizations:\n\n")
    lines.append("| Person | Organization | Relationship |\n")
    lines.append("|--------|--------------|-------------|\n")
    lines.append("| Attorney | LawFirm | WORKS_AT |\n")
    lines.append("| CaseManager | LawFirm | WORKS_AT |\n")
    lines.append("| Doctor | MedicalProvider | WORKS_AT |\n")
    lines.append("| Adjuster | Insurer | WORKS_AT |\n")
    lines.append("| Expert | Organization | WORKS_AT |\n")
    lines.append("| Mediator | Organization | WORKS_AT |\n")
    lines.append("| CircuitJudge | CircuitDivision | PRESIDES_OVER |\n")
    lines.append("| DistrictJudge | DistrictDivision | PRESIDES_OVER |\n")
    lines.append("| AppellateJudge | AppellateDistrict | PRESIDES_OVER |\n")
    lines.append("| SupremeCourtJustice | SupremeCourtDistrict | PRESIDES_OVER |\n")
    lines.append("| CourtClerk | Court | WORKS_AT |\n")
    lines.append("| MasterCommissioner | Court | APPOINTED_BY |\n")
    lines.append("| CourtAdministrator | Court | WORKS_AT |\n")

    # Hierarchies
    lines.append("\n## Hierarchical Structures\n")
    lines.append("\n### Court System:\n")
    lines.append("```\n")
    lines.append("Court\n")
    lines.append("  ↑ [PART_OF]\n")
    lines.append("CircuitDivision/DistrictDivision\n")
    lines.append("  ↑ [PRESIDES_OVER]\n")
    lines.append("Judge\n")
    lines.append("```\n")

    lines.append("\n### Healthcare System:\n")
    lines.append("```\n")
    lines.append("HealthSystem\n")
    lines.append("  ↑ [PART_OF]\n")
    lines.append("MedicalProvider\n")
    lines.append("  ↑ [WORKS_AT]\n")
    lines.append("Doctor\n")
    lines.append("```\n")

    lines.append("\n### Law Firm:\n")
    lines.append("```\n")
    lines.append("LawFirm\n")
    lines.append("  ↑ [WORKS_AT]\n")
    lines.append("Attorney/CaseManager\n")
    lines.append("```\n")

    # Save
    output_file = Path("/Volumes/X10 Pro/Roscoe/GRAPH_SCHEMA.md")
    with open(output_file, 'w') as f:
        f.writelines(lines)

    print(f"\n✅ Generated schema documentation:")
    print(f"   {output_file}")
    print(f"   Entities: {len(entities)}")
    print(f"   Relationships: {len(relationships)}")


if __name__ == "__main__":
    generate_schema_doc()
