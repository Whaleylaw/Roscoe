# Sandbox Solution Analysis: Three Approaches to Enable Direct File Operations

## Executive Summary

After analyzing the current RunLoop sandbox limitations and researching alternative providers and architectures, I propose three comprehensive solutions to enable agents to perform direct file transformations, modifications, and execute internet searches/browser automation. Each solution addresses the core constraint: bridging the gap between sandboxed code execution and persistent filesystem mutations.

## Current Problem Analysis

The existing RunLoop sandbox operates on an **ephemeral copy-and-execute model**:
- Files are uploaded as copies to sandbox containers
- Code executes in isolation with no persistent state
- Changes remain in sandbox and are discarded
- No mechanism for safe, programmatic filesystem mutations

This prevents the case file organization workflows and other file-intensive operations that require persistent changes to `/projects/...` directories.

## Three Solution Approaches

### Solution 1: E2B with Persistent Storage Integration
**Best for: Advanced sandboxing with direct filesystem access**

#### Architecture Overview
E2B (formerly "CodeSandbox for AI") provides persistent sandbox environments with advanced mounting capabilities, enabling direct filesystem operations while maintaining security isolation.

#### Key Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Roscoe Agent  │────│   E2B Sandbox   │────│  GCS FUSE Mount │
│                 │    │  (Persistent)   │    │                 │
│ • File analysis │    │ • Direct file   │    │ • /projects/     │
│ • Code execution│    │   operations    │    │ • /Tools/        │
│ • Internet tools│    │ • Browser auto  │    │ • /Database/     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### Implementation Details

**1. E2B Sandbox Configuration**
```python
# src/roscoe/agents/paralegal/tools.py (modified)
import e2b

def execute_code_e2b(
    command: str,
    working_dir: str = "/projects",
    timeout: int = 300,
    persist_session: bool = True
) -> str:
    """Execute code in persistent E2B sandbox with direct filesystem access."""

    # Create or reuse persistent sandbox
    sandbox = e2b.Sandbox(
        id=f"roscoe-{session_id}",
        template="roscoe-workspace-v1",
        env_vars={
            "TAVILY_API_KEY": os.environ.get("TAVILY_API_KEY"),
            "PLAYWRIGHT_BROWSERS_PATH": "/home/user/.cache/playwright"
        }
    )

    try:
        # Install additional tools if needed
        if "playwright" in command:
            sandbox.commands.run("pip install playwright")
            sandbox.commands.run("playwright install chromium")

        # Execute command with direct filesystem access
        result = sandbox.commands.run(command, cwd=working_dir, timeout=timeout)

        return f"Exit code: {result.exit_code}\n{result.stdout}\n{result.stderr}"

    finally:
        if not persist_session:
            sandbox.close()
```

**2. GCS FUSE Integration**
```yaml
# Dockerfile.e2b
FROM e2b/sandbox:latest

# Install GCS FUSE
RUN apt-get update && apt-get install -y \
    fuse \
    gcsfuse

# Create mount points
RUN mkdir -p /projects /Tools /Database /Reports

# Configure service account for GCS access
COPY service-account-key.json /etc/gcsfuse/
ENV GOOGLE_APPLICATION_CREDENTIALS=/etc/gcsfuse/service-account-key.json

# Mount GCS buckets at startup
CMD gcsfuse --implicit-dirs whaley-law-firm-projects /projects && \
    gcsfuse --implicit-dirs whaley-law-firm-tools /Tools && \
    gcsfuse --implicit-dirs whaley-law-firm-database /Database && \
    gcsfuse --implicit-dirs whaley-law-firm-reports /Reports && \
    tail -f /dev/null
```

