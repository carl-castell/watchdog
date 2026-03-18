"""
config.py — loads .env and exposes all SM_* constants.
Import from here in every module that needs a setting.
"""
import os
from pathlib import Path


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
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_dotenv()

# Required
URL       = os.environ["SM_URL"]
BOT_TOKEN = os.environ["SM_BOT_TOKEN"]
CHAT_ID   = os.environ["SM_CHAT_ID"]

# Optional with defaults
PRODUCT_NAME      = os.getenv("SM_PRODUCT_NAME", "Product")
IN_STOCK_PHRASE   = os.getenv("SM_IN_STOCK_PHRASE", "schema.org/instock")
CHECK_INTERVAL    = int(os.getenv("SM_INTERVAL", "60"))
RANDOM_JITTER     = int(os.getenv("SM_JITTER", "15"))
TIMEOUT           = int(os.getenv("SM_TIMEOUT", "20"))
DAILY_REPORT_HOUR = int(os.getenv("SM_REPORT_HOUR", "20"))
MAX_RETRIES       = int(os.getenv("SM_MAX_RETRIES", "3"))
RETRY_BACKOFF     = int(os.getenv("SM_RETRY_BACKOFF", "5"))
ALERT_COOLDOWN    = int(os.getenv("SM_ALERT_COOLDOWN", "300"))
USER_AGENT        = os.getenv("SM_USER_AGENT", "Mozilla/5.0 (StockMonitor)")
LOG_FILE          = os.getenv("SM_LOG_FILE", "")
