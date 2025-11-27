# Sandbox Solution Evaluation: Final Ranking and Recommendation

**Evaluated by:** Claude Opus 4.5  
**Date:** November 27, 2025  
**Documents Reviewed:** sandbox-solution-1.md through sandbox-solution-6.md

---

## Executive Summary

After reviewing all six proposed solutions for enabling direct file operations in the Roscoe paralegal agent, I have identified **8 distinct architectural patterns** across the documents. Several solutions are **functionally equivalent** despite different naming. My recommendation is a **phased approach** starting with **Solution Pattern A (Plan & Apply Mutation Service)** for immediate deployment, with optional progression to Pattern B (Docker Containers) for full capabilities.

---

## Problem Recap

The RunLoop sandbox operates on an **ephemeral copy-and-execute model**:
- Files are uploaded as copies to sandbox containers
- Code executes in isolation
- **Changes are discarded** when the container exits
- No mechanism to write changes back to the persistent `/projects/` tree

This prevents the agent from performing file reorganization, transformations, and modifications that are core to the paralegal workflow.

---

## Solution Categories Identified

After analysis, the 6 documents propose solutions that fall into **8 distinct architectural patterns**:

| Pattern | Description | Appears In |
|---------|-------------|------------|
| **A** | Plan & Apply Mutation Service (FastAPI) | Solutions 1, 2, 3, 4, 6 |
| **B** | Per-Case Docker Containers | Solutions 2, 6 |
| **C** | E2B Provider with GCS FUSE | Solutions 3, 4, 5 |
| **D** | GKE/Kubernetes with gVisor | Solutions 3, 4, 5, 6 |
| **E** | Dagger Pipelines | Solution 1 only |
| **F** | Queued Background Worker | Solution 2 only |
| **G** | Hybrid RunLoop + Privileged Executor | Solution 1 only |
| **H** | Modal Serverless | Solution 5 only |

---

## Consolidated Rankings

### 🥇 Rank 1: Pattern A — Plan & Apply Mutation Service

**Source Solutions:** 1 (VM-Native Mutation Service), 2 (Proposal A), 3 (Plan-Verify-Apply Sidecar), 4 (GCP-Native File Ops Worker), 6 (Workspace Mutation Service)

**Core Concept:** Deploy a FastAPI service on the GCE VM that:
1. Accepts JSON plans describing file operations
2. Validates plans (path safety, existence checks, size limits)
3. Executes operations with full audit logging
4. Generates rollback scripts automatically

**Why Rank 1:**
- ✅ **Fastest implementation** (1-2 weeks)
- ✅ **Lowest complexity** — single service to deploy and maintain
- ✅ **Uses existing infrastructure** — leverages current gcsfuse mount
- ✅ **Strongest safety model** — LLM proposes plans, human-written validator executes
- ✅ **Complete audit trail** — every operation logged with actor, timestamp, reason
- ✅ **Built-in rollback** — auto-generated scripts for recovery
- ✅ **No per-operation container overhead** — direct filesystem access

**Limitations:**
- ❌ Does not directly support Playwright/browser automation (continue using RunLoop for that)
- ❌ Cannot run arbitrary Python scripts (only structured file operations)

**Best Implementation:** Solution 6 provides the most complete, production-ready code including:
- Full FastAPI implementation with Pydantic models
- Safety validation with path traversal protection
- Rollback script generation
- systemd service configuration
- Agent tool integration (`submit_reorganization_plan`, `apply_plan`, `rollback_plan`)

**Estimated Cost:** $0 additional infrastructure cost  
**Implementation Time:** 1-2 weeks

---

### 🥈 Rank 2: Pattern B — Per-Case Docker Containers

**Source Solutions:** 2 (Proposal C), 6 (Scoped Mutable Containers)

**Core Concept:** When mutation is requested, spin up a short-lived Docker container with:
- The specific case folder mounted read-write (`-v /projects/Case:/case:rw`)
- Tools directory mounted read-only (`-v /Tools:/tools:ro`)
- Full Python/bash execution environment

**Why Rank 2:**
- ✅ **Reuses existing scripts** — run `/Tools/create_file_inventory.py` directly
- ✅ **Full Playwright support** — install browsers in container image
- ✅ **Internet access** — container can make HTTP requests
- ✅ **Isolated execution** — each operation in fresh container
- ✅ **Resource limits** — CPU/memory constraints prevent runaway processes

