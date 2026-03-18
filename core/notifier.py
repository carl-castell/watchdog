"""
core/notifier.py — Telegram notification sender.
"""
import logging

import requests

from config import BOT_TOKEN, CHAT_ID

log = logging.getLogger("stock_monitor")


def send_telegram(message):
    """Send an HTML-formatted message to the configured Telegram chat."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=10)
        if resp.status_code != 200:
            log.warning("Telegram API returned %s: %s", resp.status_code, resp.text)
    except Exception as exc:
        log.error("Telegram send failed: %s", exc)
