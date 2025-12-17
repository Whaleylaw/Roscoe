# Notes Summary: claude_skills_articles

These notes summarize the 4 docs in `/Volumes/X10 Pro/Roscoe/.claude/claude_skills_articles/` so we can reuse the ideas later.

## 01 — Introducing Agent Skills (Oct 16, 2025)
- **What Skills are**: A *folder-packaged capability* (instructions + scripts + resources) that Claude can load **only when relevant**.
- **Core properties**:
  - **Composable**: multiple skills can stack; Claude coordinates.
  - **Portable**: same skill format works across Claude surfaces (Claude apps, Claude Code, API).
  - **Efficient**: minimal loading; avoids flooding context.
  - **Powerful**: can include executable code (more reliable than pure text generation for some tasks).
- **Surfaces**:
  - **Claude apps**: skills can be enabled; skill-creator helps generate structure interactively.
  - **API**: skills can be attached to Messages API; `/v1/skills` for versioning/management; requires code execution tool beta.
  - **Claude Code**: install via marketplace plugins or manually in `~/.claude/skills`; auto-loaded when relevant.
- **Security note**: skills can execute code → prefer trusted sources.

## 02 — Building Skills for Claude Code (Dec 2, 2025)
- **Main problem**: Claude Code doesn’t know *your institutional knowledge* (schemas, business definitions, required filters), so it outputs generic best practices.
- **Solution**: skills provide *procedural knowledge* via **progressive disclosure**.
  - Claude always sees a small “index” (name/description).
  - It loads detailed docs only when needed.
- **Skill anatomy**:
  - `SKILL.md` is core. **YAML frontmatter** with:
    - `name`: stable identifier
    - `description`: determines when it triggers
  - Body should be *scannable workflow guidance* + links to deeper reference files.
  - `references/` holds detailed docs (schemas, metrics, edge cases) loaded on demand.
- **Important principle**: avoid duplicating info between `SKILL.md` and reference files; keep `SKILL.md` lean.
- **Skills vs `CLAUDE.md`**:
  - `CLAUDE.md` is *always* loaded (project-specific guidance).
  - Skills are conditional + cross-surface + can bundle code/resources.
- **Good candidates**:
  - cross-repo relevance
  - multi-audience value
  - stable patterns
- **Sharing approaches**: zip, internal repo, git repo, plugin bundle.

## 03 — How to create Skills: steps, limitations, examples (Nov 19, 2025)
- **5-step workflow**:
  1) define requirements & success criteria
  2) write `name` (short, hyphenated)
  3) write `description` (most important for triggering; verbs/use cases/boundaries)
  4) write structured instructions (overview → prerequisites → steps → examples → error handling → limitations)
  5) upload depending on surface (Claude.ai, Claude Code plugin/project, Skills API)
- **Triggering facts**:
  - only `name` + `description` impact triggering
  - semantic matching, not strict keywords
  - overly broad descriptions mis-trigger; too narrow misses
- **Context sizing**: use a “menu” approach + split into multiple reference files; load only what’s needed.
- **Testing matrix**:
  - normal usage
  - edge cases
  - out-of-scope requests (ensure it stays dormant)
  - triggering tests + functional tests (consistency/usability/doc accuracy)
- **Examples emphasize**: decision trees, crisp boundaries, concrete inputs/outputs, and validation steps.

## 04 — Effective harnesses for long-running agents (Nov 26, 2025)
- **Core problem**: long tasks span many context windows; each session begins without full memory.
- **Observed failure modes**:
  - one-shotting too much → runs out of context mid-implementation
  - later sessions declare victory prematurely
  - incomplete testing leads to false “done”
- **Two-part harness**:
  - **Initializer agent** (first run): creates environment scaffolding
    - `init.sh` (how to start/verify)
    - `claude-progress.txt` (log of work)
    - initial git commit
    - a comprehensive feature list file (prefer JSON) with pass/fail flags
  - **Coding agent** (subsequent runs): incremental progress
    - work **one feature at a time**
    - leave repo in a clean, merge-ready state
    - write progress notes + git commits
    - verify end-to-end behavior (browser automation recommended)
- **Key artifacts**:
  - feature list JSON prevents premature completion and gives next sessions a to-do map
  - progress file + git log are “breadcrumbs” for continuity
- **Recommended startup routine each session**:
  - check `pwd`, read progress, inspect feature list, check git log
  - run dev server via `init.sh`
  - smoke-test fundamental flows

