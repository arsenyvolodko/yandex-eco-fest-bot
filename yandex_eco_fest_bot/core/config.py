import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent.parent
MEDIA_DIR = BASE_DIR / "media"

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Database
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")

# ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID"))
# ADMIN_TG_URL = os.environ.get("ADMIN_URL", "https://t.me/arseny_volodko")
# BOT_URL = os.environ.get("BOT_URL", "https://t.me/CyberNexVpnBot")
# BOT_ID = int(os.environ.get("BOT_ID"))