**Limitations:**
- ⚠️ Container spin-up overhead (2-5 seconds per operation)
- ⚠️ No built-in approval workflow (combine with Pattern A for human review)
- ⚠️ Requires Docker on VM with appropriate permissions

**Best Implementation:** Solution 6 provides complete Docker executor with:
- Mutator Dockerfile with Playwright pre-installed
- Python execution module with audit logging
- `execute_case_mutation()` and `reorganize_case_files()` tools

**Estimated Cost:** $0-50/month additional (minimal compute overhead)  
**Implementation Time:** 2-3 weeks

---

### 🥉 Rank 3: Pattern E — Dagger Pipelines

**Source Solutions:** Solution 1 only

**Core Concept:** Use Dagger (CI/CD pipeline as code) to orchestrate containerized execution with:
- Volume mounting to gcsfuse filesystem
- Reproducible, portable execution
- Programmable pipelines as Python code

**Why Rank 3:**
- ✅ **Reproducible** — same container environment every time
- ✅ **Portable** — works on any Docker host (VM, local, cloud)
- ✅ **Developer-friendly** — define execution as code, easy testing
- ✅ **Good caching** — speeds up repeated operations

**Limitations:**
- ⚠️ Newer technology, less familiar to most teams
- ⚠️ Learning curve for Dagger SDK
- ⚠️ Less community support than pure Docker

**Best Implementation:** Solution 1 provides complete Dagger module with:
- `execute_file_reorganization()` function
- `run_browser_automation()` function
- FastAPI service wrapper

**Estimated Cost:** $0 additional  
**Implementation Time:** 3-5 days

---

### Rank 4: Pattern G — Hybrid RunLoop + Privileged Executor

**Source Solutions:** Solution 1 only

**Core Concept:** Keep RunLoop sandbox for read-only operations, add intelligent routing:
- Operation classifier detects mutations vs. read-only
- Read-only → RunLoop sandbox (safe, isolated)
- Mutations → Privileged VM executor (requires approval)

**Why Rank 4:**
- ✅ **Best of both worlds** — safety of sandbox + power of direct access
- ✅ **Backward compatible** — existing tools continue to work
- ✅ **Automatic escalation** — smart classification of operations
- ✅ **Explicit approval** — user controls dangerous operations

**Limitations:**
- ⚠️ More moving parts to maintain
- ⚠️ Classification accuracy may miss edge cases
- ⚠️ SSH dependency between components

**Estimated Cost:** $0 additional  
**Implementation Time:** 5-7 days

---

### Rank 5: Pattern D — GKE/Kubernetes with gVisor

**Source Solutions:** 3 (Self-Hosted gVisor), 4 (GKE Sandbox), 5 (Hybrid Cloud-Native), 6 (GKE Agent Sandbox)

**Core Concept:** Deploy GKE cluster with Agent Sandbox (gVisor) enabled:
- Persistent Volume Claims backed by Filestore or GCS FUSE
- gVisor kernel-level isolation for maximum security
- Kubernetes Jobs for execution

**Why Rank 5:**
- ✅ **Enterprise-grade security** — strongest isolation (gVisor syscall filtering)
- ✅ **Highly scalable** — Kubernetes auto-scaling, multi-agent concurrent execution
- ✅ **Multi-tenancy** — namespace isolation for different workloads
- ✅ **Full audit trail** — Kubernetes events, pod logs, custom logging

**Limitations:**
- ❌ **Highest complexity** — requires Kubernetes expertise
- ❌ **Longest implementation** (4-8 weeks)
- ❌ **Highest cost** ($300-500/month for GKE cluster)
- ❌ **Operational overhead** — cluster management, upgrades, monitoring

**Best For:** Enterprise deployments, multi-firm SaaS, compliance-heavy environments

**Estimated Cost:** $300-500/month  
**Implementation Time:** 4-8 weeks

---

### Rank 6: Pattern C — E2B Provider with GCS FUSE

**Source Solutions:** 3 (E2B with FUSE), 4 (AI-Native Sandbox Provider), 5 (E2B Persistent Storage)

**Core Concept:** Switch from RunLoop to E2B (CodeSandbox for AI):
- Custom sandbox template with gcsfuse pre-installed
- Mount GCS buckets directly into sandbox
- Persistent or long-lived sessions

