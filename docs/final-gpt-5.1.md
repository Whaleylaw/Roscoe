## Ranking of Sandbox Solutions for Real `/projects` Mutations

### 1. Plan-and-Apply Workspace Mutation Service on the Existing GCE VM / Cloud Run **(Top Recommendation)**

**Concept (merged solution)**  
Introduce a small, privileged “mutation service” that runs inside your GCP trust boundary (on the current GCE VM with the `gcsfuse` mount, or on Cloud Run) and exposes a **Plan → Validate → Apply** API for file operations.  
The LLM never gets raw shell access to `/projects`; it only produces **structured plans** (JSON describing moves/creates/deletes), which the service validates and then applies with full audit logging and optional approval/rollback.

**Sources (very similar variants)**  
- `sandbox-solution-1.md`: **Solution 1 – VM‑Native Workspace Mutation Service** (detailed FastAPI implementation, plan/validate/apply, approval + audit).  
- `sandbox-solution-2.md`: **Proposal A – Workspace Mutation Service (Plan & Apply API)** (same pattern, simpler description).  
- `sandbox-solution-3.md`: **Solution 3 – “Plan, Verify, Apply” Sidecar** (same architecture, framed as a privileged sidecar).  
- `sandbox-solution-4.md`: **Solution 1 – GCP‑Native File Operations Worker** (Cloud Run or VM daemon, driven by JSON plans).  
- `sandbox-solution-6.md`: **Solution 1 – Mutation Service (Plan & Apply API + rollback)** (most complete: strict validation, rollback scripts, audit JSON, clear agent tools).

**Why this ranks #1**
- **Perfect fit for current setup**: Works directly with your existing GCE VM and `gcsfuse`-mounted workspace (`/mnt/workspace/projects`, `/Tools`, `/Database`) without changing Runloop or moving data.
- **Preserves the safety model**: Runloop remains an *analysis* sandbox; only the mutation service can touch real `/projects`, and only via validated, human‑designed logic.
- **Clear, enforceable guardrails**: 
  - Path allow‑lists (no `..`, no cross‑case moves).
  - Per‑plan operation limits and size checks.
  - Dry‑run validation with human‑readable summaries.
  - Optional approval step and explicit “Apply” call.
  - Audit logs and, in the best variants, an auto‑generated rollback script.
- **Straightforward to implement**: A small FastAPI app plus some file‑system logic and an HTTP client in the paralegal agent; no new external vendors and no major infra changes.
- **Extensible**: This pattern can later drive containerized or K8s jobs (plans become the contract), so it’s a good “spine” for any future architecture.

**Best concrete instantiation**  
- The implementation in **`sandbox-solution-6`** is the strongest single variant:
  - Very explicit FastAPI code for `ReorganizationPlan`, validation, execution, rollback, and health checks.
  - Thoughtful safety features (backups before delete, rollback script, per‑plan caps, audit JSON).
  - Clean agent tools (`submit_reorganization_plan`, `apply_plan`, `rollback_plan`) that align directly with your existing `execute_code` tooling.
- The **`sandbox-solution-1`** mutation service is also strong (adds approval and richer validation), but `solution-6` integrates more cleanly with your current paralegal agent patterns and emphasizes rollback.

**Recommendation**  
Implement this **first** as your primary path to safe mutation of the real `/projects` tree, keeping Runloop for read‑only analysis, internet work, and heavy compute. Treat plans (JSON) as the canonical contract between LLM and filesystem.

---

### 2. Scoped Mutable Containers on the Existing GCE VM (Docker / Dagger‑Style Executor)

**Concept (merged solution)**  
When a reorganization or tool run is needed, spin up a **short‑lived container on your existing GCE VM** that mounts the *real* case directory read‑write (e.g., `/mnt/workspace/projects/CaseXYZ:/case:rw`) and `/Tools` read‑only. The container then runs Python/bash (including your existing `Tools` scripts, Playwright, etc.), and exits; all changes persist because it is operating directly on the mounted GCS‑backed filesystem.

**Sources (functionally equivalent patterns)**
- `sandbox-solution-1.md`: **Solution 2 – Dagger‑Based Containerized Execution Pipeline** (uses Dagger SDK to orchestrate containers with `/mnt/workspace` mounted).
- `sandbox-solution-2.md`: **Proposal C – Scoped Mutable Containers (Per‑Case Docker Sessions)** (direct `docker run` with case‑folder bind mounts).
- `sandbox-solution-5.md`: **Parts of Solutions 1 & 2** (E2B / Modal examples also rely on running containers with mounted storage, conceptually similar once adapted to your VM).  
- `sandbox-solution-6.md`: **Solution 2 – Scoped Mutable Containers (Docker on GCE VM + mutator image)** (most detailed, with `roscoe-mutator` image, `mutation_executor.py`, and agent tools like `execute_case_mutation` and `reorganize_case_files`).

