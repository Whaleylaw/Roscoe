#!/usr/bin/env python3
"""
Process inline user annotations from review files.

Parses user comments, executes actions, creates diff files for review.
"""

import re
import json
from pathlib import Path
from collections import defaultdict


ENTITIES_DIR = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities")


class AnnotationProcessor:
    def __init__(self):
        self.actions_log = []
        self.entities_added = defaultdict(list)
        self.entities_ignored = set()
        self.corrections_made = []
        self.case_specific_mappings = defaultdict(dict)  # case_name -> {entity -> correction}

    def load_entity_file(self, filename: str) -> list:
        """Load entity JSON file."""
        filepath = ENTITIES_DIR / filename
        if not filepath.exists():
            return []
        with open(filepath) as f:
            return json.load(f)

    def save_entity_file(self, filename: str, data: list):
        """Save entity JSON file."""
        filepath = ENTITIES_DIR / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def add_entity(self, entity_type: str, name: str, attributes: dict, source_file: str) -> bool:
        """Add new entity to appropriate file."""
        type_to_file = {
            "Attorney": "attorneys.json",
            "Defendant": "defendants.json",
            "Organization": "organizations.json",
            "Vendor": "vendors.json",
            "Mediator": "mediators.json",
            "Witness": "witnesses.json",
            "CourtClerk": "court_clerks.json",
            "Adjuster": "adjusters.json",
        }

        filename = type_to_file.get(entity_type)
        if not filename:
            return False

        entities = self.load_entity_file(filename)
        existing_names = {e['name'] for e in entities}

        if name in existing_names:
            return False  # Already exists

        new_entity = {
            "card_type": "entity",
            "entity_type": entity_type,
            "name": name,
            "attributes": attributes,
            "source_id": "inline_annotation_processing",
            "source_file": source_file
        }

        entities.append(new_entity)
        self.save_entity_file(filename, entities)

        self.entities_added[entity_type].append(name)
        self.actions_log.append(f"ADDED {entity_type}: {name}")

        return True

    def process_annotation(self, entity_name: str, current_status: str, annotation: str,
                          entity_type_section: str, case_name: str) -> tuple[str, dict]:
        """
        Process a single annotation and return new status line + metadata.

        Returns: (new_status_line, action_metadata)
        """
        annotation_lower = annotation.lower()
        action = {"type": "none", "details": ""}

        # IGNORE
        if 'ignore' in annotation_lower:
            self.entities_ignored.add(entity_name)
            self.actions_log.append(f"IGNORED: {entity_name}")
            return "✓ IGNORED", {"type": "ignore"}

        # ADD AS DEFENDANT
        if re.search(r'(needs to be added|add) as (a )?defendant', annotation_lower):
            added = self.add_entity("Defendant", entity_name, {}, case_name)
            status = "✓ ADDED as Defendant" if added else "✓ Already added as Defendant"
            return status, {"type": "add", "entity_type": "Defendant"}

        # ADD AS ORGANIZATION
        if re.search(r'add (as|to) (an? )?organization', annotation_lower):
            added = self.add_entity("Organization", entity_name, {}, case_name)
            status = "✓ ADDED as Organization" if added else "✓ Already added"
            return status, {"type": "add", "entity_type": "Organization"}

        # ADD AS VENDOR
        if re.search(r'add (as|to) vendor', annotation_lower):
            added = self.add_entity("Vendor", entity_name, {}, case_name)
            status = "✓ ADDED as Vendor" if added else "✓ Already added"
            return status, {"type": "add", "entity_type": "Vendor"}

        # ADD AS ADJUSTER (with context)
        if re.search(r'add as (an? )?adjuster', annotation_lower):
            # Look for insurance company in annotation or context
            added = self.add_entity("Adjuster", entity_name, {}, case_name)
            status = "✓ ADDED as Adjuster" if added else "✓ Already added"
            return status, {"type": "add", "entity_type": "Adjuster"}

        # CLERK FOR COURT
        if 'clerk' in annotation_lower and 'court' in annotation_lower:
            court_match = re.search(r'for ([A-Za-z ]+(?:Circuit|District) Court[^.]*)', annotation, re.IGNORECASE)
            court_name = court_match.group(1).strip() if court_match else ""

            attrs = {"clerk_type": "circuit" if "circuit" in annotation_lower else "district"}
            added = self.add_entity("CourtClerk", entity_name, attrs, case_name)
            status = f"✓ ADDED as CourtClerk ({court_name})" if added else "✓ Already added"
            return status, {"type": "add", "entity_type": "CourtClerk"}

        # WITNESS
        if 'witness' in annotation_lower:
            added = self.add_entity("Witness", entity_name, {}, case_name)
            status = "✓ ADDED as Witness" if added else "✓ Already added"
            return status, {"type": "add", "entity_type": "Witness"}

        # CORRECTION: "This is X"
        if re.search(r'(this is|should be|it\'s) ([A-Za-z ]+)', annotation, re.IGNORECASE):
            correction_match = re.search(r'(this is|should be|it\'s) ([A-Za-z .,&\-()]+?)(?:\.|$)', annotation, re.IGNORECASE)
            if correction_match:
                corrected_name = correction_match.group(2).strip()
                self.case_specific_mappings[case_name][entity_name] = corrected_name
                self.corrections_made.append(f"{case_name}: {entity_name} → {corrected_name}")
                return f"✓ CORRECTED: {corrected_name}", {"type": "correction", "corrected_to": corrected_name}

        # TYPE CORRECTION: "She's an attorney, not a client"
        if re.search(r"(she's|he's|it's) (a |an )?(\w+), not", annotation_lower):
            type_match = re.search(r"(she's|he's|it's) (a |an )?(\w+)", annotation_lower)
            if type_match:
                correct_type = type_match.group(3).capitalize()
                return f"✓ TYPE CORRECTED: {correct_type} (was {entity_type_section})", {"type": "type_correction", "correct_type": correct_type}

        # FROM DIRECTORY - needs to be added
        if '(from directory)' in current_status and not annotation.startswith('✓'):
            # Determine type from section
            type_map = {
                "Organization": "Organization",
                "Vendor": "Vendor",
                "Defendant": "Defendant",
                "Adjuster": "Adjuster",
            }
            target_type = type_map.get(entity_type_section)
            if target_type:
                added = self.add_entity(target_type, entity_name, {}, case_name)
                if added:
                    return f"✓ ADDED as {target_type} (from directory)", {"type": "add_from_directory", "entity_type": target_type}

        # No action needed
        return current_status, {"type": "none"}

    def process_review_file(self, review_file: Path) -> dict:
        """Process all annotations in a review file."""
        case_name = review_file.stem.replace('review_', '')

        with open(review_file) as f:
            content = f.read()

        lines = content.split('\n')
        updated_lines = []
        current_section = None

        stats = {"added": 0, "ignored": 0, "corrected": 0, "unchanged": 0}

        for line in lines:
            # Track current entity type section
            section_match = re.match(r'### ([A-Za-z]+) \(\d+ consolidated\)', line)
            if section_match:
                current_section = section_match.group(1)
                updated_lines.append(line)
                continue

            # Process entity lines with annotations
            # Pattern: - [ ] Name — *status* annotation
            match = re.match(r'(- \[ \] (?:\*\*)?([^*—]+?)(?:\*\*)? — )(\*[^*]+\*)(\s*.+)?', line)
            if match:
                prefix = match.group(1)
                entity_name = match.group(2).strip()
                current_status = match.group(3)
                annotation = match.group(4).strip() if match.group(4) else ""

                if annotation:
                    # Process annotation
                    new_status, action_meta = self.process_annotation(
                        entity_name, current_status, annotation, current_section, case_name
                    )

                    # Build new line
                    new_line = f"{prefix}{new_status}"

                    # Track stats
                    if action_meta["type"] == "add" or action_meta["type"] == "add_from_directory":
                        stats["added"] += 1
                    elif action_meta["type"] == "ignore":
                        stats["ignored"] += 1
                    elif action_meta["type"] in ["correction", "type_correction"]:
                        stats["corrected"] += 1
                    else:
                        stats["unchanged"] += 1

                    updated_lines.append(new_line)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Save updated file
        updated_content = '\n'.join(updated_lines)
        with open(review_file, 'w') as f:
            f.write(updated_content)

        return stats

    def create_diff_file(self, original_file: Path, updated_file: Path, diff_file: Path):
        """Create diff file showing changes."""
        with open(original_file) as f:
            original_lines = f.readlines()
        with open(updated_file) as f:
            updated_lines = f.readlines()

        diff_content = []
        diff_content.append(f"# Diff: {original_file.name}\n")
        diff_content.append(f"Showing changes made by annotation processing\n")
        diff_content.append("=" * 80 + "\n\n")

        for i, (orig, new) in enumerate(zip(original_lines, updated_lines), 1):
            if orig != new:
                diff_content.append(f"Line {i}:\n")
                diff_content.append(f"  BEFORE: {orig.rstrip()}\n")
                diff_content.append(f"  AFTER:  {new.rstrip()}\n")
                diff_content.append("\n")

        with open(diff_file, 'w') as f:
            f.writelines(diff_content)


