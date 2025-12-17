Alright, here’s your map.
No fluff. No cute cloud diagrams. Just the exact sequence to get your paralegal agent running on a Google VM with your GCS data mounted, inside Docker, reachable from LangSmith.

If you follow this, you go from **zero → working cloud paralegal**.

I’ll break it into **10 clean stages**.

---

# 0. PREREQUISITES (your local machine)

You should have:

* Google Cloud project created
* Billing enabled
* gcloud CLI installed
* Your 100GB case files uploaded to a GCS bucket:

  ```
  gs://pi-cases-bucket/workspace/
  ```

That’s it.

---

# 1. CREATE THE VM

This is the raw “computer in the sky.”

From your terminal:

```bash
gcloud compute instances create paralegal-vm \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --boot-disk-size=100GB \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --scopes=storage-rw
```

Key points:

* Ubuntu 22.04 base
* Enough CPU/RAM to run your agent
* VM has permission to read/write your GCS bucket

---

# 2. SSH INTO THE VM

```bash
gcloud compute ssh paralegal-vm --zone=us-central1-a
```

Now you’re inside your cloud computer.

---

# 3. INSTALL gcsfuse

This is what mounts your GCS bucket like a folder.

```bash
sudo apt-get update
sudo apt-get install gcsfuse -y
```

---

# 4. CREATE THE MOUNT POINT

```bash
sudo mkdir /mnt/workspace
sudo chmod 777 /mnt/workspace
```

(Yes, chmod 777. Spare me. We can tighten permissions later.)

---

# 5. MOUNT YOUR GCS BUCKET

```bash
gcsfuse pi-cases-bucket /mnt/workspace
```

Now test:

```bash
ls /mnt/workspace
```

You should see:

```
projects/
dataset/
...
```

This is your entire PI case library, now “inside” your VM.

---

# 6. INSTALL DOCKER

Your VM will host your agent container.

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg -y

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io -y
```

Then:

```bash
sudo usermod -aG docker $USER
exit
```

Then SSH back in:

```bash
gcloud compute ssh paralegal-vm
```

Docker is now ready.

---

# 7. PULL YOUR AGENT DOCKER IMAGE

Assuming you’ve pushed your agent image to Docker Hub or GCP Artifact Registry.

Example (Docker Hub):

```bash
docker pull yourusername/paralegal-agent:latest
```

Or Artifact Registry:

```bash
gcloud auth configure-docker us-central1-docker.pkg.dev

docker pull us-central1-docker.pkg.dev/YOUR_PROJECT/agent/paralegal-agent:latest
```

---

# 8. RUN THE AGENT CONTAINER + MOUNT THE GCS DIRECTORY

This is the key piece.

```bash
docker run \
  -d \
  --name paralegal-agent \
  -p 8080:8080 \
  -v /mnt/workspace:/workspace \
  yourusername/paralegal-agent:latest
```

Inside the container:

* `/workspace` = your GCS bucket
* The agent can run:

  * `ls /workspace/projects`
  * `python whatever_tool.py /workspace/projects/John_Smith/...`
  * generate files
  * read/write JSON
  * everything you’re used to

---

# 9. FIND YOUR VM’S PUBLIC IP

```bash
gcloud compute instances describe paralegal-vm \
  --zone=us-central1-a \
  --format="value(networkInterfaces[0].accessConfigs[0].natIP)"
```

Suppose it returns:

```
34.122.55.10
```

Your agent’s URL is now:

```
http://34.122.55.10:8080
```

(This is what you put into LangSmith.)

---

# 10. TEST FROM YOUR LOCAL MACHINE

```bash
curl http://34.122.55.10:8080/health
```

Or if your agent expects a POST:

```bash
curl -X POST http://34.122.55.10:8080/run \
  -H "Content-Type: application/json" \
  -d '{"message": "hello paralegal"}'
```

If you get a valid response, congratulations —
your paralegal is now alive, floating in the cloud,
and ready to shovel through 100GB of PI case files from anywhere.

---

# OPTIONAL (but smart)

## 11. Make GCS auto-mounted at boot

Edit `/etc/fstab`:

```bash
sudo nano /etc/fstab
```

Add:

```
pi-cases-bucket /mnt/workspace gcsfuse rw,noauto,user
```

Then at boot:

```bash
sudo mount /mnt/workspace
```

Or use a systemd service to auto-mount.

---

## 12. Give the VM a persistent static IP

In GCP Console → VPC → External IP addresses → Reserve

Otherwise your VM IP can change.

---

## 13. (Highly Recommended) Put HTTPS in front

You can use:

* Google Cloud Load Balancer
* OR Caddy/NGINX on VM
* OR Cloudflare DNS with TLS termination

That lets you have:

```
https://paralegal.yourdomain.com
```

---

# SUMMARY (you can print this part)

```
1. Create VM
2. SSH in
3. Install gcsfuse
4. Mount GCS → /mnt/workspace
5. Install Docker
6. Pull your agent container
7. Run it with -v /mnt/workspace:/workspace
8. Expose port 8080
9. Use VM public IP in LangSmith
10. Agent sees files exactly like local
```

You follow this, you get a fully functional cloud version of your system.

---

If you want, I can also give you:

* a version using Docker Compose
* a version using Cloud Run instead of VM
* or a version using GKE + Filestore (more scalable)

Just say which direction you’re leaning.
