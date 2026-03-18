"""
core/scheduler.py — timing helpers for the daily report and uptime.
"""
from datetime import datetime, timedelta
from config import DAILY_REPORT_HOUR


def next_report_time(now=None):
    """Return the next datetime when the daily report should fire."""
    now = now or datetime.now()
    report = now.replace(hour=DAILY_REPORT_HOUR, minute=0, second=0, microsecond=0)
    if now >= report:
        report += timedelta(days=1)
    return report


def get_uptime():
    """Read system uptime from /proc/uptime (Linux/Raspberry Pi)."""
    try:
        seconds = float(open("/proc/uptime").read().split()[0])
        m, _ = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        return f"{d}d {h}h {m}m"
    except Exception:
        return "N/A"
