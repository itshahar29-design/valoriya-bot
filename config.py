import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN") or "8660553505:AAEF_NQBe9HzmpE-Fz18SAND9rq20QHZ-Wk"
OWNER_ID = int(os.getenv("OWNER_ID", "0")) if os.getenv("OWNER_ID", "").strip().isdigit() else None
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "NAKAMA_02").lower().lstrip("@")
DB_PATH = BASE_DIR / "ritsarlar.db"

# O'yin doimiylari
MAX_LEVEL = 50
HOURLY_BASE_GOLD = 100
HOURLY_BASE_FOOD = 80
BASE_HP = 100
BASE_ATTACK = 20
BASE_DEFENSE = 10