**Why this ranks #2**
- **Directly addresses “run my existing scripts on the real tree”**: You can call `/Tools/create_file_inventory.py` or any future reorg script against `/case` and have it mutate live case files.
- **Natural extension of current workflow**: It feels like an upgraded `execute_code` that runs on your own VM instead of Runloop, but still sandboxed per execution via containers.
- **Supports browser & internet use cases**: Containers can run Playwright, headless Chromium, ffmpeg, and perform HTTP requests, satisfying your AI‑paralegal requirements (web research, scraping, video analysis).
- **Good blast‑radius control**: By mounting only a specific case (and `/Tools` read‑only), mistakes are scoped; you can still stack this under the plan/approval layer from Solution #1 for extra safety.

**Trade‑offs**
- Requires Docker and a new “mutator” image on the VM, with appropriate security hardening.
- Slightly higher operational complexity and launch latency than the pure mutation‑service API.
- Needs careful resource limits and logging to avoid runaway jobs.

**Best concrete instantiation**
- **`sandbox-solution-6`** again has the most production‑ready variant:
  - A dedicated `roscoe-mutator` image with dependencies and non‑root user.
  - A `mutation_executor.py` module that sets up mounts, env vars, limits, and audit logs.
  - High‑level tools (`execute_case_mutation`, `reorganize_case_files`) that mesh with case‑centric workflows.
- `sandbox-solution-2`’s Proposal C is a simpler conceptual version of the same idea; `sandbox-solution-1`’s Dagger pipeline is the same pattern wrapped in Dagger.

**Recommendation**  
Layer this **after** the plan‑based mutation service, using it as an execution backend for *approved* plans or for more complex scripts (e.g., Playwright + file reorg) that are awkward to express as pure “move/copy/delete” JSON.

---

### 3. Background Worker / Queue‑Driven Plan Application

**Concept (merged solution)**  
Rather than applying plans synchronously from the agent, store them in a **queue or file‑based inbox** (e.g., `/Database/reorg_queue/*.json` or a Pub/Sub topic), and have a **background worker** on the VM (or in Modal) pull, validate, and execute them. Approvals can be Slack‑based or file‑status based, and operations are batched and throttled.

**Sources**
- `sandbox-solution-2.md`: **Proposal B – Queued Background Worker (Plan Files + Approval Queue)** (file‑based queue, systemd/cron worker, Slack `/roscoe-approve` flow).
- `sandbox-solution-5.md`: **Solution 2 – Modal with Background Worker Architecture** (Modal background workers consuming operation plans and applying them to GCS with audit logging).
- Elements of this pattern also dovetail naturally with the plan‑based services in `sandbox-solution-1`, `4`, and `6`.

**Why this ranks #3**
- **Operational robustness**: A queue decouples the agent from execution; large reorgs can be retried, paused, or rate‑limited without blocking user interactions.
- **Good human‑in‑the‑loop affordances**: “Plan generated → validation report → Slack approval → worker applies” aligns well with legal practice and risk tolerance.
- **Naturally extends Solution #1**: The same plan and validation schema can be reused; only the execution mode switches from “immediate API call” to “queued worker”.

**Trade‑offs**
- Higher complexity than a pure API: you have to manage queue state, retries, and monitoring.
- Adds latency between plan creation and application, which may or may not matter for your workflow.

**Recommendation**  
Treat this as a **Phase 2 enhancement** to the plan‑and‑apply mutation service: start with synchronous plan execution, then introduce a file/Pub‑Sub queue + worker once you’re comfortable with volumes and want more resilience and approval mechanics.

---

### 4. External AI‑Native Sandbox Providers (E2B, Modal) with GCS Mounts or GCS APIs

**Concept (merged solution)**  
Replace or augment Runloop with external, AI‑oriented sandbox services (e.g., **E2B**, **Modal**) that support:
- Custom images or templates,
- Persistent or long‑lived sessions,
- Mounting GCS buckets via `gcsfuse` or using GCS APIs directly,
- Built‑in support for Playwright and internet access.
Agents call provider APIs to run code that operates directly on `/projects` (via mounts or GCS client libraries).

**Sources**
- `sandbox-solution-3.md`: **Solution 1 – E2B (CodeSandbox for AI) with FUSE Mounts** (custom template that mounts your GCS buckets).
- `sandbox-solution-4.md`: **Solution 2 – AI‑Native Sandbox Provider (E2B)** (E2B with GCS mounts, as a complement to a GCP file worker).
- `sandbox-solution-5.md`: 
  - **Solution 1 – E2B + Persistent Storage Integration** (detailed E2B integration code and Dockerfile).
  - **Solution 2 – Modal with Background Worker Architecture** (Modal as both analysis and execution substrate).

