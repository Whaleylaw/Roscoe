# Sandbox Mutation Alternatives

Below are three candidate architectures for enabling safe, programmatic changes to the real `/projects` tree while preserving the benefits of sandboxed analysis and minimizing operational risk.

---

## Proposal A – Workspace Mutation Service (Plan & Apply API)

**Summary**
- Deploy a small FastAPI (or Fastify) service on the existing GCE VM—either as a sidecar container or systemd service—that mounts `/mnt/workspace` (already exposed via gcsfuse).
- The service exposes curated endpoints:
  1. `POST /plans` – upload a JSON plan describing desired moves/renames/creates/deletes.
  2. `POST /plans/{id}/validate` – run dry-run validation (existence checks, bucket rules, collision detection) and return a diff-style report.
  3. `POST /plans/{id}/apply` – after approval, execute the plan with direct file operations using Python’s `pathlib` + `shutil`, logging every mutation to `/Database/reorg_audit/{timestamp}.json`.
- LangGraph tools change from “execute code” to “submit/validate/apply plan,” keeping the AI unprivileged. Optionally require a Slack approval or a manual `POST /plans/{id}/approve` call before apply.

**Pros**
- No per-plan container spin-up; fastest path to production.
- Validation/apply logic lives in one place, so guardrails (allowed roots, max file count, rollback logs) are easier to enforce.
- Works with existing GCS mount; no need to upload whole case folders.

**Cons**
- Requires building and maintaining a new API surface.
- Must design robust rate limiting and safety checks to avoid mass deletions.

**Implementation Notes**
- Reuse LangGraph tool schema: LLM outputs plan JSON (stored in `/Reports/{case}/reorg_plan.json`), tool uploads to service.
- Dry-run returns an annotated table that can be rendered back to the user for review.
- Apply command writes summary to Slack and persists operation history for auditing / undo.

---

## Proposal B – Queued Background Worker (Plan Files + Approval Queue)

**Summary**
- Keep plan creation in RunLoop sandbox (read-only). Plans are JSON or shell scripts saved under `/Database/reorg_queue/{timestamp}-{case}.json`.
- A background worker (Python script executed via systemd timer or cron on the VM) polls the queue:
  1. Moves plans to `/Database/reorg_queue/pending`.
  2. Validates them; writes results to `/Reports/{case}/reorg_validation.md`.
  3. Waits for approval: Slack command (`/roscoe-approve plan_id`) or human toggles status file from `pending` → `approved`.
  4. On approval, worker executes the plan (direct filesystem access) and records logs.

**Pros**
- No long-running API needed; relies on file-based queueing—simple to reason about and easy to pause.
- Approval UX can be as simple as editing a status file or using Slack slash commands.
- Worker can batch changes, throttle operations, and auto-backup files before moves.

**Cons**
- Higher latency (worker loop) unless we invest in event triggers.
- Monitoring queue state requires additional tooling (e.g., Slack notifications).
- Need careful design for concurrency (e.g., multiple plans touching same case).

**Implementation Notes**
- Worker script can live in repo (e.g., `scripts/apply_reorg_queue.py`) and run under systemd with GCS-mounted workspace.
- Each operation logged to `/Database/reorg_history/{plan_id}.json`.
- Optionally include `rollback.sh` generated per plan to allow manual undo.

---

## Proposal C – Scoped Mutable Containers (Per-Case Docker Sessions)

**Summary**
- When a tool call requests mutation of `CaseXYZ`, the middleware launches a short-lived Docker container on the VM:
  ```bash
  docker run --rm \
    -v /mnt/workspace/projects/CaseXYZ:/case \
    -v /mnt/workspace/Tools:/tools:ro \
    roscoe-mutator:latest \
    python /tools/create_file_inventory.py --root /case
  ```
- Container has direct read/write access to that specific case path, but nothing else.
- LangGraph receives command output / logs; once container exits, changes are already reflected in `/projects/CaseXYZ`.
- For multi-case operations, spin separate containers or mount additional directories as needed.

**Pros**
- Preserves the “sandbox” feel while actually mutating the real filesystem.
- Isolation per case minimizes blast radius; the container can run with a restricted user inside.
- Developers can reuse the same flow as today (run Python scripts), just with a different backend.

**Cons**
- Requires Docker in privileged mode and careful handling of user permissions on the VM.
- Harder to audit: scripts run inside container could do more than intended unless validated beforehand.
- Does not provide built-in approval workflow; we’d still want pre-plan validation to avoid unexpected moves.

**Implementation Notes**
- Build tiny `roscoe-mutator` image with necessary Python deps.
- Add a LangGraph middleware `execute_mutation_case(command, case_path, tools=[...])` that:
  1. Validates command (whitelist interpreter).
  2. Launches container via Docker SDK / CLI, streaming stdout/stderr back to the agent.
  3. Captures exit code + writes log to `/Reports/{case}/mutation_logs/{timestamp}.txt`.
- Optionally pair with Proposal A’s validator so that only approved commands run inside containers.

---

### Next Steps
1. Review these options, pick the preferred baseline (service vs. queue vs. per-case containers).
2. Flesh out safety requirements (max operations, rollback strategy, access control).
3. Prototype validator module + sample plan format (common prerequisite for all three options).