**Why Rank 6:**
- ✅ **Simplest conceptually** — closest to existing RunLoop workflow
- ✅ **Purpose-built for AI agents** — designed for this use case
- ✅ **Full Playwright support** — native browser automation
- ✅ **Familiar dev environment** — feels like VS Code dev container

**Limitations:**
- ❌ **Third-party dependency** — data leaves your infrastructure
- ❌ **Security/compliance concerns** — case files accessible to E2B
- ❌ **Additional cost** — E2B subscription fees
- ❌ **Network latency** — FUSE operations over network slower than local

**Best For:** Rapid prototyping, teams without infrastructure expertise

**Estimated Cost:** $50-200/month (E2B subscription)  
**Implementation Time:** 2-4 weeks

---

### Rank 7: Pattern H — Modal Serverless

**Source Solutions:** Solution 5 only

**Core Concept:** Use Modal for serverless container execution:
- Ephemeral functions for analysis
- Background workers for file operations
- Persistent volumes for workspace access

**Why Rank 7:**
- ✅ **Serverless benefits** — auto-scaling, pay-per-use
- ✅ **Separation of concerns** — analysis vs. execution isolation
- ✅ **Cost-effective** — pay only for execution time

**Limitations:**
- ❌ **Another third-party** — data leaves your infrastructure
- ❌ **Complex queue management** — coordinating between functions
- ❌ **Background processing latency** — not real-time

**Estimated Cost:** Variable (pay-per-use)  
**Implementation Time:** 2-3 weeks

---

### Rank 8: Pattern F — Queued Background Worker

**Source Solutions:** Solution 2 (Proposal B) only

**Core Concept:** File-based queue with background worker:
- Plans saved as JSON files to `/Database/reorg_queue/`
- Worker polls queue, validates, waits for approval
- Approval via Slack command or status file toggle

**Why Rank 8:**
- ✅ **Simplest architecture** — file-based, easy to debug
- ✅ **No long-running API** — reduces surface area
- ✅ **Can batch changes** — efficient for large reorganizations

**Limitations:**
- ❌ **Higher latency** — worker polling interval
- ❌ **Limited approval UX** — editing files or Slack commands
- ❌ **Harder to monitor** — no API for queue status
- ❌ **Concurrency issues** — multiple plans touching same case

**Estimated Cost:** $0 additional  
**Implementation Time:** 2-3 weeks

---

## Comparison Matrix

| Criterion | Pattern A | Pattern B | Pattern E | Pattern D | Pattern C | Pattern H | Pattern F |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| **Implementation Time** | 1-2 wks | 2-3 wks | 3-5 days | 4-8 wks | 2-4 wks | 2-3 wks | 2-3 wks |
| **Complexity** | Low | Medium | Medium | High | Low | Medium | Low |
| **Cost** | $0 | $0-50/mo | $0 | $300-500/mo | $50-200/mo | Variable | $0 |
| **Security** | High | Medium | Medium | Very High | Medium | Medium | Medium |
| **Scalability** | Medium | Medium | Medium | Very High | High | High | Low |
| **Data Stays In-House** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Browser/Playwright** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Run Existing Scripts** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Human Approval Flow** | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ |
| **Rollback Support** | ✅ Auto | ⚠️ Manual | ⚠️ Manual | ⚠️ Snapshots | ⚠️ Manual | ⚠️ Manual | ✅ Auto |
| **Uses Existing Infra** | ✅ | ✅ | ✅ | ⚠️ New GKE | ❌ New Provider | ❌ New Provider | ✅ |

---

## Final Recommendation

### Immediate Implementation (Next 2 Weeks)

**Deploy Pattern A (Plan & Apply Mutation Service)** using the implementation from **Solution 6**.

This provides:
- Safe, audited file operations on the real `/projects/` tree
- No new infrastructure or third-party dependencies
- Complete rollback capability
- Clear separation: LLM proposes plans → service validates → service executes

Combine with existing RunLoop sandbox for:
- Internet searches (Tavily)
- Read-only code analysis
- Capabilities that don't need filesystem mutations

### Phase 2 (Weeks 3-4, Optional)

If you need **full script execution and browser automation**, add **Pattern B (Docker Containers)**:
- Build `roscoe-mutator` Docker image with Playwright
- Add `execute_case_mutation()` tool
- Run existing `/Tools/` scripts directly on case folders

