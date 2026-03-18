"""
core/checker.py — HTTP fetch and stock detection logic.
"""
import logging
import time

import requests

from config import (
    URL, IN_STOCK_PHRASE, USER_AGENT,
    TIMEOUT, MAX_RETRIES, RETRY_BACKOFF,
)

log = logging.getLogger("stock_monitor")


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
                log.warning("Attempt %d/%d failed — retrying in %ds",
                            attempt, MAX_RETRIES, wait)
                time.sleep(wait)
    raise last_exc
