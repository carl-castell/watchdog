# Stock Monitor

Checks a product page for out-of-stock phrases and sends a Telegram alert the moment they disappear (= back in stock).

## How It Works

1. Fetches the page every ~60 seconds
2. Searches for "sold out" and "not in stock" in the page text
3. If those phrases disappear -> Telegram alert
4. If they come back -> notifies you of that too
5. Daily status report at 8 PM

## Setup

```
git clone https://github.com/yourusername/stock-monitor.git
cd stock-monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
python stock_monitor.py
```

## systemd Service (Raspberry Pi)

Create /etc/systemd/system/stockmonitor.service:

```
[Unit]
Description=Stock Monitor
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/home/pi/stock-monitor/venv/bin/python /home/pi/stock-monitor/stock_monitor.py
WorkingDirectory=/home/pi/stock-monitor
Restart=always
RestartSec=30
User=pi

[Install]
WantedBy=multi-user.target
```

Then:
```
sudo systemctl daemon-reload
sudo systemctl enable stockmonitor
sudo systemctl start stockmonitor
journalctl -u stockmonitor -f
```

## Configuration (.env)

| Variable | Required | Default | Description |
|---|---|---|---|
| SM_URL | Yes | - | Product page URL |
| SM_BOT_TOKEN | Yes | - | Telegram bot token |
| SM_CHAT_ID | Yes | - | Telegram chat ID |
| SM_OUT_OF_STOCK_PHRASES | | sold out,not in stock | Comma-separated phrases |
| SM_INTERVAL | | 60 | Seconds between checks |
| SM_JITTER | | 15 | Random extra seconds |
| SM_REPORT_HOUR | | 20 | Daily report hour (24h) |
| SM_MAX_RETRIES | | 3 | Retries before error alert |
| SM_ALERT_COOLDOWN | | 300 | Min seconds between alerts |
| SM_LOG_FILE | | empty | Log to file (optional) |
