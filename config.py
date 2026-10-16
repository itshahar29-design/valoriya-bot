import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN") or "8660553505:AAEF_NQBe9HzmpE-Fz18SAND9rq20QHZ-Wk"
OWNER_ID = int(os.getenv("OWNER_ID", "0")) if os.getenv("OWNER_ID", "").strip().isdigit() and int(os.getenv("OWNER_ID", "0")) > 0 else None
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "NAKAMA_02").lower().lstrip("@")
DB_PATH = BASE_DIR / "ritsarlar.db"

# O'yin doimiylari
MAX_LEVEL = 50
HOURLY_BASE_GOLD = 100
HOURLY_BASE_FOOD = 80
BASE_HP = 100
BASE_ATTACK = 20
BASE_DEFENSE = 10

def is_owner(user_id: int | None = None, username: str | None = None) -> bool:
    """
    Mutloq Owner (God-Mode) tekshiruvi.
    Faqatgina @NAKAMA_02 (yoki OWNER_ID) uchun ruxsat beriladi.
    Hech qanday boshqa akkaunt yoki baza yozuvi buni chetlab o'ta olmaydi.
    """
    clean_username = (username or "").lower().lstrip("@")
    if OWNER_USERNAME and clean_username == OWNER_USERNAME:
        return True
    if OWNER_ID and OWNER_ID > 0 and user_id and user_id == OWNER_ID:
        return True
    return False