def main():
    processor = AnnotationProcessor()
    reviews_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/reviews")

    review_files = [
        "review_Abby-Sitgraves-MVA-7-13-2024.md",
        "review_Abigail-Whaley-MVA-10-24-2024.md",
        "review_Alma-Cristobal-MVA-2-15-2024.md",
    ]

    print("=" * 80)
    print("PROCESSING INLINE ANNOTATIONS")
    print("=" * 80)
    print()

    for filename in review_files:
        review_file = reviews_dir / filename

        if not review_file.exists():
            print(f"⚠️  Skipping {filename}")
            continue

        # Backup original
        backup_file = review_file.with_suffix('.md.backup')
        with open(review_file) as f:
            original_content = f.read()
        with open(backup_file, 'w') as f:
            f.write(original_content)

        print(f"Processing {filename}...")
        stats = processor.process_review_file(review_file)

        print(f"  Added: {stats['added']}, Ignored: {stats['ignored']}, Corrected: {stats['corrected']}")

        # Create diff
        diff_file = reviews_dir / f"{review_file.stem}.diff.md"
        processor.create_diff_file(backup_file, review_file, diff_file)
        print(f"  ✓ Diff created: {diff_file.name}")
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    print("Entities Added:")
    for entity_type, entities in sorted(processor.entities_added.items()):
        print(f"  {entity_type}: {len(entities)}")
        for e in entities[:5]:
            print(f"    - {e}")
        if len(entities) > 5:
            print(f"    ... and {len(entities) - 5} more")

    print()
    print(f"Entities Ignored: {len(processor.entities_ignored)}")
    for e in sorted(processor.entities_ignored)[:10]:
        print(f"  - {e}")
    if len(processor.entities_ignored) > 10:
        print(f"  ... and {len(processor.entities_ignored) - 10} more")

    print()
    print(f"Corrections Made: {len(processor.corrections_made)}")
    for c in processor.corrections_made[:10]:
        print(f"  - {c}")

    print()
    print("✅ Review diff files before proceeding:")
    for filename in review_files:
        diff_file = reviews_dir / f"{Path(filename).stem}.diff.md"
        if diff_file.exists():
            print(f"  - {diff_file.name}")


if __name__ == "__main__":
    main()