### Future Enterprise Track (If Needed)

For multi-firm SaaS, compliance requirements, or 10x scale:
- Migrate to **Pattern D (GKE with gVisor)**
- Leverage Kubernetes auto-scaling and security policies
- Use Filestore PVCs for shared workspace access

---

## Implementation Roadmap

```
Week 1-2: Pattern A (Mutation Service)
├── Day 1-2: Deploy FastAPI mutation service on GCE VM
├── Day 3-4: Add agent tools (submit_reorganization_plan, apply_plan)
├── Day 5-7: Test with sample case reorganizations
└── Week 2: Add monitoring, alerts, documentation

Week 3-4: Pattern B (Docker, optional)
├── Day 1-2: Build roscoe-mutator Docker image
├── Day 3-4: Add execute_case_mutation() tool
├── Day 5-7: Test full workflows with Playwright
└── Week 4: Production deployment

Month 2-3: Pattern D (GKE, if needed)
├── Set up GKE cluster with Agent Sandbox
├── Configure Filestore PVC
├── Deploy job templates
└── Migrate agent tools to K8s executor
```

---

## Solution Document Quality Assessment

| Document | Comprehensiveness | Code Quality | Practicality | Unique Value |
|----------|-------------------|--------------|--------------|--------------|
| **Solution 1** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Dagger, Hybrid patterns |
| **Solution 2** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | Queued worker pattern |
| **Solution 3** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | E2B focus |
| **Solution 4** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | GCP-native focus |
| **Solution 5** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Modal pattern |
| **Solution 6** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Most complete implementation |

**Best Overall Document:** Solution 6 — most production-ready code, clearest architecture diagrams, comprehensive implementation details

**Most Creative:** Solution 1 — unique Dagger and Hybrid patterns not seen elsewhere

**Most Concise:** Solution 2 — efficient summary of three distinct approaches

---

## Appendix: Which Solutions Are Functionally Equivalent

### Group 1: Plan & Apply Mutation Service
These all propose the same core architecture with minor variations:
- **Solution 1** (VM-Native Workspace Mutation Service)
- **Solution 2** (Proposal A – Workspace Mutation Service)
- **Solution 3** (Plan, Verify, Apply Pattern)
- **Solution 4** (GCP-Native File Operations Worker)
- **Solution 6** (Workspace Mutation Service)

**Key Differences:**
- Solution 1 & 6 provide the most complete code
- Solution 2 is the most concise description
- Solution 3 emphasizes the "sidecar" terminology
- Solution 4 mentions Cloud Run as alternative to GCE service

### Group 2: Per-Case Docker Containers
- **Solution 2** (Proposal C – Scoped Mutable Containers)
- **Solution 6** (Scoped Mutable Containers)

**Key Differences:**
- Solution 6 provides complete Docker executor code
- Solution 2 provides conceptual overview

### Group 3: E2B Provider
- **Solution 3** (E2B with FUSE Mounts)
- **Solution 4** (AI-Native Sandbox Provider / E2B)
- **Solution 5** (E2B with Persistent Storage Integration)

**Key Differences:**
- All essentially the same approach
- Solution 5 provides most detailed E2B implementation

### Group 4: GKE/Kubernetes
- **Solution 3** (Self-Hosted gVisor)
- **Solution 4** (GKE Sandbox with gVisor)
- **Solution 5** (Hybrid Cloud-Native / K8s)
- **Solution 6** (GKE Agent Sandbox)

**Key Differences:**
- Solution 6 provides most complete K8s manifests and Python client
- Solution 4 emphasizes GKE Autopilot
- Solution 3 is more conceptual

---

## Conclusion

**Start with Pattern A (Plan & Apply Mutation Service)** — it's the fastest path to production with the strongest safety guarantees. The implementation from Solution 6 is production-ready and can be deployed within 1-2 weeks on your existing GCE VM + GCS infrastructure.

This approach maintains the principle that the LLM proposes structured plans, but a human-written validator controls execution. Combined with automatic rollback scripts and complete audit logging, this provides enterprise-grade safety for legal document management.

For full script execution and browser automation, add Pattern B (Docker Containers) in Phase 2. Reserve Pattern D (GKE) for future enterprise scaling needs.

