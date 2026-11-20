import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY = os.environ.get("SECRET_KEY", "kisan-mandi-bhav-dev-key")
# Database: SQLite by default (free, no XAMPP needed). MySQL if env vars set.
DB_TYPE = os.environ.get("DB_TYPE", "sqlite")  # sqlite | mysql
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DB = os.environ.get("MYSQL_DB", "crop_price_db")
SQLITE_PATH = os.path.join(BASE_DIR, "app.db")
# Free alerts: Gmail SMTP (set env, never hardcode password) + Telegram bot token (env)
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
# Open-Meteo: free, no API key needed
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
