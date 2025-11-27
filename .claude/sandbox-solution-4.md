## Sandbox Solution Analysis (GPT-5.1): Enabling Real File Operations

### Executive Summary

The current `execute_code` tool uses Runloop devboxes to run arbitrary code in an **ephemeral, copy-only sandbox**. This is excellent for analysis, internet access, and heavy computation, but it **cannot safely mutate the real `/projects` tree** in your GCS-backed workspace. Below are **three concrete solution patterns** that fit your Google Cloud Storage + GCE VM setup and give agents a way to perform real file operations, browser automation (Playwright), and internet access:

- **Solution 1 – GCP‑native File Operations Worker (preferred short‑term)**: Keep Runloop for generic compute, but introduce a small, privileged GCP service (Cloud Run or a daemon on your GCE VM) that consumes **file‑operation plans** from the agents and applies them directly to `/projects` via GCS APIs or `gcsfuse`.
- **Solution 2 – Replace Runloop with an AI‑native sandbox provider (e.g., E2B) + GCS mounts**: Move code execution to a provider that supports **persistent sandboxes and custom images**, and mount your GCS buckets inside those sandboxes so agents can operate directly on `/projects`.
- **Solution 3 – GKE Sandbox with gVisor + Cloud Storage FUSE (long‑term, enterprise)**: Run file‑mutating jobs as Kubernetes Jobs/Pods in GKE, isolated with **gVisor sandboxing**, and mount `/projects` via Cloud Storage FUSE or GCE persistent disks for full control and observability.

Each approach separates **“LLM thinking + planning”** from **“privileged file mutation”**, with explicit safety rails (plan validation, audit logs, and limited identities/permissions).

---

### Current Constraint Recap (from Codebase and Problem Statement)

- Paralegal agent uses a `FilesystemBackend` with `virtual_mode=True`, but **actual code execution** is delegated to Runloop via `execute_code` in `src/roscoe/agents/paralegal/tools.py`.
- `execute_code`:
  - Creates a fresh Runloop devbox using a blueprint (`RUNLOOP_BLUEPRINT_ID`).
  - Optionally uploads **input files** from `workspace_paralegal` into the sandbox.
  - Runs a shell command there and returns stdout/stderr, then shuts the devbox down.
  - The sandbox **only sees uploaded copies** of `/Tools/...` and `/projects/...`; there is **no write‑back** to your real GCS/GCE filesystem.
- You can:
  - Read `/projects`, `/Database`, `/Tools` via read-only tools.
  - Generate reports and reorg maps and save them to the workspace.
- You cannot:
  - Have the agent directly move/rename/create/delete files under the real `/projects/...` tree.
  - Round‑trip changes from the Runloop sandbox back into GCS automatically.

The core design change needed: **introduce a controlled, privileged component that lives “next to” the real filesystem**, and have the LLM send it **plans**, not raw shell access.

---

### Solution 1 – GCP‑Native File Operations Worker (Cloud Run / GCE Daemon)

**Concept**  
Keep Runloop devboxes for general sandboxed compute, but introduce a **dedicated “file operations worker” service** running **inside your trust boundary** (same VPC / same VM / Cloud Run connected to your GCS project). Agents never directly shell into this worker; instead they:

1. Analyze the existing structure (read‑only).
2. Generate a **structured reorganization plan** (JSON).
3. Submit the plan to the worker via a **high‑level tool**.
4. The worker validates the plan and uses **GCS APIs or a mounted filesystem** to apply changes to `/projects`.

#### High‑Level Architecture

- **Roscoe agents (LangGraph / DeepAgents)**  
  - Continue using `execute_code` (Runloop) for arbitrary compute/internet/Playwright when needed.  
  - Add a new tool, e.g. `submit_file_ops_plan(plan: dict) -> status`, that sends JSON to a backend API.

- **File Operations Worker (new component)**  
  - Runs as:
    - A small **Flask/FastAPI** service on your existing GCE VM, or
    - A **Cloud Run** service with access to your GCS buckets and/or a GCE persistent disk.
  - Responsibilities:
    - Validate each operation in the plan (allowed paths, no `../`, size limits, dry‑run mode).
    - Execute file operations:
      - Either via **GCS JSON API** (rename = copy + delete),
      - Or via **`gcsfuse`‑mounted** filesystem if the VM mounts the bucket as `/projects`.
    - Emit **audit logs** (to a GCS bucket, BigQuery, or Cloud Logging).

- **Queue / Idempotency (optional but recommended)**  
  - Store each plan in a **GCS object** or **Pub/Sub message** with an ID.
  - Worker processes plans from the queue to support retries and back‑pressure.

#### Example Plan Shape

