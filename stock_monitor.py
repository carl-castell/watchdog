#!/usr/bin/env python3
"""
Stock Monitor - checks a product page for an in-stock indicator
and sends a Telegram alert when it appears (= back in stock).
"""
import logging, os, random, signal, sys, time
from datetime import datetime, timedelta
from pathlib import Path
import requests


# ---------------------------------------------------------------------------
# LOAD .env
# ---------------------------------------------------------------------------

def load_dotenv(path=".env"):
    env_path = Path(path)
    if not env_path.is_file():
        env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.is_file():
        return
    with open(env_path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip(chr(34) + chr(39)))


load_dotenv()


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

URL              = os.environ["SM_URL"]
BOT_TOKEN        = os.environ["SM_BOT_TOKEN"]
CHAT_ID          = os.environ["SM_CHAT_ID"]
PRODUCT_NAME     = os.getenv("SM_PRODUCT_NAME", "Product")

IN_STOCK_PHRASE  = os.getenv("SM_IN_STOCK_PHRASE", "schema.org/instock")

CHECK_INTERVAL   = int(os.getenv("SM_INTERVAL", "60"))
RANDOM_JITTER    = int(os.getenv("SM_JITTER", "15"))
TIMEOUT          = int(os.getenv("SM_TIMEOUT", "20"))
DAILY_REPORT_HOUR = int(os.getenv("SM_REPORT_HOUR", "20"))
MAX_RETRIES      = int(os.getenv("SM_MAX_RETRIES", "3"))
RETRY_BACKOFF    = int(os.getenv("SM_RETRY_BACKOFF", "5"))
ALERT_COOLDOWN   = int(os.getenv("SM_ALERT_COOLDOWN", "300"))
USER_AGENT       = os.getenv("SM_USER_AGENT", "Mozilla/5.0 (StockMonitor)")
LOG_FILE         = os.getenv("SM_LOG_FILE", "")


# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

log = logging.getLogger("stock_monitor")
log.setLevel(logging.DEBUG)
_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                         datefmt="%Y-%m-%d %H:%M:%S")
_sh = logging.StreamHandler(sys.stdout)
_sh.setFormatter(_fmt)
log.addHandler(_sh)
if LOG_FILE:
    _fh = logging.FileHandler(LOG_FILE)
    _fh.setFormatter(_fmt)
    log.addHandler(_fh)


# ---------------------------------------------------------------------------
# GRACEFUL SHUTDOWN
# ---------------------------------------------------------------------------

_running = True


def _handle_signal(signum, _frame):
    global _running
    log.info("Received signal %s - shutting down.", signum)
    _running = False


signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)


# ---------------------------------------------------------------------------
# MESSAGES  — edit all notification text here
# ---------------------------------------------------------------------------

