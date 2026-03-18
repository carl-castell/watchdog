# Stock Monitor

A lightweight Python script that watches a product page for an in-stock indicator and sends a Telegram alert the moment it appears. Built to run 24/7 on a Raspberry Pi.

## Project Structure

stock-monitor/
  app.py            - Entry point, main loop, signal handling
  config.py         - Loads .env and exposes all settings
  messages.py       - All Telegram notification templates
  requirements.txt
  .env.example      - Copy to .env and fill in your values
  core/
    checker.py      - HTTP fetch, stock detection, retries
    notifier.py     - Telegram sender
    scheduler.py    - Daily report timing and uptime helper

## Setup

1. Clone the repo
   git clone git@github.com:your-username/stock-monitor.git
   cd stock-monitor

2. Install dependencies
   pip install -r requirements.txt

3. Configure
   cp .env.example .env
   (edit .env with your values)

4. Run
   python app.py

## Configuration Reference

Variable              Default                    Description
SM_URL                -                          Product page URL (required)
SM_BOT_TOKEN          -                          Telegram bot token (required)
SM_CHAT_ID            -                          Telegram chat ID (required)
SM_PRODUCT_NAME       Product                    Display name in notifications
SM_IN_STOCK_PHRASE    schema.org/instock         Text to search for on the page
SM_INTERVAL           60                         Seconds between checks
SM_JITTER             15                         Random extra delay (anti-bot)
SM_TIMEOUT            20                         HTTP request timeout (seconds)
SM_REPORT_HOUR        20                         Hour for daily report (24h)
SM_MAX_RETRIES        3                          Retries before giving up
SM_RETRY_BACKOFF      5                          Base seconds for backoff
SM_ALERT_COOLDOWN     300                        Seconds between repeat alerts
SM_USER_AGENT         Mozilla/5.0 (StockMonitor) HTTP user agent
SM_LOG_FILE           (empty)                    Optional log file path

## Deploying to Raspberry Pi

First time:
  git clone git@github.com:your-username/stock-monitor.git
  cd stock-monitor
  pip install -r requirements.txt
  cp .env.example .env
  python app.py

Run as a systemd service (/etc/systemd/system/stock-monitor.service):

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

Then:
  sudo systemctl daemon-reload
  sudo systemctl enable stock-monitor
  sudo systemctl start stock-monitor

Check logs:
  sudo journalctl -u stock-monitor -f

## Updating

On your PC - push changes:
  git add .
  git commit -m "your message"
  git push

On the Pi - pull and restart:
  cd ~/stock-monitor
  git pull
  sudo systemctl restart stock-monitor

Optional shortcut in ~/.bashrc on the Pi:
  alias sm-update="cd ~/stock-monitor && git pull && sudo systemctl restart stock-monitor"

Then just run: sm-update

## Notifications

Event               When
Startup             Script starts
Back in Stock       In-stock phrase detected
Out of Stock Again  Was in stock, now gone
Fetch Failed        All retries exhausted
Daily Report        Every day at SM_REPORT_HOUR
Stopped             Graceful shutdown

All message text lives in messages.py - edit copy and emojis there without touching any logic.