```json
{
  "case_name": "Abby-Sitgraves-MVA-07-13-2024",
  "dry_run": true,
  "operations": [
    {
      "type": "move",
      "from": "Abby-Sitgraves-MVA-07-13-2024/uncategorized/file1.pdf",
      "to": "Abby-Sitgraves-MVA-07-13-2024/Medical Records/file1.pdf"
    },
    {
      "type": "mkdir",
      "path": "Abby-Sitgraves-MVA-07-13-2024/Investigation/photos"
    }
  ]
}
```

The agent produces this plan after analyzing `/projects/...` via read‑only tools.

#### Implementation Sketch

- **Backend API (on GCE or Cloud Run)**:
  - Endpoint: `POST /file-ops/plans`
  - Steps:
    1. Validate JSON against a strict schema.
    2. Check each path is under allowed prefixes (e.g., `projects/{case}/` only).
    3. If `dry_run: true`, compute and return a **diff** without mutating anything.
    4. If `dry_run: false`, apply operations:
       - For GCS:
         - `move`: `storage.Blob.rewrite()` then `source_blob.delete()`.
         - `mkdir`: create a placeholder object (or rely on implicit directories).
       - For `gcsfuse` mount:
         - Use standard `os.rename`, `os.makedirs`, etc.
    5. Log each operation (who, when, from, to, result) to an **audit bucket**.

- **Agent Tool Integration**:
  - Add a tool (e.g., `apply_reorg_plan(plan_json: str, dry_run: bool)`):
    - Constructs the above JSON from its internal plan.
    - Calls the backend API over HTTPS (using an internal service account).
    - Returns the worker’s summary back to the user.

#### Pros

- **Direct, real mutations** of `/projects` with no manual SSH or downloads.
- Stays entirely inside your **GCP trust boundary**; no third‑party sandbox needs write access to GCS.
- Very **incremental**: you can add this without disturbing existing Runloop usage.
- Strong safety model: LLM only proposes **plans**; a human‑written validator actually executes them.

#### Cons / Trade‑offs

- Requires you to build and operate a small API service (or daemon) and possibly a queue.
- Validation logic must be carefully tested to avoid dangerous operations (e.g., deleting entire `projects/`).

---

### Solution 2 – AI‑Native Sandbox Provider with Persistent Environments (E2B or Similar)

**Concept**  
Replace (or augment) Runloop with a provider that offers **persistent, customizable sandboxes** designed for AI agents (e.g., E2B). You build a custom sandbox image that:

- Mounts your GCS buckets (`/projects`, `/Tools`, `/Database`) via `gcsfuse` or the Cloud Storage FUSE driver.
- Pre‑installs Python, Playwright, Chrome/Chromium, and any analysis tools.
- Exposes an API for “run this command in sandbox X” that you wrap as a LangGraph/DeepAgents tool.

Agents then get **direct filesystem semantics** for `/projects` inside the sandbox while still being isolated from your main VM.

#### High‑Level Architecture

- **Roscoe agent** calls `execute_code_e2b(...)` instead of (or in addition to) `execute_code` with Runloop.
- **E2B sandbox**:
  - Persistent or long‑lived dev environment per user or per session.
  - Custom Dockerfile that:
    - Installs `gcsfuse` and configures service account credentials.
    - Mounts:
      - `whaley-law-firm-projects` → `/projects`
      - `whaley-law-firm-tools` → `/Tools`
      - `whaley-law-firm-database` → `/Database`
  - Runs commands on behalf of the agent (Python scripts, shell, Playwright).

#### Capabilities

- **Real file mutations**: renames, moves, deletes within `/projects` are operations on the actual GCS bucket.
- **Internet access**: the sandbox can reach external APIs and websites as needed.
- **Browser automation**: full Playwright flows (including headless Chrome) for web workflows.

#### Implementation Sketch

- **Custom sandbox image**:
  - Start from provider’s base image.
  - Install:
    - `gcsfuse` (or Cloud Storage FUSE).
    - `python3`, `pip`, `playwright`, `google-cloud-storage`.
  - Mount GCS buckets at container start using a service account with **restricted** permissions (only the buckets you need).

- **Agent tool wrapper**:
  - New tool `execute_code_e2b(command: str, working_dir: str = "/projects", timeout: int = 300)`:
    - Creates or reuses a persistent sandbox (`session_id`).
    - Executes the command in that sandbox.
    - Returns stdout/stderr and optionally file diffs (e.g., via `git status` or a custom watcher).

- **Migration from Runloop**:
  - Keep Runloop for quick, ephemeral jobs if desired.
  - Use E2B‑style sandboxes when you explicitly need:
    - Direct `/projects` access.
    - Long‑running environments (e.g., repeated Playwright runs).

#### Pros

