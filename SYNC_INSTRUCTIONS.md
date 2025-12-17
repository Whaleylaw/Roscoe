# Syncing workspace_paralegal with GCS Bucket

Your `workspace_paralegal/` folder should match the GCS bucket (`whaley_law_firm`) where all the production file organization has happened.

## Quick Sync (Recommended)

Run the sync script:

```bash
cd "/Volumes/X10 Pro/Roscoe"
./sync-from-gcs.sh
```

This will:
1. Authenticate with Google Cloud (opens browser)
2. Download all new/changed files from GCS → local
3. Preserve local files not in GCS (safe, won't delete your work)

## Manual Sync (Alternative)

If the script doesn't work, do it manually:

### Step 1: Authenticate

```bash
gcloud auth login --update-adc
```

This opens your browser to authenticate.

### Step 2: Sync

```bash
gsutil -m rsync -r -c \
  gs://whaley_law_firm/ \
  "/Volumes/X10 Pro/Roscoe/workspace_paralegal/"
```

**Flags explained**:
- `-m`: Multi-threaded (faster)
- `-r`: Recursive (all subdirectories)
- `-c`: Compare checksums (accurate detection of changes)

### Step 3: Verify

```bash
cd "/Volumes/X10 Pro/Roscoe/workspace_paralegal"
ls -lh Database/  # Check latest database files
ls -lh Tools/     # Check latest tools
```

## What Gets Synced

From `gs://whaley_law_firm/` bucket:

- ✅ **Database/** - Latest case data (caselist.json, insurance.json, etc.)
- ✅ **Tools/** - All tool scripts (including new ones)
- ✅ **Skills/** - Skill definitions
- ✅ **projects/** - All case folders with reorganized files
- ✅ **workflow_engine/** - Checklists, templates, schemas
- ✅ **Prompts/** - Context chunks
- ✅ **Reports/** - Agent-generated analysis

## Troubleshooting

### "Reauthentication required"

Run:
```bash
gcloud auth login --update-adc
```

### "Permission denied"

Make sure you're logged into the correct Google account:
```bash
gcloud auth list
gcloud config set account your-email@gmail.com
```

### Check what would change (dry run)

```bash
gsutil rsync -r -c -n \
  gs://whaley_law_firm/ \
  "/Volumes/X10 Pro/Roscoe/workspace_paralegal/"
```

The `-n` flag shows what would change without actually changing it.

## Sync Direction

**Download (GCS → Local)**:
```bash
gsutil -m rsync -r -c \
  gs://whaley_law_firm/ \
  "/Volumes/X10 Pro/Roscoe/workspace_paralegal/"
```

**Upload (Local → GCS)** - BE CAREFUL:
```bash
gsutil -m rsync -r -c \
  "/Volumes/X10 Pro/Roscoe/workspace_paralegal/" \
  gs://whaley_law_firm/
```

## After Syncing

Your local workspace will have:
- Latest database files with all case updates
- All file reorganizations done by the agent
- Latest tools/skills/checklists
- AI-generated scripts in Tools/_generated/

Then you can run:
```bash
cd local-dev-code
langgraph dev
```

And test with the latest data!
