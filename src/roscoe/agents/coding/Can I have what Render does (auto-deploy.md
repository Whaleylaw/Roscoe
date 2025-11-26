Can I have what Render does (auto-deploy from GitHub) but on my Google VM?”

Short version:
There’s no magic “sync with GitHub” button on a VM, but you can get almost the same behavior with a very simple setup.

I’ll give you 3 levels of maturity:

Option 1: “Lazy but effective” – git pull on the VM

This is the simplest and honestly fine for you right now.

1. Clone your repo onto the VM

SSH into the VM:

cd /opt
sudo mkdir paralegal-agent
sudo chown $USER:$USER paralegal-agent
cd paralegal-agent

git clone https://github.com/YOU/PARALEGAL_REPO.git .


Now your repo lives at /opt/paralegal-agent on the VM.

Assume your repo has:

Dockerfile

docker-compose.yml or instructions to run the container

2. Build and run your container from the repo

Example using Docker directly:

cd /opt/paralegal-agent

docker build -t paralegal-agent:latest .

docker run -d \
  --name paralegal-agent \
  -p 8080:8080 \
  -v /mnt/workspace:/workspace \
  paralegal-agent:latest

3. Make a tiny deploy.sh script

In /opt/paralegal-agent/deploy.sh:

#!/bin/bash
set -e

cd /opt/paralegal-agent

echo "Pulling latest code..."
git pull

echo "Building Docker image..."
docker build -t paralegal-agent:latest .

echo "Restarting container..."
docker stop paralegal-agent || true
docker rm paralegal-agent || true

docker run -d \
  --name paralegal-agent \
  -p 8080:8080 \
  -v /mnt/workspace:/workspace \
  paralegal-agent:latest

echo "Done."


Then:

chmod +x deploy.sh


Now your “deploy flow” becomes:

Make changes locally

git push to GitHub

SSH into VM

Run:

/opt/paralegal-agent/deploy.sh


That’s it. Render was doing this for you. Now you’re just doing it yourself on the VM.

If you want to be extra lazy, you can:

Add a GitHub Action that SSHes into the VM and runs deploy.sh when main updates.
But that’s optional.

Option 2: Slightly more civilized – Docker Hub / Artifact Registry + pull

Here the VM doesn’t build the image; it just pulls it.

Flow:

GitHub → CI builds Docker image and pushes to:

Docker Hub, or

Google Artifact Registry

On the VM:

docker pull your-registry/paralegal-agent:latest

docker stop paralegal-agent || true
docker rm paralegal-agent || true

docker run -d \
  --name paralegal-agent \
  -p 8080:8080 \
  -v /mnt/workspace:/workspace \
  your-registry/paralegal-agent:latest


You can wrap that in deploy.sh too.

This is nicer when builds are heavy and you don’t want to compile on the VM.

Option 3: Fully-managed style – move the agent API to Cloud Run

You could move the HTTP-facing bit (the orchestrator) to Cloud Run, and then:

Cloud Run is linked to your GitHub repo.

On push → Cloud Build builds image → redeploys Cloud Run service.

LangSmith points to the Cloud Run URL.

Meanwhile, the heavy file-system-bash-happy paralegal worker might still live on a VM or GKE.

That’s more architecture work, but it gives you proper “Render-like” behavior on GCP.