def msgs(event, **ctx):
    now = ctx.get("now", datetime.now())

    if event == "startup":
        return (
            f"\U0001f50c <b>Stock Monitor Online</b>\n"
            f"<code>{now:%Y-%m-%d %H:%M}</code> \u2014 uptime: {ctx['uptime']}\n"
            f"\n"
            f"<b>Watching:</b> <a href=\"{URL}\">{PRODUCT_NAME}</a>"
        )
    if event == "in_stock":
        return (
            f"\U0001f6a8 <b>BACK IN STOCK!</b> \U0001f6a8\n"
            f"\n"
            f"<a href=\"{URL}\">{PRODUCT_NAME}</a>\n"
            f"\n"
            f"<i>GO GO GO!</i>"
        )
    if event == "out_of_stock_again":
        return (
            f"\U0001f4e6 <b>Out of Stock Again</b>\n"
            f"<a href=\"{URL}\">{PRODUCT_NAME}</a>"
        )
    if event == "fetch_error":
        return (
            f"\u26a0\ufe0f <b>Fetch Failed</b>\n"
            f"Retries: <code>{MAX_RETRIES}</code>\n"
            f"Total errors: <code>{ctx['errors']}</code>\n"
            f"<i>{ctx['exc']}</i>"
        )
    if event == "daily_report":
        stock_str = (
            "Unknown" if ctx["was_in_stock"] is None
            else "\u2705 IN STOCK" if ctx["was_in_stock"]
            else "\u274c Out of stock"
        )
        return (
            f"\U0001f4ca <b>Daily Report</b> \u2014 <i>{now:%Y-%m-%d %H:%M}</i>\n"
            f"\n"
            f"<b>Product:</b> <a href=\"{URL}\">{PRODUCT_NAME}</a>\n"
            f"<b>Status:</b> {stock_str}\n"
            f"<b>Checks:</b> <code>{ctx['checks']}</code>\n"
            f"<b>Errors:</b> <code>{ctx['errors']}</code>"
        )
    if event == "stopped":
        return "\U0001f6d1 <b>Stock Monitor Stopped</b>"

    return f"[unknown event: {event}]"


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }, timeout=10)
        if resp.status_code != 200:
            log.warning("Telegram API returned %s", resp.status_code)
    except Exception as exc:
        log.error("Telegram send failed: %s", exc)


def check_stock():
    """Return True if the in-stock phrase is present on the page."""
    resp = requests.get(URL, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    resp.raise_for_status()
    return IN_STOCK_PHRASE.lower() in resp.text.lower()


def check_with_retries():
    """Try up to MAX_RETRIES times with exponential backoff."""
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return check_stock()
        except Exception as exc:
            last_exc = exc
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF * (2 ** (attempt - 1))
                log.warning("Attempt %d/%d failed - retrying in %ds",
                            attempt, MAX_RETRIES, wait)
                time.sleep(wait)
    raise last_exc


def next_report_time(now):
    report = now.replace(hour=DAILY_REPORT_HOUR, minute=0, second=0, microsecond=0)
    if now >= report:
        report += timedelta(days=1)
    return report


def get_uptime():
    try:
        s = float(open("/proc/uptime").read().split()[0])
        m, _ = divmod(int(s), 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        return f"{d}d {h}h {m}m"
    except Exception:
        return "N/A"


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    global _running
    now = datetime.now()
    log.info("Starting stock monitor for: %s", URL)
    log.info("In-stock phrase: %s", IN_STOCK_PHRASE)

    send_telegram(msgs("startup", now=now, uptime=get_uptime()))

    was_in_stock = None
    checks = 0
    errors = 0
    next_report = next_report_time(now)
    last_alert_time = 0.0

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
                status = "IN STOCK"
                if was_in_stock is not True:
                    if time.time() - last_alert_time >= ALERT_COOLDOWN:
                        log.info("BACK IN STOCK!")
                        send_telegram(msgs("in_stock"))
                        last_alert_time = time.time()
                was_in_stock = True
            else:
                status = "OUT OF STOCK"
                if was_in_stock is None:
                    log.info("Initial check: %s", status)
                elif was_in_stock is True:
                    log.info("Product went back out of stock.")
                    send_telegram(msgs("out_of_stock_again"))
                was_in_stock = False
            log.debug("Check #%d: %s", checks, status)

        # ---- daily report ----
        now = datetime.now()
        if now >= next_report:
            log.info("Sending daily report.")
            send_telegram(msgs("daily_report", now=now, was_in_stock=was_in_stock,
                               checks=checks, errors=errors))
            checks = 0
            errors = 0
            next_report = next_report_time(now + timedelta(seconds=10))

        # sleep in 1s increments for fast signal response
        delay = CHECK_INTERVAL + random.randint(0, RANDOM_JITTER)
        deadline = time.time() + delay
        while _running and time.time() < deadline:
            time.sleep(1)

    log.info("Stock monitor stopped.")
    send_telegram(msgs("stopped"))


if __name__ == "__main__":
    main()
