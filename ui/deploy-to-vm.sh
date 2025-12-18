#!/bin/bash

set -e

VM_NAME="roscoe-paralegal-vm"
VM_ZONE="us-central1-a"
VM_PATH="/home/aaronwhaley/roscoe-ui-v2"

echo "📦 Deploying UI to VM..."

# Step 1: Sync source files (using rsync via gcloud ssh)
echo "1️⃣  Syncing files to VM..."
gcloud compute ssh ${VM_NAME} --zone=${VM_ZONE} --command="mkdir -p ${VM_PATH}"
rsync -avz --progress \
  --exclude=".next" \
  --exclude="node_modules" \
  --exclude=".git" \
  --exclude=".env.local" \
  -e "gcloud compute ssh ${VM_NAME} --zone=${VM_ZONE} --" \
  ./ \
  :${VM_PATH}/

# Step 2: Copy production environment
echo "2️⃣  Copying production environment..."
gcloud compute scp \
  --zone="${VM_ZONE}" \
  .env.production \
  aaronwhaley@${VM_NAME}:${VM_PATH}/.env.local

echo "✅ Files synced!"
echo ""
echo "Next steps (run on VM):"
echo "  gcloud compute ssh ${VM_NAME} --zone=${VM_ZONE}"
echo "  cd ${VM_PATH}"
echo "  npm install"
echo "  npm run dev"
