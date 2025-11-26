#!/bin/bash
# Upload all remaining case files after Destiny-Adkins

set -e

cd "/Volumes/X10 Pro/Roscoe/workspace_paralegal/projects"

echo "Uploading all case files from Dewayne-Ward onwards..."
echo ""

# Get list of folders to upload (after Destiny-Adkins alphabetically)
FOLDERS_TO_UPLOAD=$(ls -1 | awk '/^Dewayne-Ward/,0')

# Count them
COUNT=$(echo "$FOLDERS_TO_UPLOAD" | wc -l)
echo "Found $COUNT folders to upload"
echo ""

# Upload each in parallel using background processes
for folder in $FOLDERS_TO_UPLOAD; do
    echo "Uploading: $folder"
    gcloud storage cp -r "$folder" gs://whaley_law_firm/projects/ --recursive &

    # Limit to 10 parallel uploads at a time
    if [[ $(jobs -r -p | wc -l) -ge 10 ]]; then
        wait -n
    fi
done

# Wait for all remaining uploads
wait

echo ""
echo "✅ Upload complete!"
echo ""
echo "Total in GCS:"
gcloud storage du -s gs://whaley_law_firm/projects/