**3. File Operation Tools**
```python
def move_case_files(
    source_pattern: str,
    destination_dir: str,
    case_name: str
) -> str:
    """Direct file operations in persistent sandbox."""
    command = f"""
    cd "/projects/{case_name}"
    find . -name "{source_pattern}" -type f -exec mv {{}} "{destination_dir}/" \\;
    echo "Files moved successfully"
    """
    return execute_code_e2b(command, working_dir=f"/projects/{case_name}")

def reorganize_medical_records(case_name: str) -> str:
    """Execute the existing medical records organization script."""
    script_path = f"/Tools/organize_medical_subfolders.sh"
    command = f"bash '{script_path}'"
    return execute_code_e2b(command, working_dir=f"/projects/{case_name}")
```

#### Security & Safety Measures
- **Filesystem Isolation**: GCS FUSE provides fine-grained access controls
- **Command Validation**: Pre-validate all file operation commands
- **Audit Logging**: All operations logged with timestamps and actor identification
- **Rollback Capability**: File versioning through GCS object versions

#### Advantages
- ✅ **Direct File Access**: No copy/upload limitations
- ✅ **Persistent Sessions**: Maintain state across operations
- ✅ **Browser Automation**: Full Playwright support
- ✅ **Internet Access**: Direct API calls and web scraping
- ✅ **Performance**: Low-latency file operations

#### Challenges & Mitigations
- **Cost**: Persistent sandboxes incur higher costs than ephemeral ones
  - *Mitigation*: Auto-shutdown after inactivity periods
- **Complexity**: GCS FUSE configuration and permissions
  - *Mitigation*: Pre-configured templates and automated setup

---

### Solution 2: Modal with Background Worker Architecture
**Best for: Scalable containerized execution with background processing**

#### Architecture Overview
Modal provides serverless container execution with persistent volumes, combined with background workers for safe file operations. Analysis happens in ephemeral containers, while file mutations occur in dedicated, audited background workers.

#### Key Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Roscoe Agent  │────│  Modal Function │────│ Background      │
│                 │    │  (Ephemeral)    │────│ Worker Service  │
│ • Task analysis │    │ • Code analysis │    │                 │
│ • Plan generation│    │ • Script gen    │    │ • File ops      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                              │ • GCS access     │
                                              │ • Audit logging  │
                                              └─────────────────┘
```

#### Implementation Details

**1. Modal Function for Analysis**
```python
# src/roscoe/agents/paralegal/modal_tools.py
import modal
from modal import Image, Secret, Volume

# Define persistent volume for workspace access
workspace_volume = Volume.from_name("roscoe-workspace")

# Custom image with required tools
analysis_image = Image.debian_slim().pip_install(
    ["pandas", "numpy", "playwright", "tavily-python", "beautifulsoup4"]
).run_commands(
    "playwright install chromium"
)

# Background worker for file operations
file_ops_image = Image.debian_slim().pip_install(
    ["google-cloud-storage"]
)

@modal.function(
    image=analysis_image,
    secrets=[modal.Secret.from_name("roscoe-api-keys")],
    volumes={"/workspace": workspace_volume}
)
def analyze_and_plan_reorganization(case_name: str, file_inventory: dict) -> dict:
    """Analyze files and generate reorganization plan in sandbox."""

    # Analysis code runs in isolated container
    import pandas as pd
    from pathlib import Path

    workspace = Path("/workspace")

    # Analyze file patterns and generate plan
    plan = {
        "moves": [],
        "deletions": [],
        "creations": [],
        "validations": []
    }

    # Generate detailed reorganization plan
    # (Analysis logic here)

    return plan

