# 🎉 Roscoe Google Cloud Deployment - COMPLETE!

## ✅ What's Live

**Permanent IP**: `34.63.223.97` (static, won't change)

**Services Running:**
- **Agent Server**: http://34.63.223.97:8123 (LangGraph API)
- **DeepAgents UI**: http://34.63.223.97:3000 (Visual interface)
- **API Docs**: http://34.63.223.97:8123/docs

**Infrastructure:**
- Google Compute VM: `roscoe-paralegal-vm` (us-central1-a)
- PostgreSQL + Redis (state management)
- GCS Bucket: `gs://whaley_law_firm` (auto-mounted at boot)
- Docker images on Docker Hub

---

## 🚀 Auto-Restart on Reboot

✅ **GCS auto-mounts** on VM boot (systemd service)
✅ **Docker Compose auto-starts** after GCS mounts
✅ **Static IP** - won't change even if VM restarts

**To test:** Restart the VM and everything comes back automatically:
```bash
gcloud compute instances stop roscoe-paralegal-vm --zone=us-central1-a
gcloud compute instances start roscoe-paralegal-vm --zone=us-central1-a
# Wait ~2 minutes, then check:
curl http://34.63.223.97:8123/ok
```

---

## 🔄 Auto-Deploy from GitHub (Render-Style)

I created `.github/workflows/deploy.yml` that auto-deploys when you push to main:

**How it works:**
1. Push code to GitHub `main` branch
2. GitHub Actions runs automatically
3. Builds Docker image with `langgraph build`
4. Pushes to Docker Hub
5. SSHs into your VM and updates the container
6. Verifies deployment

**Setup (one-time):**

1. **Push your repo to GitHub** (if not already):
   ```bash
   cd "/Volumes/X10 Pro/Roscoe"
   git remote add origin https://github.com/yourusername/roscoe.git
   git push -u origin main
   ```

2. **Add GitHub Secrets** (in repo Settings → Secrets and variables → Actions):
   - `DOCKER_USERNAME`: `agwhaley`
   - `DOCKER_PASSWORD`: Your Docker Hub password/token
   - `GCP_SA_KEY`: Service account JSON key (see below)

3. **Create GCP Service Account** for GitHub Actions:
   ```bash
   gcloud iam service-accounts create github-deploy \
     --display-name="GitHub Actions Deploy"

   gcloud projects add-iam-policy-binding roscoe-479117 \
     --member="serviceAccount:github-deploy@roscoe-479117.iam.gserviceaccount.com" \
     --role="roles/compute.instanceAdmin"

   gcloud iam service-accounts keys create ~/github-sa-key.json \
     --iam-account=github-deploy@roscoe-479117.iam.gserviceaccount.com

   # Copy contents of ~/github-sa-key.json to GitHub secret GCP_SA_KEY
   cat ~/github-sa-key.json
   ```

**Then:** Every push to `main` → auto-deploy! Just like Render.

---

## 📤 Uploading Case Files

**Status:** Uploading ~94 remaining case folders in background

**To sync more files later:**
```bash
cd "/Volumes/X10 Pro/Roscoe"
./sync-to-gcs.sh
```

**Check upload progress:**
```bash
gcloud storage du -s gs://whaley_law_firm/projects/
gcloud storage ls gs://whaley_law_firm/projects/ | wc -l
```

---

## 🎯 How to Use Roscoe

### Option 1: DeepAgents UI (Visual - EASIEST)

**Open**: http://34.63.223.97:3000

**Enter:**
- Deployment URL: `http://34.63.223.97:8123`
- Assistant ID: `roscoe_paralegal` (or `roscoe_coding`)
- LangSmith API Key: `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`

### Option 2: Python SDK

```python
from langgraph_sdk import get_client

client = get_client(url="http://34.63.223.97:8123")

# Create thread
thread = client.threads.create()

# Run agent
for chunk in client.runs.stream(
    thread["thread_id"],
    "roscoe_paralegal",
    input={"messages": [{"role": "user", "content": "Analyze Abby Sitgraves case"}]}
):
    print(chunk)
```

### Option 3: REST API

```bash
# Create thread
THREAD_ID=$(curl -s -X POST http://34.63.223.97:8123/threads | jq -r '.thread_id')

# Send message
curl -X POST http://34.63.223.97:8123/runs/stream \
  -H "Content-Type: application/json" \
  -d "{\"assistant_id\":\"roscoe_paralegal\",\"thread_id\":\"$THREAD_ID\",\"input\":{\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}}"
```

---

## 🔍 Monitoring & Debugging

**LangSmith**: https://smith.langchain.com/ (traces already being sent)

**View logs on VM:**
```bash
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a
sudo docker compose -f /tmp/docker-compose.yml logs -f roscoe
```

**Check services:**
```bash
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a
sudo docker compose -f /tmp/docker-compose.yml ps
```

---

## 💰 Monthly Costs (Estimate)

- **VM** (e2-standard-4, 24/7): ~$120/month
- **Static IP**: ~$1.50/month
- **GCS Storage** (100GB): ~$2/month
- **GCS Bandwidth**: ~$1-5/month (minimal)
- **Total**: ~$125/month

**To reduce costs:**
- Use smaller VM (e2-medium) if performance allows
- Stop VM when not in use (data persists in GCS)
- Use preemptible VM (cheaper but can be terminated)

---

## 🛠️ Common Operations

### Update Agent Code
```bash
# Local: Make changes and push
git commit -am "Update agent"
git push

# Auto-deploy via GitHub Actions, OR manually:
langgraph build -t agwhaley/roscoe-agents:latest
docker push agwhaley/roscoe-agents:latest

# On VM:
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a
cd /tmp
sudo docker compose pull roscoe
sudo docker compose up -d --no-deps roscoe
```

### Stop Everything
```bash
gcloud compute instances stop roscoe-paralegal-vm --zone=us-central1-a
```

### Start Everything
```bash
gcloud compute instances start roscoe-paralegal-vm --zone=us-central1-a
# Wait ~2 min for auto-mount and docker to start
```

### Delete Everything (Cleanup)
```bash
# Stop and delete VM
gcloud compute instances delete roscoe-paralegal-vm --zone=us-central1-a

# Delete static IP
gcloud compute addresses delete roscoe-static-ip --region=us-central1

# Keep or delete GCS bucket (your case files)
# gcloud storage rm -r gs://whaley_law_firm  # CAREFUL!
```

---

## 📋 What Was Built

**Docker Images:**
- `agwhaley/roscoe-agents:standalone` - Agent Server (LangGraph build)
- `agwhaley/roscoe-ui:latest` - DeepAgents UI

**Configuration Files:**
- `Dockerfile` - Custom dockerfile (reference only)
- `docker-compose.yml` - Full stack orchestration
- `.dockerignore` - Optimized build context
- `.github/workflows/deploy.yml` - Auto-deploy pipeline
- `sync-to-gcs.sh` - File upload script

**VM Services:**
- `gcsfuse-mount.service` - Auto-mount GCS at boot
- `roscoe-docker.service` - Auto-start Docker Compose

---

## 🎓 Next Steps

1. ✅ Set up GitHub auto-deploy (add secrets to repo)
2. ✅ Upload remaining case files (running in background)
3. ✅ Test the UI at http://34.63.223.97:3000
4. ⏳ Wait for `langgraph build` to finish, then push and deploy
5. Optional: Set up HTTPS with domain name

---

## 📞 Support

**Issues:**
- Check VM logs: `sudo docker compose -f /tmp/docker-compose.yml logs`
- Check services: `sudo docker compose -f /tmp/docker-compose.yml ps`
- Restart: `sudo docker compose -f /tmp/docker-compose.yml restart`

**GitHub**: Push your repo for version control and auto-deploy

---

**You can now turn off your Mac and access Roscoe from anywhere!** 🎊
