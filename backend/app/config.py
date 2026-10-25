import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "./data/wind.db")
    CORS_ORIGINS = [
        o.strip()
        for o in os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
        if o.strip()
    ]
    ADMIN_REFRESH_SECRET = os.environ.get("ADMIN_REFRESH_SECRET", "")
    ELEXON_API_BASE_URL = os.environ.get(
        "ELEXON_API_BASE_URL", "https://data.elexon.co.uk/bmrs/api/v1"
    )
    DECISION_CUTOFF_LOCAL_TIME = os.environ.get("DECISION_CUTOFF_LOCAL_TIME", "11:00")
    DECISION_DAY_OFFSET = int(os.environ.get("DECISION_DAY_OFFSET", "-1"))
    DECISION_TZ = "Europe/London"
    MAPE_ACTUAL_FLOOR_MW = float(os.environ.get("MAPE_ACTUAL_FLOOR_MW", "50"))
    SCHEDULER_ENABLED = os.environ.get("SCHEDULER_ENABLED", "true").lower() == "true"
    REFRESH_CRON_HOUR = int(os.environ.get("REFRESH_CRON_HOUR", "6"))
    REFRESH_CRON_MINUTE = int(os.environ.get("REFRESH_CRON_MINUTE", "0"))
    RATELIMIT_DEFAULT = os.environ.get("RATELIMIT_DEFAULT", "120 per minute")
    TESTING = False


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False


class TestConfig(Config):
    TESTING = True
    DATABASE_PATH = ":memory:"
    SCHEDULER_ENABLED = False
    ADMIN_REFRESH_SECRET = "test-admin-secret"
    RATELIMIT_ENABLED = False  # flask-limiter reads this from app.config