**Why this ranks #4**
- **Technically powerful**: These providers are designed for agent workloads, with great support for persistent environments, headless browsers, and arbitrary Python tooling.
- **Can unify compute and mutation**: If a sandbox has `/projects` mounted, local file ops are immediately persisted to GCS; no separate mutation service is needed.
- **Good for experimentation**: Especially E2B/Modal can rapidly prototype complex flows without much ops burden on your side.

**Concerns / trade‑offs**
- **Data sensitivity & compliance**: Legal case data leaving your GCP perimeter for a third‑party sandbox is a significant risk; you’d need strong contractual and technical guarantees.
- **Vendor lock‑in and cost**: These introduce new billable services, with pricing and SLAs you don’t fully control.
- **Overlap with what you can already do on your own VM/GKE**: Given you already have a GCE VM and GCS, most benefits here can be reproduced in‑house (Solutions #1–3).

**Recommendation**  
Treat external sandbox providers as **optional extensions or prototyping environments**, not as your primary path for mutating `/projects`. For production legal workflows, prefer keeping all file operations inside GCP (Solutions #1–3).

---

### 5. GKE / gVisor‑Backed Sandbox Cluster with Persistent Volumes

**Concept (merged solution)**  
Spin up a **GKE cluster** where file‑mutating jobs run as Kubernetes Jobs or Pods:
- Pods use **GKE Sandbox (gVisor)** for strong isolation.
- `/workspace` or `/projects` is mounted via Cloud Storage FUSE, Filestore, or a GCE Persistent Disk.
- Agents submit jobs via a small “job orchestrator” service; job logs and outcomes are collected via Kubernetes APIs and Cloud Logging.

**Sources**
- `sandbox-solution-4.md`: **Solution 3 – GKE Sandbox with gVisor + Cloud Storage FUSE**.
- `sandbox-solution-5.md`: **Solution 3 – Hybrid Cloud‑Native Architecture (K8s + PV)**.
- `sandbox-solution-6.md`: **Solution 3 – GKE Agent Sandbox with Persistent Volumes** (comprehensive YAML + Python client); conceptually similar to `solution-4`/`5` variants.
- `sandbox-solution-3.md`: **Solution 2 – Self‑Hosted “Sandboxed Worker” on GCE with gVisor** (a single‑VM variant of the same isolation idea).

**Why this ranks #5 (still valid, but long‑term)**
- **Enterprise‑grade isolation and scale**: Great if you later need many concurrent jobs, multi‑tenant support, or formal compliance around sandboxing.
- **Rich control plane**: Kubernetes gives you RBAC, network policies, resource quotas, and sophisticated observability.
- **Reusable for many workloads**: Beyond file reorg, the same cluster can run research, summarization, and heavy analytics.

**Trade‑offs**
- **Substantial operational complexity**: Managing GKE, storage classes, PVs, job specs, and security policies is non‑trivial and probably overkill for a single‑firm MVP.
- **Higher cost and overhead**: Cluster costs, Filestore/PD storage, and engineering time.
- **You still need the “plan vs. raw commands” discipline**: gVisor does not replace the need for a plan/validation/approval layer.

**Recommendation**  
Keep this as a **future, scale‑out option** if/when Roscoe becomes a multi‑firm, multi‑tenant platform. When that time comes, you can lift‑and‑shift the **plan contract and mutation logic from Solution #1** into K8s Jobs.

---

## Overall Conclusion and Final Recommendation

- Across all six sandbox documents, there is strong convergence on one core idea: **separate “thinking in a sandbox” from “mutating the real filesystem,” and introduce a controlled, plan‑driven mutation layer that lives inside your GCP perimeter.**
- The **Plan‑and‑Apply Workspace Mutation Service on your existing GCE VM (Solution #1)**—as detailed most clearly in `sandbox-solution-6` and reinforced by `sandbox-solution-1`, `2`, `3`, and `4`—is the best near‑term design: it is safe, practical, tightly aligned with your current Roscoe codebase, and forms a solid foundation for later containerized or K8s execution.
- The **Scoped Mutable Container Executor (Solution #2)** is the best next layer for running rich tools (Playwright, heavy Python scripts) directly against `/projects`, ideally invoked by or under the control of the mutation service.
- External sandbox providers and full GKE/gVisor clusters are valuable ideas, but given your current environment and legal‑data sensitivity, they should be considered **optional or long‑term**, not the first thing you implement.


