#!/bin/bash
# Sync local case files to Google Cloud Storage
# This uploads new/changed files to your GCS bucket

set -e

echo "========================================="
echo "Syncing Local Files to GCS"
echo "========================================="
echo ""

LOCAL_DIR="/Volumes/X10 Pro/whaley law firm"
GCS_BUCKET="gs://whaley_law_firm"

echo "Local directory: $LOCAL_DIR"
echo "GCS bucket: $GCS_BUCKET"
echo ""

# Check if local directory exists
if [ ! -d "$LOCAL_DIR" ]; then
    echo "❌ Error: Local directory not found: $LOCAL_DIR"
    exit 1
fi

echo "📊 Checking what needs to be uploaded..."
echo ""

# Dry run first (show what would be synced)
gcloud storage rsync -r "$LOCAL_DIR" "$GCS_BUCKET" --dry-run | head -50

echo ""
read -p "Continue with upload? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Upload cancelled"
    exit 0
fi

echo ""
echo "📤 Uploading files..."
echo ""

# Actual sync (only uploads new/changed files)
gcloud storage rsync -r "$LOCAL_DIR" "$GCS_BUCKET"

echo ""
echo "✅ Sync complete!"
echo ""

# Show bucket size
echo "📊 Total size in GCS:"
gcloud storage du -s "$GCS_BUCKET"

echo ""
echo "Files are now accessible to your agent at:"
echo "  http://35.223.94.19:8123"
echo ""
