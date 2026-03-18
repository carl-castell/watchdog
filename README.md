# Watchdog

A lightweight Python script that watches a product page for an in-stock indicator and sends a Telegram alert the moment it appears. Built to run 24/7 on a Raspberry Pi.

---

## Project Structure
```
watchdog/
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
git clone https://github.com/carl-castell/watchdog.git
cd watchdog
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
| `SM_USER_AGENT` | `Mozilla/5.0 (Watchdog)` | HTTP user agent string |
| `SM_LOG_FILE` | *(empty)* | Optional path to write logs to a file |

---

## Deploying to Raspberry Pi

### First time
```bash
git clone https://github.com/carl-castell/watchdog.git
cd watchdog
pip install -r requirements.txt
cp .env.example .env
# edit .env with your values
python app.py
```

### Run as a systemd service (auto-start on boot)

Create `/etc/systemd/system/watchdog.service`:
```ini
[Unit]
Description=Watchdog
After=network.target

[Service]
WorkingDirectory=/home/pi/watchdog
ExecStart=/usr/bin/python3 /home/pi/watchdog/app.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable watchdog
sudo systemctl start watchdog
```

Check logs:
```bash
sudo journalctl -u watchdog -f
```

---

## Updating

### On your PC — push changes
```bash
git add .
git commit -m "your message"
git push
```

### On the Pi — pull and restart
```bash
cd ~/watchdog
git pull
sudo systemctl restart watchdog
```

### Optional shortcut

Add to `~/.bashrc` on the Pi:
```bash
alias sm-update="cd ~/watchdog && git pull && sudo systemctl restart watchdog"
```

Then just run:
```bash
sm-update
```

---

## Notifications

| Event | When |
|---|---|
| 🔌 **Startup** | Script starts |
| 🚨 **Back in Stock** | In-stock phrase detected |
| 📦 **Out of Stock Again** | Was in stock, now gone |
| ⚠️ **Fetch Failed** | All retries exhausted |
| 📊 **Daily Report** | Every day at `SM_REPORT_HOUR` |
| 🛑 **Stopped** | Graceful shutdown |

All message text lives in `messages.py` — edit copy and emojis there without touching any logic.