- Purpose‑built for AI: providers like E2B focus on **AI agent sandboxes** (ephemeral or persistent).
- You get a **familiar dev environment**: it feels like a remote VS Code dev container with your buckets mounted.
- Simplifies Workflows: the agent often just needs to run `python /Tools/create_file_inventory.py /projects/...`.

#### Cons / Trade‑offs

- Introduces a **new third‑party** with access to your case files (even if encrypted/in a limited scope); may require additional legal/security review.
- You still need to design guardrails:
  - Path allow‑lists.
  - “Dry‑run” modes for dangerous operations.
  - Possibly an approval workflow for large batch reorganizations.

---

### Solution 3 – GKE Sandbox with gVisor + Cloud Storage FUSE (Enterprise Track)

**Concept**  
For a more “cloud‑native” and highly controlled environment, move file‑mutating code execution into **Google Kubernetes Engine (GKE)** with:

- **gVisor‑based sandbox pods** (GKE Sandbox) for strong kernel isolation.
- **Cloud Storage FUSE** or GCE persistent disks mounted into the pods, exposing `/projects` and `/Tools`.
- A simple **job submission API** that the agents call to run reorganization/processing jobs as Kubernetes Jobs.

This is similar in spirit to the Kubernetes‑based solution in the Grok analysis, but explicitly leverages **GKE Sandbox (gVisor)** as the isolation layer and is tailored to your GCS bucket workspace.

#### High‑Level Architecture

- **Roscoe agent**:
  - Still runs wherever you prefer (current GCE VM).
  - Adds a tool `submit_k8s_job(plan_or_command)` that calls a small “job orchestrator” API.

- **Job Orchestrator (small service in cluster)**:
  - Accepts a JSON plan or a high‑level command (e.g., “run `reorganize_case.py` on case X”).
  - Creates a **Kubernetes Job** with:
    - A container image that:
      - Mounts `/projects` via Cloud Storage FUSE or a PV.
      - Includes your `Tools` scripts and dependencies.
    - Pod configuration that uses **gVisor** runtime for sandboxing.
  - Watches job status and exposes logs/results via the API.

- **Kubernetes Jobs**:
  - One job per reorg batch or per case.
  - Can operate directly on `/projects/{case}` at scale.
  - Emit structured logs to Cloud Logging and audits to BigQuery or GCS.

#### Why gVisor Matters

- **Stronger isolation**: gVisor intercepts syscalls in user space, limiting the blast radius if a script is compromised.
- Designed and maintained by Google; integrates cleanly with GKE via **GKE Sandbox**.
- Lets you safely run more powerful tools (e.g., headless browsers, complex Python stacks) closer to your data.

#### Pros

- **Enterprise‑grade control**: RBAC, NetworkPolicies, PodSecurity, audit logging, backups.
- Horizontal scalability: run dozens of reorg jobs in parallel without overloading a single VM.
- Clear separation of concerns:
  - Roscoe agents remain stateless orchestrators.
  - Cluster is the execution substrate.

#### Cons / Trade‑offs

- Higher **operational complexity**: you must manage a GKE cluster, deployments, job specs, and monitoring.
- Requires containerization of your tools and some Kubernetes expertise.

---

### Comparative Overview

| Criterion | Solution 1 – GCP File Ops Worker | Solution 2 – AI Sandbox Provider | Solution 3 – GKE + gVisor |
|----------|----------------------------------|----------------------------------|---------------------------|
| **Time to implement** | **Short** (days–1 week) | Medium | Long |
| **Infra complexity** | Low–Medium | Medium | High |
| **Keeps data in GCP only** | Yes | No (third‑party access) | Yes |
| **Direct `/projects` mutations** | Yes | Yes | Yes |
| **Internet / Playwright support** | Via worker container | Full in sandbox | Full in pods |
| **Security isolation strength** | Good (container/user separation) | Good (provider dependent) | Very strong (gVisor + K8s) |
| **Best use case** | Near‑term, pragmatic fix | Flexible agent sandboxes | Enterprise, multi‑tenant scale |

---

### Recommendations

- **Short‑term (most practical next step)**: Implement **Solution 1 (GCP‑native File Operations Worker)**. It gives you safe, programmatic restructuring of the real `/projects` tree without tearing out Runloop or changing your agent architecture.
- **If you want richer, long‑lived sandboxes for agents** (not just batch file ops): experiment with **Solution 2** using an E2B‑style provider, but treat it as an extension, not a replacement, until security and cost are fully vetted.
- **For a future, highly scalable platform** that might support multiple firms or workloads, plan towards **Solution 3 (GKE + gVisor)** as your long‑term execution substrate, reusing the same “plan‑based file operations” pattern you establish in Solution 1.


