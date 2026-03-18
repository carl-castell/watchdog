"""
messages.py — all Telegram notification templates in one place.
Edit copy, emojis and formatting here without touching business logic.
"""
from datetime import datetime
from config import URL, PRODUCT_NAME, MAX_RETRIES


def msgs(event, **ctx):
    now = ctx.get("now", datetime.now())

    if event == "startup":
        return (
            f"\U0001f50c <b>Watchdog awake</b>\n"
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
        return "\U0001f6d1 <b>Watchdog Stopped</b>"

    return f"[unknown event: {event}]"
