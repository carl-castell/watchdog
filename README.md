# Stock Monitor

A lightweight Python script that watches a product page for an in-stock indicator and sends a Telegram alert the moment it appears. Built to run 24/7 on a Raspberry Pi.

---

## Project Structure
```
stock-monitor/
├── app.py               # Entry point, main loop, signal handling
├── config.py            # Loads .env and exposes all settings
├── messages.py          # All Telegram notification templates
├── requirements.txt
├── .env.example         # Copy to .env and fill in your values
└── core/
    ├── checker.py       # HTTP fetch, stock detection, retries
    ├── notifier.py      # Telegram sender
    └── scheduler.py     # Daily report timing and uptime helper
```

---

## Setup

### 1. Clone the repo
```bash
git clone git@github.com:your-username/stock-monitor.git
cd stock-monitor
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure
```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
# Required
SM_URL=https://example.com/product-page/
SM_BOT_TOKEN=your_telegram_bot_token
SM_CHAT_ID=your_telegram_chat_id

# Optional
SM_PRODUCT_NAME=My Product
SM_IN_STOCK_PHRASE=schema.org/instock
SM_INTERVAL=60
SM_JITTER=15
SM_REPORT_HOUR=20
```

### 4. Run
```bash
python app.py
```

---

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `SM_URL` | — | Product page URL to monitor (**required**) |
| `SM_BOT_TOKEN` | — | Telegram bot token (**required**) |
| `SM_CHAT_ID` | — | Telegram chat ID (**required**) |
| `SM_PRODUCT_NAME` | `Product` | Display name in notifications |
| `SM_IN_STOCK_PHRASE` | `schema.org/instock` | Text to search for on the page |
| `SM_INTERVAL` | `60` | Seconds between checks |
| `SM_JITTER` | `15` | Random extra delay (anti-bot protection) |
| `SM_TIMEOUT` | `20` | HTTP request timeout in seconds |
| `SM_REPORT_HOUR` | `20` | Hour of day for daily report (24h) |
| `SM_MAX_RETRIES` | `3` | Retries before giving up on a check |
| `SM_RETRY_BACKOFF` | `5` | Base seconds for exponential backoff |
| `SM_ALERT_COOLDOWN` | `300` | Seconds between repeat in-stock alerts |
| `SM_USER_AGENT` | `Mozilla/5.0 (StockMonitor)` | HTTP user agent string |
| `SM_LOG_FILE` | *(empty)* | Optional path to write logs to a file |

---

## Deploying to Raspberry Pi

### First time
```bash
git clone git@github.com:your-username/stock-monitor.git
cd stock-monitor
pip install -r requirements.txt
cp .env.example .env
# edit .env with your values
python app.py
```

### Run as a systemd service (auto-start on boot)

Create `/etc/systemd/system/stock-monitor.service`:
```ini
[Unit]
Description=Stock Monitor
After=network.target

[Service]
WorkingDirectory=/home/pi/stock-monitor
ExecStart=/usr/bin/python3 /home/pi/stock-monitor/app.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Enable a
