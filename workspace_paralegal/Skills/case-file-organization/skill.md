---
name: case-file-organization
description: Orchestrate end-to-end organization of disorganized personal-injury case folders (rename + categorize + dedupe + verify) using the firm's bucket system and strict naming/date rules. Use when a case folder needs full cleanup from start to finish (not one-off renames). Uses sub-agents for bounded phases and persists progress artifacts under /projects/{case_name}/Reports/ so long-running runs can resume safely.
---

# Case File Organization

## Required announcement (do this first)

Before proceeding, announce that you are using this skill (keeps the user oriented):

> "I’m activating the Case File Organization skill to standardize and organize this case folder end-to-end (inventory → mapping → QA → execution → verification)."

## Overview

This is a **single orchestrator** for an end-to-end workflow. It is designed for **long-running** folder cleanups that can span many context windows by leaving durable artifacts in `Reports/` and working phase-by-phase.

**Core principles:**
- **One end-to-end run**: inventory → mapping → QA → execution → verification (no “ok now do the next step”).
- **Progressive disclosure**: this file stays short; details live in linked docs.
- **Safe resumption**: always resume from `Reports/` artifacts instead of guessing.
- **Delegation**: sub-agents do bounded, well-specified phases; main agent validates gate checks and performs the irreversible execution step.

## When to Use

Use this skill when:
- Case files are disorganized or in the root folder
- Filenames don't follow a standard pattern
- Files need categorization into proper subdirectories
- Preparing files for downstream workflows (search, drafting, exports)
- Client asks for file organization or cleanup
- Processing a "Review_Needed" folder

When NOT to use:
- Files are already properly organized and named
- Non-case files (internal firm documents, templates)
- Active documents being edited

## What this skill changes

This workflow can:
- **Rename** files to the standard convention
- **Move** files into bucket folders (and provider/carrier subfolders where applicable)
- **Delete** true duplicates (only when the mapping/QA approves)

If the user is uncomfortable with deletions, run with “no-delete” constraints (see `[TROUBLESHOOTING.md](TROUBLESHOOTING.md)`).

## Long-running harness (required for big cleanups)

All durable progress artifacts live here (per case):
- `/projects/{case_name}/Reports/case_file_organization_state.json`
- `/projects/{case_name}/Reports/case_file_organization_progress.md`

Use the harness routines in:
- `[docs/HARNESS.md](docs/HARNESS.md)` (how to start/resume safely)
- `[docs/OPERATIONS.md](docs/OPERATIONS.md)` (phase-by-phase steps + commands)

## Start here (decision tree)

1) **If this is a fresh run** (no state file exists): follow `[docs/HARNESS.md](docs/HARNESS.md)` → initialize state, then proceed to Phase 1 in `[docs/OPERATIONS.md](docs/OPERATIONS.md)`.

2) **If resuming** (state file exists): read the state + last progress entry, then continue the next incomplete phase from `[docs/OPERATIONS.md](docs/OPERATIONS.md)`.

## Phase map (high level)

Details and exact commands are in `[docs/OPERATIONS.md](docs/OPERATIONS.md)`.

1. **Phase 1 — Inventory + filename de-biasing** (main agent; script)
2. **Phase 1.5 — Optional markdown cleanup** (main agent; script)
3. **Phase 2 — Analysis & mapping** (sub-agent(s); writes map)
4. **Phase 2 gate — Validate mapping is complete** (main agent; MUST pass)
5. **Phase 3 — Quality review** (sub-agent; writes QA summary)
6. **Phase 4 — Execution** (sub-agent generates JSON plan; main agent runs script)
7. **Phase 5 — Verification** (sub-agent; writes final summary)

## Reference

All bucket definitions, naming/date rules, email handling rules, and multi-party rules live in:
- `[docs/REFERENCE.md](docs/REFERENCE.md)`


