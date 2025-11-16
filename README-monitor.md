# PDF Conversion Monitoring Script

## Quick Start

The `monitor_conversion.py` script automatically monitors the PDF to Markdown conversion process and alerts you when action is needed.

### Option 1: Check Once (Manual)

```bash
python monitor_conversion.py --check-once
```

This shows current status and exits. Good for manual checking.

### Option 2: Continuous Monitoring (Automated)

```bash
# Check every hour (3600 seconds)
python monitor_conversion.py --check-interval 3600

# Check every 30 minutes
python monitor_conversion.py --check-interval 1800

# Check every 15 minutes (more frequent)
python monitor_conversion.py --check-interval 900
```

This runs continuously and alerts you when:
- ❌ Process has crashed → Time to troubleshoot
- ⏹️ Process stopped but incomplete → Time to restart
- ✅ Process completed → Time to review results

### Option 3: Run in Background

```bash
# Start monitoring in background
nohup python monitor_conversion.py --check-interval 3600 > monitor.log 2>&1 &

# View the monitoring output
tail -f monitor.log

# Stop monitoring
ps aux | grep monitor_conversion.py
kill <PID>
```

## What It Monitors

✅ **Process Status** - Is the converter running?
✅ **Progress** - How many files converted?
✅ **Errors** - How many files failed?
✅ **Crashes** - Did the process crash?
✅ **Completion** - Is conversion finished?

## What It Reports

Every check shows:

```
================================================================================
PDF CONVERSION STATUS - 2025-11-10T14:45:00
================================================================================

📊 Progress: 150/8521 files (1.8%)
   Remaining: 8371 files

🔄 Process Running: ✅ YES
❌ Errors: 8
💥 Crashed: ✅ No

📝 Recent Log (last 10 lines):
--------------------------------------------------------------------------------
[Shows last 10 lines from pdf_conversion.log]
================================================================================
```

## When to Take Action

### 🟢 Everything is OK
```
💬 Status: PDF conversion is running normally.
```
→ No action needed, wait for next check

### 🟡 Process Stopped (But Not Complete)
```
⚠️  ACTION REQUIRED!
💬 Status: The PDF conversion process has STOPPED but is not complete.
```
→ Restart the conversion:
```bash
export SUPABASE_URL="https://pdhrmsoydwvoafunalez.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-key-here"
python pdf_to_markdown_converter.py
```

### 🔴 Process Crashed
```
⚠️  ACTION REQUIRED!
💬 Status: The PDF conversion process has CRASHED.
```
→ Check crash report and troubleshoot:
```bash
cat conversion_crash_report.log
tail -100 pdf_conversion.log
```

### 🎉 Conversion Complete
```
✅ CONVERSION COMPLETE!
```
→ Review results and errors:
```bash
# Count converted files
find converted_documents -name "*.md" | wc -l

# Review errors
cat conversion_errors.csv
```

## Integration with Claude Code

The monitor will print suggestions for Claude Code:

```
💡 You should now run: claude code
   And tell Claude: Check the PDF conversion status
```

When you see this, open Claude Code and say:
- "Check the PDF conversion status"
- "The monitor says the process crashed, investigate"
- "Monitor shows conversion is complete, verify results"

Claude will automatically:
1. Read the monitoring plan
2. Check logs and status
3. Take appropriate action
4. Report findings

## Customization

Edit the script to change:
- `total = 8521` - Update if file count changes
- Check interval - Use `--check-interval` flag
- Notification methods - Add email/SMS alerts

## Troubleshooting

**Monitor shows wrong progress:**
- Markdown count may include files from previous runs
- Check database for accurate count

**Monitor can't find logs:**
- Make sure you're in the project directory
- Logs are in: `/Users/aaronwhaley/Documents/GitHub/Whaley-Law-Firm/`

**Want to stop monitoring:**
- Press `Ctrl+C` if running in foreground
- Use `kill` if running in background

## Example Session

```bash
# Terminal 1: Run the monitor
$ python monitor_conversion.py --check-interval 3600
🔍 Starting conversion monitor (checking every 3600s)
📋 Monitoring plan: docs/plans/pdf-conversion-monitoring-plan.md
⏰ Press Ctrl+C to stop

CHECK #1 - 2025-11-10 14:00:00
================================================================================
📊 Progress: 57/8521 files (0.7%)
🔄 Process Running: ✅ YES
❌ Errors: 8
💥 Crashed: ✅ No
💬 Status: PDF conversion is running normally.
⏰ Next check at: 15:00:00
   Sleeping for 3600s...

CHECK #2 - 2025-11-10 15:00:00
...
```

## Tips

1. **Run in tmux/screen** - Keeps monitor running if you disconnect
2. **Redirect to log file** - Save monitoring history
3. **Check more frequently initially** - Use 15-30 min intervals for first few hours
4. **Reduce frequency later** - Switch to 1-2 hour intervals once stable

## Files

- `monitor_conversion.py` - The monitoring script
- `docs/plans/pdf-conversion-monitoring-plan.md` - Detailed monitoring procedures
- `pdf_conversion.log` - Main conversion log
- `conversion_errors.csv` - Error tracking
- `conversion_crash_report.log` - Crash details (if any)
