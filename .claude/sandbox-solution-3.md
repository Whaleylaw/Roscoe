# Sandbox Solution Analysis: Enabling Direct File Operations and Enhanced Tooling

## Problem Overview
The current RunLoop sandbox architecture creates a disconnect between the execution environment and the persistent data store (`/projects` on GCS/GCE). While excellent for safe, isolated analysis, it prevents agents from performing essential "paralegal" tasks:
1.  **Direct File Manipulation:** Renaming, moving, or organizing files in the persistent workspace.
2.  **Complex Tooling:** Running browsers (Playwright), authenticated internet searches, or system-level installations that persist.
3.  **State Continuity:** Changes made in the sandbox are lost when the session ends.

## Proposed Solutions

Below are three distinct solutions to bridge this gap, ranging from a provider switch to an architectural redesign.

---

### Solution 1: E2B (CodeSandbox for AI) with FUSE Mounts
**Type:** *Alternative Provider*
**Best For:** Rapid implementation, native agent support, and strong browser/multimedia capabilities.

**Concept:**
Switch the execution backend from RunLoop to **E2B**. E2B is designed specifically for AI agents and supports long-running sessions, custom Dockerfiles, and root access, enabling the installation of tools like `gcsfuse`.

**Architecture:**
1.  **Custom Sandbox Template:** Create an E2B template (Dockerfile) that installs `gcsfuse` and the Google Cloud SDK.
2.  **Runtime Mounting:** When the agent starts a session, the sandbox startup script uses `gcsfuse` to mount your GCS `/projects` bucket to a local directory (e.g., `/mnt/projects`).
3.  **Direct Execution:** The agent writes Python/Bash scripts that operate on `/mnt/projects`. Changes are immediately reflected in your GCS bucket.

**Pros:**
*   **True Persistence:** The "filesystem" is the GCS bucket.
*   **Rich Tooling:** Native support for Playwright, ffmpeg, and other heavy dependencies.
*   **Security:** Code runs in a Firecracker microVM, isolated from your main infrastructure.

**Cons:**
*   **Latency:** FUSE operations over the network are slower than local disk (acceptable for file organization, slower for heavy I/O).
*   **Cost:** Additional subscription cost for E2B.

---

### Solution 2: Self-Hosted "Sandboxed Worker" on GCE (Docker + gVisor)
**Type:** *Alternative Architecture (Self-Hosted)*
**Best For:** Data gravity (keeping code close to data), cost efficiency, and maximum performance.

**Concept:**
Instead of sending code *out* to a 3rd party sandbox, bring the sandbox *to* your data. Host a code execution service on your existing Google Compute Engine (GCE) infrastructure, using **gVisor** (Google's container sandbox) to safely run untrusted agent code.

**Architecture:**
1.  **Worker VM:** A dedicated GCE VM (or your existing one) runs a Docker daemon configured with the `runsc` (gVisor) runtime.
2.  **Volume Mounting:** This VM has the `/projects` GCS bucket mounted locally (via GCS FUSE or NFS) at high speed.
3.  **Execution API:** A lightweight API (FastAPI) accepts code snippets from the agent.
4.  **Sandboxed Execution:** The API spins up a *fresh* Docker container for each task, mounting the local `/projects` path into the container. The container runs with `runtime=runsc` to prevent container escape.

**Pros:**
*   **Zero Latency:** Code runs right next to the data.
*   **Cost:** Uses existing GCE credits/infra; no third-party fees.
*   **Control:** You define the exact environment (OS, tools, network policies).

**Cons:**
*   **Maintenance:** You must manage the Docker/gVisor setup and security updates.
*   **Security:** Requires careful configuration to ensure the mounted volume cannot be maliciously wiped (though backups mitigate this).

---

### Solution 3: "Plan, Verify, Apply" Pattern (The Sidecar Approach)
**Type:** *Architectural Pattern*
**Best For:** Maximum safety, keeping the current RunLoop setup, and human-in-the-loop capability.

**Concept:**
De-couple "safe analysis" from "dangerous mutation." Keep using RunLoop for analysis and script generation, but introduce a privileged "Sidecar" service to apply changes.

**Architecture:**
1.  **Phase 1 (Sandbox):** The agent uses the current RunLoop sandbox to *read* files (copies) and generate a **Mutation Plan** (e.g., a JSON list of `{"op": "move", "src": "A", "dest": "B"}` or a verified Shell script).
2.  **Phase 2 (Verify):** The agent verifies the plan in the sandbox (simulating the moves).
3.  **Phase 3 (Apply):** The agent submits the finalized plan to a **Privileged Sidecar Tool**.
    *   This tool runs on your GCE VM (outside the sandbox) and has write access to the real `/projects` tree.
    *   It parses the plan and executes the operations (moves, renames, writes) securely.

**Pros:**
*   **Safety:** The sandbox *never* has write access. Malicious/buggy code can't accidentally wipe the drive; only valid "plans" are executed.
*   **Stability:** No need to mess with FUSE mounts inside ephemeral containers.
*   **Auditability:** Every "Apply" action is a distinct, loggable event.

**Cons:**
*   **Complexity:** Requires building the "Sidecar" API/tool.
*   **Indirect:** The agent can't "just run python"; it must "plan then apply," which adds a step to the cognitive loop.

## Recommendation

**Go with Solution 1 (E2B)** for the immediate "just make it work" experience. It aligns best with your goal of "running code freely" and supports the browser/internet requirements out of the box without managing infrastructure.

**Go with Solution 2 (Self-Hosted)** if you expect high-volume file processing (terabytes of legal discovery) where network latency would be a bottleneck.

