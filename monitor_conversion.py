#!/usr/bin/env python3
"""
PDF Conversion Monitoring Daemon

This script monitors the PDF to Markdown conversion process and can optionally
trigger Claude Code to check status at regular intervals.

Usage:
    python monitor_conversion.py --check-interval 3600  # Check every hour
    python monitor_conversion.py --notify-only          # Just show status, don't prompt Claude
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timedelta


class ConversionMonitor:
    """Monitors the PDF conversion process"""

    def __init__(self, check_interval: int = 3600):
        self.check_interval = check_interval
        self.monitoring_plan = Path("docs/plans/pdf-conversion-monitoring-plan.md")
        self.conversion_log = Path("pdf_conversion.log")
        self.error_csv = Path("conversion_errors.csv")
        self.crash_log = Path("conversion_crash_report.log")
        self.output_dir = Path("converted_documents")

    def is_process_running(self, process_name: str = "pdf_to_markdown_converter.py") -> bool:
        """Check if the conversion process is running"""
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                check=True
            )
            return process_name in result.stdout
        except Exception as e:
            print(f"Error checking process: {e}")
            return False

    def count_converted_files(self) -> int:
        """Count successfully converted markdown files"""
        if not self.output_dir.exists():
            return 0

        result = subprocess.run(
            ["find", str(self.output_dir), "-name", "*.md"],
            capture_output=True,
            text=True,
            check=True
        )
        return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0

    def count_errors(self) -> int:
        """Count total errors from CSV"""
        if not self.error_csv.exists():
            return 0

        with open(self.error_csv, 'r') as f:
            # Subtract 1 for header row
            return max(0, len(f.readlines()) - 1)

    def get_recent_log_lines(self, lines: int = 20) -> str:
        """Get recent lines from conversion log"""
        if not self.conversion_log.exists():
            return "Log file not found"

        result = subprocess.run(
            ["tail", f"-{lines}", str(self.conversion_log)],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout

    def check_for_crashes(self) -> bool:
        """Check if there's a crash report"""
        return self.crash_log.exists()

    def get_crash_report(self) -> str:
        """Get crash report content"""
        if not self.crash_log.exists():
            return "No crash report found"

        with open(self.crash_log, 'r') as f:
            return f.read()

    def calculate_progress(self, converted: int, total: int = 8521) -> dict:
        """Calculate conversion progress"""
        if total == 0:
            return {"percent": 0, "remaining": total}

        percent = (converted / total) * 100
        remaining = total - converted

        return {
            "converted": converted,
            "total": total,
            "percent": percent,
            "remaining": remaining
        }

    def generate_status_report(self) -> dict:
        """Generate comprehensive status report"""
        is_running = self.is_process_running()
        converted = self.count_converted_files()
        errors = self.count_errors()
        has_crashed = self.check_for_crashes()
        progress = self.calculate_progress(converted)

        return {
            "timestamp": datetime.now().isoformat(),
            "is_running": is_running,
            "converted_files": converted,
            "error_count": errors,
            "has_crashed": has_crashed,
            "progress": progress,
            "recent_log": self.get_recent_log_lines(10) if self.conversion_log.exists() else None
        }

    def print_status_report(self, status: dict):
        """Print formatted status report"""
        print("\n" + "="*80)
        print(f"PDF CONVERSION STATUS - {status['timestamp']}")
        print("="*80)
        print(f"\n📊 Progress: {status['progress']['converted']}/{status['progress']['total']} files " +
              f"({status['progress']['percent']:.1f}%)")
        print(f"   Remaining: {status['progress']['remaining']} files")
        print(f"\n🔄 Process Running: {'✅ YES' if status['is_running'] else '❌ NO'}")
        print(f"❌ Errors: {status['error_count']}")
        print(f"💥 Crashed: {'⚠️  YES - CHECK LOGS!' if status['has_crashed'] else '✅ No'}")

        if status['recent_log']:
            print(f"\n📝 Recent Log (last 10 lines):")
            print("-" * 80)
            print(status['recent_log'])

        print("="*80 + "\n")

    def create_claude_prompt(self, status: dict) -> str:
        """Create a prompt for Claude to check status"""
        if status['has_crashed']:
            return (
                f"The PDF conversion process has CRASHED. "
                f"Please read {self.monitoring_plan} and follow the troubleshooting steps. "
                f"Check {self.crash_log} for details."
            )
        elif not status['is_running']:
            if status['progress']['remaining'] > 0:
                return (
                    f"The PDF conversion process has STOPPED but is not complete. "
                    f"{status['progress']['remaining']} files remaining. "
                    f"Please read {self.monitoring_plan} and restart the process."
                )
            else:
                return (
                    f"The PDF conversion appears COMPLETE! "
                    f"{status['converted_files']} files converted. "
                    f"Please verify completion and review any errors."
                )
        else:
            return (
                f"PDF conversion is running normally. "
                f"Progress: {status['progress']['converted']}/{status['progress']['total']} "
                f"({status['progress']['percent']:.1f}%). "
                f"Errors so far: {status['error_count']}. "
                f"Continue monitoring."
            )

    def run_monitoring_loop(self, notify_only: bool = False):
        """Main monitoring loop"""
        print(f"🔍 Starting conversion monitor (checking every {self.check_interval}s)")
        print(f"📋 Monitoring plan: {self.monitoring_plan}")
        print(f"⏰ Press Ctrl+C to stop\n")

        check_count = 0

        try:
            while True:
                check_count += 1
                print(f"\n{'='*80}")
                print(f"CHECK #{check_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*80}")

                # Get status
                status = self.generate_status_report()
                self.print_status_report(status)

                # Generate Claude prompt
                claude_prompt = self.create_claude_prompt(status)
                print(f"💬 Status: {claude_prompt}\n")

                # If not running and not complete, or crashed, alert
                if status['has_crashed'] or (not status['is_running'] and status['progress']['remaining'] > 0):
                    print("⚠️  ACTION REQUIRED!")
                    if not notify_only:
                        print(f"\n💡 You should now run: claude code")
                        print(f"   And tell Claude: Check the PDF conversion status\n")

                # Check if complete
                if not status['is_running'] and status['progress']['remaining'] <= 0:
                    print("✅ CONVERSION COMPLETE!")
                    print(f"   Total converted: {status['converted_files']}")
                    print(f"   Total errors: {status['error_count']}")
                    print(f"\n🎉 Monitoring complete!")
                    break

                # Wait for next check
                next_check = datetime.now() + timedelta(seconds=self.check_interval)
                print(f"⏰ Next check at: {next_check.strftime('%H:%M:%S')}")
                print(f"   Sleeping for {self.check_interval}s...")
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print(f"\n\n⏹️  Monitoring stopped by user")
            print(f"   Total checks performed: {check_count}")
            print(f"\n💡 To resume: python {sys.argv[0]} --check-interval {self.check_interval}")


def main():
    parser = argparse.ArgumentParser(
        description='Monitor PDF to Markdown conversion process'
    )
    parser.add_argument(
        '--check-interval',
        type=int,
        default=3600,
        help='Interval between checks in seconds (default: 3600 = 1 hour)'
    )
    parser.add_argument(
        '--notify-only',
        action='store_true',
        help='Only show status without prompting for Claude interaction'
    )
    parser.add_argument(
        '--check-once',
        action='store_true',
        help='Run a single check and exit'
    )

    args = parser.parse_args()

    monitor = ConversionMonitor(check_interval=args.check_interval)

    if args.check_once:
        # Single check mode
        status = monitor.generate_status_report()
        monitor.print_status_report(status)
        claude_prompt = monitor.create_claude_prompt(status)
        print(f"💬 Suggested action: {claude_prompt}\n")
    else:
        # Continuous monitoring mode
        monitor.run_monitoring_loop(notify_only=args.notify_only)


if __name__ == '__main__':
    main()