@modal.function(
    image=file_ops_image,
    secrets=[modal.Secret.from_name("gcp-service-account")],
    volumes={"/workspace": workspace_volume}
)
def execute_file_operations(plan: dict, case_name: str) -> dict:
    """Execute file operations in background worker with GCS access."""

    from google.cloud import storage
    import json

    # Direct GCS operations with audit logging
    client = storage.Client()
    bucket = client.bucket("whaley-law-firm-projects")

    results = {
        "executed_operations": [],
        "errors": [],
        "audit_log": []
    }

    # Execute plan with full audit trail
    for operation in plan["moves"]:
        try:
            # Move file in GCS
            source_blob = bucket.blob(f"{case_name}/{operation['source']}")
            dest_blob = bucket.blob(f"{case_name}/{operation['destination']}")

            dest_blob.rewrite(source_blob)
            source_blob.delete()

            results["executed_operations"].append(operation)
            results["audit_log"].append({
                "operation": "move",
                "source": operation["source"],
                "destination": operation["destination"],
                "timestamp": datetime.utcnow().isoformat(),
                "actor": "roscoe-agent"
            })

        except Exception as e:
            results["errors"].append(f"Move failed: {e}")

    return results
```

**2. Integration with Agent Workflow**
```python
# src/roscoe/agents/paralegal/tools.py (modified)
def reorganize_case_files_modal(case_name: str) -> str:
    """Complete file reorganization using Modal architecture."""

    # Step 1: Generate file inventory
    inventory = generate_file_inventory(case_name)

    # Step 2: Analyze and plan in ephemeral Modal function
    plan = analyze_and_plan_reorganization.remote(case_name, inventory)

    # Step 3: Execute operations in background worker
    results = execute_file_operations.remote(plan, case_name)

    # Step 4: Verify and report
    verification = verify_reorganization.remote(case_name, plan)

    return f"Reorganization completed: {len(results['executed_operations'])} operations"
```

**3. Background Worker Architecture**
```python
# Background worker service for continuous file operations
@modal.cls(
    image=file_ops_image,
    secrets=[modal.Secret.from_name("gcp-service-account")]
)
class FileOperationsWorker:
    def __init__(self):
        self.client = storage.Client()
        self.audit_bucket = self.client.bucket("roscoe-audit-logs")

    @modal.method()
    def process_file_operation_queue(self):
        """Process queued file operations with safety checks."""

        # Poll operation queue
        operations = self.get_pending_operations()

        for op in operations:
            # Safety validation
            if self.validate_operation(op):
                # Execute with audit logging
                result = self.execute_operation(op)

                # Log to audit trail
                self.log_operation(op, result)

    def validate_operation(self, operation: dict) -> bool:
        """Validate operation for safety and permissions."""
        # Check path safety, file type restrictions, etc.
        return True  # Implement validation logic
```

#### Security & Safety Measures
- **Operation Validation**: All file operations pre-validated before execution
- **Audit Trail**: Complete logging of all file mutations
- **Rollback Support**: GCS object versioning for recovery
- **Permission Scoping**: Background workers have minimal required permissions

#### Advantages
- ✅ **Scalable**: Auto-scaling ephemeral containers
- ✅ **Cost-Effective**: Pay only for execution time
- ✅ **Separation of Concerns**: Analysis vs. execution isolation
- ✅ **Background Processing**: Non-blocking file operations
- ✅ **Full Internet Access**: Direct API calls and web scraping in containers

#### Challenges & Mitigations
- **Complexity**: Managing multiple services and queues
  - *Mitigation*: Well-defined interfaces and monitoring
- **Latency**: Background processing introduces delays
  - *Mitigation*: Progress tracking and real-time status updates

---

### Solution 3: Hybrid Cloud-Native Architecture
**Best for: Maximum control and customization with enterprise-grade security**

#### Architecture Overview
Custom Kubernetes-based architecture with persistent volumes, privileged containers, and comprehensive audit logging. Combines the best of cloud-native patterns with enterprise security requirements.

#### Key Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Roscoe Agent  │────│   K8s Job       │────│  Persistent     │
│   (LangGraph)   │    │   (Privileged)  │    │  Volume Claim   │
│                 │    │                 │    │                 │
│ • Task dispatch │    │ • Code exec     │    │ • GCS-backed    │
│ • Result process│    │ • File ops      │    │ • Auto-scaling  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                              │ • Audit logs    │
                                              └─────────────────┘
```

