#!/bin/bash

set -e

VM_NAME="roscoe-paralegal-vm"
VM_ZONE="us-central1-a"
VM_PATH="/home/aaronwhaley/roscoe-ui-v2"

echo "🚀 Starting dev server on VM..."

gcloud compute ssh ${VM_NAME} --zone=${VM_ZONE} --command="
  cd ${VM_PATH} && \
  npm install && \
  nohup npm run dev > /tmp/roscoe-ui-dev.log 2>&1 &
  echo 'Dev server started! View logs: tail -f /tmp/roscoe-ui-dev.log'
"

echo "✅ Dev server started on VM"
echo "🌐 Access at: http://34.63.223.97:3000"
