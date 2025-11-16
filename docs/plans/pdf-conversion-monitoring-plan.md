# PDF to Markdown Conversion - Monitoring Plan

**Created:** 2025-11-10
**Status:** Active - Conversion in Progress
**Background Process ID:** 34296a

## Overview

The PDF to Markdown converter is running in the background converting 8,521 PDF files from Supabase storage to Markdown format. This document provides instructions for monitoring and troubleshooting the conversion process.

## Current Status

- **Total Files:** 8,521 PDFs
- **Previously Converted:** 57 files (before improvements)
- **Remaining:** ~8,464 files
- **Process ID:** 34296a
- **Started:** 2025-11-10 ~13:45 (after improvements)

## Monitoring Schedule

**Check every 60 minutes until completion:**

1. Check if process is still running
2. Review recent log entries
3. Check error count
4. Count successfully converted files
5. Estimate progress and remaining time
6. If crashed or stuck: diagnose, fix, and restart

## Automated Monitoring (RECOMMENDED)

### Use the Monitor Script

```bash
# Quick single check
python monitor_conversion.py --check-once

# Continuous monitoring (checks every hour)
python monitor_conversion.py --check-interval 3600

# Run in background
nohup python monitor_conversion.py --check-interval 3600 > monitor.log 2>&1 &
```

See `README-monitor.md` for full documentation.

## Manual Monitoring

### 1. Check Process Status

```bash
# Method 1: Check background process
BashOutput tool with bash_id: 34296a

# Method 2: Check if Python process is running
ps aux | grep pdf_to_markdown_converter.py
```

### 2. Review Recent Logs

```bash
# Last 50 lines of main log
tail -50 pdf_conversion.log

# Check for errors
grep -i "error\|critical\|fatal" pdf_conversion.log | tail -20

# Check memory usage logs
grep "Memory usage:" pdf_conversion.log | tail -10
```

### 3. Check Error Count

```bash
# Total errors (minus header)
wc -l < conversion_errors.csv

# Recent errors
tail -10 conversion_errors.csv

# Error types summary
cut -d',' -f6 conversion_errors.csv | sort | uniq -c
```

### 4. Count Successful Conversions

```bash
# Count markdown files
find converted_documents -name "*.md" | wc -l

# List recently created files
find converted_documents -name "*.md" -mmin -60 | wc -l
```

### 5. Check for Crash Reports

```bash
# Check if crash report exists
test -f conversion_crash_report.log && echo "CRASH DETECTED" || echo "No crashes"

# View crash report if it exists
cat conversion_crash_report.log
```

## Troubleshooting Steps

### If Process Has Crashed

1. **Read crash report:**
   ```bash
   cat conversion_crash_report.log
   ```

2. **Check end of main log:**
   ```bash
   tail -100 pdf_conversion.log
   ```

3. **Identify the issue:**
   - Memory error? Reduce `--max-size` or add swap space
   - Connection timeout? Check network/Supabase status
   - Specific file causing crash? Check conversion_errors.csv
   - Python package error? May need to reinstall dependencies

4. **Restart the converter:**
   ```bash
   export SUPABASE_URL="https://pdhrmsoydwvoafunalez.supabase.co"
   export SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBkaHJtc295ZHd2b2FmdW5hbGV6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzkwMjQ1NCwiZXhwIjoyMDY5NDc4NDU0fQ.sK89R5rqq5ScGt_qHYcN_57mikg5716rdxhHkq_YhUY"
   /opt/homebrew/bin/python3 /Users/aaronwhaley/Documents/GitHub/Whaley-Law-Firm/pdf_to_markdown_converter.py
   ```

5. **Note:** The converter automatically skips already-converted files by checking the database, so it's safe to restart.

### Common Issues and Solutions

**Issue: Out of Memory**
- Solution: Restart with smaller max file size: `--max-size 25`
- Or: Free up disk space/RAM before restarting

**Issue: Network Timeouts**
- Solution: Check Supabase connection, retry failed files later
- Errors are logged in conversion_errors.csv

**Issue: Specific Files Failing**
- Solution: Review conversion_errors.csv for patterns
- Files without .pdf extension in URLs will fail (expected)
- Can address these separately after main batch completes

**Issue: Process Killed by System**
- Solution: Check system logs, may need to reduce load
- Consider running with `--limit` to process in smaller batches

## Progress Estimation

Approximate conversion times:
- Small files (< 100KB): 1-5 seconds
- Medium files (100KB-1MB): 5-30 seconds
- Large files (1MB-50MB): 30-120 seconds

**Estimated total time:** 12-24 hours for all 8,521 files

To calculate progress:
```bash
# Files completed
completed=$(find converted_documents -name "*.md" | wc -l)
total=8521
progress=$(awk "BEGIN {printf \"%.2f\", ($completed/$total)*100}")
echo "Progress: $completed / $total ($progress%)"
```

## Files to Monitor

- `pdf_conversion.log` - Main conversion log
- `conversion_errors.csv` - All errors (download, conversion, critical)
- `conversion_crash_report.log` - Fatal crashes only
- `converted_documents/` - Output directory with markdown files

## Success Criteria

✅ Conversion is complete when:
- Process exits with code 0
- Log shows "Conversion Summary" with totals
- ~8,500+ markdown files exist in converted_documents/
- Error count is reasonable (< 5% of total)

## Next Steps After Completion

1. Review conversion_errors.csv for patterns
2. Address files with missing .pdf extensions in Supabase
3. Manually handle any large files that were skipped
4. Verify markdown quality with spot checks
5. Update database queries to use markdown_path field

## Emergency Contact

If Claude crashes and you need to resume monitoring:
1. Read this document
2. Run status checks above
3. Use bash_id 34296a with BashOutput tool if process is still running
4. If stopped, check logs and restart as needed

---

**Last Updated:** 2025-11-10
**Next Check Due:** 2025-11-10 ~14:45 (1 hour from start)
