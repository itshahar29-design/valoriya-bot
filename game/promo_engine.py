# =====================================================================
# VALORIYA: PROMO-KODLAR VA REKLAMA TRAFIGI MOTOR (AD INGESTION ENGINE)
# =====================================================================
# Reklama (Target, Bloggerlar, Telegram kanallar, TikTok) trafigini qabul qilish.
# Har bir reklama oqimi maxsus sovg'alar va start bonuslari bilan kutib olinadi.
# =====================================================================

from typing import Dict, Any, Tuple, Optional

OFFICIAL_PROMO_CODES = {
    "VALORIYA2026": {
        "gold": 2500,
        "gems": 20,
        "potions": 5,
        "desc": "🌟 Rasmiy Start Bonusi: 2,500 Oltin + 20 Javohir + 5 Eliksir!",
        "max_uses": 100000,
        "campaign": "official_launch"
    },
    "NAKAMA": {
        "gold": 5000,
        "gems": 50,
        "potions": 10,
        "desc": "👑 Yaratuvchi Maxsus Sovg'asi: 5,000 Oltin + 50 Javohir!",
        "max_uses": 50000,
        "campaign": "owner_exclusive"
    },
    "START100": {
        "gold": 1500,
        "gems": 10,
        "potions": 3,
        "desc": "🗡 Yangi Jangchi Paketi: 1,500 Oltin + 10 Javohir!",
        "max_uses": 1000000,
        "campaign": "starter_pack"
    },
    "TELEGRAM": {
        "gold": 2000,
        "gems": 15,
        "potions": 4,
        "desc": "✈️ Telegram Hamjamiyati Bonusi: 2,000 Oltin + 15 Javohir!",
        "max_uses": 500000,
        "campaign": "tg_ads"
    },
    "TIKTOK": {
        "gold": 3000,
        "gems": 25,
        "potions": 6,
        "desc": "🎵 TikTok Sarguzashtchilar Sovg'asi: 3,000 Oltin + 25 Javohir!",
        "max_uses": 500000,
        "campaign": "tiktok_influencer"
    },
    "YOUTUBE": {
        "gold": 3500,
        "gems": 30,
        "potions": 8,
        "desc": "📺 YouTube Obunachilar Paketi: 3,500 Oltin + 30 Javohir!",
        "max_uses": 500000,
        "campaign": "youtube_partner"
    }
}

def get_promo_info(code: str) -> Optional[Dict[str, Any]]:
    clean_code = code.strip().upper()
    return OFFICIAL_PROMO_CODES.get(clean_code)