## Implications for Roscoe (how we can apply later)
- **Progressive disclosure**: keep global always-loaded prompts small; put large, reusable workflows into skill folders.
- **Trigger reliability**: invest in crisp `description` with verbs + scenarios + explicit “not for …” boundaries.
- **References directory**: separate schemas/checklists per domain (e.g., litigation, medical, exports) so the agent only loads what’s needed.
- **Long-running tasks**: for multi-hour workflows (import/organize/analyze/export), adopt a harness pattern:
  - one-time initializer that writes a structured “feature/task list” + runbook
  - subsequent runs operate on one task, log progress, and verify outcomes

## Addendum — Structural patterns from example skills in `claude_skills_articles/skills/`

I reviewed the skills under:
- `/Volumes/X10 Pro/Roscoe/.claude/claude_skills_articles/skills/`

Focus here is **how the folders/files are organized** and **how skills orchestrate tooling**, not the domain content.

### Common folder layout patterns
- **Every skill has `SKILL.md` at the skill root**.
  - Uses YAML frontmatter (at minimum `name` + `description`) to drive triggering.
  - Main body tends to be a “router”: high-level workflow + links to deeper files.
- **Support content lives next to SKILL.md and is linked relatively** (e.g., `[OPERATIONS.md](OPERATIONS.md)`), enabling progressive disclosure.
- **Dedicated subfolders by artifact type** (varies by skill):
  - `scripts/` for executable utilities (often Python)
  - `tools/` for executable helpers that act like “APIs” for the skill
  - `docs/` for longer-form background/reference reading
  - `cookbook/` for scenario-based execution recipes
  - `prompts/` for prompt templates (to be filled “in memory”, not necessarily written back)

### Pattern 1: “Ops manual” skill (worktree-manager-skill)
- **Split documentation by intent**:
  - `SKILL.md` = trigger + decision tree + guardrails (what to do / what NOT to do)
  - `OPERATIONS.md` = step-by-step procedures (create/list/remove)
  - `EXAMPLES.md` = worked examples / usage patterns
  - `TROUBLESHOOTING.md` = symptom → diagnosis → fixes
  - `REFERENCE.md` = compact technical reference
- **Clear guardrails**: explicitly prohibits ad-hoc bash/git and requires using provided commands.
- **Decision-tree first**: maps user phrasing to the right operation, then delegates to the relevant doc.
- **Tool gating**: uses an `allowed-tools` frontmatter field to constrain tool usage.
  - Note: some docs/specs say only `name`/`description` are standard; `allowed-tools` looks like a Claude Code extension. Pattern: treat as optional / best-effort depending on runtime.

### Pattern 2: “Scripted utility” skill (video-processor)
- **Single entrypoint script** under `scripts/` with a clear CLI.
- **PEP 723 inline dependencies** used in the Python script header (and/or an `uv run` shebang), so execution is reproducible without a full project venv.
- `SKILL.md` includes:
  - prerequisites (system tools like ffmpeg + whisper)
  - exact invocation commands (e.g., `uv run <path> <subcommand> ...`)
  - a workflow section + multiple examples + error handling + performance tips
- **Key structural idea**: keep the “how to run” info in `SKILL.md`, keep the deterministic behavior in the script.

### Pattern 3: “Meta skill” that teaches skill creation (meta-skill)
- `SKILL.md` requires prereading from a `docs/` directory.
- This makes `SKILL.md` a *workflow checklist* and uses `docs/` for deeper architecture + best practices.
- Includes explicit “progressive disclosure” framing:
  1) frontmatter metadata
  2) SKILL.md instructions
  3) linked docs/scripts/resources on demand

### Pattern 4: “Tool orchestrator + cookbook” (fork-terminal)
- Organizes execution guidance into:
  - `tools/` (the executable; here, `fork_terminal.py` opens a new terminal window and runs a command)
  - `cookbook/` (recipes for different execution backends)
  - `prompts/` (a prompt template to fill in-memory for “fork with summary” flows)
- `SKILL.md` uses:
  - **feature flags / toggles** at the top (e.g., enable raw CLI vs agentic tools)
  - explicit workflow steps: understand request → read tool code → consult cookbook → execute tool
  - a “template prompt” file that is explicitly *not* to be edited; rather, copy/fill in memory then pass to the selected backend.

### Cross-skill documentation conventions that seem to work well
- **Routing at the top**: decision tree / “when to use / when not to use” early.
- **Progressive disclosure by file**: SKILL.md stays relatively short; deep details move to dedicated docs.
- **Executable helpers are small and focused**: scripts expose clear CLI or function-style entrypoints.
- **Explicit prerequisites**: system packages, command availability checks, and verification commands.
- **Examples-as-tests**: examples are written in a way that can be executed to validate the skill.