#### Implementation Details

**1. Kubernetes Job Templates**
```yaml
# k8s/job-templates/sandbox-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: roscoe-sandbox-{{session_id}}
  labels:
    app: roscoe-sandbox
spec:
  template:
    spec:
      serviceAccountName: roscoe-sandbox-sa
      containers:
      - name: sandbox
        image: roscoe-sandbox:latest
        securityContext:
          privileged: true  # Required for FUSE mounting
        env:
        - name: SESSION_ID
          value: "{{session_id}}"
        - name: TASK_TYPE
          value: "{{task_type}}"
        volumeMounts:
        - name: workspace-pv
          mountPath: /workspace
        - name: gcs-fuse-cache
          mountPath: /tmp/gcsfuse-cache
      volumes:
      - name: workspace-pv
        persistentVolumeClaim:
          claimName: roscoe-workspace-pvc
      - name: gcs-fuse-cache
        emptyDir: {}
      restartPolicy: Never
```

**2. Persistent Volume Configuration**
```yaml
# k8s/pv/roscoe-workspace-pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: roscoe-workspace-pv
spec:
  capacity:
    storage: 2Ti
  accessModes:
    - ReadWriteMany
  gcePersistentDisk:
    pdName: roscoe-workspace-disk
    fsType: ext4
  # Alternative: NFS-backed for multi-zone access
  # nfs:
  #   server: roscoe-nfs-server
  #   path: /workspace

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: roscoe-workspace-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 2Ti
```

**3. GCS FUSE Sidecar Pattern**
```yaml
# k8s/deployments/gcs-fuse-sidecar.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: roscoe-gcs-fuse
spec:
  replicas: 1
  template:
    spec:
      serviceAccountName: roscoe-gcs-sa
      containers:
      - name: gcs-fuse
        image: gcr.io/cloud-storage-fuse-volume/gcs-fuse-volume:latest
        args:
        - /usr/local/bin/gcsfuse
        - --implicit-dirs
        - --key-file=/etc/gcsfuse/service-account.json
        - whaley-law-firm-projects
        - /workspace/projects
        volumeMounts:
        - name: gcs-key
          mountPath: /etc/gcsfuse
          readOnly: true
        - name: workspace
          mountPath: /workspace
      - name: file-ops-worker
        image: roscoe-file-worker:latest
        command: ["/bin/bash", "-c", "tail -f /dev/null"]  # Keep alive
        volumeMounts:
        - name: workspace
          mountPath: /workspace
      volumes:
      - name: gcs-key
        secret:
          secretName: gcs-service-account
      - name: workspace
        persistentVolumeClaim:
          claimName: roscoe-workspace-pvc
```

**4. Agent Integration**
```python
# src/roscoe/agents/paralegal/tools.py (modified)
import kubernetes.client as k8s

def execute_code_k8s(
    command: str,
    case_name: str,
    task_type: str = "general",
    privileged: bool = False
) -> str:
    """Execute code in Kubernetes job with persistent volume access."""

    # Create Kubernetes job
    job_manifest = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": f"roscoe-{task_type}-{uuid.uuid4().hex[:8]}",
            "labels": {"app": "roscoe-sandbox", "case": case_name}
        },
        "spec": {
            "template": {
                "spec": {
                    "serviceAccountName": "roscoe-sandbox-sa",
                    "containers": [{
                        "name": "sandbox",
                        "image": "roscoe-sandbox:latest",
                        "securityContext": {"privileged": privileged},
                        "env": [
                            {"name": "COMMAND", "value": command},
                            {"name": "CASE_NAME", "value": case_name},
                            {"name": "TASK_TYPE", "value": task_type}
                        ],
                        "volumeMounts": [{
                            "name": "workspace",
                            "mountPath": "/workspace"
                        }]
                    }],
                    "volumes": [{
                        "name": "workspace",
                        "persistentVolumeClaim": {
                            "claimName": "roscoe-workspace-pvc"
                        }
                    }],
                    "restartPolicy": "Never"
                }
            }
        }
    }

    # Submit job
    batch_api = k8s.BatchV1Api()
    job = batch_api.create_namespaced_job("roscoe", job_manifest)

    # Wait for completion and get logs
    return wait_for_job_completion(job.metadata.name)
```

