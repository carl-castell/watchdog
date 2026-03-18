#!/usr/bin/env python3
"""
app.py — entry point.
Wires config, checker, notifier, scheduler and messages together.
"""
import logging
import random
import signal
import sys
import time
from datetime import datetime, timedelta

from config import CHECK_INTERVAL, RANDOM_JITTER, ALERT_COOLDOWN
from messages import msgs
from core.checker import check_with_retries
from core.notifier import send_telegram
from core.scheduler import next_report_time, get_uptime


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

log = logging.getLogger("stock_monitor")
log.setLevel(logging.DEBUG)
_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                         datefmt="%Y-%m-%d %H:%M:%S")
_sh = logging.StreamHandler(sys.stdout)
_sh.setFormatter(_fmt)
log.addHandler(_sh)

# Optional file logging — set SM_LOG_FILE in .env
from config import LOG_FILE
if LOG_FILE:
    _fh = logging.FileHandler(LOG_FILE)
    _fh.setFormatter(_fmt)
    log.addHandler(_fh)


# ---------------------------------------------------------------------------
# Graceful shutdown
# ---------------------------------------------------------------------------

_running = True


def _handle_signal(signum, _frame):
    global _running
    log.info("Received signal %s — shutting down.", signum)
    _running = False


signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    global _running
    now = datetime.now()
    log.info("Stock monitor starting.")
    send_telegram(msgs("startup", now=now, uptime=get_uptime()))

    was_in_stock  = None
    checks        = 0
    errors        = 0
    next_report   = next_report_time(now)
    last_alert_at = 0.0

    while _running:
        checks += 1

        try:
            in_stock = check_with_retries()
        except Exception as exc:
            errors += 1
            log.error("Fetch failed: %s", exc)
            send_telegram(msgs("fetch_error", errors=errors, exc=exc))
        else:
            if in_stock:
                if was_in_stock is not True:
                    if time.time() - last_alert_at >= ALERT_COOLDOWN:
                        log.info("BACK IN STOCK!")
                        send_telegram(msgs("in_stock"))
                        last_alert_at = time.time()
                was_in_stock = True
            else:
                if was_in_stock is True:
                    log.info("Went back out of stock.")
                    send_telegram(msgs("out_of_stock_again"))
                elif was_in_stock is None:
                    log.info("Initial check: OUT OF STOCK")
                was_in_stock = False
            log.debug("Check #%d: %s", checks, "IN STOCK" if in_stock else "OUT OF STOCK")

        # Daily report
        now = datetime.now()
        if now >= next_report:
            log.info("Sending daily report.")
            send_telegram(msgs("daily_report", now=now, was_in_stock=was_in_stock,
                               checks=checks, errors=errors))
            checks = 0
            errors = 0
            next_report = next_report_time(now + timedelta(seconds=10))

        # Sleep in 1s increments for fast signal response
        delay = CHECK_INTERVAL + random.randint(0, RANDOM_JITTER)
        deadline = time.time() + delay
        while _running and time.time() < deadline:
            time.sleep(1)

    log.info("Stock monitor stopped.")
    send_telegram(msgs("stopped"))


if __name__ == "__main__":
    main()