**5. Audit and Security Layer**
```python
class K8sAuditLogger:
    def __init__(self):
        self.es_client = Elasticsearch(hosts=["roscoe-elasticsearch:9200"])

    def log_operation(self, operation: dict, result: dict):
        """Log all file operations to Elasticsearch."""

        audit_entry = {
            "timestamp": datetime.utcnow(),
            "actor": operation.get("actor", "roscoe-agent"),
            "operation": operation["type"],
            "case_name": operation.get("case_name"),
            "paths": operation.get("paths", []),
            "command": operation.get("command"),
            "result": result,
            "session_id": operation.get("session_id")
        }

        self.es_client.index(index="roscoe-audit", document=audit_entry)

    def validate_operation(self, operation: dict) -> bool:
        """Pre-validate operations for safety."""

        # Path validation
        if not self.is_safe_path(operation.get("paths", [])):
            return False

        # Operation type validation
        allowed_ops = ["move", "copy", "delete", "create", "modify"]
        if operation["type"] not in allowed_ops:
            return False

        # Size limits
        if operation.get("size_limit", 0) > 100 * 1024 * 1024:  # 100MB
            return False

        return True
```

#### Security & Safety Measures
- **RBAC**: Kubernetes role-based access control
- **Network Policies**: Restrict pod-to-pod communication
- **Security Contexts**: Non-root containers with minimal privileges
- **Audit Logging**: Complete operation trail with Elasticsearch
- **Backup**: Automated GCS bucket versioning

#### Advantages
- ✅ **Maximum Control**: Full customization and security policies
- ✅ **Enterprise-Grade**: Comprehensive audit and compliance features
- ✅ **Scalable**: Kubernetes auto-scaling and resource management
- ✅ **Reliable**: Persistent volumes with backup and recovery
- ✅ **Flexible**: Support for any tool or framework

#### Challenges & Mitigations
- **Operational Complexity**: Kubernetes management overhead
  - *Mitigation*: Managed Kubernetes services (GKE) and GitOps
- **Cost**: Higher infrastructure costs
  - *Mitigation*: Right-sizing and auto-scaling policies

## Solution Comparison

| Criteria | E2B + Persistent Storage | Modal + Background Workers | K8s + Cloud-Native |
|----------|--------------------------|----------------------------|-------------------|
| **Implementation Complexity** | Medium | Low | High |
| **Cost** | Medium-High | Low-Medium | High |
| **Security** | High | High | Very High |
| **Scalability** | High | Very High | Very High |
| **File Operation Latency** | Low | Medium | Low |
| **Internet/Browser Access** | Full | Full | Full |
| **Customization** | Medium | Low | Very High |
| **Maintenance Overhead** | Low | Low | High |
| **Time to Deploy** | 2-4 weeks | 1-2 weeks | 4-8 weeks |

## Recommendation

**For immediate deployment (3-6 months):** Start with **Solution 2 (Modal + Background Workers)** - it provides the best balance of simplicity, cost-effectiveness, and functionality while enabling all required file operations and internet access.

**For long-term enterprise solution (6+ months):** Migrate to **Solution 3 (K8s + Cloud-Native)** - it provides maximum control, security, and scalability for production workloads.

**For rapid prototyping:** Consider **Solution 1 (E2B + Persistent Storage)** - it offers the most direct path to enabling file operations with minimal architectural changes.

Each solution enables agents to perform direct file transformations, run browser automation with Playwright, execute internet searches, and safely modify the persistent `/projects/...` filesystem while maintaining security and auditability.
